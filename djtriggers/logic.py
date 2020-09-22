import datetime
from inspect import isabstract
from logging import getLogger

from dateutil.relativedelta import relativedelta
from django.apps import apps
from django.conf import settings
from django.db import connections
from django.db.models import Q
from lockfile import AlreadyLocked, FileLock, LockTimeout

from djtriggers.exceptions import ProcessError, ProcessLaterError
from djtriggers.models import Trigger

logger = getLogger(__name__)


def clean_triggers():
    """
    Clean old processed triggers from the database.

    This uses the DJTRIGGERS_TYPE_TO_TABLE setting, which has information about which trigger has information in which
    table. This setting is a dict with the trigger types as keys and two kwargs for values:
        - a string containing the table where the trigger information is stored (with a trigger_ptr_id to link it)
        - a tuple containing elements of two possible types:
            - a string containing the table where the trigger information is stored (with a trigger_ptr_id to link it)
            - a tuple containing a tablename and an id field

    An example:
    DJTRIGGERS_TYPE_TO_TABLE = {
        'simple_trigger': 'simple_trigger_table',
        'complex_trigger': ('complex_trigger_table1', 'complex_trigger_table2'),
        'complexer_trigger': (('complexer_trigger_table1', 'complexer_trigger_id'), 'complexer_trigger_table2'),
    }
    """
    cursor = connections["default"].cursor()

    # Get triggers to be deleted
    to_be_deleted = Trigger.objects.filter(
        date_processed__lte=datetime.now() - relativedelta(months=2)
    )
    logger.info("Deleting %s records" % to_be_deleted.count())

    # Delete each trigger
    for trigger in to_be_deleted:
        # Delete the specific trigger information
        table = settings.DJTRIGGERS_TYPE_TO_TABLE[trigger.trigger_type]
        if isinstance(table, tuple):
            for t in table:
                if isinstance(t, tuple):
                    cursor.execute(
                        "DELETE FROM %s WHERE %s = %s" % (t[0], t[1], trigger.id)
                    )
                else:
                    cursor.execute(
                        "DELETE FROM %s WHERE trigger_ptr_id = %s" % (t, trigger.id)
                    )
        else:
            cursor.execute(
                "DELETE FROM %s WHERE trigger_ptr_id = %s" % (table, trigger.id)
            )

        # Delete the trigger from the main table
        trigger.delete()


def process_triggers(**kwargs):
    """
    Process all triggers in order of trigger type. This blocks while
    processing the triggers.
    """
    lock = FileLock("process_triggers")

    try:
        lock.acquire(-1)
    except (AlreadyLocked, LockTimeout):
        return

    # Get statsd if necessary
    if kwargs.get("use_statsd"):
        from django_statsd.clients import statsd

    now = datetime.datetime.now()
    logger.info("Processing all triggers from %s" % now)
    try:
        # Get all database models
        for trigger_model in apps.get_models():
            # Check whether it's a trigger
            if (
                not issubclass(trigger_model, Trigger)
                or getattr(trigger_model, "typed", None) is None
                or isabstract(trigger_model)
            ):
                continue

            # Get all triggers of this type that need to be processed
            triggers = trigger_model.objects.filter(
                Q(process_after__isnull=True) | Q(process_after__lt=now),
                date_processed__isnull=True,
            )
            logger.info(
                "Start processing %d triggers of type %s",
                triggers.count(),
                trigger_model.typed,
            )
            count_done, count_error, count_exception = 0, 0, 0

            # Process each trigger
            for trigger in triggers:
                try:
                    trigger.process()

                    # Send stats to statsd if necessary
                    if kwargs["use_statsd"]:
                        statsd.incr("triggers.%s.processed" % trigger.trigger_type)
                        if trigger.date_processed and trigger.process_after:
                            statsd.timing(
                                "triggers.%s.process_delay_seconds"
                                % trigger.trigger_type,
                                (
                                    trigger.date_processed - trigger.process_after
                                ).total_seconds(),
                            )
                # The trigger didn't need processing yet
                except ProcessLaterError:
                    pass
                # The trigger raised an (expected) error while processing
                except ProcessError:
                    count_error += 1
                # A general exception occurred
                except Exception as e:
                    count_exception += 1
                    logger.exception(
                        "Processing of %s %s raised a %%s"
                        % (trigger_model.typed, trigger.pk),
                        type(e).__name__,
                    )
                # The trigger was successfully processed
                else:
                    count_done += 1

            logger.info(
                "success: %s, error: %s, exception: %s",
                count_done,
                count_error,
                count_exception,
            )
    finally:
        lock.release()


def process_trigger(trigger_id, trigger_app_label, trigger_class, *args, **kwargs):
    try:
        apps.get_model(trigger_app_label, trigger_class).objects.get(
            id=trigger_id
        ).process(*args, **kwargs)
    except Trigger.DoesNotExist:
        pass

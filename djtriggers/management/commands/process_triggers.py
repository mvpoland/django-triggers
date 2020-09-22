from optparse import make_option

from django.core.management.base import NoArgsCommand

from djtriggers.logic import process_trigger


class Command(NoArgsCommand):
    option_list = NoArgsCommand.option_list + (
        make_option(
            "--use-statsd",
            dest="use_statsd",
            action="store_true",
            default=False,
            help="Send stats about processing to Statsd",
        ),
    )

    def handle_noargs(self, **options):
        process_trigger(**options)

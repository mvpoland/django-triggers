from builtins import object
from django.utils import timezone
from factory.django import DjangoModelFactory

from djtriggers.tests.models import DummyTrigger


class DummyTriggerFactory(DjangoModelFactory):
    class Meta(object):
        model = DummyTrigger

    trigger_type = 'dummy_trigger_test'
    source = 'tests'
    date_received = timezone.now()
    date_processed = None
    process_after = None

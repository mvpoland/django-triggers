from datetime import timedelta
from mock import patch

from django.test import override_settings
from django.test.testcases import TestCase
from django.utils import timezone

from djtriggers.logic import process_triggers
from djtriggers.tests.factories.triggers import DummyTriggerFactory


class SynchronousExecutionTest(TestCase):

    def test_process_after_now(self):
        trigger = DummyTriggerFactory()
        process_triggers()
        trigger.refresh_from_db()

        assert trigger.date_processed is not None

    def test_process_after_yesterday(self):
        trigger = DummyTriggerFactory(process_after=timezone.now() - timedelta(days=1))
        process_triggers()
        trigger.refresh_from_db()

        assert trigger.date_processed is not None

    def test_process_after_tomorrow(self):
        trigger = DummyTriggerFactory(process_after=timezone.now() + timedelta(days=1))
        process_triggers()
        trigger.refresh_from_db()
        assert trigger.date_processed is None

    def test_already_processed(self):
        now = timezone.now()
        trigger = DummyTriggerFactory(date_processed=now)
        process_triggers()
        trigger.refresh_from_db()
        assert trigger.date_processed == now

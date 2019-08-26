from datetime import datetime, timedelta
from logging import ERROR, WARNING

from mock import patch, MagicMock
from pytest import raises
from django.test import override_settings
from django.test.testcases import TestCase
from django.utils import timezone

from djtriggers.exceptions import ProcessLaterError
from djtriggers.loggers.base import TriggerLogger
from djtriggers.models import Trigger
from djtriggers.tests.factories.triggers import DummyTriggerFactory


class TriggerTest(TestCase):

    def test_handle_execution_success(self):
        trigger = DummyTriggerFactory(process_after=datetime.now() - timedelta(hours=1))
        trigger.process()

        assert trigger.date_processed is not None

    @patch.object(TriggerLogger, 'log_result')
    def test_process(self, mock_logger):
        trigger = DummyTriggerFactory()
        trigger.process(force=True)

        mock_logger.assert_called_with(trigger, trigger._process({}))

    @patch.object(TriggerLogger, 'log_result')
    def test_process_already_processed(self, mock_logger):
        """Reprocessing already processed triggers should just do nothing."""
        trigger = DummyTriggerFactory(date_processed=timezone.now())

        assert trigger.date_processed is not None
        assert not mock_logger.called

    def test_process_process_later(self):
        trigger = DummyTriggerFactory(process_after=timezone.now() + timedelta(minutes=1))
        with raises(ProcessLaterError):
            trigger.process()

    def test_process_exception_during_execution(self):
        trigger = DummyTriggerFactory()

        with patch.object(trigger, '_process', side_effect=Exception), raises(Exception):
            trigger.process(force=True)

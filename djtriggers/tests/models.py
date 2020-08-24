from builtins import object
from djtriggers.models import Trigger


class DummyTrigger(Trigger):
    class Meta(object):
        proxy = True

    typed = 'dummy_trigger'

    def _process(self, dictionary):
        pass

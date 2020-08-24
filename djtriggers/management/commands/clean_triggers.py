from django.core.management.base import NoArgsCommand

from djtriggers.logic import clean_triggers


class Command(NoArgsCommand):
    help = __doc__.strip()

    def handle_noargs(self, **options):
        clean_triggers()

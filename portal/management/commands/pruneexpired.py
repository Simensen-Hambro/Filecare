from django.core.management.base import BaseCommand, CommandError
from portal.models import Share


class Command(BaseCommand):
    help = "Prunes expired shares by deleting them and their respective UUID-directories"

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Pruning...'))
        Share.objects.prune_expired()
        self.stdout.write(self.style.SUCCESS('Pruning complete.'))

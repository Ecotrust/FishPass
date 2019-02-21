from django.core.management.base import BaseCommand
from django.conf import settings
class Command(BaseCommand):
    help = 'Delete all Focus Area records'

    def handle(self, *args, **options):
        from fishpass.models import FocusArea
        FocusArea.objects.all().delete()
        print("All Focus Area records removed from database")

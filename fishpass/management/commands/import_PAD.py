from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

class Command(BaseCommand):
    help = 'Import PAD. 1 argument - an Excel spreadsheet exported from the PAD with appropriate fields (see docs)'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)

    def handle(self, *args, **options):
        import sys
        from io import StringIO, BytesIO
        from fishpass.models import FocusArea
        from openpyxl import Workbook
        # https://openpyxl.readthedocs.io/en/stable/usage.html
        # file in:
        #   FishPASS Team Share
        #       Optipass
        #           FISHPass_Input_20180410.xls
        # NOTE: In the past, I have used xlrd - we'll see what works. xlrd is only a reader.
        #   other options include pandas (data manipulation tool), xlutils, and pyexcel

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError, DataError

class Command(BaseCommand):
    help = 'Import PAD. 1 argument - an Excel spreadsheet exported from the PAD with appropriate fields (see docs)'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)
        # test file in:
        #   FishPASS Team Share
        #       Optipass
        #           FISHPass_Input_20180410.xls

    def handle(self, *args, **options):
        import sys
        import xlrd
        from datetime import datetime
        from io import StringIO, BytesIO
        from fishpass.models import Barrier, BarrierType, BarrierStatus, OwnershipType, FocusArea, BarrierCost

        print('deleting all old barrier records')
        Barrier.objects.all().delete()

        field_lookup = {
            'PAD_ID': 'pad_id',
            'PassageID': 'passage_id',
            'StreamName': 'stream_name',
            'TributaryTo': 'tributary_to',
            'SiteName': 'site_name',
            'SiteType': 'site_type',
            'BarStatus': 'barrier_status',
            'Protocol': 'protocol',
            'AssessedBy': 'assessed_by',
            'HUC8_Code': 'huc8_code',
            'HUC8_Name': 'huc8_name',
            'County': 'county',
            'OwnershipType': 'ownership_type',
            'NHDCOMID': 'nhd_com_id',
            'NHDComMeas': 'nhd_com_meas',
            'Point_X': 'longitude',
            'Point_Y': 'latitude',
            'State': 'state',
            'Updated': 'updated',
            'HUC10_Code': 'huc10_code',
            'HUC10_Name': 'huc10_name',
            'HUC12_Code': 'huc12_code',
            'HUC12_Name': 'huc12_name',
            'ESU_COHO': 'esu_coho',
            'ESU_CHIN': 'esu_chinook',
            'ESU_STEEL': 'esu_steelhead',
            'Miles_Upst': 'upstream_miles',
            'DS_ID': 'downstream_id',
            'DS_Barrier': 'downstream_barrier_count',
        }

        print('reading PAD excel sheet')
        book = xlrd.open_workbook(options['file'])
        sheet = book.sheet_by_index(0)

        # for each line
        headers = []
        for row_num in range(sheet.nrows):
            sheet.row(row_num)
            row_dict = {}
            for col_num in range(sheet.ncols):
                if row_num == 0:
                    headers.append(sheet.cell_value(row_num,col_num))
                else:
                    if sheet.cell_value(row_num,col_num) == '':
                        row_dict[field_lookup[headers[col_num]]] = None
                    else:
                        row_dict[field_lookup[headers[col_num]]] = sheet.cell_value(row_num,col_num)
            if not row_num == 0:
                #     get or create BarrierType
                (barrierType, created) = BarrierType.objects.get_or_create(name=row_dict['site_type'])
                row_dict['site_type'] = barrierType
                #     get or create BarrierStatus
                (barrierStatus, created) = BarrierStatus.objects.get_or_create(name=row_dict['barrier_status'])
                row_dict['barrier_status'] = barrierStatus
                #     get or create OwnershipType
                try:
                    ownership_name = settings.OWNERSHIP_LOOKUP[str(int(row_dict['ownership_type']))]
                except:
                    ownsership_name = settings.OWNERSHIP_LOOKUP[settings.OWNERSHIP_DEFAULT]
                    row_dict['ownership_type'] = int(settings.OWNERSHIP_DEFAULT)
                (ownershipType, created) = OwnershipType.objects.get_or_create(id=int(row_dict['ownership_type']))
                ownershipType.name = ownership_name
                ownershipType.save()
                row_dict['ownership_type'] = ownershipType
                # parse datetime
                updated = datetime(*xlrd.xldate_as_tuple(row_dict['updated'], book.datemode))
                row_dict['updated'] = updated
                try:
                    # create Barrier
                    Barrier.objects.create(**row_dict)
                except ValueError:
                    print('row: %d, value:%s' % (row_num, row_dict))
                    import ipdb; ipdb.set_trace()

        # print('deleting mismatched barrier cost overrides')
        # for barrierCost in BarrierCost.objects.all():
        #     if Barrier.objects.filter(pad_id=barrierCost.pad_id).count() == 0:
        #         barrierCost.delete()

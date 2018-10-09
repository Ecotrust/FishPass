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
        from fishpass.models import Barrier, BarrierType, BarrierStatus, OwnershipType, FocusArea, BarrierCost, BlockedSpeciesType, TreatmentStatus

        print("IMPORTING PAD")

        field_lookup = {
            'PAD_ID': 'pad_id',
            'PassageID': 'passage_id',
            'StreamName': 'stream_name',
            'TributaryTo': 'tributary_to',
            'SiteName': 'site_name',
            'Road': 'road',                         # New in PAD - add to model!
            'PostMile': 'post_mile',                # New in PAD - add to model!
            'SiteType': 'site_type',
            'BarStatus': 'barrier_status',
            'Protocol': 'protocol',
            'AssessedBy': 'assessed_by',
            'SpeciesBlocked': 'species_blocked',    # New in PAD - add to model!
            'Notes': 'notes',                       # New in PAD - add to model!
            'TrtStatus': 'treatment_status',        # New in PAD - add to model!
            'TrtRecom': 'treatment_recommendation', # New in PAD - add to model!
            'Photo': 'image_link',                  # New in PAD - add to model!
            'HUC8_Code': 'huc8_code',
            'HUC8_Name': 'huc8_name',
            'HUC10_Code': 'huc10_code',
            'HUC10_Name': 'huc10_name',
            'HUC12_Code': 'huc12_code',
            'HUC12_Name': 'huc12_name',
            'County': 'county',
            'OwnershipCodePAD': 'ownership_type',
            'NHDCOMID': 'nhd_com_id',
            'NHDComMeas': 'nhd_com_meas',
            'Point_X': 'longitude',
            'Point_Y': 'latitude',
            'Miles_Upst': 'upstream_miles',
            'DS_ID': 'downstream_id',
            'DS_Num': 'downstream_barrier_count',
            'ESU_COHO': 'esu_coho',
            'ESU_STEEL': 'esu_steelhead',
            'ESU_CHIN': 'esu_chinook',
            'ACCESSIBLE': 'accessible',             # New in PAD - add to model!
            'LIKELYEXP': 'likely_exp',              # New in PAD - add to model!
            'OwnershipType': 'ownership_type',              # Missing in latest PAD
            'DS_Barrier': 'downstream_barrier_count',       # Missing in latest PAD
            'Updated': 'updated',                           # Missing in latest PAD
            'State': 'state',                               # Missing in latest PAD
        }

        REQUIRED_MODEL_FIELDS = [
            'pad_id',
            'site_type',
            'barrier_status',
            'longitude',
            'latitude',
            'upstream_miles',
        ]

        required_field_reverse_lookup = {}
        for x in REQUIRED_MODEL_FIELDS:
            required_field_reverse_lookup[x] = [y for y in field_lookup.keys() if x == field_lookup[y]]

        warnings = []
        errors = []

        try:
            book = xlrd.open_workbook(options['file'])
            sheet = book.sheet_by_index(0)
        except FileNotFoundError:
            errors.append('%s not found' % options['file'])
            print(errors[-1])
            sys.exit(errors[-1])
        except:
            errors.append('Could not open %s as .xls or workbook does not have a worksheet.' % options['file'])
            print(errors[-1])
            sys.exit(errors[-1])

        # for each line
        headers = []
        import_count = 0
        for row_num in range(sheet.nrows):
            sheet.row(row_num)
            row_dict = {}
            for col_num in range(sheet.ncols):
                if row_num == 0:
                    headers.append(sheet.cell_value(row_num,col_num))
                    if sheet.cell_value(row_num,col_num) not in field_lookup.keys():
                        warnings.append('%s not in list of accepted column names. Column will be ignored.')
                        print(warnings[-1])
                else:
                    if sheet.cell_value(row_num,col_num) == '':
                        row_dict[field_lookup[headers[col_num]]] = None
                    else:
                        row_dict[field_lookup[headers[col_num]]] = sheet.cell_value(row_num,col_num)
            # Check that required Fields are present in
            if row_num == 0:
                for required_field in REQUIRED_MODEL_FIELDS:
                    available_PAD_options = required_field_reverse_lookup[required_field]
                    match_found = False
                    for option in available_PAD_options:
                        if option in headers:
                            match_found = True
                    if not match_found:
                        if len(available_PAD_options) > 1:
                            either = 'either '
                        else:
                            either = ''
                        errors.append('Could not find required header %s%s' % (either, ' or '.join(available_PAD_options)))
                        print(errors[-1])
                if len(errors) > 0:
                    sys.exit('; '.join(errors))
                else:
                    print('deleting all old barrier records')
                    Barrier.objects.all().delete()
            else:
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
                if 'species_blocked' in row_dict.keys() and row_dict['species_blocked']:
                    (species_block_type, created) = BlockedSpeciesType.objects.get_or_create(name=row_dict['species_blocked'].lower().title())
                    row_dict['species_blocked'] = species_block_type
                if 'treatment_status' in row_dict.keys() and row_dict['treatment_status']:
                    (treatment_status_type, created) = TreatmentStatus.objects.get_or_create(name=row_dict['treatment_status'].lower().title())
                    row_dict['treatment_status'] = treatment_status_type
                # parse datetime
                if 'updated' in row_dict.keys() and row_dict['updated']:
                    updated = datetime(*xlrd.xldate_as_tuple(row_dict['updated'], book.datemode))
                    row_dict['updated'] = updated
                try:
                    # create Barrier
                    Barrier.objects.create(**row_dict)
                    import_count += 1
                except ValueError:
                    warnings.append('row: %d, value:%s' % (row_num, row_dict))
                    print(warnings[-1])
                    pass

        # print('deleting mismatched barrier cost overrides')
        # for barrierCost in BarrierCost.objects.all():
        #     if Barrier.objects.filter(pad_id=barrierCost.pad_id).count() == 0:
        #         barrierCost.delete()

        print("%d barriers added." % import_count)

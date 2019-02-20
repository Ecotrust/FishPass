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
        from django.core.cache import cache
        from fishpass.models import Barrier, BarrierType, BarrierStatus, OwnershipType, FocusArea, BarrierCost, BlockedSpeciesType, TreatmentStatus

        def format_return(success, errors, warnings, import_count=None):
            # We need info about how this ran, but management commands are required to return a string, so.... json to the rescue!
            import json
            return json.dumps({
                'success': success,
                'errors': errors,
                'warnings': warnings,
                'import_count': import_count
            })

        print("IMPORTING PAD")
        cache.clear()

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
            'Miles_Upstream': 'upstream_miles',
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
            return(format_return(False, errors, warnings))
        except:
            errors.append('Could not open %s as .xls or workbook does not have a worksheet.' % options['file'])
            print(errors[-1])
            return(format_return(False, errors, warnings))

        headers = []
        other_columns = []
        import_count = 0
        # for each line
        for row_num in range(sheet.nrows):
            sheet.row(row_num)
            row_dict = {}
            for col_num in range(sheet.ncols):
                if row_num == 0:
                    headers.append(sheet.cell_value(row_num,col_num))
                    if sheet.cell_value(row_num,col_num) not in field_lookup.keys():
                        warnings.append('Column header "%s" not in list of accepted column names. Column will be stored under "overflow".' % sheet.cell_value(row_num,col_num))
                        print(warnings[-1])
                elif headers[col_num] in field_lookup.keys():
                    if sheet.cell_value(row_num,col_num) == '':
                        row_dict[field_lookup[headers[col_num]]] = None
                    else:
                        row_dict[field_lookup[headers[col_num]]] = sheet.cell_value(row_num,col_num)
                else:   # header is not in lookup and needs to be added to an "overflow" dict
                    if "overflow" in row_dict.keys():
                        row_dict["overflow"][headers[col_num]] = sheet.cell_value(row_num,col_num)
                    else:
                        row_dict["overflow"] = {
                            headers[col_num]: sheet.cell_value(row_num,col_num)
                        }
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
                    return(format_return(False, errors, warnings))
                else:
                    print('deleting all old barrier records')
                    Barrier.objects.all().delete()
            else:
                try:
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
                except Exception as e:
                    warnings.append('Barrier ID %s (row %s) could not import: %s' % (str(row_dict['pad_id']), str(row_num), str(e)))
                    print(warnings[-1])
                    pass

        # print('deleting mismatched barrier cost overrides')
        # for barrierCost in BarrierCost.objects.all():
        #     if Barrier.objects.filter(pad_id=barrierCost.pad_id).count() == 0:
        #         barrierCost.delete()

        # Check for mismatch DS Barriers
        for barrier in Barrier.objects.all():
            try:
                if barrier.downstream_id == 0:
                    if not barrier.downstream_barrier_count == 0:
                        warnings.append('Barrier %d: "%s" has no downstream barrier id, but claims to have %d downstream barriers. Assuming 0.' % (barrier.pad_id, str(barrier), barrier.downstream_barrier_count))
                        barrier.downstream_barrier_count = 0
                        barrier.save()
                elif Barrier.objects.filter(pad_id=barrier.downstream_id).count() < 1:
                    if barrier.downstream_id == None:
                        warnings.append('Barrier %d: "%s" has unknown downstream barrier id. Setting it to NA and 0 downstream barrier count (from %d).' % (barrier.pad_id, str(barrier), barrier.downstream_barrier_count))
                    else:
                        warnings.append('Barrier %d: "%s" has unrecognized downstream barrier id "%d". Setting it to NA and 0 downstream barrier count (from %d).' % (barrier.pad_id, str(barrier), barrier.downstream_id, barrier.downstream_barrier_count))
                    barrier.downstream_id = 0
                    barrier.downstream_barrier_count = 0
                    barrier.save()
            except Exception as e:
                warnings.append("Error with determining downstream barrier id for barrier %d. Setting it to NA and 0 downstream barrier count. Error details: %s" % (barrier.pad_id, str(e)))
                barrier.downstream_id = 0
                barrier.downstream_barrier_count = 0
                barrier.save()
                pass


        print("%d barriers added." % import_count)
        return(format_return(True, errors, warnings, import_count))

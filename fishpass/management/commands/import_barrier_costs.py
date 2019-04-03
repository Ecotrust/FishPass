from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from django.db.utils import IntegrityError, DataError

class Command(BaseCommand):
    help = 'Import barrier costs. 1 argument - an Excel spreadsheet or barriers with appropriate fields (see docs)'
    def add_arguments(self, parser):
        parser.add_argument('file',  type=str)
        # test file in:
        #   FishPASS Team Share
        #       Optipass
        #           FISHPass_Input_20180410.xls

    def handle(self, *args, **options):
        import sys
        import xlrd
        # # from datetime import datetime
        # from io import StringIO, BytesIO
        from fishpass.models import Barrier, BarrierType, BarrierStatus, OwnershipType, BarrierCost

        def format_return(success, errors, warnings, import_count=None):
            # We need info about how this ran, but management commands are required to return a string, so.... json to the rescue!
            import json
            return json.dumps({
                'success': success,
                'errors': errors,
                'warnings': warnings,
                'import_count': import_count
            })

        print("IMPORTING BARRIER COSTS")

        field_lookup = {
            'PAD_ID': 'pad_id',
            'Cost': 'cost',
            'SiteType': 'site_type',
            'Bar_Stat': 'barrier_status',
            # 'comment',
        }

        REQUIRED_MODEL_FIELDS = [
            'pad_id',
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

        # for each line
        headers = []
        import_count = 0
        for row_num in range(sheet.nrows):
            sheet.row(row_num)
            row_dict = {}
            comments_list = []
            for col_num in range(sheet.ncols):
                if row_num == 0:
                    headers.append(sheet.cell_value(row_num,col_num))
                    if sheet.cell_value(row_num,col_num) not in field_lookup.keys():
                        warnings.append('Column header "%s" not in list of accepted column names. Column will be added to comments field.' % sheet.cell_value(row_num,col_num))
                        print(warnings[-1])
                elif headers[col_num] in field_lookup.keys():
                    if sheet.cell_value(row_num,col_num) == '':
                        row_dict[field_lookup[headers[col_num]]] = None
                    else:
                        row_dict[field_lookup[headers[col_num]]] = sheet.cell_value(row_num,col_num)
                else:
                    comments_list.append(
                        (
                            str(sheet.cell_value(0,col_num)),
                            str(sheet.cell_value(row_num,col_num))
                        )
                    )
                if len(comments_list) > 0:
                    row_dict['comment'] = '; '.join(["%s: %s" % (x[0], x[1]) for x in comments_list])

            # Check that required Fields are present in
            if row_num == 0:
                for required_field in REQUIRED_MODEL_FIELDS:
                    available_field_options = required_field_reverse_lookup[required_field]
                    match_found = False
                    for option in available_field_options:
                        if option in headers:
                            match_found = True
                    if not match_found:
                        if len(available_field_options) > 1:
                            either = 'either '
                        else:
                            either = ''
                        errors.append('Could not find required header %s%s' % (either, ' or '.join(available_field_options)))
                        print(errors[-1])
                if len(errors) > 0:
                    return(format_return(False, errors, warnings))
                # else:
                #     print('deleting all old barrier-specific records')
                #     BarrierCost.objects.all().delete()
            else:
                #     get or create BarrierType
                if 'site_type' in row_dict.keys() and row_dict['site_type']:
                    type_matches = BarrierType.objects.filter(name__iexact=row_dict['site_type']).order_by('order')
                    if type_matches.count() == 0:
                        (barrierType, created) = BarrierType.objects.get_or_create(name=row_dict['site_type'].title())
                    else:
                        barrierType = type_matches[0]
                        created = False
                    row_dict['site_type'] = barrierType
                #     get or create BarrierStatus
                if 'barrier_status' in row_dict.keys() and row_dict['barrier_status']:
                    status_matches = BarrierStatus.objects.filter(name__iexact=row_dict['barrier_status']).order_by('order')
                    if status_matches.count() == 0:
                        (barrierStatus, created) = BarrierStatus.objects.get_or_create(name=row_dict['barrier_status'].title())
                    else:
                        barrierStatus = status_matches[0]
                        created = False
                    row_dict['barrier_status'] = barrierStatus
                #     get or create OwnershipType
                if 'cost' in row_dict.keys() and row_dict['cost']:
                    if not type(row_dict['cost']) == int:
                        if type(row_dict['cost']) == float:
                            row_dict['cost'] = int(row_dict['cost'])
                        elif type(row_dict['cost']) == str:
                            if row_dict['cost'].isnumeric():
                                row_dict['cost'] = int(float(row_dict['cost']))
                            elif '$' in row_dict['cost']:
                                try:
                                    row_dict['cost'] = int(float(foo.strip('$')))
                                except:
                                    warnings.append('could not interpret cost value %s as an integer' % row_dict['cost'])
                                    print(warnings[-1])
                                    row_dict['cost'] = None
                                    pass
                            else:
                                warnings.append('could not interpret cost value %s as an integer' % row_dict['cost'])
                                print(warnings[-1])
                                row_dict['cost'] = None
                        else:
                            warnings.append('could not interpret cost value %s as an integer' % row_dict['cost'])
                            print(warnings[-1])
                            row_dict['cost'] = None
                try:
                    # create Barrier
                    (barrierCost, created) = BarrierCost.objects.get_or_create(pad_id=int(row_dict['pad_id']))
                    if 'cost' in row_dict.keys() and row_dict['cost']:
                        barrierCost.cost = row_dict['cost']
                    if 'site_type' in row_dict.keys() and row_dict['site_type']:
                        barrierCost.site_type = row_dict['site_type']
                    if 'barrier_status' in row_dict.keys() and row_dict['barrier_status']:
                        barrierCost.barrier_status = row_dict['barrier_status']
                    if 'comment' in row_dict.keys() and row_dict['comment']:
                        barrierCost.comment = row_dict['comment']
                    barrierCost.save()

                    import_count += 1
                except ValueError:
                    warnings.append('row: %d, value:%s' % (row_num, row_dict))
                    print(warnings[-1])
                    pass

        # print('deleting mismatched barrier cost overrides')
        # for barrierCost in BarrierCost.objects.all():
        #     if Barrier.objects.filter(pad_id=barrierCost.pad_id).count() == 0:
        #         barrierCost.delete()

        print("%d barrier-specific details added." % import_count)
        return(format_return(True, errors, warnings, import_count))

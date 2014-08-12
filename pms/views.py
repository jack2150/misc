from django.shortcuts import render
from django.http import HttpResponse
from models import OverallPos, Position, InstrumentPos, StockPos, OptionPos
from control import OpenDir, OpenCSV, ImportPosition, ViewControl
from os import rename
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError, ObjectDoesNotExist


def position(request, date=None):
    """
    display latest positions and overall
    """
    view_control = ViewControl(date=date)
    overall, positions = view_control.get_json_data()

    parameters = {'overall': overall,
                  'mix_all': positions,
                  'date': view_control.date}

    return render(request, 'pms/position/view/index.html', parameters)


def position_select_files(request):
    """
    select files (with date) for import into db
    """
    files = OpenDir().to_json()

    # format file, sort it
    files = sorted(files, reverse=True)

    # json format
    files = '[{ id: -1, value: "Positions", data: %s }]' % files

    # set parameters into html
    parameters = {'files': files}

    return render(request, 'pms/position/import/index.html', parameters)
    #return render(request, 'pms/import/select_date.html', parameters)


def position_import_single(request, date=None):
    """
    import one day position files
    after import it move file into imported folder
    """
    # get date path
    path = ''
    for f in OpenDir().get_files():
        if f['Date'] == date:
            path = f['Path']
            break

    # after open date, then subtract one day
    date = datetime.strptime(date, '%Y-%m-%d') - timedelta(days=1)
    date = date.strftime('%Y-%m-%d')

    if path:
        position, overall = OpenCSV(f=path).get_symbol_lines()

        #instrument_count, option_count = 0, 0

        # save position and overall
        import_pos = ImportPosition(date=date, position=position, overall=overall)
        instrument_count, option_count = import_pos.save_position()
        import_pos.save_overall()

        # move save files into imported folder
        imported_folder = path.split('\\')
        imported_folder.insert(-1, 'imported')
        imported_folder = '\\'.join(imported_folder)
        rename(path, imported_folder)

        parameters = {'found': True, 'date': date, 'path': path.split('\\')[-1],
                      'instrument_count': instrument_count,
                      'option_count': option_count}

    else:
        # file not found
        parameters = {'found': False, 'date': date, 'path': path.split('\\')[-1],
                      'instrument_count': 0,
                      'option_count': 0}

    return render(request, 'pms/import/import_done.html', parameters)


def position_exists(request, date=None):
    """
    ajax check date is exists
    """
    if date:
        try:
            OverallPos.objects.get(date=date)
            found = True
        except ValidationError:
            found = False
        except ObjectDoesNotExist:
            found = False
    else :
        found = False

    return HttpResponse(found)















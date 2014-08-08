from django.shortcuts import render
from django.http import HttpResponse
from models import OverallPos, Position, InstrumentPos, StockPos, OptionPos
from controls import OpenDir, OpenCSV
from controls import ImportPosition
from os import rename


def import_select_date(request):
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

    return render(request, 'pms/import/select_date.html', parameters)


def import_position(request, date=None):
    """
    import one day position files
    after import it move file into imported folder
    """
    path = ''

    # get files
    files = OpenDir().get_files()

    # get date path
    for f in files:
        if f['Date'] == date:
            path = f['Path']
            break

    if path:
        position, overall = OpenCSV(f=path).get_symbol_lines()

        instrument_count, option_count = 0, 0

        # save position and overall
        import_pos = ImportPosition(date=date, position=position, overall=overall)
        #instrument_count, option_count = import_pos.save_position()
        #import_pos.save_overall()

        # move save files into imported folder
        imported_folder = path.split('\\')
        imported_folder.insert(-1, 'imported')
        imported_folder = '\\'.join(imported_folder)
        #rename(path, imported_folder)

        parameters = {'found': True, 'date': date, 'path': path.split('\\')[-1],
                      'instrument_count': instrument_count,
                      'option_count': option_count}

    else:
        # file not found
        parameters = {'found': False, 'date': date, 'path': path.split('\\')[-1],
                      'instrument_count': 0,
                      'option_count': 0}

    return render(request, 'pms/import/import_done.html', parameters)


def index(request):
    """
    display latest positions and overall
    """
    # get latest date from db, only one per day
    overall = OverallPos.objects.latest('date')

    # more than one, one day
    # position first
    positions = Position.objects.filter(date=overall.date)

    portfolio = []
    for position in positions:
        symbol = dict()
        symbol['position'] = position
        symbol['instrument'] = InstrumentPos.objects.get(position=position)
        symbol['stock'] = StockPos.objects.get(position=position)
        symbol['options'] = OptionPos.objects.filter(position=position)
        portfolio.append(symbol)

    #instrument = InstrumentPos.objects.filter(position=positions)
    #stock_pos = StockPos.objects.filter(position=positions)

    #option_pos = OptionPos.objects.filter(position=positions)

    parameters = {'overall': overall,
                  'portfolio': portfolio}

    return render(request, 'pms/index.html', parameters)


def index2(request):
    """
    preparing view with json type of data
    """
    # get latest date from db, only one per day
    # need use list, if not error occur
    overall = OverallPos.objects.latest('date')
    positions = Position.objects.filter(date=overall.date)
    #options = OptionPos.objects.filter(position=positions)
    #stocks = StockPos.objects.filter(position=positions)
    #instruments = InstrumentPos.objects.filter(position=positions)

    #pos_json = '[' + ','.join([str(p.to_json()) for p in positions]) + ']'
    #option_json = '[' + ','.join([str(o.to_json()) for o in options]) + ']'
    #stock_json = '[' + ','.join([str(s.to_json()) for s in stocks]) + ']'
    #instrument_json = '[' + ','.join([str(i.to_json()) for i in instruments]) + ']'

    # join all
    mix_all = []
    for position in positions:
        instrument = InstrumentPos.objects.get(position=position)
        stock = StockPos.objects.get(position=position)
        options = OptionPos.objects.filter(position=position)

        mix_all += [
            '{%s, data: [%s, %s]}' %
            (
                str(instrument.to_json(with_open=True))[1:-1],
                str(stock.to_json()),
                ','.join([str(o.to_json()) for o in options])
            )
        ]



        #instruments = InstrumentPos.objects.filter(position=position)
        #mix_all += [str(i.to_json(with_open=True)) for i in instruments]



        #stocks = StockPos.objects.filter(position=position)
        #mix_all += [str(s.to_json()) for s in stocks]

        #options = OptionPos.objects.filter(position=position)
        #mix_all += [str(o.to_json()) for o in options]

    mix_all = '[' + ','.join(mix_all) + ']'

    parameters = {'overall': overall.to_json(),
                  #'positions': pos_json,
                  #'options': option_json,
                  #'stocks': stock_json,
                  #'instruments': instrument_json,
                  'mix_all': mix_all}

    return render(request, 'pms/index2.html', parameters)


# todo: css color
# todo: import and file select pages

















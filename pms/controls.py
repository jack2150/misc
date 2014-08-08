from misc.settings import BASE_DIR
from models import Position, InstrumentPos, StockPos, OptionPos, OverallPos
from glob import glob


class OpenDir(object):
    """
    open the csv dir and get all files
    """
    def __init__(self):
        self.folder = BASE_DIR + '\\pms\\files\\positions\\'

        self.files = []

    def get_files(self):
        files = glob(self.folder + '*.csv')

        for f in files:
            self.files.append({'Date': f.split('\\')[-1][:10], 'Path': f})

        return self.files

    def to_json(self):
        files = glob(self.folder + '*.csv')

        for f in files:
            file_name = f.split('\\')[-1]
            self.files.append({'id': file_name[:10], 'value': file_name})

        return self.files


class OpenCSV(object):
    """
    open a single csv file of statements
    """
    def __init__(self, f):
        self.file = f

    def get_symbol_lines(self):
        """
        split lines into each symbol group
        each symbol group got 3 parts
        summary, underlying and options

        make sure you have follow order columns:
        Instrument,Qty,Days,Trade Price,Mark,Mrk Chng,Delta,
        Gamma,Theta,Vega,% Change,P/L Open,P/L Day,BP Effect
        """
        lines = open(self.file).readlines()

        # Instrument,Qty,Days,Trade Price,Mark,Mrk Chng,Delta,
        # Gamma,Theta,Vega,% Change,P/L Open,P/L Day,BP Effect
        columns = ['name', 'quantity', 'days', 'trade_price', 'mark', 'mark_change',
                   'delta', 'gamma', 'theta', 'vega', 'pct_change', 'pl_open', 'pl_day', 'bp_effect']

        raw_overall = []
        position = {}
        symbol = None

        for l in lines:
            # split every line using ','
            items = map(lambda x: x.rstrip(), l.split(','))

            # check first item do not have space
            # to get underlying
            if len(items) == 14:
                if ' ' in items[0]:
                    # is stock or option
                    first = items[0].split()

                    if first[-1] in ('CALL', 'PUT') and first[0].isdigit():
                        # and first item is a digit
                        # first last item is call or put
                        #print 'is option', first
                        option = {c: i for c, i in zip(columns, items)}

                        position[symbol]['Options'].append(option)
                    else:
                        # if not it is stock
                        #print 'is stock', first
                        stock = {c: i for c, i in zip(columns, items)}
                        position[symbol]['Stock'] = stock
                else:
                    if items[0] != 'Instrument':
                        # is underlying summary
                        symbol = items[0]

                        instrument = {c: i for c, i in zip(columns, items)}
                        position[symbol] = {'Instrument': [], 'Stock': [], 'Options': []}
                        position[symbol]['Instrument'] = instrument

        # footer overall only
        for l in lines[-5:]:
            # header or footer
            items = l.split('"')

            if len(items) == 3:
                raw_overall.append(items[1].rstrip())
            else:
                items = l.split(',')
                if len(items) == 2:
                    raw_overall.append(items[1].rstrip())

        # overall columns rename
        overall_columns = ['cash_sweep', 'pl_ytd', 'bp_adjustment', 'futures_bp', 'available_dollars']
        overall = {c: o for c, o in zip(overall_columns, raw_overall)}

        return position, overall


class ImportPosition(object):
    """
    use for import csv data into db
    combine all models class and run
    as once
    """
    def __init__(self, date, position, overall):
        self.date = date
        self.position = position
        self.overall = overall

    def save_position(self):
        """
        save all into db
        """
        instrument_count = 0
        option_count = 0

        # now import all symbol position in files into db
        for symbol, items in self.position.items():
            instrument = items['Instrument']
            stock = items['Stock']
            options = items['Options']

            # get company name
            company = stock['name']

            # first insert position

            position = Position(symbol=symbol, company=company, date=self.date)
            position.save()

            # second insert instrument
            instrument_pos = InstrumentPos()
            instrument_pos.save_raw_data(position=position, raw_instrument=instrument)

            # third insert stock
            stock_pos = StockPos()
            stock_pos.save_raw_data(position=position, raw_stock=stock)

            # fourth and final insert option
            for option in options:
                option_pos = OptionPos()
                option_pos.save_raw_data(position=position, raw_option=option)

                option_count += 1

            # update insert count
            instrument_count += 1

        # after finish clear data
        self.position = None

        return instrument_count, option_count

    def save_overall(self):
        """
        save overall data into db
        only one overall in one day
        """
        overall_pos = OverallPos()
        overall_pos.save_raw_data(date=self.date, raw_overall=self.overall)

        return overall_pos.id






















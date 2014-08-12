from misc.settings import BASE_DIR
from models import Position, InstrumentPos, StockPos, OptionPos, OverallPos
from glob import glob
from django.core.exceptions import ValidationError, ObjectDoesNotExist
import numpy as np


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
            # remove new line
            l = l.rstrip()

            # replace all "" ',' to empty
            if '"' in l:
                l = l.split('"')
                for k, i in enumerate(l):
                    if k % 2 and ',' in i:
                        l[k] = i.replace(',', '')

                l = ''.join(l)

            # split every line using ','
            items = map(lambda x: x.rstrip(), l.split(','))
            # check leg_identify item do not have space
            # to get underlying
            if len(items) == 14:
                if ' ' in items[0]:
                    # is stock or option
                    first = items[0].split()

                    if first[-1] in ('CALL', 'PUT') and first[0].isdigit():
                        # and leg_identify item is a digit
                        # leg_identify last item is call or put
                        #print 'is option', leg_identify
                        option = {c: i for c, i in zip(columns, items)}

                        position[symbol]['Options'].append(option)
                    else:
                        # if not it is stock
                        #print 'is stock', leg_identify
                        stock = {c: i for c, i in zip(columns, items)}
                        position[symbol]['Stock'] = stock
                else:
                    if items[0] != 'Instrument' and items[0]:
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

            # leg_identify insert position

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


class ViewControl(object):
    def __init__(self, date):
        self.date = date

        try:
            if self.date:
                self.overall = OverallPos.objects.get(date=self.date)
            else:
                self.overall = OverallPos.objects.latest('date')
                self.date = self.overall.date.strftime('%Y-%m-%d')

            self.positions = Position.objects.filter(date=self.overall.date)
            self.instruments = InstrumentPos.objects.filter(position=self.positions)

        except ValidationError:
            self.overall = None
            self.positions = None
        except ObjectDoesNotExist:
            self.overall = None
            self.positions = None

    def get_json_data(self):
        """
        preparing view with json type of data
        """
        # get latest date from db, only one per day
        # need use list, if not error occur
        if self.overall and self.positions:
            # join all
            mix_all = []
            for position in self.positions:
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

            mix_all = '[' + ','.join(mix_all) + ']'

            positions_json = mix_all
            overall_json = self.overall.to_json()
        else:
            overall_json, positions_json = False, False

        return overall_json, positions_json

    def pl_open_summary(self):
        """
        use all position for date
        and sum up all good and bad
        """
        # all profit and keep profit
        report = {
            'profit': {'count': 0, 'sum': 0, 'percent': 0},
            'even': {'count': 0, 'sum': 0, 'percent': 0},
            'loss': {'count': 0, 'sum': 0, 'percent': 0}
        }

        for i in self.instruments:
            pl_open = float(i.pl_open)
            if pl_open > 0:
                report['profit']['count'] += 1
                report['profit']['sum'] += pl_open
            elif pl_open < 0:
                report['loss']['count'] += 1
                report['loss']['sum'] += pl_open

            else:
                report['even']['count'] += 1
                report['even']['sum'] += pl_open

        total_instrument = len(self.instruments)
        for k in report.keys():
            report[k]['percent'] = round(report[k]['count'] /
                                                 float(total_instrument), 2)

        return report

    def pl_open_deep_summary(self):
        """
        use all position for date
        and sum up all good and bad
        with using pl day detail
        """
        # pl open deep summary report
        report = {
            'profit': {
                'day_continue': {'count': 0, 'sum': 0, 'percent': 0},
                'day_reverse': {'count': 0, 'sum': 0, 'percent': 0},
                'day_no_move': {'count': 0, 'sum': 0, 'percent': 0}
            },
            'loss': {
                'day_continue': {'count': 0, 'sum': 0, 'percent': 0},
                'day_reverse': {'count': 0, 'sum': 0, 'percent': 0},
                'day_no_move': {'count': 0, 'sum': 0, 'percent': 0}
            },
            'even': {
                'day_continue': {'count': 0, 'sum': 0, 'percent': 0},
                'day_reverse': {'count': 0, 'sum': 0, 'percent': 0},
                'day_no_move': {'count': 0, 'sum': 0, 'percent': 0}
            }
        }

        for i in self.instruments:
            pl_open = float(i.pl_open)
            pl_day = float(i.pl_day)

            if pl_open > 0:
                if i.pl_day > 0:
                    report['profit']['day_continue']['count'] += 1
                    report['profit']['day_continue']['sum'] += pl_day
                elif i.pl_day < 0:
                    report['profit']['day_reverse']['count'] += 1
                    report['profit']['day_reverse']['sum'] += pl_day
                else:
                    report['profit']['day_no_move']['count'] += 1
                    report['profit']['day_no_move']['sum'] += pl_day
            elif pl_open < 0:
                if i.pl_day > 0:
                    report['loss']['day_reverse']['count'] += 1
                    report['loss']['day_reverse']['sum'] += pl_day
                elif i.pl_day < 0:
                    report['loss']['day_continue']['count'] += 1
                    report['loss']['day_continue']['sum'] += pl_day
                else:
                    report['loss']['day_no_move']['count'] += 1
                    report['loss']['day_no_move']['sum'] += pl_day
            else:
                if i.pl_day > 0:
                    report['even']['day_continue']['count'] += 1
                    report['even']['day_continue']['sum'] += pl_day
                elif i.pl_day < 0:
                    report['even']['day_reverse']['count'] += 1
                    report['even']['day_reverse']['sum'] += pl_day
                else:
                    report['even']['day_no_move']['count'] += 1
                    report['even']['day_no_move']['sum'] += pl_day

        return report

    def top3positions(self):
        """
        use pl open and pl day and
        get the best 3 and worst 3
        """
        pl_open_report = {
            'best3': [],
            'worst3': []
        }

        pl_day_report = {
            'best3': [],
            'worst3': []
        }

        pl_opens = []
        pl_days = []
        for i in self.instruments:
            symbol = str(i.position.symbol)
            pl_opens.append({'name': symbol, 'pl': float(i.pl_open)})
            pl_days.append({'name': symbol, 'pl': float(i.pl_day)})

        pl_opens = sorted(pl_opens, key=lambda x: x['pl'], reverse=True)
        pl_days = sorted(pl_days, key=lambda x: x['pl'], reverse=True)

        pl_open_report['best3'] = pl_opens[:3]
        pl_open_report['worst3'] = pl_opens[-3:]

        pl_day_report['best3'] = pl_days[:3]
        pl_day_report['worst3'] = pl_days[-3:]

        return pl_open_report, pl_day_report

    def instrument_describe(self):
        """
        for all field in instrument
        do sum, avg, mean, max, min
        weight need to use max pl from spread
        """
        report = {
            'delta': {'sum': 0, 'mean': 0, 'std': 0},
            'gamma': {'sum': 0, 'mean': 0, 'std': 0},
            'theta': {'sum': 0, 'mean': 0, 'std': 0},
            'vega': {'sum': 0, 'mean': 0, 'std': 0},
            'bp_effect': {'sum': 0, 'mean': 0, 'std': 0}
        }

        items = {
            'delta': [],
            'gamma': [],
            'theta': [],
            'vega': [],
            'bp_effect': []
        }

        for i in self.instruments:
            items['delta'].append(float(i.delta))
            items['gamma'].append(float(i.gamma))
            items['theta'].append(float(i.theta))
            items['vega'].append(float(i.vega))
            items['bp_effect'].append(float(i.bp_effect))

        for c in items.keys():
            report[c]['sum'] = round(np.sum(items[c]), 2)
            report[c]['mean'] = round(np.average(items[c]), 2)
            report[c]['std'] = round(np.std(items[c]), 2)

        return report

























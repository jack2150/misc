from django.test import TestCase
from django.core.urlresolvers import reverse
from django.core import serializers
from datetime import datetime
from misc.settings import BASE_DIR


from controls import OpenDir, OpenCSV, ImportPosition
from models import InstrumentPos, StockPos, OptionPos, Option, Position, OverallPos

test_file = BASE_DIR + r'\pms\files\positions\2014-08-02-PositionStatement.csv'

test_symbol = 'QCOM'
test_company = 'QUALCOMM INC COM'
test_date = '2014-08-01'
test_raw_data = {
    'Instrument': {'mark_change': '', 'name': 'QCOM', 'pl_open': '$14.00',
                   'days': '', 'mark': '', 'vega': '-1.02', 'pl_day': '$14.00',
                   'delta': '-11.11', 'bp_effect': '($100.00)', 'theta': '.54',
                   'pct_change': '-3.05%', 'quantity': '', 'gamma': '-2.31', 'trade_price': ''},
    'Options': [{'mark_change': '-.965', 'name': '100 AUG 14 75 CALL', 'pl_open': '$32.00',
                 'days': '15', 'mark': '.62', 'vega': '-5.59', 'pl_day': '$32.00',
                 'delta': '-33.12', 'bp_effect': '', 'theta': '3.12', 'pct_change': '',
                 'quantity': '-1', 'gamma': '-12.46', 'trade_price': '.94'},
                {'mark_change': '-.61', 'name': '100 AUG 14 76 CALL', 'pl_open': '($18.00)',
                 'days': '15', 'mark': '.36', 'vega': '4.57', 'pl_day': '($18.00)',
                 'delta': '22.01', 'bp_effect': '', 'theta': '-2.58', 'pct_change': '',
                 'quantity': '+1', 'gamma': '10.16', 'trade_price': '.54'}],
    'Stock': {'mark_change': '-2.32', 'name': 'QUALCOMM INC COM', 'pl_open': '$0.00',
              'days': '', 'mark': '73.72', 'vega': '.00', 'pl_day': '$0.00', 'delta': '.00',
              'bp_effect': '', 'theta': '.00', 'pct_change': '', 'quantity': '0', 'gamma': '.00',
              'trade_price': '.00'}}

test_raw_overall = {'futures_bp': '$1873.49', 'pl_ytd': '($5609.52)', 'cash_sweep': '$3773.49',
                    'available_dollars': '$1873.49', 'bp_adjustment': '$0.00'}


#noinspection PyPep8Naming
class TestOpenDir(TestCase):
    def setUp(self):
        self.od = OpenDir()

    def tearDown(self):
        del self.od

    def test_get_files(self):
        print 'current import directory: \n%s \n' % self.od.folder

        self.od.get_files()

        print 'files inside directory:'
        for f in self.od.files:
            print f
            try:
                datetime.strptime(f['Date'], '%Y-%m-%d')
            except ValueError:
                raise

            self.assertIn('PositionStatement.csv', f['Path'])

    def test_get_filenames(self):
        print self.od.to_json()


#noinspection PyPep8Naming
class TestOpenCSV(TestCase):
    def setUp(self):
        self.oc = OpenCSV(f=test_file)

    def tearDown(self):
        del self.oc

    def test_get_symbol_lines(self):
        position, overall = self.oc.get_symbol_lines()

        #print position
        print 'Positions in portfolio:'
        for s, p in position.items():
            print s

            for i, d in p.items():
                print i, d

            print

        print '\n'
        print 'Overall Item at Footer:'
        print overall


#noinspection PyPep8Naming
class TestPosition(TestCase):
    def test_save_raw_data(self):
        position = Position(symbol=test_symbol, company=test_company, date=test_date)
        position.save()

        print 'position row count in db: %d\n' % len(Position.objects.all())
        self.assertEqual(len(Position.objects.all()), 1)

        print 'Position in db:'
        print Position.objects.all()

#noinspection PyPep8Naming
class TestInstrumentPos(TestCase):
    def setUp(self):
        self.position = Position(symbol=test_symbol, company=test_company, date=test_date)
        self.position.save()

        self.raw_instrument = test_raw_data['Instrument']

    def tearDown(self):
        del self.raw_instrument

    def test_save_raw_data(self):
        ip = InstrumentPos()
        ip.save_raw_data(position=self.position, raw_instrument=self.raw_instrument)

        print 'instrument row count in db: %d\n' % len(InstrumentPos.objects.all())
        self.assertEqual(len(InstrumentPos.objects.all()), 1)

        print 'Instrument Position in db:'
        print InstrumentPos.objects.get(id=1)


#noinspection PyPep8Naming
class TestStockPos(TestCase):
    def setUp(self):
        self.position = Position(symbol=test_symbol, company=test_company, date=test_date)
        self.position.save()

        self.raw_stock = test_raw_data['Stock']

    def tearDown(self):
        del self.raw_stock

    def test_save_data(self):
        sp = StockPos()
        sp.save_raw_data(position=self.position, raw_stock=self.raw_stock)

        print 'stock row count in db: %d\n' % len(StockPos.objects.all())
        self.assertEqual(len(StockPos.objects.all()), 1)

        print 'Stock Position in db:'
        print StockPos.objects.get(id=1)


#noinspection PyPep8Naming
class TestOption(TestCase):
    def setUp(self):
        self.raw_option_names = ['100 AUG 14 67.5 CALL', '100 (Weeklys) AUG1 14 115 CALL']

    def tearDown(self):
        del self.raw_option_names

    def test_save_raw_data(self):
        ids = []

        for raw_option_name in self.raw_option_names:
            oc = Option()
            oc.save_raw_data(raw_contract=raw_option_name)
            ids.append(oc.id)

        print 'Inserted IDs: %s\n' % ids

        print 'option row count in db: %d' % len(Option.objects.all())

        print 'option rows:\n%s\n%s\n' % \
              (Option.objects.get(id=1), Option.objects.get(id=2))


#noinspection PyPep8Naming
class TestOptionPos(TestCase):
    def setUp(self):
        self.position = Position(symbol=test_symbol, company=test_company, date=test_date)
        self.position.save()

        self.raw_options = test_raw_data['Options']

    def tearDown(self):
        del self.raw_options

    def test_format_saves(self):
        ids = []

        for raw_option in self.raw_options:
            # create new option position object
            op = OptionPos()

            # save into db
            op.save_raw_data(position=self.position, raw_option=raw_option)

            # get id
            ids.append(op.id)

        print 'Inserted IDs: %s\n' % ids

        print 'option row count in db: %d' % len(Option.objects.all())
        print 'option position row count in db: %d\n' % len(OptionPos.objects.all())

        print 'option rows:\n%s\n%s\n' % \
              (Option.objects.get(id=1), Option.objects.get(id=2))

        print 'option position rows:\n%s\n%s\n' % \
              (OptionPos.objects.get(id=1), OptionPos.objects.get(id=2))


#noinspection PyPep8Naming
class TestOverallPos(TestCase):
    def test_save_raw_data(self):
        overall_pos = OverallPos()
        overall_pos.save_raw_data(date=test_date, raw_overall=test_raw_overall)

        print 'Inserted IDs: %s' % overall_pos.id
        print 'option row count in db: %d\n' % len(OverallPos.objects.all())
        print 'Overall Data:'
        print overall_pos

        self.assertTrue(overall_pos.id)
        self.assertEqual(len(OverallPos.objects.all()), 1)

    def test_to_json(self):
        overall_pos = OverallPos()
        overall_pos.save_raw_data(date=test_date, raw_overall=test_raw_overall)

        json_data = overall_pos.to_json()

        print json_data

        #self.assertContains(json_data)


#noinspection PyPep8Naming
class TestImportPosition(TestCase):
    def setUp(self):
        oc = OpenCSV(f=test_file)
        position, overall = oc.get_symbol_lines()

        self.ip = ImportPosition(date=test_date, position=position, overall=overall)

    def tearDown(self):
        del self.ip

    def test_save_position(self):
        self.ip.save_position()

        positions = Position.objects.all()
        print 'Total position in db: %d\n' % len(positions)
        print 'Display all positions...'
        for p in positions:
            print p

        self.assertEqual(len(positions), 19)

        print '\n' + '-' * 100 + '\n'

        instruments = InstrumentPos.objects.all()
        print 'Total instruments in db: %d\n' % len(instruments)
        print 'Display all instruments...'
        for i in instruments:
            print i

        self.assertEqual(len(instruments), 19)

        print '\n' + '-' * 100 + '\n'

        stocks = StockPos.objects.all()
        print 'Total stocks in db: %d\n' % len(stocks)
        print 'Display all stocks...'
        for s in stocks:
            print s

        self.assertEqual(len(stocks), 19)

        print '\n' + '-' * 100 + '\n'

        options = OptionPos.objects.all()
        print 'Total options in db: %d\n' % len(options)
        print 'Display all options...'
        for o in options:
            print o

    def test_save_overall(self):
        self.ip.save_overall()

        print 'option row count in db: %d\n' % len(OverallPos.objects.all())
        print 'Overall Data:'
        print OverallPos.objects.get(id=1)

        self.assertEqual(len(OverallPos.objects.all()), 1)
















class TestViews(TestCase):
    def test_import_select_date(self):
        response = self.client.get(reverse('import_select_date'))

        print 'status code: %d' % response.status_code
        print 'files parameter:'
        print response.context['files']

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PositionStatement")
        self.assertGreater(len(response.context['files']), 1)

    def test_import_position(self):
        response = self.client.get(reverse('import_position', kwargs={'date': test_date}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "PositionStatement")
        self.assertContains(response, test_date)

        positions = Position.objects.all()
        print 'Total position in db: %d\n' % len(positions)
        print 'Display all positions...'
        for p in positions:
            print p

        self.assertEqual(len(positions), 21)

        print '\n' + '-' * 100 + '\n'

        instruments = InstrumentPos.objects.all()
        print 'Total instruments in db: %d\n' % len(instruments)
        print 'Display all instruments...'
        for i in instruments:
            print i

        self.assertEqual(len(instruments), 21)

        print '\n' + '-' * 100 + '\n'

        stocks = StockPos.objects.all()
        print 'Total stocks in db: %d\n' % len(stocks)
        print 'Display all stocks...'
        for s in stocks:
            print s

        self.assertEqual(len(stocks), 21)

        print '\n' + '-' * 100 + '\n'

        options = OptionPos.objects.all()
        print 'Total options in db: %d\n' % len(options)
        print 'Display all options...'
        for o in options:
            print o

        self.assertEqual(len(options), 43)

        print '\n' + '-' * 100 + '\n'

        overall = OverallPos.objects.all()
        print 'Total overall in db: %d\n' % len(overall)
        print 'Display all overall...'
        for o in overall:
            print o

        self.assertEqual(len(overall), 1)


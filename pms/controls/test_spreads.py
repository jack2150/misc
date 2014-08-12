from unittest import TestCase
from misc.settings import BASE_DIR
from spreads import Spreads
from pms.models import OverallPos, Position, InstrumentPos, StockPos, OptionPos
from pms.control import OpenDir, OpenCSV, ImportPosition, ViewControl

test_file = BASE_DIR + r'\pms\files\positions\2014-08-01-PositionStatement.csv'
test_file2 = BASE_DIR + r'\pms\files\positions\2014-08-02-PositionStatement.csv'
test_date = '2014-08-01'
test_date2 = '2014-08-02'

# specific test files
stock_options_combine_file = BASE_DIR + r'\pms\files\positions\tests\2014-03-10-PositionStatement.csv'


#noinspection PyPep8Naming
class TestSpreads(TestCase):
    def setUp(self):
        for f, d in [(test_file, test_date), (test_file2, test_date2)]:
            oc = OpenCSV(f=f)
            position, overall = oc.get_symbol_lines()
            ip = ImportPosition(date=d, position=position, overall=overall)
            ip.save_overall()
            ip.save_position()

            del oc, ip

        self.overall = OverallPos.objects.get(date=test_date)
        self.positions = Position.objects.filter(date=self.overall.date)
        #self.stocks = StockPos.objects.filter(position=self.positions)
        #self.options = OptionPos.objects.filter(position=self.positions)

        # test symbol using qcom
        self.qcom_pos = Position.objects.filter(date=self.overall.date, symbol='QCOM')

        # test symbol using qcom
        self.spx_pos = Position.objects.filter(date=self.overall.date, symbol='SPX')

    def tearDown(self):
        del self

    def ready_up(self, date, filename):
        """
        open file insert into db and start testing
        """
        print 'date: %s, filename: %s' % (date, filename)
        oc = OpenCSV(f=filename)
        position, overall = oc.get_symbol_lines()
        ip = ImportPosition(date=date, position=position, overall=overall)
        ip.save_overall()
        ip.save_position()

        positions = Position.objects.filter(date=date)

        self.assertTrue(positions.count())

        return positions

    def test_get_stock_options(self):
        self.spreads = Spreads(position=self.spx_pos)

        print 'spreads stock: %s' % self.spreads.stock
        print 'spreads options: %s\n' % self.spreads.options
        self.assertFalse(self.spreads.stock)
        self.assertFalse(self.spreads.options)

        print 'running spreads get stock options:'
        self.spreads.get_stock_options()
        print 'done running...\n'

        print 'spreads stock: %s' % self.spreads.stock
        print 'spreads options: %s' % self.spreads.options
        print 'options length with drop: %d' % len(self.spreads.options)
        self.assertEqual(len(self.spreads.options), 2)

        # without drop
        print 'options length without drop: %d' % \
              len(OptionPos.objects.filter(position=self.spx_pos))

    def test_leg_identify(self):
        # create spread and ready up
        self.spreads = Spreads(position=self.qcom_pos)
        self.spreads.get_stock_options()
        self.spreads.leg_identify()

        total_leg = self.spreads.leg

        print 'total leg:'
        print total_leg
        self.assertEqual(total_leg['stock'], 0)
        self.assertEqual(total_leg['options']['count'], 2)

    def test_type_identify(self):
        # create spread and ready up
        self.spreads = Spreads(position=self.qcom_pos)
        self.spreads.get_stock_options()
        self.spreads.leg_identify()

        self.spreads.type_identify()

        print self.spreads.leg
        print self.spreads.name

    def test_is_stock_only(self):
        self.spreads = Spreads(position=self.qcom_pos)
        self.spreads.get_stock_options()

        for direction in [100, -100]:
            self.spreads.leg = {'options': {'count': 0, 'legs': []}, 'stock': direction}
            self.spreads.is_stock_only()
            print 'using "%+d" will result "%s"' % (direction, self.spreads.name)

    def test_is_stock_options_combine(self):
        self.spreads = Spreads(position=self.qcom_pos)
        self.spreads.get_stock_options()

        for s, o, t in [(s, o, t) for s in [100, -100] for o in [1, -1] for t in ['CALL', 'PUT']]:
            self.spreads.leg['stock'] = s
            self.spreads.leg['options'] = {
                'count': 1,
                'legs': [{'qty': o, 'type': t, 'ex_date': '14SEP'}]
            }

            print self.spreads.leg
            self.spreads.is_stock_options_combine()
            print 'name: %s\n' % self.spreads.name

    def test_is_stock_only_with_imported_file(self):
        # save stock only file
        stock_only_file = BASE_DIR + r'\pms\files\positions\tests\2014-03-10-stock_only.csv'
        stock_only_date = '2014-03-10'
        positions = self.ready_up(date=stock_only_date, filename=stock_only_file)

        # the create spreads
        for position in positions:
            self.spreads = Spreads(position=position)
            self.spreads.leg_identify()
            self.spreads.type_identify()
            #self.spreads.is_stock_only()

            print 'name: %s, leg: %s' % (self.spreads.name, self.spreads.leg)

            self.assertTrue(self.spreads.leg['stock'])
            if self.spreads.leg['stock'] > 0:
                self.assertEqual(self.spreads.name, 'Long Stock')
            else:
                self.assertEqual(self.spreads.name, 'Short Stock')

    def test_is_stock_options_combine_with_imported_file(self):
        # save stock only file
        stock_only_file = BASE_DIR + r'\pms\files\positions\tests\2014-03-11-stock_options_combine.csv'
        stock_only_date = '2014-03-11'
        positions = self.ready_up(date=stock_only_date, filename=stock_only_file)

        # the create spreads
        for position in positions:
            self.spreads = Spreads(position=position)
            self.spreads.leg_identify()
            self.spreads.type_identify()

            #self.spreads.is_stock_options_combine()

            print 'name: %s, leg: %s' % (self.spreads.name, self.spreads.leg)

    def test_is_one_legs_options(self):
        contracts = [(x, y) for x in [1, -1] for y in ['CALL', 'PUT']]

        for x in contracts:
            self.spreads = Spreads(position=self.qcom_pos)
            self.spreads.get_stock_options()

            self.spreads.leg['stock'] = 0
            self.spreads.leg['options'] = {
                'count': 1,
                'legs': [{'qty': x[0], 'type': x[1], 'ex_date': '14SEP'}]
            }

            self.spreads.is_one_leg_options()

            print '%20s , %s' % (self.spreads.name, self.spreads.leg)

    def test_is_two_legs_options(self):
        contracts = [(x, y) for x in [1, -1] for y in ['CALL', 'PUT']]

        for x, y in [(x, y) for x in contracts for y in contracts]:
            #print x, y

            self.spreads = Spreads(position=self.qcom_pos)
            self.spreads.get_stock_options()

            if x[0] != y[0] and x[1] == y[1]:
                for a, b in [('14SEP', '14SEP'), ('14SEP', '14OCT')]:
                    self.spreads.leg['stock'] = 0
                    self.spreads.leg['options'] = {
                        'count': 2,
                        'legs': [{'qty': x[0], 'type': x[1], 'ex_date': a},
                                 {'qty': y[0], 'type': y[1], 'ex_date': b}]
                    }

                    self.spreads.is_two_legs_options()

                    print '%20s , %s' % (self.spreads.name, self.spreads.leg)
            else:
                self.spreads.leg['stock'] = 0
                self.spreads.leg['options'] = {
                    'count': 2,
                    'legs': [{'qty': x[0], 'type': x[1], 'ex_date': '14SEP'},
                             {'qty': y[0], 'type': y[1], 'ex_date': '14OCT'}]
                }

                self.spreads.is_two_legs_options()

                print '%20s , %s' % (self.spreads.name, self.spreads.leg)

    def test_pl_stock_only_with_imported_file(self):
        # save stock only file
        stock_only_file = BASE_DIR + r'\pms\files\positions\tests\2014-03-10-stock_only.csv'
        stock_only_date = '2014-03-10'
        positions = self.ready_up(date=stock_only_date, filename=stock_only_file)

        # the create spreads
        for position in positions:
            self.spreads = Spreads(position=position)
            self.spreads.leg_identify()
            self.spreads.type_identify()

            print 'name: %s, leg: %s' % (self.spreads.name, self.spreads.leg)

            self.spreads.pl_stock_only()
            print 'pl: ', self.spreads.pl, '\n'

    def test_pl_stock_options_combine_with_imported_file(self):
        # save stock only file
        stock_only_file = BASE_DIR + r'\pms\files\positions\tests\2014-03-11-stock_options_combine.csv'
        stock_only_date = '2014-03-11'
        positions = self.ready_up(date=stock_only_date, filename=stock_only_file)

        # the create spreads
        for position in positions:
            self.spreads = Spreads(position=position)
            self.spreads.leg_identify()
            self.spreads.type_identify()

            #self.spreads.is_stock_options_combine()
            print 'name: %s' % self.spreads.name

            self.spreads.pl_stock_option_combine()
            #for k, i in self.spreads.pl.items():
            #    print k, i
            print 'pl: ', self.spreads.pl

            print '\n' + '-' * 100 + '\n'


























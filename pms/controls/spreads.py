from django.db.models.query import QuerySet
from pms.models import Position, StockPos, OptionPos
from django.core.exceptions import ValidationError, ObjectDoesNotExist


class Spreads(object):
    """
    use for identify spread type
    on a instrument position
    """
    def __init__(self, position):
        # @type self.stock: StockPos
        """
        @type position: QuerySet of Position
        """
        self.position = position
        self.stock = None
        self.options = None
        self.get_stock_options()

        self.leg = {
            'stock': 0,
            'options': {'count': 0, 'legs': []}
        }

        self.name = ''
        self.describe = ''

        self.pl = {}

    def get_stock_options(self):
        """
        get stock options using position
        without getting zero quantity option
        """
        try:
            # include zero quantity
            stock = StockPos.objects.get(position=self.position)
            # not include zero quantity
            options = OptionPos.objects.filter(position=self.position).exclude(quantity=0)
        except ValidationError:
            stock = None
            options = None
        except ObjectDoesNotExist:
            stock = None
            options = None

        self.stock = stock
        self.options = options

    def leg_identify(self):
        """
        use for identify total leg in Position
        only use quantity more than zero position
        """
        # if no option position
        # then it is stock position
        # if have option position
        # it is something like covered call
        if self.stock:
            # stock position with or without options
            if self.stock.quantity:
                # holding stock
                self.leg['stock'] = self.stock.quantity

            if self.options:
                # holding options position
                self.leg['options']['count'] = self.options.count()

                for op_pos in self.options:
                    self.leg['options']['legs'].append(
                        {
                            'qty': op_pos.quantity,
                            'type': str(op_pos.option.contract),
                            'ex': '%s%s' % (op_pos.option.ex_year, op_pos.option.ex_month)
                        }
                    )

    def type_identify(self):
        """
        after found leg for stock and options
        use type identify to find spreads type
        """
        if self.leg['stock']:
            if self.leg['options']['count'] == 1:
                # join stock options position
                self.is_stock_options_combine()
            else:
                # stock only position
                self.is_stock_only()
        else:
            option_legs = self.leg['options']['count']
            if option_legs == 1:
                # pure options position
                self.is_one_leg_options()
            elif option_legs == 2:
                # pure options position
                self.is_two_legs_options()
            elif option_legs == 4:
                # pure options position
                pass
            else:
                # no stock or options
                pass

    def is_stock_only(self):
        """
        using stock, check is long or short stock
        return name
        """
        if self.leg['stock'] > 0:
            # long stock
            self.name = 'Long Stock'
        elif self.leg['stock'] < 0:
            # short stock
            self.name = 'Short Stock'

    def is_stock_options_combine(self):
        """
        using stock and options check
        what type of joining strategy
        """
        if self.leg['stock'] > 0:
            # long stock and ...
            if self.leg['options']['count'] == 1:
                # long call, short call
                # long put, short put
                option_leg = self.leg['options']['legs'][0]

                if option_leg['qty'] > 0:
                    if option_leg['type'] == 'CALL':
                        # long stock long call
                        self.name = 'Long Stock Long Call'
                    elif option_leg['type'] == 'PUT':
                        # long stock long put, protective put
                        self.name = 'Protective Put'
                elif option_leg['qty'] < 0:
                    if option_leg['type'] == 'CALL':
                        # long stock short call, covered call
                        self.name = 'Covered Call'
                    elif option_leg['type'] == 'PUT':
                        # long stock short put
                        self.name = 'Long Stock Short Put'
            else:
                # custom spreads???
                self.name = 'Custom'
        elif self.leg['stock'] < 0:
            # short stock and ...
            if self.leg['options']['count'] == 1:
                option_leg = self.leg['options']['legs'][0]

                if option_leg['qty'] > 0:
                    if option_leg['type'] == 'CALL':
                        # short stock long call, protective call
                        self.name = 'Protective Call'
                    elif option_leg['type'] == 'PUT':
                        # short stock long put
                        self.name = 'Short Stock Long Put'
                elif option_leg['qty'] < 0:
                    if option_leg['type'] == 'CALL':
                        # short stock short call
                        self.name = 'Short Stock Short Call'
                    elif option_leg['type'] == 'PUT':
                        # short stock short put
                        self.name = 'Covered Put'
            else:
                # custom spreads???
                self.name = 'Custom Spreads'

    def is_one_leg_options(self):
        """
        primary identify single legs options
        """
        option = self.leg['options']['legs'][0]
        
        if option['type'] == 'CALL':
            if option['qty'] > 0:
                self.name = 'Long Call'
            elif option['qty'] < 0:
                self.name = 'Naked Call'
        elif option['type'] == 'PUT':
            if option['qty'] > 0:
                self.name = 'Long Put'
            elif option['qty'] < 0:
                self.name = 'Naked Put'

    def is_two_legs_options(self):
        """
        primary for two legs options
        popular got straddle, strangle
        vertical and synthetic...
        """
        first_option = self.leg['options']['legs'][0]
        second_option = self.leg['options']['legs'][1]

        if first_option['type'] == 'CALL' and first_option['qty'] > 0:
            # buy call
            if second_option['type'] == 'CALL' and second_option['qty'] > 0:
                # buy call and buy call...
                self.name = 'Double Long Calls'
            elif second_option['type'] == 'CALL' and second_option['qty'] < 0:
                # buy call and sell call, vertical
                if first_option['ex_date'] == second_option['ex_date']:
                    self.name = 'Call Vertical'
                else:
                    self.name = 'Call Calendar'
            elif second_option['type'] == 'PUT' and second_option['qty'] > 0:
                # buy call and buy put, long strangle or straddle
                self.name = 'Strangle or Straddle'
            elif second_option['type'] == 'PUT' and second_option['qty'] < 0:
                # buy call and sell put, risk reversal
                self.name = 'Long Risk Reversal'
        elif first_option['type'] == 'CALL' and first_option['qty'] < 0:
            # sell call
            if second_option['type'] == 'CALL' and second_option['qty'] > 0:
                # sell call and buy call, vertical
                if first_option['ex_date'] == second_option['ex_date']:
                    self.name = 'Call Vertical'
                else:
                    self.name = 'Call Calendar'
            elif second_option['type'] == 'CALL' and second_option['qty'] < 0:
                # sell call and sell call...
                self.name = 'Double Naked Calls'
            elif second_option['type'] == 'PUT' and second_option['qty'] > 0:
                # sell call and buy put, risk reversal
                self.name = 'Short Risk Reversal'
            elif second_option['type'] == 'PUT' and second_option['qty'] < 0:
                # sell call and sell put, short strangle or short straddle
                self.name = 'Strangle or Straddle'
        elif first_option['type'] == 'PUT' and first_option['qty'] > 0:
            # buy put
            if second_option['type'] == 'CALL' and second_option['qty'] > 0:
                # buy put and buy call, long strangle or straddle
                self.name = 'Strangle or Straddle'
            elif second_option['type'] == 'CALL' and second_option['qty'] < 0:
                # buy put and sell call, risk reversal
                self.name = 'Short Risk Reversal'
            elif second_option['type'] == 'PUT' and second_option['qty'] > 0:
                # buy put and buy put...
                self.name = 'Double Long Puts'
            elif second_option['type'] == 'PUT' and second_option['qty'] < 0:
                # buy put and sell put, vertical
                if first_option['ex_date'] == second_option['ex_date']:
                    self.name = 'Put Vertical'
                else:
                    self.name = 'Put Calendar'
        elif first_option['type'] == 'PUT' and first_option['qty'] < 0:
            # sell put
            if second_option['type'] == 'CALL' and second_option['qty'] > 0:
                # sell put and buy call, risk reversal
                self.name = 'Long Risk Reversal'
            elif second_option['type'] == 'CALL' and second_option['qty'] < 0:
                # sell put and sell call, short strangle or straddle
                self.name = 'Strangle or Straddle'
            elif second_option['type'] == 'PUT' and second_option['qty'] > 0:
                # sell put and buy put, vertical
                if first_option['ex_date'] == second_option['ex_date']:
                    self.name = 'Put Vertical'
                else:
                    self.name = 'Put Calendar'
            elif second_option['type'] == 'PUT' and second_option['qty'] < 0:
                # sell put and sell put...
                self.name = 'Double Naked Puts'

    def is_four_legs_options(self):
        # todo: later
        pass

    def pl_identify(self):
        """
        profit and loss identify
        max profit, max loss, breakeven
        """
        pass

    def pl_stock_only(self):
        """
        buy or sell stock only
        profit and loss identify
        """
        bp = float(self.stock.trade_price * self.stock.quantity)

        if self.name == 'Long Stock':
            self.pl = {
                'breakeven': float(self.stock.trade_price),
                'max_profit': 'Unlimited',
                'max_loss': bp
            }
        elif self.name == 'Short Stock':
            self.pl = {
                'breakeven': float(self.stock.trade_price),
                'max_profit': bp,
                'max_loss': 'Unlimited'
            }

    def pl_stock_option_combine(self):
        """
        buy or sell stock options combine
        profit and loss identify
        """
        stock_trade_price = self.stock.trade_price
        stock_quantity = self.stock.quantity
        option_trade_price = self.options[0].trade_price
        option_strike_price = self.options[0].option.strike_price

        #print 'stock_trade_price', stock_trade_price
        #print 'option_trade_price', option_trade_price
        #print 'option_strike_price', option_strike_price, '\n'

        if self.name == 'Protective Put':
            breakeven = float(stock_trade_price + option_trade_price)
            self.pl = {
                'breakeven': breakeven,
                'max_profit': 'Unlimited',
                'max_profit_price': '>= %.2f' % breakeven,
                'max_loss': float((option_trade_price + stock_trade_price
                                   - option_strike_price) * stock_quantity),
                'max_loss_price': '<= %.2f' % option_strike_price,
            }
        elif self.name == 'Protective Call':
            breakeven = float(stock_trade_price - option_trade_price)
            self.pl = {
                'breakeven': breakeven,
                'max_profit': float(stock_trade_price * stock_quantity * -1),
                'max_profit_price': '<= %.2f' % breakeven,
                'max_loss': float((option_trade_price - stock_trade_price
                                   + option_strike_price) * -stock_quantity),
                'max_loss_price': '>= %.2f' % option_strike_price
            }
        elif self.name == 'Covered Call':
            self.pl = {
                'breakeven': float(stock_trade_price - option_trade_price),
                'max_profit': float((option_trade_price - stock_trade_price
                                     + option_strike_price) * stock_quantity),
                'max_profit_price': '>= %.2f' % option_strike_price,
                'max_loss': float(stock_trade_price * stock_quantity * -1),
                'max_loss_price': 0.0
            }
        elif self.name == 'Covered Put':
            self.pl = {
                'breakeven': float(stock_trade_price + option_trade_price),
                'max_profit': float((option_trade_price + stock_trade_price
                                     - option_strike_price) * stock_quantity * -1),
                'max_profit_price': '<= %.2f' % option_strike_price,
                'max_loss': 'Unlimited',
                'max_loss_price': 'Unlimited',
            }
        else:
            self.pl = {
                'custom': 'Unknown'
            }

    def pl_one_leg_options(self):
        """
        for one leg options only
        profit and loss identify
        """
        # todo: next
        pass
































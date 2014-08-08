from django.db import models


class Position(models.Model):
    """
    a position contain:
    a single InstrumentPosition
    a single StockPosition
    multiple OptionPosition

    columns:
    Instrument,Qty,Days,Trade Price,Mark,Mrk Chng,Delta, Gamma,
    Theta,Vega,% Change,P/L Open,P/L Day,BP Effect, 'Right',
    'Special', 'ExpireMonth', 'ExpireYear', 'StrikePrice', 'Contract'
    """
    symbol = models.CharField(max_length=20)
    company = models.CharField(max_length=300)
    date = models.DateField()

    #noinspection PyClassHasNoInit
    class Meta:
        # unique symbol and date for position
        unique_together = ('symbol', 'date')

    def to_json(self):
        """
        use all property and output json format string
        """
        str_json = '{'

        str_json += 'symbol: "%s", ' % self.symbol
        str_json += 'company: "%s", ' % self.company
        str_json += 'date: "%s"' % self.date

        str_json += '}'

        return str_json

    def __unicode__(self):
        desc = 'Symbol: %s, ' % self.symbol
        desc += 'Company: %s, ' % self.company
        desc += 'Date: %s' % self.date

        return desc


class InstrumentPos(models.Model):
    position = models.ForeignKey(Position)

    delta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    gamma = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    theta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    vega = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pct_change = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    bp_effect = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save_raw_data(self, position, raw_instrument):
        """
        for instrument raw data, format it
        set it into class and save it
        """
        instrument_pos = raw_instrument

        # remove un-relate columns
        for key in ['name', 'days', 'quantity', 'trade_price', 'mark', 'mark_change']:
            try:
                del instrument_pos[key]
            except KeyError:
                pass

        for column_name, instrument_data in instrument_pos.items():
            # remove $ and %
            instrument_data = instrument_data.replace('%', '').replace('$', '')

            # remove () with negative
            if instrument_data[:1] == '(' and instrument_data[-1:] == ')':
                instrument_data = float(instrument_data[1:-1]) * -1

            # replace empty and convert float
            if not instrument_data or instrument_data == 'N/A':
                instrument_data = 0.0
            else:
                instrument_data = float(instrument_data)

            instrument_pos[column_name] = instrument_data

        # set variables into class, keep position, then save
        self.__init__(position=position, **instrument_pos)
        self.save()

    def to_json(self, with_open=False):
        """
        use all property and output json format string
        """
        str_json = '{'

        str_json += 'name: "%s", ' % self.position.company

        str_json += 'quantity: 0, '
        str_json += 'days: 0, '
        str_json += 'trade_price: 0, '
        str_json += 'mark: 0, '
        str_json += 'mark_change: 0, '
        str_json += 'delta: %.2f, ' % self.delta
        str_json += 'gamma: %.2f, ' % self.gamma
        str_json += 'theta: %.2f, ' % self.theta
        str_json += 'vega: %.2f, ' % self.vega
        str_json += 'pct_change: %.2f, ' % self.pct_change
        str_json += 'pl_open: %.2f, ' % self.pl_open
        str_json += 'pl_day: %.2f, ' % self.pl_day

        if with_open:
            str_json += 'bp_effect: %.2f, ' % self.bp_effect
            str_json += 'open: false'
        else:
            str_json += 'bp_effect: %.2f' % self.bp_effect

        str_json += '}'

        return str_json

    def __unicode__(self):
        desc = 'Position: <%s>, ' % self.position
        desc += 'Delta: %+.2f, ' % self.delta
        desc += 'Gamma: %+.2f, ' % self.delta
        desc += 'Theta: %+.2f, ' % self.theta
        desc += 'Vega: %+.2f, ' % self.vega
        desc += 'Pct_Change: %+.2f, ' % self.pct_change
        desc += 'PL_Open: %+.2f, ' % self.pl_open
        desc += 'PL_Day: %+.2f, ' % self.pl_day
        desc += 'BP_Effect: %+.2f' % self.bp_effect

        return desc


class StockPos(models.Model):
    position = models.ForeignKey(Position)

    quantity = models.IntegerField(default=0)
    trade_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mark = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mark_change = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    pct_change = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    bp_effect = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save_raw_data(self, position, raw_stock):
        """
        using raw stock data, format it,
        set it and save it into class
        """
        stock_pos = raw_stock

        # remove un-relate columns
        for key in ['name', 'delta', 'gamma', 'theta', 'vega', 'days']:
            try:
                del stock_pos[key]
            except KeyError:
                pass

        for column_name, stock_data in stock_pos.items():
            # remove $ and %
            stock_data = stock_data.replace('%', '').replace('$', '')

            # remove () with negative
            if stock_data[:1] == '(' and stock_data[-1:] == ')':
                stock_data = float(stock_data[1:-1]) * -1

            # replace empty and convert float
            if not stock_data or stock_data == 'N/A':
                stock_data = 0.0
            else:
                stock_data = float(stock_data)

            stock_pos[column_name] = stock_data

        self.__init__(position=position, **stock_pos)
        self.save()

    def to_json(self):
        """
        use all property and output json format string
        """
        str_json = '{'

        str_json += 'name: "%s", ' % self.position.symbol
        str_json += 'quantity: %+d, ' % self.quantity
        str_json += 'days: 0, '
        str_json += 'trade_price: %.2f, ' % self.trade_price
        str_json += 'mark: %.2f, ' % self.mark
        str_json += 'mark_change: %.2f, ' % self.mark_change
        str_json += 'delta: 0, '
        str_json += 'gamma: 0, '
        str_json += 'theta: 0, '
        str_json += 'vega: 0, '
        str_json += 'pct_change: %.2f, ' % self.pct_change
        str_json += 'pl_open: %.2f, ' % self.pl_open
        str_json += 'pl_day: %.2f, ' % self.pl_day
        str_json += 'bp_effect: %.2f' % self.bp_effect

        str_json += '}'

        return str_json

    def __unicode__(self):
        desc = 'Position: <%s>, ' % self.position
        desc += 'Quantity: %+.2f, ' % self.quantity
        desc += 'Trade_Price: %+.2f, ' % self.trade_price
        desc += 'Mark: %+.2f, ' % self.mark
        desc += 'Mark_Change: %+.2f, ' % self.mark_change
        desc += 'Pct_Change: %+.2f, ' % self.pct_change
        desc += 'PL_Open: %+.2f, ' % self.pl_open
        desc += 'PL_Day: %+.2f, ' % self.pl_day
        desc += 'BP_Effect: %+.2f' % self.bp_effect

        return desc


class Option(models.Model):
    right = models.IntegerField(default=100)
    special = models.CharField(max_length=100)
    ex_month = models.CharField(max_length=3)
    ex_year = models.IntegerField()
    strike_price = models.DecimalField(max_digits=6, decimal_places=2)
    contract = models.CharField(max_length=4)

    def save_raw_data(self, raw_contract):
        """
        using raw option contract name
        split it and set it into class
        """
        columns = ['right', 'special', 'ex_month', 'ex_year', 'strike_price', 'contract']

        # split the name into columns
        option_contract = raw_contract.split()

        # remove () in special columns or set normal if empty
        if len(option_contract) == 5:
            option_contract.insert(1, 'Normal')
        else:
            option_contract[1] = option_contract[1][1:-1]

        # match columns name
        option_contract = {c: i for c, i in zip(columns, option_contract)}

        # format option name
        option_contract['right'] = int(option_contract['right'])
        option_contract['ex_year'] = int(option_contract['ex_year'])
        option_contract['strike_price'] = float(option_contract['strike_price'])

        # save into option class
        self.__init__(**option_contract)
        self.save()

    def __unicode__(self):
        """
        display row data in string
        """
        desc = '%d %s %s %d %.2f %s' \
               % (self.right, self.special, self.ex_month,
                  self.ex_year, float(self.strike_price), self.contract)

        return desc


class OptionPos(models.Model):
    position = models.ForeignKey(Position)

    option = models.ForeignKey(Option)

    quantity = models.IntegerField(default=0)
    days = models.IntegerField(default=0)
    trade_price = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mark = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    mark_change = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    delta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    gamma = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    theta = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    vega = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pct_change = models.DecimalField(max_digits=6, decimal_places=2, default=0.0)
    pl_open = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    pl_day = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    bp_effect = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save_raw_data(self, position, raw_option):
        """
        only 1 optionPos and 1 Option
        using raw dict data from csv after split section
        it will auto get the save_raw_data data and set class variables
        """
        ##############################
        # option contract section
        ##############################
        option = Option()
        option.save_raw_data(raw_contract=raw_option.pop('name'))
        option.save()

        ##############################
        # option position section
        ##############################
        option_pos = raw_option

        for column_name, option_data in option_pos.items():
            # replace n/a, , remove $ and %
            option_data = option_data.replace('%', '').replace('$', '')

            # remove () with negative
            if option_data[:1] == '(' and option_data[-1:] == ')':
                option_data = float(option_data[1:-1]) * -1

            # replace empty and convert float
            if not option_data or option_data == 'N/A':
                option_data = 0.0
            else:
                option_data = float(option_data)

            # save back into dict
            option_pos[column_name] = option_data

        # set into class variables then save
        self.__init__(position=position, option=option, **option_pos)
        self.save()

    def to_json(self):
        """
        use all property and output json format string
        """
        str_json = '{'

        str_json += 'name: "%s", ' % self.option

        str_json += 'quantity: %d, ' % self.quantity
        str_json += 'days: %d, ' % self.days
        str_json += 'trade_price: %.2f, ' % self.trade_price
        str_json += 'mark: %.2f, ' % self.mark
        str_json += 'mark_change: %.2f, ' % self.mark_change
        str_json += 'delta: %.2f, ' % self.delta
        str_json += 'gamma: %.2f, ' % self.gamma
        str_json += 'theta: %.2f, ' % self.theta
        str_json += 'vega: %.2f, ' % self.vega
        str_json += 'pct_change: %.2f, ' % float(self.mark_change / self.trade_price * 100)
        str_json += 'pl_open: %.2f, ' % self.pl_open
        str_json += 'pl_day: %.2f, ' % self.pl_day
        str_json += 'bp_effect: 0'

        str_json += '}'

        return str_json

    def __unicode__(self):
        desc = 'Position: <%s>, ' % self.position
        desc += 'Contract: <%s>, ' % self.option
        desc += 'Quantity: %d, ' % self.quantity
        desc += 'Days: %d, ' % self.days
        desc += 'Trade_Price: %+.2f, ' % self.trade_price
        desc += 'Mark: %+.2f, ' % self.mark
        desc += 'Mark_Change: %+.2f, ' % self.mark_change
        desc += 'Delta: %+.2f, ' % self.delta
        desc += 'Gamma: %+.2f, ' % self.gamma
        desc += 'Theta: %+.2f, ' % self.theta
        desc += 'Vega: %+.2f, ' % self.vega
        desc += 'Pct_Change: %+.2f, ' % self.pct_change
        desc += 'PL_Open: "%+.2f", ' % self.pl_open
        desc += 'PL_Day: "%+.2f", ' % self.pl_day
        desc += 'BP_Effect: %+.2f, ' % self.bp_effect

        return desc


class OverallPos(models.Model):
    date = models.DateField(unique=True)

    cash_sweep = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    pl_ytd = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    futures_bp = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    bp_adjustment = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    available_dollars = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    def save_raw_data(self, date, raw_overall):
        """
        format raw data, set it
        into class and save it
        """
        # new empty overall
        overall = {}

        # format it
        for column_name, overall_data in raw_overall.items():
            for r in [' ', '&', '/', ',', '$']:
                overall_data = overall_data.replace(r, '')

            if overall_data[:1] == '(' and overall_data[-1:] == ')':
                overall_data = float(overall_data[1:-1]) * -1

            overall[column_name] = float(overall_data)

        self.__init__(date=date, **overall)
        self.save()

    def to_json(self):
        """
        use all property and output json format string
        """
        str_json = '{'

        str_json += 'date: "%s", ' % self.date
        str_json += 'cash_sweep: %.2f, ' % self.cash_sweep
        str_json += 'pl_ytd: %.2f, ' % self.pl_ytd
        str_json += 'futures_bp: %.2f, ' % self.futures_bp
        str_json += 'bp_adjustment: %.2f, ' % self.bp_adjustment
        str_json += 'available_dollars: %.2f' % self.available_dollars

        str_json += '}'

        return str_json

    def __unicode__(self):
        desc = 'Date: %s, ' % self.date
        desc += 'PL_YTD: %+.2f, ' % self.pl_ytd
        desc += 'Futures_BP: %.2f, ' % self.futures_bp
        desc += 'Cash_Sweep: %.2f, ' % self.cash_sweep
        desc += 'Available_Dollar: %.2f, ' % self.available_dollars
        desc += 'BP_Adjustment: %+.2f' % self.bp_adjustment

        return desc

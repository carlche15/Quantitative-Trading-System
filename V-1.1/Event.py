class Event(object):
    pass

class MarketEvent(Event):
    def __init__(self):
        self.type="MARKET"

class SignalEvent(Event):
    def __init__(self, symbol, datetime,signal_type):
        self.type="SIGNAL"
        self.symbol=symbol
        self.datetime=datetime
        self.signal_type=signal_type

class OrderEvent(Event):
    def __init__(self, symbol,order_type,quantity,direction):
        self.type="ORDER"
        self.symbol=symbol
        self.order_type=order_type
        self.quantity=quantity
        self.direction=direction
        self.print_order()
    def print_order(self):
         print "** Portfolio--> **: [Order Submitted]: Symbol=%s, Type=%s, Quantity=%s, Direction=%s **End of Msg**" % (self.symbol,self.order_type,self.quantity,self.direction)

class FillEvent(Event):
    def __init__(self, timeindex,symbol,exchange,quantity,direction,fill_cost,commission=None):
        self.type="FILL"
        self.timeindex=timeindex
        self.symbol=symbol
        self.exchange=exchange
        self.quantity=quantity
        self.direction=direction
        self.fill_cost=fill_cost
        if commission is None:
            self.commission=self.calculate_commission()
        else:
            self.commission=commission
        print "** Broker--> **: [Order Filled] Symbol=%s, Exg=%s, Quantity=%s, Direction=%s, Commission=%s **End of Msg**" % (self.symbol, self.exchange, self.quantity, self.direction,self.commission)
    def calculate_commission(self):
        full_cost=1.3
        if self.quantity<=500:
            full_cost=max(1.3,0.013*self.quantity)
        else:
            full_cost=max(1.3,0.008*self.quantity)
        full_cost=min(full_cost, 0.5/100.0*self.quantity*self.fill_cost)
        return full_cost


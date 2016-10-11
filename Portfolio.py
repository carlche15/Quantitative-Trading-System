import  numpy as np
import pandas as pd
import  Queue
from Event import *
from abc import ABCMeta, abstractmethod

class portfolio (object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def order_generation(self,event):

        raise NotImplementedError("Abstract method not implemented")

    @abstractmethod
    def fill_update(self,event):

        raise NotImplementedError("Abstract method not implemented")

class test_portfolio(portfolio):

    def __init__(self, data_handler,events,initial_capital=100000.0):
        self.data_handler=data_handler
        self.events=events
        self.symbol_list=data_handler.symbol_list
        self.initial_capital=initial_capital
        self.positions=pd.DataFrame() # position is a dataframe, the columns of which are  dates, values are series of shares
        self.current_positions=pd.Series()
        self.ini_position()
        self.holdings=pd.DataFrame()
        self.current_holdings=pd.Series()
        self.ini_holdings()
    def ini_position(self):
        data=np.zeros(len(self.symbol_list))
        index=self.symbol_list
        first=pd.Series(data,index,name=self.data_handler.current_time)
        self.current_positions=first

        self.positions=pd.DataFrame(self.current_positions)
    def ini_holdings(self):
        index=list(self.symbol_list)+["cash","commission","total"]
        data=list(np.zeros(len(self.symbol_list)))+list([self.initial_capital,0.0,self.initial_capital])
        first =pd.Series(data,index,name=self.data_handler.current_time)
        self.current_holdings=first

        self.holdings=pd.DataFrame(self.current_holdings)
    def heartbeat_update(self):
       # update self.positions
       self.current_positions=pd.Series(self.current_positions.values,self.current_positions.index,name=self.data_handler.current_time)
       self.positions=pd.concat([self.positions,self.current_positions],axis=1)
       # don't need to update current_position, because they should remain same unless some events come


       #update current_holdings, which should reflect market changes
       latest_market = self.data_handler.get_latest_data()
       market_value=0
       for s in self.symbol_list:
           self.current_holdings[s]=self.current_positions[s]*latest_market.loc[s,"close"]
           market_value+=self.current_holdings[s]
       self.current_holdings["total"]=self.current_holdings["cash"]+market_value
       self.current_holdings=pd.Series(self.current_holdings.values,self.current_holdings.index,name=self.data_handler.current_time)
       self.holdings=pd.concat([self.holdings,self.current_holdings],axis=1)


    def  fill_update_positions(self,fill):
        fill_direction=0
        if fill.direction=="BUY":
               fill_direction=1
        if fill.direction=="SELL":
                fill_direction=-1
        self.current_positions[fill.symbol]+=fill_direction*fill.quantity
        if self.current_positions.name in self.positions.columns:
              del self.positions[self.current_positions.name]
        self.positions=pd.concat([self.positions,self.current_positions],axis=1)


    def  fill_update_holdings(self,fill):
        fill_direction = 0
        if fill.direction == "BUY":
            fill_direction = 1
        if fill.direction == "SELL":
            fill_direction = -1
        fill_price=self.data_handler.historical_data.data[fill.symbol].close[fill.timeindex]
        cash_flow=fill_direction*fill_price*fill.quantity
        self.current_holdings[fill.symbol]+=cash_flow
        self.current_holdings["commission"]+=fill.commission
        self.current_holdings["cash"]-=(cash_flow+fill.commission)
        self.current_holdings["total"]-=(fill.commission)

        if self.current_holdings.name in self.holdings.columns:
              del self.holdings[self.current_holdings.name]
        self.holdings=pd.concat([self.holdings,self.current_holdings],axis=1)


    def fill_update(self,event):

        if event.type=="FILL":
            self.fill_update_positions(event)
            self.fill_update_holdings(event)

    def  order_generation(self,signal):

        order=None
        symbol=signal.symbol
        direction=signal.signal_type
        mkt_quantity=100.0
        cur_quantity=self.current_positions[symbol]
        order_type="MKT"

        if direction=="LONG" and cur_quantity==0:
            order=OrderEvent(symbol, order_type, mkt_quantity, "BUY")
        if direction=="SHORT" and cur_quantity==0:
            order=OrderEvent(symbol,order_type,mkt_quantity,"SELL")

        if direction=="EXIT" and cur_quantity>0:
            order=OrderEvent(symbol,order_type,abs(cur_quantity),"SELL")
        if direction=="EXIT" and cur_quantity<0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), "BUY")

        return order

    def signal_update(self,event):
        if event.type=="SIGNAL":
            order_event=self.order_generation(event)
            self.events.put(order_event)


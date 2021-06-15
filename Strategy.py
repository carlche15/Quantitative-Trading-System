import datetime
import numpy as np
import pandas as pd
import  Queue
from abc import ABCMeta, abstractmethod
from Event import SignalEvent
from DataHandler import*
class Strategy(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def calculate_signals(self,event):

        raise NotImplementedError("Abstract method not implemented! :(")
class BuyandHold(Strategy):
    def __init__(self,data_handler,events):
      self.data_handler=data_handler
      self.symbol_list=data_handler.symbol_list
      self.events=events
      self.bought_map=self._calculate_initial_bought()

    def _calculate_initial_bought(self):
        bought={}
        for s in self.symbol_list:
            bought[s]=False
        return bought

    def calculate_signals(self,event):
        # current_market=
        if event.type=="MARKET":
                for s in self.symbol_list:
                    if self.bought_map[s]==False:
                        signal=SignalEvent(s,self.data_handler.current_time,"LONG")
                        self.events.put(signal)
                        self.bought_map[s]=True

class MovinAvgCross(Strategy):
    def __init__(self, data_handler, events, short_period=5, long_period=9):
        self.data_handler = data_handler
        self.symbol_list = data_handler.symbol_list
        self.events = events
        self.short_period=short_period
        self.long_period=long_period
    def calculate_signals(self,event):

        temp_df=pd.DataFrame(index=self.symbol_list)
        if event.type=="MARKET":
                for s in self.symbol_list:
                    current_time=self.data_handler.current_time
                    _, short_mov=self.data_handler.historical_data.data[s].ma(self.short_period)
                    _, long_mov=self.data_handler.historical_data.data[s].ma(self.long_period)
                    previous_time=self.data_handler.time_series[list(self.data_handler.time_series).index(current_time)-1]
                    if short_mov[current_time]>long_mov[current_time] and \
                                    short_mov[previous_time] < long_mov[previous_time]:
                        signal = SignalEvent(s, self.data_handler.current_time, "SHORT")
                        self.events.put(signal)
                    elif short_mov[current_time]<long_mov[current_time] and \
                                    short_mov[previous_time] >long_mov[previous_time]:
                        signal = SignalEvent(s, self.data_handler.current_time, "LONG")
                        self.events.put(signal)









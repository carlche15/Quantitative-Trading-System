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




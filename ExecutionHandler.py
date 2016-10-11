import Queue
from Event import *
from abc import ABCMeta, abstractmethod

class ExecutionHandler(object):
    __metaclass__ = ABCMeta
    @abstractmethod
    def execute_order(self,event):
        raise NotImplementedError("Abstract method not implemented")

class Historical_Execution_Handler(ExecutionHandler):
    def __init__(self,data_handler,events):
        self.data_handler=data_handler
        self.events=events

    def execute_order(self,event):
        if event.type=="ORDER":
            latest_market=self.data_handler.get_latest_data()
            market_price=latest_market.loc[event.symbol,"close"]
            esti_cost=market_price*event.quantity
            time=self.data_handler.current_time
            fill_event=FillEvent(time, event.symbol,"ARCA",event.quantity,event.direction, esti_cost  )
            self.events.put(fill_event)
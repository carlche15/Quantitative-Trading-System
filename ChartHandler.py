from abc import ABCMeta, abstractmethod
from Stock_Info_Carl import *
import matplotlib.pyplot as plt


class ChartHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_data(self, symbol, delay=0):
        raise NotImplementedError("Abstract method not implemented :(")

    @abstractmethod
    def update_observed_data(self):
        raise NotImplementedError("Abstract method not implemented :(")

class Portfolio_ChartHandler():

    def __init__(self,portfolio):
        self.portfolio=portfolio

        self.pnl=pd.Series()
        self.riskfreerate=0.05
        self.thirtyds_sharpe=pd.Series()
        self.basic_cal()
    def basic_cal(self):

        index= self.portfolio.holdings.columns
        data = [self.portfolio.holdings.loc["total", x] for x in index]
        self.total_capital = pd.Series(data, index=index)



    def sharphandler(self):

        description_str="Sharpe Ratio"
        data=self.total_capital.values
        index=self.total_capital.index

        returns=np.diff(data)/data[:-1]
        index=index[1:]
        excess_return=returns-self.riskfreerate/252


        period_excess_return_std=[]
        mean_excess_return =pd.rolling_mean(excess_return, 30)
        for i in range(0,len(excess_return)-30):

            period_excess_return_std.append(np.std(excess_return[i:i+30]))
        period_excess_return_std=np.asarray(period_excess_return_std)
        empty = np.empty(30)
        empty[:] = np.nan
        period_excess_return_std= np.concatenate((empty, period_excess_return_std), axis=0)

        annnulized_sharpe_series=np.sqrt(252)*(mean_excess_return/period_excess_return_std)
        annnulized_sharpe_series=pd.Series(annnulized_sharpe_series,index)

        return description_str,annnulized_sharpe_series



    def pricehandler(self):
        description_str = "Portfolio Value: "
        return description_str,self.total_capital,0,0,0 # sharp ratio// drawdown// dratio


    def pnlhandler(self):

         data=self.total_capital.values
         index=self.total_capital.index
         data=np.diff(data)
         data=data.cumsum()
         self.pnl=pd.Series(data,index[1:])
         description_str = "Portfolio PnL Graph: "
         return description_str, self.pnl





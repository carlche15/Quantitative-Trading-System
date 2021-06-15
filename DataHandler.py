import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import matplotlib.ticker as ticker
from matplotlib.ticker import Formatter
from Event import *

from abc import ABCMeta, abstractmethod
from Stock_Info_Carl import *


class DataHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_data(self, symbol, delay=0):
        raise NotImplementedError("Abstract method not implemented :(")

    @abstractmethod
    def update_observed_data(self):
        raise NotImplementedError("Abstract method not implemented :(")


class Historical_DB_Handler(DataHandler):
    def __init__(self, events, historical_data):
        self.data_type = ["close", "open", "high", "low", "return", "volume"]
        self.events = events
        self.historical_data = historical_data  # sereis of stock objects
        self.time_series = self.historical_data.data[0].close.index  # Simulation of total time series
        self.current_time = self.time_series[0]
        self.symbol_list = self.historical_data.data.index  # list of all stock tickers
        self.latest_symbol_data = pd.DataFrame()
        self.continue_backtest = True


    def get_latest_data(self, symbols=0, delay=0):
        # will return a datframe of the latest data and a time index regarding to this dataframe :)
        latest = pd.DataFrame(index=self.symbol_list, columns=self.data_type)
        for s in self.symbol_list:
            for dt in self.data_type:
                latest.loc[s, dt] = self.historical_data.data[s].get_data(dt)[self.current_time]
        return latest

    #
    #
    def update_observed_data(self):
        next_time = self.time_series[list(self.time_series).index(self.current_time) + 1]
        self.current_time = next_time
        self.events.put(MarketEvent())








        # class Portfolio:
        #     def __init__(self,connection,tickers,start,end,initial_capital=1000000,weights=[]):
        #         self.portfolio=pd.DataFrame()
        #         self.tickers=tickers
        #         self.initial_stock_price=[]
        #         self.capital=initial_capital
        #         self.current_total_capital=pd.Series()
        #         self.portfolio_pnl_series=pd.Series()
        #         self.historical=[]
        #         self.historical_annual_returns=[]
        #         self.latest_close=[]
        #         self.latest_volume=[]
        #         self.latest_high=[]
        #         self.latest_low=[]
        #         self.latest_daily_return=[]
        #         self.latest_open=[]
        #         self.adv20=[]
        #         self.weight_history=[]# save historical weights data of active portfolio managment!
        #         self.period_return=np.nan
        #         self.period_avg_return=np.nan
        #         self.period_std=np.nan
        #         self.period_sharp_ratio=np.nan
        #         self.period_maximum_drawdown=np.nan
        #         self.period_maximum_drawdown_pa=np.nan
        #         self.period_market_return=0.00050
        #
        #         if(len(weights)==0):
        #                    self.weights=np.ones(len(self.tickers))/len(self.tickers)
        #         else:
        #                     temp=np.asarray(weights).sum()
        #                     self.weights=weights/temp
        #
        #
        #         for i in range(len(self.tickers)):
        #                    stock_temp=Stock_Info(connection,self.tickers[i],start,end)
        #                    self.date_index=stock_temp.index
        #                    self.historical.append(stock_temp.oney_return) # order matters
        #                    self.historical_annual_returns.append(stock_temp.annual_avg_return)
        #                    initial_price_temp=stock_temp.selected_line_info.values[0]
        #                    stock_capital_temp=self.capital*self.weights[i]
        #                    stock_share_temp=round(stock_capital_temp/initial_price_temp)
        #                    df_temp=pd.DataFrame([[stock_share_temp,stock_temp.selected_line_info]],columns=["Shares","Price data"],index=[self.tickers[i]])
        #                    self.latest_close.append(stock_temp.selected_line_info)
        #                    self.latest_volume.append(stock_temp.selected_line_info_volume)
        #                    self.latest_open.append(stock_temp.selected_line_info_open)
        #                    self.latest_high.append(stock_temp.selected_line_info_high)
        #                    self.latest_low.append(stock_temp.selected_line_info_low)
        #                    self.latest_daily_return.append(stock_temp.selected_line_info_return)
        #                    self.portfolio=pd.concat([self.portfolio,df_temp],axis=0)
        #                    print "Portfolio Constructing....("+str(i+1)+"/"+str(len(tickers))+")"
        #
        #         self.portfolio["Weighted data"]=pd.Series(self.portfolio["Shares"]*self.portfolio["Price data"],index=self.portfolio.index)
        #         self.portfolio["Latest close"]=pd.Series(self.latest_close,index=self.portfolio.index)
        #         self.portfolio["Latest volume"]=pd.Series(self.latest_volume,index=self.portfolio.index)
        #         self.portfolio["Latest open"]=pd.Series(self.latest_open,index=self.portfolio.index)
        #         self.portfolio["Latest high"] = pd.Series(self.latest_high, index=self.portfolio.index)
        #         self.portfolio["Latest low"] = pd.Series(self.latest_low, index=self.portfolio.index)
        #         self.portfolio["Latest daily return"]=pd.Series(self.latest_daily_return,index=self.portfolio.index)
        #         self.portfolio_value=self.portfolio["Weighted data"].sum()
        #
        #         print "Portfolio Construction completed! "
        #         # self.portfolio_sharp_ratio()
        #
        #     def __call__(self,weights,dates):
        #            #adjust position
        #            new_weights=weights
        #            #1. sum up the current total capital:
        #            current_total=0 # total capital
        #            shares_temp=[] #updated shares of stocks
        #            for i in range(len(self.tickers)):
        #                       current_total+=self.portfolio["Shares"].values[i]*pd.Series(self.portfolio["Latest close"][self.tickers[i]])[dates]
        #         #2. calculate how many shares of each stock:
        #            for i in range(len(self.tickers)):
        #                      share=round((new_weights[i]*current_total)/(pd.Series(self.portfolio["Latest close"][self.tickers[i]])[dates] ))
        #                      shares_temp.append(share)
        #            self.portfolio["Shares"]=shares_temp # update shares information
        #            self.portfolio["Weighted data"] = pd.Series(self.portfolio["Shares"] * self.portfolio["Price data"],index=self.portfolio.index) #update weighted price information
        #            self.weights=weights # update weight information for next total value computation
        #            self.weight_history.append(self.weights)
        #         # Show active portfolio managment result!
        #            temp_series=pd.Series(current_total,index=[dates])
        #            self.current_total_capital=self.current_total_capital.append(temp_series) ## ##
        #            if len(self.current_total_capital)>=2:
        #                     current_pnl=self.current_total_capital[-1]-self.current_total_capital[-2]
        #                     temp=pd.Series(current_pnl,index=[dates])
        #                     self.portfolio_pnl_series=self.portfolio_pnl_series.append(temp)
        #
        #     def portfolio_var(self):
        #
        #                      weight_matrix_temp=(np.mat(self.weights).T)*np.mat(self.weights)
        #                      convariance_matrix=np.mat(np.cov(self.historical))
        #                      temp_result=convariance_matrix*weight_matrix_temp
        #                      temp_result=np.diagonal(temp_result)
        #                      self.totalvar=temp_result.sum()
        #                      self.annualized_total_std=np.sqrt(252*self.totalvar)
        #                      print "portfolio annualized standard deviation: ", self.annualized_total_std
        #                      return self.annualized_total_std
        #
        #     def variance_distribution(self):
        #
        #                     weight_matrix_temp = (np.mat(self.weights).T) * np.mat(self.weights)
        #                     convariance_matrix = np.mat(np.cov(self.historical))
        #        # CONSTRUCTING THE WEIGHTED CO-VARIANCE MATRIX
        #                     df = pd.DataFrame(0.0, index=np.arange(len(convariance_matrix)), columns=np.arange(len(convariance_matrix)))
        #                     for i in range(len(convariance_matrix)):
        #                                       row_temp = np.array(convariance_matrix[i])
        #                                       column_temp = np.array(weight_matrix_temp[:, i]).reshape(1, len(convariance_matrix))
        #                                       temp_result = row_temp * column_temp
        #             # print temp_result
        #                                       for j in range(len(temp_result[0])):
        #                                                              df.iat[i, j] = temp_result[0][j]
        #
        #                     weighted_variance = np.mat(df)
        #                     weighted_variance_diag = np.diag(np.diag(weighted_variance))
        #                     weighted_variance = 2 * weighted_variance
        #                     size = weighted_variance - weighted_variance_diag
        #         # ABOVE IS STEP 2 see document "PROGRAMMING GUIDE"
        #                     df = pd.DataFrame()
        #
        #                     for i in range(len(convariance_matrix)):
        #                                     tem_str1 = "x" + str(i)
        #                                     temp_xx = i * np.ones(len(convariance_matrix))
        #                                     temp_x = pd.DataFrame(temp_xx, columns=[tem_str1])
        #                                     tem_str2 = "y" + str(i)
        #                                     temp_yy = np.arange(len(convariance_matrix))
        #                                     temp_y = pd.DataFrame(temp_yy, columns=[tem_str2])
        #                                     df = pd.concat([df, temp_x], axis=1)
        #                                     df = pd.concat([df, temp_y], axis=1)
        #                                     temp_zz = []
        #                                     tem_str3 = "z" + str(i)
        #                                     for j in np.arange(len(convariance_matrix)):
        #                                                     temp_zz.append(size[temp_xx[j], temp_yy[j]])
        #                                     temp_z = pd.DataFrame(temp_zz, columns=[tem_str3])
        #                                     df = pd.concat([df, temp_z], axis=1)
        #                                     # color=["red","green","blue","cyan","orange","grey","purple","darkgreen","gold","forestgreen","lightcyan","violet"]
        #                     description_str = "Portfolio's risk distribution: "
        #                     return description_str,df
        #     # def portfolio_sharp_ratio(self):
        #     #                 self.portfolio_expected_return=self.weights*np.asarray(self.historical_annual_returns)
        #     #                 self.portfolio_expected_return=self.portfolio_expected_return.sum()
        #     #                 print "portfolio annualized return: ",self.portfolio_expected_return
        #     #                 self.sharp_ratio=(self.portfolio_expected_return-0.017)/self.portfolio_var()
        #     #                 print "Sharp_Ratio: ",self.sharp_ratio
        #     def portfolio_val(self):
        #                     description_str="Portfolio Value: "
        #                     if len(self.current_total_capital)>0:
        #                                 return description_str,self.current_total_capital,self.period_sharp_ratio,self.period_maximum_drawdown, self.period_maximum_drawdown_pa # active portfolio management
        #                     else:
        #                                 return description_str,self.portfolio_value,-999,-999,-999
        #                                 # passive portfolio management
        #     def portfolio_pnl(self):
        #                     index=self.portfolio_pnl_series.index
        #                     data=self.portfolio_pnl_series.values
        #                     data=np.asarray(data)
        #                     data=data.cumsum()
        #                     self.portfolio_pnl_series=pd.Series(data,index=index)
        #                     description_str="Portfolio PnL Graph: "
        #                     return description_str, self.portfolio_pnl_series
        #
        #     def portfolio_weights(self):
        #                        description_str="weights"
        #                        temp=pd.Series(self.weights,index=self.tickers)
        #                        return description_str,temp
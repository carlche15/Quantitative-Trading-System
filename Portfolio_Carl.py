
"""
Portfolio Class and Backtest module
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import matplotlib.ticker as ticker
from matplotlib.ticker import Formatter
from Stock_Info_Carl import *
class MyFormatter(Formatter):
    # http://matplotlib.org/examples/pylab_examples/date_index_formatter.html
            def __init__(self, dates, fmt='%Y-%m-%d'):
                self.dates = dates
                self.fmt = fmt

            def __call__(self, x, pos=0):
                'Return the label for time x at position pos'
                ind = int(round(x))
                if ind >= len(self.dates) or ind < 0:
                    return ''

                return self.dates[ind].strftime(self.fmt)
class Strategy_elements:

    @staticmethod
    def core_1(portfolio,timemark,benchmark,delay=0): # generate elemental weights

        index=[x for x in portfolio.portfolio.columns if benchmark in x][0] # get benchmark name such as "Latest close"
        raw_temp=[]
        for i in range(len(portfolio.portfolio[index].values)):
            raw_temp.append(portfolio.portfolio[index].values[i][timemark])
        return abs(np.asarray(raw_temp))/abs(np.asarray(raw_temp)).sum()

# class Trading_strategy:
#      @staticmethod
#      def user_strategy_1(portfolio,timemark):
#          close=Strategy_elements.core_1(portfolio, timemark, benchmark="close",delay=0)
#          open=Strategy_elements.core_1(portfolio, timemark, benchmark="open",delay=0)
#          high=Strategy_elements.core_1(portfolio, timemark, benchmark="high", delay=0)
#          low=Strategy_elements.core_1(portfolio, timemark, benchmark="low", delay=0)
#          volume=Strategy_elements.core_1(portfolio, timemark, benchmark="volume", delay=0)
#          dailyreturn=Strategy_elements.core_1(portfolio, timemark, benchmark="return", delay=0)
#          print type(close)
#          print type(open)
#          print type(high)
#          print type(low)
#          print type(volume)
#          print type(dailyreturn)
#
#          strategy=[]
#          return 0







class Portfolio:
    def __init__(self,connection,tickers,start,end,initial_capital=1000000,weights=[]):
        self.portfolio=pd.DataFrame()
        self.tickers=tickers
        self.initial_stock_price=[]
        self.capital=initial_capital
        self.current_total_capital=pd.Series()
        self.portfolio_pnl_series=pd.Series()
        self.historical=[]
        self.historical_annual_returns=[]
        self.latest_close=[]
        self.latest_volume=[]
        self.latest_high=[]
        self.latest_low=[]
        self.latest_daily_return=[]
        self.latest_open=[]
        self.adv20=[]
        self.weight_history=[]# save historical weights data of active portfolio managment!
        self.period_return=np.nan
        self.period_avg_return=np.nan
        self.period_std=np.nan
        self.period_sharp_ratio=np.nan

        if(len(weights)==0):
                   self.weights=np.ones(len(self.tickers))/len(self.tickers)
        else:
                    temp=np.asarray(weights).sum()
                    self.weights=weights/temp


        for i in range(len(self.tickers)):
                   stock_temp=Stock_Info(connection,self.tickers[i],start,end)
                   self.date_index=stock_temp.index
                   self.historical.append(stock_temp.oney_return) # order matters
                   self.historical_annual_returns.append(stock_temp.annual_avg_return)
                   initial_price_temp=stock_temp.selected_line_info.values[0]
                   stock_capital_temp=self.capital*self.weights[i]
                   stock_share_temp=round(stock_capital_temp/initial_price_temp)
                   df_temp=pd.DataFrame([[stock_share_temp,stock_temp.selected_line_info]],columns=["Shares","Price data"],index=[self.tickers[i]])
                   self.latest_close.append(stock_temp.selected_line_info)
                   self.latest_volume.append(stock_temp.selected_line_info_volume)
                   self.latest_open.append(stock_temp.selected_line_info_open)
                   self.latest_high.append(stock_temp.selected_line_info_high)
                   self.latest_low.append(stock_temp.selected_line_info_low)
                   self.latest_daily_return.append(stock_temp.selected_line_info_return)
                   self.portfolio=pd.concat([self.portfolio,df_temp],axis=0)
                   print "Portfolio Constructing....("+str(i+1)+"/"+str(len(tickers))+")"

        self.portfolio["Weighted data"]=pd.Series(self.portfolio["Shares"]*self.portfolio["Price data"],index=self.portfolio.index)
        self.portfolio["Latest close"]=pd.Series(self.latest_close,index=self.portfolio.index)
        self.portfolio["Latest volume"]=pd.Series(self.latest_volume,index=self.portfolio.index)
        self.portfolio["Latest open"]=pd.Series(self.latest_open,index=self.portfolio.index)
        self.portfolio["Latest high"] = pd.Series(self.latest_high, index=self.portfolio.index)
        self.portfolio["Latest low"] = pd.Series(self.latest_low, index=self.portfolio.index)
        self.portfolio["Latest daily return"]=pd.Series(self.latest_daily_return,index=self.portfolio.index)
        self.portfolio_value=self.portfolio["Weighted data"].sum()

        print "Portfolio Construction completed! "
        # self.portfolio_sharp_ratio()

    def __call__(self,weights,dates):
           #adjust position
           new_weights=weights
           #1. sum up the current total capital:
           current_total=0 # total capital
           shares_temp=[] #updated shares of stocks
           for i in range(len(self.tickers)):
                      current_total+=self.portfolio["Shares"].values[i]*pd.Series(self.portfolio["Latest close"][self.tickers[i]])[dates]
        #2. calculate how many shares of each stock:
           for i in range(len(self.tickers)):
                     share=round((new_weights[i]*current_total)/(pd.Series(self.portfolio["Latest close"][self.tickers[i]])[dates] ))
                     shares_temp.append(share)
           self.portfolio["Shares"]=shares_temp # update shares information
           self.portfolio["Weighted data"] = pd.Series(self.portfolio["Shares"] * self.portfolio["Price data"],index=self.portfolio.index) #update weighted price information
           self.weights=weights # update weight information for next total value computation
           self.weight_history.append(self.weights)
        # Show active portfolio managment result!
           temp_series=pd.Series(current_total,index=[dates])
           self.current_total_capital=self.current_total_capital.append(temp_series) ## ##
           if len(self.current_total_capital)>=2:
                    current_pnl=self.current_total_capital[-1]-self.current_total_capital[-2]
                    temp=pd.Series(current_pnl,index=[dates])
                    self.portfolio_pnl_series=self.portfolio_pnl_series.append(temp)

    def portfolio_var(self):

                     weight_matrix_temp=(np.mat(self.weights).T)*np.mat(self.weights)
                     convariance_matrix=np.mat(np.cov(self.historical))
                     temp_result=convariance_matrix*weight_matrix_temp
                     temp_result=np.diagonal(temp_result)
                     self.totalvar=temp_result.sum()
                     self.annualized_total_std=np.sqrt(252*self.totalvar)
                     print "portfolio annualized standard deviation: ", self.annualized_total_std
                     return self.annualized_total_std

    def variance_distribution(self):

                    weight_matrix_temp = (np.mat(self.weights).T) * np.mat(self.weights)
                    convariance_matrix = np.mat(np.cov(self.historical))
       # CONSTRUCTING THE WEIGHTED CO-VARIANCE MATRIX
                    df = pd.DataFrame(0.0, index=np.arange(len(convariance_matrix)), columns=np.arange(len(convariance_matrix)))
                    for i in range(len(convariance_matrix)):
                                      row_temp = np.array(convariance_matrix[i])
                                      column_temp = np.array(weight_matrix_temp[:, i]).reshape(1, len(convariance_matrix))
                                      temp_result = row_temp * column_temp
            # print temp_result
                                      for j in range(len(temp_result[0])):
                                                             df.iat[i, j] = temp_result[0][j]

                    weighted_variance = np.mat(df)
                    weighted_variance_diag = np.diag(np.diag(weighted_variance))
                    weighted_variance = 2 * weighted_variance
                    size = weighted_variance - weighted_variance_diag
        # ABOVE IS STEP 2 see document "PROGRAMMING GUIDE"
                    df = pd.DataFrame()

                    for i in range(len(convariance_matrix)):
                                    tem_str1 = "x" + str(i)
                                    temp_xx = i * np.ones(len(convariance_matrix))
                                    temp_x = pd.DataFrame(temp_xx, columns=[tem_str1])
                                    tem_str2 = "y" + str(i)
                                    temp_yy = np.arange(len(convariance_matrix))
                                    temp_y = pd.DataFrame(temp_yy, columns=[tem_str2])
                                    df = pd.concat([df, temp_x], axis=1)
                                    df = pd.concat([df, temp_y], axis=1)
                                    temp_zz = []
                                    tem_str3 = "z" + str(i)
                                    for j in np.arange(len(convariance_matrix)):
                                                    temp_zz.append(size[temp_xx[j], temp_yy[j]])
                                    temp_z = pd.DataFrame(temp_zz, columns=[tem_str3])
                                    df = pd.concat([df, temp_z], axis=1)
                                    # color=["red","green","blue","cyan","orange","grey","purple","darkgreen","gold","forestgreen","lightcyan","violet"]
                    description_str = "Portfolio's risk distribution: "
                    return description_str,df
    # def portfolio_sharp_ratio(self):
    #                 self.portfolio_expected_return=self.weights*np.asarray(self.historical_annual_returns)
    #                 self.portfolio_expected_return=self.portfolio_expected_return.sum()
    #                 print "portfolio annualized return: ",self.portfolio_expected_return
    #                 self.sharp_ratio=(self.portfolio_expected_return-0.017)/self.portfolio_var()
    #                 print "Sharp_Ratio: ",self.sharp_ratio
    def portfolio_val(self):
                    description_str="Portfolio Value: "
                    if len(self.current_total_capital)>0:
                                return description_str,self.current_total_capital # active portfolio management
                    else:
                                return description_str,self.portfolio_value
                                # passive portfolio management
    def portfolio_pnl(self):
                    index=self.portfolio_pnl_series.index
                    data=self.portfolio_pnl_series.values
                    data=np.asarray(data)
                    data=data.cumsum()
                    self.portfolio_pnl_series=pd.Series(data,index=index)
                    description_str="Portfolio PnL Graph: "
                    return description_str, self.portfolio_pnl_series

    def portfolio_weights(self):
                       description_str="weights"
                       temp=pd.Series(self.weights,index=self.tickers)
                       return description_str,temp
class Operator:
    def __init__(self,portfolio):
      self.portfolio=portfolio
      self.index=self.portfolio.date_index

    def In_sample_test(self,strategy, show_animation=False):

        self.portfolio.weight_history=[] #for strategy animation
        for date in self.index:
            weights=Strategy_elements.core_1(self.portfolio, date, strategy, 0) # here, the weight comes from algorithm using simply an elemental signal
            # xxx=Trading_strategy.user_strategy_1(self.portfolio,date)
            # print weights\
            self.portfolio(weights,date)
        if  show_animation:
            try:
                  fig = plt.figure(figsize=(120,100))

                # Weights information
                  ax1=plt.subplot(2,1,1)
                  ax1.set_xlim([-0.2,3.2])
                  ax1.set_ylim([0,1.0])
                  (line,) = ax1.plot([], [], "bo",color="green",markersize=30,alpha=0.4)
                  text1=ax1.text(3 ,0.9,"")
                  plt.xticks(np.linspace(0, 3, len(self.portfolio.tickers)), self.portfolio.tickers)


                # Capital information

                  ax2=plt.subplot(2,1,2)
                  ax2.set_xlim([0,len(self.portfolio.current_total_capital) ])
                  ax2.set_ylim([500000,1400000])

                  # display dates properly on x axis
                  ind =np.linspace(0,len(self.portfolio.current_total_capital),len(self.portfolio.current_total_capital))
                  index=self.portfolio.current_total_capital.index
                  formatter = MyFormatter(index)
                  ax2.xaxis.set_major_formatter(formatter)
                  formatter = ticker.FormatStrFormatter("$%1.2f")
                  ax2.yaxis.set_major_formatter(formatter)


                  (line2,) = ax2.plot([], [], lw=0.3, c="dodgerblue")
                  (line3,)=ax2.plot([],[],lw=2,c="mediumpurple",alpha=0.7)
                  text2 = ax2.text(0, 0, "")

                  def init():
                             line.set_data([], [])
                             line2.set_data([],[])
                             return line, line2, text1,

                  def animate(i):
                            # for weights information
                            x =np.linspace(0,3,len(self.portfolio.tickers))
                            y =self.portfolio.weight_history[i]
                            z1 = ax1.fill_between(x, y, color="green", alpha=0.3)
                            line.set_data(x, y)
                            text=ax1.text(1,0.9,"Postition& Capital Information (Date:  "+str(self.index[i])+")",fontsize=16)

                            # for capital information
                            x2=np.linspace(0,len(self.portfolio.current_total_capital),len(self.portfolio.current_total_capital))
                            y2_hasvalue=self.portfolio.current_total_capital.values[0:i]
                            y2_novalue=np.empty(len(self.portfolio.current_total_capital)-len(y2_hasvalue))
                            y2_novalue[:]=np.nan
                            y2=np.concatenate([y2_hasvalue,y2_novalue])
                            z2=ax2.fill_between(x2,y2,color="dodgerblue",alpha=0.5 )
                            # y2=self.portfolio.current_total_capital.values[i]
                            line2.set_data(x2,y2)
                            m=sns.set_style("whitegrid")

                            # Current capital line

                            y3 = self.portfolio.current_total_capital.values[i]
                            text2 = ax2.text(len(self.portfolio.current_total_capital)*0.75, y3+10000,
                                             "Current Capital:  " + str(y3),
                                             fontsize=14,color="mediumpurple")
                            line3.set_data(x2,y3)
                            return line,line2, text,z2,line3,text2,z1

                  anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(self.portfolio.weight_history), interval=10, blit=True,repeat=False)

                  # anim.save('basic_animation.mp4', fps=20,bitrate=-1)
                  plt.title("Active Portfolio Management Animation ")
                  # ticker1 = plt.xticks(np.linspace(0,3,len(self.portfolio.tickers)), self.portfolio.tickers)
                  # plt.xticks(np.linspace(0, 3, len(self.portfolio.tickers)), self.portfolio.tickers)
                  # plt.xticks(np.linspace(0,len(self.portfolio.current_total_capital),len(self.portfolio.current_total_capital)), self.portfolio.current_total_capital.index)
                  sns.set_style("whitegrid")
                  plt.show()
            except IndexError:
                print "Index Error"
                return -1

            # Calculate Sharp Ratio
        data=self.portfolio.current_total_capital.values
        index=self.portfolio.current_total_capital.index
        data_diff=np.diff(data)
        data=data[:-1]
        index=index[1:]
        returns=data_diff/data
        trading_period=len(returns)
        self.portfolio.period_return=pd.Series(returns,index=index)
        self.portfolio.period_avg_return=np.mean(self.portfolio.period_return.values)
        self.portfolio.period_std=np.std(self.portfolio.period_return)
        self.portfolio.period_sharp_ratio=np.sqrt(trading_period)*self.portfolio.period_avg_return/self.portfolio.period_std
        print self.portfolio.period_sharp_ratio



    def close(self,delay=0):
        print Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="close")
        return Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="close")
    def open(self,delay=0):
       print Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="open")
       return Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="open")
    def high(self,delay=0):
        print Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="high")
        return Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="high")
    def low(self,delay=0):
        print Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="low")
        return Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="low")
    def returns(self,delay=0):
        print Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="return")
        return Strategy_elements.core_1(self.portfolio,delay=delay,benchmark="return")


# class collection:
#     def __init__(self, num,connection):
#       self.var=[]
#       self.ret=[]
#       ticker = ["CSCO", "BMY", "IBM", "HON"]
#       start = "2016-01-01"
#       end = "2016-08-19"
#       for i in range(num):
#
#             weights2 = list(abs(np.random.randn(len(ticker))))
#             portfolio_temp = Portfolio(connection, ticker, start, end, weights=weights2)
#             self.var.append(portfolio_temp.annualized_total_std)
#             self.ret.append(portfolio_temp.portfolio_expected_return)
#             print "calculation on going", i,"/",num

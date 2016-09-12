"""
Portfolio Object & functional tools 
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )

"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from Stock_Info_Carl import *
class Strategy_elements:

    @staticmethod
    def core_1(portfolio,timemark,benchmark,delay=0):


        index=[x for x in portfolio.portfolio.columns if benchmark in x][0] # get benchmark name such as "Latest close"
        raw_temp=[]
        for i in range(len(portfolio.portfolio[index].values)):
            raw_temp.append(portfolio.portfolio[index].values[i][timemark])
        return abs(np.asarray(raw_temp))/abs(np.asarray(raw_temp).sum())
class Portfolio:
    def __init__(self,connection,tickers,start,end,initial_capital=1000000,weights=[]):
        self.portfolio=pd.DataFrame()
        self.tickers=tickers
        self.initial_stock_price=[]
        self.capital=initial_capital
        self.current_total_capital=pd.Series()
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
                   self.latest_daily_return.append(stock_temp.oney_return)
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
        self.portfolio_sharp_ratio()

    def __call__(self,weights,dates):
           #adjust position
           new_weights=weights
           #1.current total capital:
           current_total=0 # total capital
           shares_temp=[] #updated shares of stocks
           for i in range(len(self.tickers)):
                      current_total+=self.portfolio["Shares"].values[i]*pd.Series(self.portfolio["Latest close"][self.tickers[i]])[dates]
        # print "first",self.weights[i],"second",pd.Series(self.portfolio["Latest close"][self.tickers[i]])[dates]
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
    def portfolio_sharp_ratio(self):
                    self.portfolio_expected_return=self.weights*np.asarray(self.historical_annual_returns)
                    self.portfolio_expected_return=self.portfolio_expected_return.sum()
                    print "portfolio annualized return: ",self.portfolio_expected_return
                    self.sharp_ratio=(self.portfolio_expected_return-0.017)/self.portfolio_var()
                    print "Sharp_Ratio: ",self.sharp_ratio
    def portfolio_val(self):
                    description_str="Portfolio Value: "
                    if len(self.current_total_capital)>0:
                                return description_str,self.current_total_capital
                    else:
                                return description_str,self.portfolio_value
    def portfolio_weights(self):
                       description_str="weights"
                       temp=pd.Series(self.weights,index=self.tickers)
                       return description_str,temp
class Operator:
    def __init__(self,portfolio):
      self.portfolio=portfolio
      self.index=self.portfolio.date_index
    def In_sample_test(self,show_animation=False):

        self.portfolio.weight_history=[]
        print "In sample test result: "
        for date in self.index:
            weights=Strategy_elements.core_1(self.portfolio, date, "close", 0)
            self.portfolio(weights,date)
        if  show_animation:
            try:
                  fig=plt.figure()
                  ax=plt.axes(xlim=(-1,4),ylim=(0,0.5))
                  (line,) = ax.plot([], [], "bo",markersize=20,alpha=0.4)
                  def init():
                             line.set_data([], [])
                             return line,

                  def animate(i):
                            global f
                            x =np.linspace(0,3,len(self.portfolio.tickers))
                            y =self.portfolio.weight_history[i]
                            line.set_data(x, y)
                            return line,

                  anim = animation.FuncAnimation(fig, animate, init_func=init, frames=len(self.portfolio.weight_history), interval=100, blit=True,repeat=False)
                  plt.title("Active Portfolio Management Animation ")
                  plt.xticks(np.linspace(0,3,len(self.portfolio.tickers)),self.portfolio.tickers)
                  plt.show()
            except IndexError:
                return -1




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


"""
Stock & Portfolio Data Visualization Tools
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )

"""
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import Formatter
import matplotlib.ticker as ticker
from matplotlib import gridspec
from yahoo_finance import Share
from matplotlib.finance import candlestick_ohlc as candle
from  Cursor_Haunter_Carl import *
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
class Chart_Factory:
  #global indicator
         indicator=0
         def __init__(self):
                      self.portfolio={}
                      self.data_stack={}
                      self.price_data={}
                      self.candleprice_data={}
                      self.subline_rsi={}
                      self.subline_macd={}
                      self.subline_obv={}
                      self.subline_volume={}
                      self.current_indicator=0
                      self.figure_map={"candle":False,"price":False,"rsi":False,"macd":False,"obv":False,"portfolio":False,"volume":False}

 # This is a cheap shot, has to be mended later on~~~~~
         def add_index(self,stockticker):
                    self.index=stockticker.price()[1].index

         def push_data(self,method,isprice=False,iscandle=False,issubline_rsi=False,issubline_macd=False,issubline_obv=False,isportolio=False, issubline_volume=False):

                    if (iscandle):
                             index, value = method
                             self.candleprice_data[index] = value
                             self.figure_map["candle"]=True

                    elif (isprice):
                             index, value = method
                             self.price_data[index] = value
                             self.figure_map["price"]=True
                    elif(isportolio):
                             index,value=method
                             self.portfolio[index]=value
                             self.figure_map["portfolio"]=True
                    elif(issubline_rsi):
                             self.indicator += 1
                             index, value = method
                             self.subline_rsi[index] = value
                             self.figure_map["rsi"]=True
                    elif(issubline_macd):
                            self.indicator += 1
          # index,value=method
          # self.subline_macd[index]=value
                            for i in range(0, len(method), 2):
                                         index = method[i]
                                         value = method[1 + i]
                                         self.subline_macd[index] = value
                            self.figure_map["macd"]=True

                    elif(issubline_obv):
                             self.indicator += 1
                             for i in range(0, len(method), 2):
                                         index = method[i]
                                         value = method[1 + i]
                                         self.subline_obv[index] = value
                             self.figure_map["obv"] = True

                    elif (issubline_volume):
                        self.indicator += 1
                        for i in range(0, len(method), 2):
                            index = method[i]
                            value = method[1 + i]
                            self.subline_volume[index] = value
                        self.figure_map["volume"] = True


                    else:
                                 for i in range(0,len(method),2):
                                                index=method[i]
                                                value=method[1+i]
                                                self.data_stack[index]=value

         def plot_price(self,ax):
                    ax=ax
                    for i in self.price_data:
                                  index = self.price_data[i].index
                                  data = self.price_data[i].values
                                  ind = np.arange(len(index))  #
                                  formatter = MyFormatter(index)  #

                                  ax.xaxis.set_major_formatter(formatter)  #

                                  ax.plot(ind, data, lw=3, c="skyblue")  #
                                  formatter = ticker.FormatStrFormatter('$%1.2f')
                                  ax.yaxis.set_major_formatter(formatter)
                                  min_temp = np.min(data)
                                  max_temp=np.max(data)
                                  plt.xticks()
                                  ax.set_title("Price",fontsize=12)

          ######designed for equally displaying codes!!!!!!!
                                  date_min = np.min(ind)
                                  date_max = np.max(ind)
                                  plt.xlim([date_min, date_max])
                                  density_temp = len(ind) / 20
                                  zip = np.arange(date_min, date_max, density_temp + 1)
                                  plt.xticks(zip)

          #start text
                                  tickerr="AAPL"
                                  current_price = Share(tickerr).get_price()  # latest
                                  open_price = Share(tickerr).get_open()
                                  high_price=Share(tickerr).get_days_high()
                                  low_price=Share(tickerr).get_days_low()
                                  change_price = Share(tickerr).get_change()
                                  current_time = Share(tickerr).get_trade_datetime()
                                  Last_price=Share(tickerr).get_prev_close()
                                  volume=Share(tickerr).get_volume()
                                  current_price="Current: "+current_price
                                  open_price="Open: "+open_price
                                  high_price="High: "+high_price
                                  low_price="Low: "+low_price
                                  Last_price="Last: "+Last_price
                                  change_price="Chg: "+change_price
                                  volume="Volume: "+volume
                                  ss=current_time+'    '+ current_price+"    "+open_price+"    "+high_price+"    "+low_price+"    "+Last_price+"    "+volume+"    "+change_price
                                  plt.text(date_min+2,max_temp+8,ss,fontsize=15)

                                  ax.fill_between(ind, min_temp - 10.0, data, color="dodgerblue",alpha=0.4)

                                  cursor1 = Cursor_haunter(ax, ind, data, "Close price", 1)



         def plot_other_data(self,ax):
                    ax=ax
                    for i in self.data_stack:
                                index=self.data_stack[i].index
                                data=self.data_stack[i].values
                                ind = np.arange(len(index))  #
                                formatter = MyFormatter(index)  #
                                ax.xaxis.set_major_formatter(formatter)  #
                                ax.plot(ind, data,alpha=0.8)  #
          # fig.autofmt_xdate()  #
                                date_min = np.min(ind)
                                date_max = np.max(ind)
                                plt.xlim([date_min, date_max])
                    plt.legend(self.price_data.keys()+self.data_stack.keys(),fontsize=12)

         def plot_candle_price(self,ax):
                     ax=ax
                     for i in self.candleprice_data:
           # minor ticks on the days

                                     list = self.candleprice_data[i]
                                     index = self.index
           # The 2 lines of code below this is really magnificent!!!
                                     for i in range(len(list)):
                                                           list[i][0] = i
                                     ind = np.arange(len(index))  #
                                     formatter = MyFormatter(index)  #
                                     ax.xaxis.set_major_formatter(formatter)  #
                                     candle(ax, list, width=0.6)
                     plt.title("", fontsize=20)
                     plt.ylabel("Price/USD", fontsize=14)



         def plot_sub_rsi(self,ax,fig,gs):

                     if (len(self.subline_rsi) != 0):
                               plt.title(str(self.subline_rsi.keys()[0]), fontsize=13)
                               for i in self.subline_rsi:
                                                index = self.subline_rsi[i].index
                                                data = self.subline_rsi[i].values
                                                overboughtband = data * 0 + 70
                                                oversoldband = data * 0 + 30

                                                ind = np.arange(len(index))  #
                                                formatter = MyFormatter(index)  #
                                                ax.xaxis.set_major_formatter(formatter)  #
                                                ax.plot(ind, data, color="tomato")  #
                                                ax.set_title("Relative Strength Index", fontsize=12)
                                                # fig.autofmt_xdate()  #

                                                date_min = np.min(ind)
                                                date_max = np.max(ind)
                                                plt.xlim([date_min, date_max])

                                                cursor2 = Cursor_haunter(ax, ind, data, "Relative Strength Index:", 1)
                                                ax.plot(ind, overboughtband, '--', color="steelblue", linewidth=1.2, )
                                                ax.plot(ind, oversoldband, '--', color="steelblue", linewidth=1.2)

         def plot_sub_macd(self,ax,fig,gs):
                    if (len(self.subline_macd) != 0):

                                 sig_temp=[x for x in self.subline_macd.keys() if "signal" in x]# since this kind of data should ne shown as a bar chart
                                 plt.title(str(self.subline_macd.keys()[0]), fontsize=13)
                                 for i in self.subline_macd:
                                               if i not in sig_temp:
                                                      index = self.subline_macd[i].index
                                                      data = self.subline_macd[i].values
                                                      ind = np.arange(len(index))  #
                                                      formatter = MyFormatter(index)  #
                                                      ax.xaxis.set_major_formatter(formatter)  #
                                                      ax.plot(ind, data,alpha=0.8)  #
                                                      # fig.autofmt_xdate()  #
                                                      date_min = np.min(ind)
                                                      date_max = np.max(ind)
                                                      plt.xlim([date_min, date_max])
                                 ax.set_title("Moving Average Convergence Divergence Line", fontsize=12)
                                 index=self.subline_macd[sig_temp[0]].index
                                 data=self.subline_macd[sig_temp[0]].values
                                 ax.bar(ind, data,color="teal",alpha=0.8)
                                 # cursor2 = Cursor_haunter(ax, index, data, "MACD Signal:", 1)
                                 # the above line of code is remained to be seen sicne it is far too slow to run!!!!
                                 plt.legend(self.subline_macd.keys(), fontsize=12)


         def plot_sub_obv(self,ax,fig,gs):

                   if (len(self.subline_obv) != 0):

                            sig_temp = [x for x in self.subline_obv.keys() if "balance" in x]
                            color_map = ["r", "g"]
                            temp_i = 0
                            plt.title(str(self.subline_obv.keys()[0]), fontsize=13)
                            for i in self.subline_obv:
                                       if i not in sig_temp:
                                                      index = self.subline_obv[i].index
                                                      data = self.subline_obv[i].values
                                                      ind = np.arange(len(index))  #
                                                      formatter = MyFormatter(index)  #
                                                      ax.xaxis.set_major_formatter(formatter)  #
                                                      ax.bar(ind, data, color=color_map[temp_i],alpha=0.7)  #
                                                      temp_i += 1
                                                      date_min = np.min(ind)
                                                      date_max = np.max(ind)
                                                      plt.xlim([date_min, date_max])
                            ax.set_title("On Balance Volume", fontsize=12)
                            index = self.subline_obv[sig_temp[0]].index
                            data = self.subline_obv[sig_temp[0]].values
                            ind = np.arange(len(index))  #
                            formatter = MyFormatter(index)  #
                            ax.xaxis.set_major_formatter(formatter)  #
                            ax.plot(ind, data)  #
                            cursor2 = Cursor_haunter(ax, ind, data, "On Balance Volume:", 1)
                           # fig.autofmt_xdate()  #
                            plt.legend(["OBV", "Trading volume"], fontsize=12)


         def plot_sub_volume(self, ax, fig, gs):
                if (len(self.subline_volume) != 0):

                          sig_temp = [x for x in self.subline_volume.keys() if "balance" in x]
                          color_map = ["r", "g"]
                          temp_i = 0
                          plt.title(str(self.subline_volume.keys()[0]), fontsize=13)
                          for i in self.subline_volume:
                                    if i not in sig_temp:
                                           index = self.subline_volume[i].index
                                           data = self.subline_volume[i].values
                                           ind = np.arange(len(index))  #
                                           formatter = MyFormatter(index)  #
                                           ax.xaxis.set_major_formatter(formatter)  #
                                           ax.bar(ind, data, color=color_map[temp_i], alpha=0.7)  #
                                           temp_i += 1
                                           date_min = np.min(ind)
                                           date_max = np.max(ind)
                                           plt.xlim([date_min, date_max])
                          ax.set_title("Trading Volume",fontsize=12)
                          index = self.subline_volume[sig_temp[0]].index
                          data = self.subline_volume[sig_temp[0]].values
                          ind = np.arange(len(index))  #
                          formatter = MyFormatter(index)  #
                          ax.xaxis.set_major_formatter(formatter)  #
                          # ax.plot(ind, data)  #
                          # cursor2 = Cursor_haunter(ax, ind, data, "On Balance Volume:", 1)
        # fig.autofmt_xdate()  #



         def plot_all(self):
                  fig=plt.figure()
                  plot_map_1=[1.8]
                  plot_map_2=[1.8,1]
                  plot_map_3 = [1.8,1,1]
                  plot_map_4 = [1.8,1,1,1]
                  plot_map_5=[1.8,1,1,1,1]
                  plot_map=[plot_map_1,plot_map_2,plot_map_3,plot_map_4,plot_map_5]
                  gs = gridspec.GridSpec(self.indicator+1, 1, height_ratios=plot_map[self.indicator])
                  ax = fig.add_subplot(gs[self.current_indicator])
                  # ax.set_axis_bgcolor('darkslategray')
                  self.plot_price(ax)
                  self.plot_other_data(ax)
                  self.plot_candle_price(ax)
                  if(self.figure_map["rsi"]):
                           self.current_indicator+=1
                           ax = fig.add_subplot(gs[self.current_indicator], sharex=ax)
                           self.plot_sub_rsi(ax,fig,gs)

                  if(self.figure_map["macd"]):
                               self.current_indicator +=1
                               ax = fig.add_subplot(gs[self.current_indicator], sharex=ax)
                               self.plot_sub_macd(ax,fig,gs)

                  if(self.figure_map["obv"]):
                                 self.current_indicator +=1
                                 ax = fig.add_subplot(gs[self.current_indicator], sharex=ax)
                                 self.plot_sub_obv(ax,fig,gs)

                  if (self.figure_map["volume"]):

                      self.current_indicator += 1
                      ax = fig.add_subplot(gs[self.current_indicator], sharex=ax)
                      self.plot_sub_volume(ax, fig, gs)
                  plt.show()
class Chart_Factory_Portfolio:
  #global indicator
  indicator2=0
  def __init__(self):
      self.portfolio={}
      self.current_indicator=0
      self.figure_map={"portfolio":False,"weights":False,"risk":False,"pnl":False}

  def push_data(self,method,isportfolio=False,isweight=False,isrisk=False,ispnl=False):
              if(isportfolio):
                         index,value=method
                         self.portfolio[index]=value
                         self.figure_map["portfolio"]=True

              if(isweight):
                         self.indicator2+=1
                         index,value=method
                         self.portfolio[index]=value
                         self.figure_map["weights"]=True

              if(ispnl):
                         self.indicator2+=1
                         index, value=method
                         self.portfolio[index]=value
                         self.figure_map["pnl"]=True

              if(isrisk):
                         self.indicator2+=1
                         index,value=method
                         self.portfolio[index]=value
                         self.figure_map["risk"]=True

  def plot_portfolio_risk(self,ax):
            ax=ax
            df=self.portfolio["Portfolio's risk distribution: "]
            for i in range(len(df)):
                        x_str_temp="x"+str(i)
                        y_str_temp="y"+str(i)
                        z_str_temp="z"+str(i)
                        # color=np.random.rand(len(df[x_str_temp]))
                        color=["red","green","blue","cyan","orange","grey","purple","darkgreen","gold","forestgreen","lightcyan","violet"]
                        area=np.pi * (600000* df[z_str_temp].values) ** 2
                        plt.scatter(x=df[x_str_temp].values, y=df[y_str_temp].values, s=area, c=color, edgecolors=None, alpha=0.4)
            plt.title("Current Portfolio Management Risk Distribution",fontsize=18)
            tickers=self.portfolio["weights"].index
            plt.xticks(np.arange(len(tickers)), tickers)
            plt.yticks(np.arange(len(tickers)), tickers)


  def plot_portfolio_val(self,ax):
          ax=ax
          index = self.portfolio["Portfolio Value: "].index
          data = self.portfolio["Portfolio Value: "].values
          ind = np.arange(len(index))  #
          formatter = MyFormatter(index)  #
          ax.xaxis.set_major_formatter(formatter)  #
          ax.plot(ind, data,color="dodgerblue",lw=2)  #
          formatter = ticker.FormatStrFormatter('$%1.2f')
          ax.yaxis.set_major_formatter(formatter)
          min_temp = np.min(data)
          max_temp=np.max(data)
          plt.xticks()

          date_min = np.min(ind)
          date_max = np.max(ind)
          plt.xlim([date_min, date_max])

          ######designed for equally display codes!!!!!!

          ax.set_title("Portfolio Capital",fontsize=16)
          ax.set_xlabel("Date", fontsize=10)
          ax.set_ylabel("Portfolio capital / USD", fontsize=10)
          ax.fill_between(ind,0, data, color="dodgerblue",alpha=0.45)
          # fig.autofmt_xdate()
          # cursor1 = Cursor_haunter(ax, ind, data, "Portfolio Value", 1)

  def plot_weights(self,ax):
      ax=ax
      if (len(self.portfolio["weights"]) != 0):
               index=self.portfolio["weights"].index
               data=self.portfolio["weights"].values
               fake=np.arange(len(index))
               plt.xticks(fake,index)
               ax.bar(fake,data,color=["limegreen","deepskyblue","plum","darkorange","tomato","y"],alpha=0.7)
               ax.set_title("Final Positions", fontsize=16)
               ax.set_xlabel("Stock symbols", fontsize=10)
               ax.set_ylabel("Volume/Share", fontsize=10)

               # xxx=self.portfolio["weights"]
               # xxx.plot(kind="bar",color="salmon",colour=["limegreen","deepskyblue","plum","darkslategray","r"])
               # ax.bar(index, data, color="green")  #
               # plt.legend(["OBV", "Trading volume"], fontsize=12)

  def plot_pnl(self, ax):
              ax = ax
              index = self.portfolio["Portfolio PnL Graph: "].index
              data = self.portfolio["Portfolio PnL Graph: "].values
              ind = np.arange(len(index))
              formatter=MyFormatter(index)
              ax.xaxis.set_major_formatter(formatter)
              ax.plot(ind,data,color="green",lw=1.44,alpha=0.9)
              ax.set_title("Profit and Loss Graph", fontsize=16)
              formatter=ticker.FormatStrFormatter("$%1.2f")
              ax.yaxis.set_major_formatter(formatter)
              ax.set_xlabel("Date", fontsize=10)
              ax.set_ylabel("Profit & Loss / USD", fontsize=10)
              # xxx=self.portfolio["weights"]
              # xxx.plot(kind="bar",color="salmon",colour=["limegreen","deepskyblue","plum","darkslategray","r"])
              # ax.bar(index, data, color="green")  #
              # plt.legend(["OBV", "Trading volume"], fontsize=12)

  def plot_all(self):

      plot_map_1=[2]
      plot_map_2=[2,1]
      plot_map_3 = [2,1,1]
      plot_map_4 = [2,1,1,1]
      plot_map=[plot_map_1,plot_map_2,plot_map_3,plot_map_4]
      fig = plt.figure()
      gs = gridspec.GridSpec(self.indicator2, 1, height_ratios=plot_map[self.indicator2-1])
      ax = fig.add_subplot(gs[self.current_indicator])
      # ax.set_axis_bgcolor('darkslategray')
      self.plot_portfolio_val(ax)

      if(self.figure_map["pnl"]):
                     self.current_indicator+=1
                     ax=fig.add_subplot(gs[self.current_indicator])
                     self.plot_pnl(ax)

      if (self.figure_map["weights"]):
                     self.current_indicator += 1
                     ax = fig.add_subplot(gs[self.current_indicator])
                     self.plot_weights(ax)

      if (self.figure_map["risk"]):
                      ff=plt.figure()
                      self.current_indicator += 1
                      ax=plt.subplot()
                      self.plot_portfolio_risk(ax)


      plt.show()
      sns.set_style("whitegrid")

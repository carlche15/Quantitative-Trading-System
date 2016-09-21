"""
Important Note:
This integrated script is no longer the latest version.
For any usage or modification please contact the author:
Tongda (Carl) Che 
carlche@bu.edu
Thanks
"""
import pandas as pd
import numpy as np
import seaborn as sns
from yahoo_finance import Share
import matplotlib.pyplot as plt
import sqlite3 as sql
import time
import datetime
import matplotlib.dates as mdates
import scipy.spatial as spatial
from matplotlib import gridspec
import matplotlib.ticker as ticker
from matplotlib.ticker import Formatter
from matplotlib.finance import candlestick_ohlc as candle
from itertools import permutations
import time


connection=sql.connect("stock_data_94.db")
def database_ini():
 df=pd.DataFrame()
 print "Start constructing the stock database...."
 ticker=["AAPL","GOOG","MSFT","XOM","BRK-A","AMZN","FB","JNJ","GE","T",
         "WFC","JPM","WMT","VZ","PG","PFE","CVX","KO","V","HD","ORCL",
         "CMCSA","INTC","MRK","DIS","PEP","IBM","PM","CSCO","BAC","UNH",
         "MO","C","BMY","AMGN","MDT","GILD","SLB","MCD","MMM","ABBV","KHC",
         "CVS","MA","AGN","UPS","NKE","QCOM","HON","WBA"]
 start='2014-06-25'
 end='2016-08-10'
 for i in range(len(ticker)):
      temp1=Share(ticker[i]).get_historical(start,end)
      temp2=pd.DataFrame(temp1)
      df=pd.concat([df,temp2],axis=0)
      print i+1, "/50 is completed!"
 print "Database construction is completed! "

 df=df[["Symbol","Date","Close","Open","Volume","High","Low"]]
 df=df.sort_values(by=["Date","Symbol"],ascending=[True,True])
 df["Close"] = df["Close"].astype(float)
 df["Open"]=df["Open"].astype(float)
 df["Volume"]=df["Volume"].astype(float)
 df["High"]=df["High"].astype(float)
 df["Low"]=df["Low"].astype(float)


 df.to_sql(con=connection,name="stock_data",flavor="sqlite",if_exists="replace" )
def update():
    pdx = pd.read_sql_query("SELECT * From stock_data WHERE date=(select max(date) from stock_data)", con=connection)
    current_time = time.strftime("%Y-%m-%d")
    latest_time = pdx.iat[0, 2]
    if (current_time <= latest_time):
        print "Data is up to date."
    else:
        df = pd.DataFrame()
        print "Start updating the stock database...."
        ticker = ["AAPL", "GOOG", "MSFT", "XOM", "BRK-A", "AMZN", "FB", "JNJ", "GE", "T",
                  "WFC", "JPM", "WMT", "VZ", "PG", "PFE", "CVX", "KO", "V", "HD", "ORCL",
                  "CMCSA", "INTC", "MRK", "DIS", "PEP", "IBM", "PM", "CSCO", "BAC", "UNH",
                  "MO", "C", "BMY", "AMGN", "MDT", "GILD", "SLB", "MCD", "MMM", "ABBV", "KHC",
                  "CVS", "MA", "AGN", "UPS", "NKE", "QCOM", "HON", "WBA"]
        start = latest_time
        end = current_time
        for i in range(len(ticker)):
            temp1 = Share(ticker[i]).get_historical(start, end)
            temp2 = pd.DataFrame(temp1)
            df = pd.concat([df, temp2], axis=0)
            print i + 1, "/50 is updated!"
        print "Database is up to date! "
        df = df[["Symbol", "Date", "Adj_Close", "Open", "Volume", "High", "Low"]]
        df = df.sort_values(by=["Date", "Symbol"], ascending=[True, True])
        df["Adj_Close"] = df["Adj_Close"].astype(float)
        df["Open"] = df["Open"].astype(float)
        df["Volume"] = df["Volume"].astype(float)
        df["High"] = df["High"].astype(float)
        df["Low"] = df["Low"].astype(float)
        df.to_sql(con=connection, name="stock_data", flavor="sqlite", if_exists="append")
def trans(a):
    x=datetime.datetime.strptime(a,"%Y-%m-%d")
    xx=datetime.date(x.year,x.month,x.day)
    return xx
def fmt(x, y, type):
    return type+':{y:0.2f}'.format(y=y)
class Cursor_haunter(object):
    """Display the x,y location of the nearest data point.
    Special thanks to:
    http://stackoverflow.com/a/4674445/190597 (Joe Kington)
    http://stackoverflow.com/a/20637433/190597 (unutbu)
    """
    #define static
    @staticmethod
    def alpha():
        return
    def __init__(self, ax, x, y,ttype, ith=0, formatter=fmt):
        try:
            x = np.asarray(x, dtype='float')
        except (TypeError, ValueError):
            x = np.asarray(mdates.date2num(x), dtype='float')
        y = np.asarray(y, dtype='float')
        mask = ~(np.isnan(x) | np.isnan(y))
        x = x[mask]
        y = y[mask]
        self._points = np.column_stack((x, y))
        # All plots use the same pointer now
        # if(ith==0):
        self.offsets =(-20,20)
        # else:
        #  self.offsets=(-20-10*ith,20+25*ith)

        self.type=ttype
        y = y[np.abs(y - y.mean()) <= 3 * y.std()]
        self.scale = x.ptp()
        self.scale = y.ptp() / self.scale if self.scale else 1
        self.tree = spatial.cKDTree(self.scaled(self._points))
        self.formatter = formatter
        self.ax = ax
        self.fig = ax.figure
        self.ax.xaxis.set_label_position('top')
        self.dot = ax.scatter(
            [x.min()], [y.min()], s=130, color='green', alpha=0.7)
        self.annotation = self.setup_annotation()
        plt.connect('motion_notify_event', self)

    def scaled(self, points):
        points = np.asarray(points)
        return points * (self.scale, 1)

    def __call__(self, event):
        ax = self.ax
        # event.inaxes is always the current axis. If you use twinx, ax could be
        # a different axis.
        if event.inaxes == ax:
            x, y = event.xdata, event.ydata
        elif event.inaxes is None:
            return
        else:
            inv = ax.transData.inverted()
            x, y = inv.transform([(event.x, event.y)]).ravel()
        annotation = self.annotation
        x,y = self.snap(x,y)
        annotation.xy = x, y
        annotation.set_text(self.formatter(x, y,self.type))
        self.dot.set_offsets((x, y))
        event.canvas.draw()

    def setup_annotation(self):
        """Draw and hide the annotation box."""
        annotation = self.ax.annotate(
            '', xy=(0, 0), ha = 'right',
            xytext = self.offsets, textcoords = 'offset points', va = 'bottom',
            bbox = dict(
                boxstyle='round,pad=0.5', fc='green', alpha=0.75),
            arrowprops = dict(
                arrowstyle='->', connectionstyle='arc3,rad=0'))
        return annotation

    def snap(self, x, y):
        """Return the value in self.tree closest to x, y."""
        dist, idx = self.tree.query(self.scaled((x, y)), k=1, p=1)
        try:
            return self._points[idx]
        except IndexError:
            # IndexError: index out of bounds
            return self._points[0]
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
#Choose stock!
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
      self.current_indicator=0
      self.figure_map={"candle":False,"price":False,"rsi":False,"macd":False,"obv":False,"portfolio":False}


 # This is a cheap shot, has to be mended later on~~~~~
  def add_index(self,stockticker):
      self.index=stockticker.price()[1].index

  def push_data(self,method,isprice=False,iscandle=False,issubline_rsi=False,issubline_macd=False,issubline_obv=False,isportolio=False):

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
          ax.plot(ind, data)  #
          formatter = ticker.FormatStrFormatter('$%1.2f')
          ax.yaxis.set_major_formatter(formatter)
          min_temp = np.min(data)
          max_temp=np.max(data)
          plt.xticks()

          ######designed for equally display codes!!!!!!!
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
          ss=current_time+'    '+ current_price+"    "+open_price+"    "+high_price+"    "+low_price+"    "+Last_price+"    "+volume+"    "\
          +change_price

          plt.text(date_min+2,max_temp+12,ss,fontsize=15)




          ax.fill_between(ind, min_temp - 10.0, data, color="lightsteelblue")
          # fig.autofmt_xdate()
          cursor1 = Cursor_haunter(ax, ind, data, "Close price", 1)



  def plot_other_data(self,ax):
      ax=ax
      for i in self.data_stack:
          index=self.data_stack[i].index
          data=self.data_stack[i].values
          ind = np.arange(len(index))  #
          formatter = MyFormatter(index)  #
          ax.xaxis.set_major_formatter(formatter)  #
          ax.plot(ind, data)  #
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
         # fig.autofmt_xdate()
         #

     plt.title("", fontsize=20)
     plt.ylabel("Price/USD", fontsize=14)
     # plt.xlabel("Dates", fontsize=14)

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
                ax.plot(ind, data,)  #
                # fig.autofmt_xdate()  #
                date_min = np.min(ind)
                date_max = np.max(ind)
                plt.xlim([date_min, date_max])



          index=self.subline_macd[sig_temp[0]].index
          data=self.subline_macd[sig_temp[0]].values
          ax.bar(ind, data,color="teal")
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

                  ax.bar(ind, data, color=color_map[temp_i])  #
                  # fig.autofmt_xdate()#
                  temp_i += 1
                  date_min = np.min(ind)
                  date_max = np.max(ind)
                  plt.xlim([date_min, date_max])

          index = self.subline_obv[sig_temp[0]].index
          data = self.subline_obv[sig_temp[0]].values
          ind = np.arange(len(index))  #
          formatter = MyFormatter(index)  #
          ax.xaxis.set_major_formatter(formatter)  #
          ax.plot(ind, data)  #
          cursor2 = Cursor_haunter(ax, ind, data, "On Balance Volume:", 1)
          # fig.autofmt_xdate()  #

          plt.legend(["OBV", "Trading volume"], fontsize=12)


  def plot_all(self):
      fig=plt.figure()
      plot_map_1=[3]
      plot_map_2=[3,1]
      plot_map_3 = [3,1,1]
      plot_map_4 = [3,1,1,1]
      plot_map=[plot_map_1,plot_map_2,plot_map_3,plot_map_4]

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

      plt.show()
class Chart_Factory_Portfolio:
  #global indicator
  indicator2=0
  def __init__(self):
      self.portfolio={}
      self.current_indicator=0
      self.figure_map={"portfolio":False,"weights":False,"risk":False}

  def push_data(self,method,isportfolio=False,isweight=False,isrisk=False):

      if(isportfolio):
          index,value=method
          self.portfolio[index]=value
          self.figure_map["portfolio"]=True

      if(isweight):
           self.indicator2+=1
           index,value=method
           self.portfolio[index]=value
           self.figure_map["weights"]=True

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
              area=np.pi * (60000000* df[z_str_temp].values) ** 2
              plt.scatter(x=df[x_str_temp].values, y=df[y_str_temp].values, s=area, c=color, edgecolors=None, alpha=0.4)

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
          ax.plot(ind, data,color="orange")  #
          formatter = ticker.FormatStrFormatter('$%1.2f')
          ax.yaxis.set_major_formatter(formatter)
          min_temp = np.min(data)
          max_temp=np.max(data)
          plt.xticks()

          date_min = np.min(ind)
          date_max = np.max(ind)
          plt.xlim([date_min, date_max])

          ######designed for equally display codes!!!!!!

          ax.fill_between(ind,0, data, color="navajowhite")
          # fig.autofmt_xdate()
          # cursor1 = Cursor_haunter(ax, ind, data, "Portfolio Value", 1)

  def plot_weights(self,ax):
      ax=ax
      if (len(self.portfolio["weights"]) != 0):

          index=self.portfolio["weights"].index
          data=self.portfolio["weights"].values
          fake=np.arange(len(index))
          plt.xticks(fake,index)
          plt.bar(fake,data,color=["limegreen","deepskyblue","plum","darkorange","tomato","y"])
          # xxx=self.portfolio["weights"]
          # xxx.plot(kind="bar",color="salmon",colour=["limegreen","deepskyblue","plum","darkslategray","r"])
          # ax.bar(index, data, color="green")  #
          # plt.legend(["OBV", "Trading volume"], fontsize=12)

  def plot_all(self):
      fig=plt.figure()
      plot_map_1=[3]
      plot_map_2=[3,1]
      plot_map_3 = [3,1,1]
      plot_map_4 = [3,1,1,1]
      plot_map=[plot_map_1,plot_map_2,plot_map_3,plot_map_4]

      gs = gridspec.GridSpec(self.indicator2+1, 1, height_ratios=plot_map[self.indicator2])
      ax = fig.add_subplot(gs[self.current_indicator])
      # ax.set_axis_bgcolor('darkslategray')
      self.plot_portfolio_val(ax)

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
class Stock_Methods:

    @staticmethod
    def ma(stock, window):
        data = stock.selected_line_info.values
        index = stock.selected_line_info.index
        ma = pd.rolling_mean(data, window)
        ma = pd.Series(ma, index=index)
        return ma
    @staticmethod
    def ewma(stock, alpha):
        data = stock.selected_line_info.values
        index =stock.selected_line_info.index
        span = 2 / alpha - 1
        ema = pd.ewma(data, span=span)
        ewma = pd.Series(ema, index=index)
        return ewma

    @staticmethod
    def MACD(stock,span1=12,span2=26,span3=9):
        data = stock.selected_line_info.values
        index = stock.selected_line_info.index
        span12=span1
        span26=span2
        ema12=pd.ewma(data,span12)
        ema26=pd.ewma(data,span26)
        macd_12_26=ema12-ema26
        macd_ema = pd.rolling_mean(macd_12_26, span3)
        macd_sig=macd_12_26-macd_ema
        macd_12_26=pd.Series(macd_12_26,index=index)
        macd_ema=pd.Series(macd_ema,index=index)
        macd_sig=pd.Series(macd_sig,index=index)

        return macd_12_26,macd_ema,macd_sig



    @staticmethod
    def rsi(stock, window):
        data = stock.selected_line_info.values
        index = stock.selected_line_info.index
        delta = np.diff(data)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        rup = pd.rolling_mean(up, window)
        rdown = pd.rolling_mean(down, window)
        rdown = np.abs(rdown)
        rsi = rup / rdown
        rsi = 100 - (100 / (1.0 + rsi))
        rsi = np.concatenate(([np.nan], rsi), axis=0)
        rsi = pd.Series(rsi, index=index)
        return rsi

    @staticmethod
    def bband(stock, window, num_std):
        data = stock.selected_line_info.values
        index = stock.selected_line_info.index
        ma = pd.rolling_mean(data, window)
        std = pd.rolling_std(data, window)
        upper = ma + std * num_std
        lower = ma - std * num_std
        bband_ma = pd.Series(ma, index=index)
        bband_upper = pd.Series(upper, index=index)
        bband_lower = pd.Series(lower, index=index)
        return bband_upper,bband_lower,bband_ma
    @staticmethod
    def OBV(stock):
        price_data=stock.selected_line_info.values
        index=stock.selected_line_info.index
        volume_data=stock.selected_line_info_volume.values

    # For OBV
        price_delta=np.diff(price_data)
        price_delta[price_delta>=0]=1
        price_delta[price_delta<0]=-1
        obv=[]
        zero_temp=[np.nan]
        for i in range(len(price_delta)):
            delta_temp = price_delta[:(i + 1)]
            volume_temp= volume_data[:i + 1]
            obv.append(np.dot(delta_temp,volume_temp))
        obv=np.concatenate((zero_temp,obv))
        on_balance_volume=pd.Series(obv,index=index)

    # For volume with different colors~~
        price_delta_temp=np.diff(price_data)
        price_delta_up,price_delta_down=price_delta_temp.copy(),price_delta.copy()
        price_delta_up[price_delta_up>=0]=1
        price_delta_up[price_delta_up<0]=0
        price_delta_down[price_delta_down>=0]=0
        price_delta_down[price_delta_down<0]=1

        price_delta_up=np.concatenate(([0],price_delta_up))
        price_delta_down=np.concatenate(([0],price_delta_down))


        volume_data_up=volume_data*price_delta_up
        volume_data_down=volume_data*price_delta_down

        volume_data_up=pd.Series(volume_data_up,index=index)
        volume_data_down=pd.Series(volume_data_down,index=index)

        return volume_data_up,volume_data_down,on_balance_volume
class Stock_Info:

    def __init__(self, connection, stock_symbol, start, end):
        self.symbol = stock_symbol
        self.all_info = pd.read_sql_query("SELECT* from stock_data", con=connection)
        self.all_info["Date"] = self.all_info["Date"].apply(trans)
        self.start = trans(start)
        self.end = trans(end)
        self.line_info = self.all_info[self.all_info["Symbol"] == self.symbol].set_index("Date")["Close"]

        self.line_info_volume = self.all_info[self.all_info["Symbol"] == self.symbol].set_index("Date")["Volume"]

        self.line_info_open=self.all_info[self.all_info["Symbol"] == self.symbol].set_index("Date")["Open"]
        self.line_info_high=self.all_info[self.all_info["Symbol"] == self.symbol].set_index("Date")["High"]
        self.line_info_low = self.all_info[self.all_info["Symbol"] == self.symbol].set_index("Date")["Low"]



    # get information for one year historical data

        start_temp=self.end-datetime.timedelta(days=365)
        while(start_temp not in self.line_info.index):
            start_temp-=datetime.timedelta(days=1)

        while (self.end not in self.line_info.index):
                self.end -= datetime.timedelta(days=1)
        self.oney_historical_selected_line_info=self.line_info[start_temp:self.end]# for most recent one year
        self.selected_line_info_return = self.line_info[self.start:self.end] # for specific time range

        diff_temp=np.diff(self.oney_historical_selected_line_info.values)
        diff_temp2=np.diff(self.selected_line_info_return.values)
        self.oney_historical_selected_line_info=self.oney_historical_selected_line_info[:-1]
        self.selected_line_info_return=self.selected_line_info_return[:-1]
        self.oney_return=diff_temp/self.oney_historical_selected_line_info
        self.selected_line_info_return=diff_temp2/self.selected_line_info_return


        self.annual_avg_return=252*np.mean(self.oney_return)


    #get information for display
        while (self.start not in self.line_info.index):
            self.start += datetime.timedelta(days=1)
        self.selected_line_info = self.line_info[self.start:self.end]
        self.selected_line_info_open=self.line_info_open[self.start:self.end]
        self.selected_line_info_high = self.line_info_high[self.start:self.end]
        self.selected_line_info_low = self.line_info_low[self.start:self.end]
        self.selected_line_info_volume = self.line_info_volume[self.start:self.end]

        # self.index is designed for strategy execution
        # these part could also be achieved by using candle information, but first need dataframe candle information
        self.index=self.selected_line_info.index[1:]
        self.selected_line_info=self.selected_line_info[1:]
        self.selected_line_info_open=self.selected_line_info_open[1:]
        self.selected_line_info_high=self.selected_line_info_high[1:]
        self.selected_line_info_low=self.selected_line_info_low[1:]

        # below is the data for candlestick~~~~

        self.selected_info=self.all_info[self.all_info["Symbol"] == self.symbol]
        self.selected_info=self.selected_info[(self.selected_info["Date"]>=self.start)&(self.selected_info["Date"]<=self.end)]
        self.candle_info=self.selected_info[["Date","Open","High","Low","Close"]]
        self.candle_info["Date"] = self.candle_info["Date"].apply(mdates.date2num)
        self.candle_info=self.candle_info.values.tolist()





    def candleprice(self):
        description_str=self.symbol+"'s candle chart "
        return description_str,self.candle_info

    def price(self):
        description_str = self.symbol + "'s close price"
        return description_str,self.selected_line_info

    def ma(self,window):
        description_str=self.symbol+"'s "+str(window)+" days moving average"
        return description_str,Stock_Methods.ma(self,window)
    def rsi(self,window):
        description_str = self.symbol + "'s " + str(window) + " days relative strength index"
        return description_str,Stock_Methods.rsi(self,window)


    def ewma(self,alpha):
        description_str = self.symbol + "'s Exponential weighted moving average (with span="+str(2 / alpha - 1)+")"
        return description_str,Stock_Methods.ewma(self,alpha)
    def bband(self,window,num_std):
        description_str1=self.symbol+"'s Upper Bollinger Band"+" ("+str(num_std)+" std(s), "+str(window)+" days)"
        description_str2 = self.symbol + "'s Lower Bollinger Band" + " (" + str(num_std) + " std(s), " + str(window) + " days)"
        description_str3 = self.symbol + "'s Middle Bollinger Band" + " (" + str(num_std) + " std(s), " + str(window) + " days)"
        upper,lower,middle=Stock_Methods.bband(self,window,num_std)
        return  description_str1,upper,description_str2,lower,description_str3,middle
    def MACD(self,span1=12,span2=26,span3=9):
        description_st1=self.symbol+"'s MACD(12-26) Line"
        description_st2=self.symbol+"'s MACD EMA(9) Line"
        description_st3=self.symbol+"'s MACD signal Line"
        macd,macd_ema,macd_sig=Stock_Methods.MACD(self,span1,span2,span3)
        return description_st1,macd,description_st2,macd_ema,description_st3,macd_sig
    def OBV(self):
        description_st1=self.symbol+"'s Trading volume(up)"
        description_st2=self.symbol+"'s Trading volume(dn)"
        description_st3=self.symbol+"'s on balance volume"
        volume_up,volume_down,obv=Stock_Methods.OBV(self)
        return description_st1,volume_up,description_st2,volume_down,description_st3,obv
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
        # print "Current Portfolio: ",self.tickers
        #
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


        fig = plt.figure()

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
#
class Operator_Methods:

    @staticmethod
    def core_1(portfolio,timemark,benchmark,delay=0):


        index=[x for x in portfolio.portfolio.columns if benchmark in x][0] # get benchmark name such as "Latest close"
        raw_temp=[]
        for i in range(len(portfolio.portfolio[index].values)):
            raw_temp.append(portfolio.portfolio[index].values[i][timemark])
        return abs(np.asarray(raw_temp))/abs(np.asarray(raw_temp).sum())


class Operator:
    def __init__(self,portfolio):
      self.portfolio=portfolio
      self.index=self.portfolio.date_index
    def In_sample_test(self):


        print "In sample test result: "
        for date in self.index:
            weights=Operator_Methods.core_1(self.portfolio, date, "close", 0)
            self.portfolio(weights,date)




    def close(self,delay=0):
        print Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="close")
        return Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="close")
    def open(self,delay=0):
       print Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="open")
       return Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="open")
    def high(self,delay=0):
        print Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="high")
        return Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="high")
    def low(self,delay=0):
        print Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="low")
        return Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="low")
    def returns(self,delay=0):
        print Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="return")
        return Operator_Methods.core_1(self.portfolio,delay=delay,benchmark="return")


start = "2015-06-01"
end = "2016-08-19"
time_Start=time.time()

# Main_func


# p1=Portfolio(connection,["AMZN","CSCO","BMY","IBM","HON","AAPL","DIS","GE","HD","JPM","GILD","CVX","CVS","INTC","MMM","MO","T","VZ","UPS"],start,end,weights=[30.0,20.0,10.0,60.0,100.0,10.0,27.0,30.0,40.0,72.0,25,25,47,45,90,67,66,20,54])
ticker2=["CSCO","BMY","IBM","HON","AAPL","DIS","GE","HD","JPM","GILD","CVX","CVS","INTC","MMM","MO","T","VZ","UPS"]
weights2=list(abs(np.random.randn(len(ticker2))))
# weights2=[-1]
p1=Portfolio(connection,ticker2,start,end,weights=weights2)
#
# pop=Operator(p1)
# pop.In_sample_test()
# pop.portfolio_update()




#
sample2=Chart_Factory_Portfolio()
sample2.push_data(p1.portfolio_val(),isportfolio =True)
sample2.push_data(p1.portfolio_weights(),isweight=True)
sample2.push_data(p1.variance_distribution(),isrisk=True)
#
# sns.set_style("whitegrid")
sample2.plot_all()


""""
apple=Stock_Info(connection,"AAPL",start,end)
sample1=Chart_Factory()
sample1.add_index(apple)

sample1.push_data(apple.price(),isprice=True)
sample1.push_data(apple.candleprice(),iscandle=True)
sample1.push_data(apple.ma(20))
sample1.push_data(apple.ewma(0.3))
sample1.push_data(apple.bband(20,1.5))
sample1.push_data(apple.rsi(14),issubline_rsi=True)
sample1.push_data(apple.MACD(),issubline_macd=True)
sample1.push_data(apple.OBV(),issubline_obv=True)

sns.set_style("whitegrid")
time_End=time.time()
print "Running time: "+str(time_End-time_Start)+" second(s)."
# there is basicially no diference between different length of data

sample1.plot_all()
"""



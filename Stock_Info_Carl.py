"""
Stock Object and functional tools 
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )

"""
import pandas as pd
import numpy as np
import matplotlib.dates as mdates
import datetime
def trans(a):
    x=datetime.datetime.strptime(a,"%Y-%m-%d")
    xx=datetime.date(x.year,x.month,x.day)
    return xx
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
        price_data=stock.selected_line_info.values #target 1
        index=stock.selected_line_info.index
        volume_data=stock.selected_line_info_volume.values# target 2


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
        self.selected_line_info_volume=self.selected_line_info_volume[1:]

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

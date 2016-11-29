from yahoo_finance import *
from  sklearn.preprocessing import maxabs_scale
from  sklearn.preprocessing import normalize
import sqlite3 as sql
import pandas as pd
import numpy as np
from math import floor
from scipy import optimize

class Data_Handler(object):
    def __init__(self):
        self.raw_connection=None
        pass

    def rsi(self,data, window=14):
        delta = np.diff(data)
        up, down = delta.copy(), delta.copy()
        up[up < 0] = 0
        down[down > 0] = 0
        rup = pd.rolling_mean(up, window)
        rdown = pd.rolling_mean(down, window)
        rdown = np.abs(rdown)
        rsi = rup / rdown
        rsi = (1 - (1 / (1.0 + rsi)))
        rsi = np.concatenate(([np.nan], rsi), axis=0)
        return rsi

    def moving_average(self,data, window):
        return pd.rolling_mean(data, window)

    def delay_func(self,sequence,delay):
        sequence=list(sequence[:-(delay-1)])
        sequence=list(np.nan*np.zeros(delay-1))+sequence
        return sequence


    def data_preprocessing(self, name="raw_data", start="2013-11-08", end="2016-10-31", ticker="^GSPC"):

        connection = sql.connect(name)
        temp1 = Share(ticker).get_historical(start, end)
        close1 = [float(x["Adj_Close"]) for x in temp1]  # 1254 close
        close1=close1[::-1]
        volume1 = [float(x["Volume"]) for x in temp1]
        volume1=volume1[::-1]
        close1 = normalize(list(close1))[0]
        volume1 = normalize(list(volume1))[0]
        # 1254 rsi
        ma9 = self.moving_average(close1, 9)  # 9 days movin avg
        ma14 = self.moving_average(close1, 14)  # 14 days movin avg
        ma25 = self.moving_average(close1, 25)  # 25 days movin avg
        rsi=self.rsi(close1)
        y = list(close1)
        y.pop(0)
        y.append(np.nan)  # standard output
        volume2 =self.delay_func(volume1,2)
        volume3 = self.delay_func(volume1,3)
        volume4 =self.delay_func(volume1,4)
        volume18=self.delay_func(volume1,18)

        close2 =self.delay_func(close1,2)
        close3 =self.delay_func(close1,3)
        close4 =self.delay_func(close1,4)
        close5 =self.delay_func(close1,5)
        close6 =self.delay_func(close1,6)
        close7 = self.delay_func(close1, 7)
        close8 = self.delay_func(close1, 8)
        close9 = self.delay_func(close1, 9)
        close10 = self.delay_func(close1,10)
        close24 = self.delay_func(close1, 24)

        # load macro data
        data = pd.read_excel("gold_data.xlsx", index_col=0, parse_dates=True)
        gold_price = data[data.columns[0]]
        gold_price = gold_price.sort_index()

        # load fx data
        data = pd.read_excel("exchange_data.xlsx", index_col=0, parse_dates=True)
        usd_chn = data[data.columns[0]]
        usd_jpy = data[data.columns[3]]
        usd_eur = data[data.columns[6]]
        new_idnex = gold_price.index

        usd_chn = usd_chn[new_idnex]
        usd_eur = usd_eur[new_idnex]
        usd_jpy = usd_jpy[new_idnex]
        usd_chn = usd_chn.sort_index()
        usd_eur = usd_eur.sort_index()
        usd_jpy = usd_jpy.sort_index()
        usd_chn = normalize(list(usd_chn[:-1].values))[0]
        usd_eur = normalize(list(usd_eur[:-1].values))[0]
        usd_jpy = normalize(list(usd_jpy[:-1].values))[0]
        gold_price =normalize(list(gold_price[:-1].values))[0]

        # usdchn1=self.delay_func(usd)


        df = pd.DataFrame()
        df["usdchntwo"]=self.delay_func(usd_chn,20)
        df["usdjpytwo"]=self.delay_func(usd_jpy,20)
        df["usdeurtwo"]=self.delay_func(usd_eur,20)
        df["goldtwo"]=self.delay_func(gold_price,20)
        # df["usdchntwo"] = usd_chn
        # df["usdjpytwo"] = usd_jpy
        # df["usdeurtwo"] = usd_eur
        # df["goldtwo"] = gold_price
        df["closetwofour"]=close24
        df["closeten"]=close10
        df["closenine"]=close9
        df["closeeight"]=close8
        df["closeseven"]=close7
        df["closesix"]=close6
        df["closefive"]=close5
        df["closefour"] = close4
        df["closethree"] = close3
        df["closetwo"] = close2
        df["closeone"] = close1
        df["volumeoneeight"]=volume18
        df["volumefour"] = volume4
        df["volumethree"] = volume3
        df["volumetwo"] = volume2
        df["volumeone"] = volume1
        df["rsione"]=rsi
        df["ma9one"] = ma9
        df["ma14one"] = ma14
        df["ma25one"] = ma25
        df["y"] = y
        df = df[50:-1]
        df.to_sql(con=connection, name="raw_data", flavor="sqlite", if_exists="replace")
        self.raw_connection=connection

    def feed_data(self,ratio,connection=None):
        if self.raw_connection==None:
            connection=connection
        else:
            connection= self.raw_connection

        statement2="SELECT rsione,closefour,volumefour,closeone,volumeone, ma25one, ma9one, ma14one,y from raw_data"
        statement3="SELECT closefour,volumefour,closeone,volumeone, ma25one, ma14one,y from raw_data"
        statement4="SELECT closeone,ma9one,ma14one,ma25one,y from raw_data" # 9 hidden
        statement5="SELECT closeone,closeten,closetwofour,volumeone,volumeoneeight,y from raw_data"#11 hidden
        statement6 = "SELECT closeone,closeten,closetwofour,volumeone,volumeoneeight,usdchntwo,usdeurtwo,usdjpytwo,goldtwo,y from raw_data"
        statement7 = "SELECT closeone, usdchntwo, usdeurtwo, usdjpytwo, goldtwo,y from raw_data"
        all_data= pd.read_sql_query(statement5, con=connection)
        all_matrix=all_data.as_matrix()

        training_matrix=all_matrix[0:floor(len(all_matrix)*ratio),:]
        testing_matrix=all_matrix[floor(len(all_matrix)*ratio):,:]

        training_input = training_matrix[:, 0:-1]
        training_output = np.reshape(training_matrix[:, -1], (len(training_matrix), 1))

        testing_input = testing_matrix[:, 0:-1]
        testing_out = np.reshape(testing_matrix[:, -1], (len(testing_matrix), 1))


        return training_input, training_output, testing_input, testing_out



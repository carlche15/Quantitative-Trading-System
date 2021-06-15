import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import matplotlib.ticker as ticker
from matplotlib.ticker import Formatter
from Stock_Info_Carl import *

class Historical_data:
    def __init__(self,connection,tickers,start,end):
        self.data=pd.Series()
        self.tickers=tickers

        stocks=[]
        for i in range(len(self.tickers)):
                   stock_temp=Stock_Info(connection,self.tickers[i],start,end,position=1000)
                   stocks.append(stock_temp)
                   self.date_index=stock_temp.index
                   print "Historical data loading....("+str(i+1)+"/"+str(len(tickers))+")"
        self.data=pd.Series(stocks,index=self.tickers)

        print "Historical data loaded! "


"""
Database manipulation Tools
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )

"""
import pandas as pd
import sqlite3 as sql
import datetime
import time
from yahoo_finance import Share

default_ticker=["AAPL","GOOG","MSFT","XOM","BRK-A","AMZN","FB","JNJ","GE","T",
         "WFC","JPM","WMT","VZ","PG","PFE","CVX","KO","V","HD","ORCL",
         "CMCSA","INTC","MRK","DIS","PEP","IBM","PM","CSCO","BAC","UNH",
         "MO","C","BMY","AMGN","MDT","GILD","SLB","MCD","MMM","ABBV","KHC",
         "CVS","MA","AGN","UPS","NKE","QCOM","HON","WBA"]
def trans(a):
    x=datetime.datetime.strptime(a,"%Y-%m-%d")
    xx=datetime.date(x.year,x.month,x.day)
    return xx
def database_ini(connection, ticker=default_ticker,start='2014-06-25',end='2016-08-10'):

           df=pd.DataFrame()
           ticker=ticker
           print "Start constructing the stock database...."
           if len(ticker)==0:
                      ticker=default_ticker
           for i in range(len(ticker)):
                    temp1=Share(ticker[i]).get_historical(start,end)
                    temp2=pd.DataFrame(temp1)
                    df=pd.concat([df,temp2],axis=0)
                    print i+1, "/50 is completed!"
           print "Database construction is completed! "
           # Transforming data to appropriate type i.e  unicode->float :)
           df=df[["Symbol","Date","Close","Open","Volume","High","Low"]]
           df=df.sort_values(by=["Date","Symbol"],ascending=[True,True])
           df["Close"] = df["Close"].astype(float)
           df["Open"]=df["Open"].astype(float)
           df["Volume"]=df["Volume"].astype(float)
           df["High"]=df["High"].astype(float)
           df["Low"]=df["Low"].astype(float)
           df.to_sql(con=connection,name="stock_data",flavor="sqlite",if_exists="replace" )
def database_update(connection, ticker=default_ticker):
          pdx = pd.read_sql_query("SELECT * From stock_data WHERE date=(select max(date) from stock_data)", con=connection)
          current_time = time.strftime("%Y-%m-%d")
          latest_time = pdx.iat[0, 2]
          latest_time = trans(latest_time)
          current_time = trans(current_time)
         # Judge if the database is up to date

          if (current_time <= latest_time):
                    print "Data is up to date."
          else:
                     df = pd.DataFrame()
          print "Start updating the stock database...."
          if len(ticker) == 0:
                   ticker = default_ticker
          start = str(latest_time + datetime.timedelta(days=1))
          end = str(current_time)
          for i in range(len(ticker)):
                      temp1 = Share(ticker[i]).get_historical(start, end)
                      temp2 = pd.DataFrame(temp1)
                      df = pd.concat([df, temp2], axis=0)
                      print i + 1, "/50 is updated!"
          print "Database is up to date! "
          df = df[["Symbol", "Date", "Close", "Open", "Volume", "High", "Low"]]
          df = df.sort_values(by=["Date", "Symbol"], ascending=[True, True])
          df["Close"] = df["Close"].astype(float)
          df["Open"] = df["Open"].astype(float)
          df["Volume"] = df["Volume"].astype(float)
          df["High"] = df["High"].astype(float)
          df["Low"] = df["Low"].astype(float)
          df.to_sql(con=connection, name="stock_data", flavor="sqlite", if_exists="append")

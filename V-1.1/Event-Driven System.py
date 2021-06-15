from DataHandler import*
from Datebase_Carl import*
from SuperVisionTools_Carl  import*
from Event import*
from ExecutionHandler import*
from Historical_Data import*
from Portfolio import *
from Stock_Info_Carl import *
from Strategy import*
from ChartHandler import *
import Queue



start = "2015-09-04"
end = "2016-07-20"
b ticker = ["AAPL", "GOOG", "MSFT", "XOM", "AMZN", "FB", "JNJ", "GE", "T",
          "WFC", "JPM", "WMT", "VZ", "PG", "PFE", "CVX", "KO", "V", "HD", "ORCL",
          "CMCSA", "INTC", "MRK", "DIS", "PEP", "IBM", "PM", "CSCO", "BAC", "UNH",
          "MO", "C", "BMY", "AMGN", "MDT", "GILD", "SLB", "MCD", "MMM", "ABBV", "KHC",
          "CVS", "MA", "AGN", "UPS", "NKE", "QCOM", "HON", "WBA"]
# ticker2=ticker[:3]
ticker2=ticker
events=Queue.Queue()
his_data=Historical_data(connection, ticker2,start,end)
datahandler=Historical_DB_Handler(events,his_data)
portfolio=test_portfolio(datahandler,events)
buyNholdstr=BuyandHold(datahandler,events)
movinAcross=MovinAvgCross(datahandler,events)
mAcd=MACD(datahandler,events)
rSi=RSI(datahandler,events)
broker=Historical_Execution_Handler(datahandler,events)
port_vharttool=Chart_Factory_Portfolio()

while True:

             if datahandler.continue_backtest==True:
                 try:
                      datahandler.update_observed_data()
                 except IndexError:
                     break
             else:
                      break
             while True: # loop of events within this heartbeat
                      try:
                              event=events.get(False)
                      except Queue.Empty:
                               break
                      else:
                               if event is not None:
                                        if event.type=="MARKET":
                                                  buyNholdstr.calculate_signals(event)
                                                  # movinAcross.calculate_signals(event)
                                                  # mAcd.ca6lculate_signals(event)
                                                  # rSi.calculate_signals(event)
                                                  portfolio.heartbeat_update()

                                        elif event.type=="SIGNAL":
                                                  portfolio.signal_update(event)
                                        elif event.type=="ORDER":
                                                  broker.execute_order(event)
                                        elif event.type=="FILL":
                                                  portfolio.fill_update(event)
                                                  pass
             # print "Current Holdigns",portfolio.current_holdings
print portfolio.current_holdings
print"****"
print portfolio.current_positions
port_charthandler=Portfolio_ChartHandler(portfolio)
port_vharttool.push_data(port_charthandler.pricehandler(),isportfolio=True)
port_vharttool.push_data(port_charthandler.pnlhandler(),ispnl=True)
port_vharttool.push_data(port_charthandler.weightshandler(),isweight=True)
port_vharttool.plot_all()




















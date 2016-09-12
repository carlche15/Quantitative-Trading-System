"""
Stock & Portfolio Data Visualization Tools
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )

"""
import numpy as np
from SuperVisionTools_Carl import *
from Datebase_Carl import *
from Stock_Info_Carl import *
from Portfolio_Carl import  *
from Cursor_Haunter_Carl import *






#Choose stock!



#
start = "2015-01-01"
end = "2016-08-19"
connection=sql.connect("stock_data_September.db")
# database_ini(connection=connection)
# database_update(connection=connection)

#
# # p1=Portfolio(connection,["AMZN","CSCO","BMY","IBM","HON","AAPL","DIS","GE","HD","JPM","GILD","CVX","CVS","INTC","MMM","MO","T","VZ","UPS"],start,end,weights=[30.0,20.0,10.0,60.0,100.0,10.0,27.0,30.0,40.0,72.0,25,25,47,45,90,67,66,20,54])
ticker2=["CSCO","BMY","IBM","HON"]
weights2=list(abs(np.random.randn(len(ticker2))))
p1=Portfolio(connection,ticker2,start,end,weights=weights2)
pop=Operator(p1)
pop.In_sample_test(show_animation=True)
# #
sample2=Chart_Factory_Portfolio()
sample2.push_data(p1.portfolio_val(),isportfolio =True)
sample2.push_data(p1.portfolio_weights(),isweight=True)
sample2.push_data(p1.variance_distribution(),isrisk=True)
sns.set_style("whitegrid")
sample2.plot_all()
#


"""

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



# there is basicially no diference between different length of data

sample1.plot_all()
"""
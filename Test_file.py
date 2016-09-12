"""
Stock & Portfolio Data Visualization Tools
author: Tongda (Carl) Che
email: carlche@bu.edu
website: http://carlche15.github.com
For modification,  usage or collaboration of this program, please contact me via email
(Considering this application is still under developing stage, license is held for now )

"""
import pandas as pd
import numpy as np
import seaborn as sns
from yahoo_finance import Share
import matplotlib.pyplot as plt
import sqlite3 as sql
import datetime
import matplotlib.dates as mdates
import scipy.spatial as spatial
from matplotlib import gridspec
import matplotlib.ticker as ticker
from matplotlib.ticker import Formatter
from matplotlib.finance import candlestick_ohlc as candle
import matplotlib.animation as animation
import time

a=Share("AAPL").get_days_high()
print a


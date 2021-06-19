import pandas as pd
import QuantLib as ql
from utilities.function_utilities import *




# -*- coding: utf-8 -*-
# @Time    : 2019-10-16 16:00
# @Author  : Carl Che
# @FileName: Portfolio.py
# @Software: PyCharm
# @License ：None


import numpy as np
from abc import ABC, abstractmethod, ABCMeta
import pyodbc
import xarray as xr


class StockHistDataHandler():
    def __init__(self, invest_universe = None, invest_horizen = None, sql=None):
        # make variables "private"
        if invest_universe is not None and invest_horizen is not None:

            self.invest_universe = invest_universe
            self.invest_horizen = invest_horizen
            self.sql = sql
            self.hist = self.get_data(invest_universe,invest_horizen,sql)



    def __call__(self, ticker = None, invest_horizen = None, sql=None, func = None,*args,**kwargs ):
        data = self.get_data(ticker , invest_horizen , sql)

        if func is None:
            return data
        else:
            return func(data,*args,**kwargs)




    def get_data(self, ticker = None, invest_horizen = None, sql=None):
        raw_data,is_hist = self._retrieve_data(ticker, invest_horizen , sql)
        if len(raw_data)==0:
            return None

        if is_hist:
            return self._to_xarray(raw_data)
        else:
            return raw_data

    @staticmethod
    # TODO: add capitalization func
    def _retrieve_data(universe=["AAPL", ""], investment_horizen=["2000-01-01", "2000-12-31"], sql_query=None):
        """
        By default, data is retrieved from hist table
        :param universe:
        :param investment_horizen:
        :param sql_query:
        :return:
        """

        connection = pyodbc.connect('Driver=SQL Server;'
                                    'Server=DESKTOP-0CQQR1E\SQLEXPRESS;'
                                    'Database=securities_master;'
                                    'Trusted_Connection=yes;')


        if not sql_query:
            if isinstance(universe, str): universe = [universe]

            assert isinstance(universe, (list, np.ndarray)) and isinstance(investment_horizen, (
            list, np.ndarray)), "Both universe and investment_horizen should be array alike variables"
            # designed to handle array alike universe with length 1
            if isinstance(universe, list):
                universe.append("")
            else:
                universe = np.append(universe, "")
            sql_query = f"SELECT * from securities_hist where ticker in {tuple(universe)} " \
                        f"and eff_date between '{investment_horizen[0]}' and '{investment_horizen[1]}'"

        raw_hist_data = pd.read_sql_query(sql_query, connection)
        is_hist_data = True if "hist" in sql_query else False

        return raw_hist_data,is_hist_data

    @staticmethod
    def _to_xarray(tabular_data):

        tabular_data.eff_date = pd.to_datetime(tabular_data.eff_date)  # transform date data type
        tabular_data["return"] = -999
        _data_grouped = tabular_data.groupby(["ticker", "eff_date"]).mean()  # exclude non numerical columns

        xarray_data = xr.DataArray(
            np.array(_data_grouped.to_xarray().to_array().transpose("ticker", "variable", "eff_date")),
            dims=["ticker", "feature", "eff_date"],
            coords={"ticker": np.unique(tabular_data.ticker),
                    "feature": _data_grouped.columns,
                    "eff_date": np.unique(tabular_data.eff_date)},
            attrs={"description": "stock timeseries data",
                   "source": "AlphaVantage"})
        return xarray_data

class ComputeSuite():
    #todo: think clear what format do you want!
    def __init__(self):
        pass
    @classmethod
    def pct_return(cls, data):
        """

        :param data: xarray data
        :return:
        """
        if data is None:
            return pd.DataFrame()
        else:
            returns = xarray2df(data,selected_feature="adj_close_price").pct_change(axis=1)
            data.loc[:,"return",:] = returns.values
            # returns =  pd.DataFrame(data.loc[:,"adj_close_price",:].values).pct_change(axis=1)
            # returns.index = data.loc[:, :, :].ticker
            # returns.columns = np.array(data.loc[:, :, :]["eff_date"])
            return returns.T

    @classmethod
    def close_price(cls,data):
        if data is None:
            return pd.DataFrame()
        else:
            price = xarray2df(data,selected_feature="adj_close_price")
            return price.TNM


# todo: i need to maintain a running xarray for intermediate comptuted values



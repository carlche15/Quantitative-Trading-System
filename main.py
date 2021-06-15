# -*- coding: utf-8 -*-
# @Time    : 2019-10-16 16:00
# @Author  : Carl Che
# @FileName: Portfolio.py
# @Software: PyCharm
# @License ：None


import numpy as np
import pandas as pd

from abc import ABC, abstractmethod, ABCMeta
import pyodbc
import xarray as xr


class StockHistDataHandler():
    def __init__(self, invest_universe, invest_horizen, sql=None):
        # make variables "private"
        self.invest_universe = invest_universe
        self.invest_horizen = invest_horizen
        self.sql = sql
        self.hist = self.load_data()

    def load_data(self):
        raw_hist = self._retrieve_data(self.invest_universe, self.invest_horizen, self.sql)
        return self._to_xarray(raw_hist)

    @staticmethod
    # TODO: add capitalization func
    def _retrieve_data(universe=["AAPL", ""], investment_horizen=["2000-01-01", "2000-12-31"], sql_query=None):

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

        return raw_hist_data

    @staticmethod
    def _to_xarray(tabular_data):

        tabular_data.eff_date = pd.to_datetime(tabular_data.eff_date)  # transform date data type
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






import pandas as pd
import numpy as np
from utilities.function_utilities import  xarray2df
# todo: event_data is eventually going to be event


class portfolio():
    def __init__(self, init_holdings, init_cash, strategy=None, alloc="equal_share"):
        self.holdings = init_holdings  # a dataframe with index be the tickers, of course, with a lot of zeros
        self.total_asset_hist = pd.Series()  # scaler
        self.total_asset = None
        self.cash = init_cash
        self.strategy = strategy
        self.allocation_method = alloc
        self.eff_date = None

        ###### todo: potential move to strategy part ##########
        self.strategy_hit_point = pd.Series()

    def update(self, event_data):
        if 0 in event_data.shape:  # this is the case when we at the starting of the rolling period
            print("init")

            return 0
        # todo: add date index
        #### step 1 : new data comes in, calculate holding values
        self.update_holding_value(event_data)

        #### step 2: generate new trading signals via the strategy
        trade_signal, hit_num = self.strategy.generate_signal(xarray2df(event_data, self.strategy.feature).T)

        self.strategy_hit_point = self.strategy_hit_point.append(pd.Series(index=[self.eff_date], data=[hit_num]))

        ### step 3: generate new target holding values, and in the future, generate orders.
        target_holdings = self.calc_target_holdings(event_data, trade_signal)
        # todo: omitting trade and feed backs, the target holdings will be the new portfolio holdings

        #### step 4, final step: set the holdings to be the target holdings, in the future, post trade hodlings
        self.holdings = target_holdings
        self.cash = 0

    def update_holding_value(self, event_data):
        # todo: I am assuming that you can buy as fraction of a share of stock!
        current_market_price = xarray2df(event_data, "adj_close_price").iloc[:, -1:]
        masked_market_price = np.nan_to_num(current_market_price.values.copy())
        holding_values = self.holdings * (masked_market_price)
        self.eff_date = event_data.eff_date.values[-1]

        self.total_asset_hist = self.total_asset_hist.append(
            pd.Series(data=[self.cash + np.sum(holding_values.values.ravel())],
                      index=[self.eff_date]))
        self.total_asset = self.total_asset_hist[self.eff_date]

        return np.sum(holding_values.values.ravel())

    def calc_target_holdings(self, event_data, trade_signal):
        # todo: I am assuming that you can buy as fraction of a share of stock!
        current_market_price = xarray2df(event_data, "adj_close_price").iloc[:, -1:]
        masked_market_price = np.nan_to_num(current_market_price.values.copy())
        if self.allocation_method == "equal_share":
            required_cash = (trade_signal[None, :].dot(masked_market_price)).ravel()[0]

            target_holdings = self.holdings.copy()
            target_holdings.loc[~(trade_signal > 0)] = 0
            target_holdings.loc[trade_signal > 0] = self.total_asset / required_cash
            return target_holdings
        elif self.allocation_method == "equal_dollar":

            trade_condition = (trade_signal > 0) & (masked_market_price.ravel() > 0)
            single_cash_amount = self.total_asset / np.sum(trade_signal[trade_condition])

            target_holdings = self.holdings.copy()
            target_holdings.loc[~trade_condition] = 0
            target_holdings.loc[trade_condition] = np.nan_to_num(
                single_cash_amount / current_market_price[trade_condition])

            return target_holdings

    def generate_trades(self, target_holdings):
        pass
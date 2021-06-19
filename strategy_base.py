from utilities import *
from abc import ABCMeta, abstractmethod
import numpy as np




def _null_handle(sig_gen_func):
    def wrapper(cls, event_data):
        if 0 in event_data.shape:
            return  np.nan*np.ones_like(event_data.columns)
        else:
            return sig_gen_func(cls, event_data)

    return wrapper

class strategy():
    def __init__(self):
       pass

    @abstractmethod
    def generate_signal(self, event_data):
        """
        :param event_data: the universe of data that the strategy relies upon,
        for example the event_data required for a strategy looks back 3 days need is 4(days)*N (invest universe) Dataframe
        :return: (N,) array represent buy/sell/hold
        """
        raise NotImplementedError("Abstract method not implemented! :(")


class buy_low_strategy(strategy):

    def __init__(self,is_test = False):
        super().__init__()
        self.feature = ["return"]
        self.is_test = is_test

    @_null_handle
    def generate_signal(self, event_data):
        sig = np.zeros(event_data.shape[1])

        previous_market = np.nanmean(event_data.values[-2])
        previous_returns = event_data.values[-2]
        actual_returns = event_data.values[-1]
        mkt_condition = (previous_market > 0.00)
        stock_condition = (previous_returns < -0.02) & (event_data.values[0] < 0.0)
        sig[stock_condition & mkt_condition] = actual_returns[stock_condition & mkt_condition]

        return sig


class buy_low_strategy_trade_1(strategy):

    def __init__(self, is_test=False):
        super().__init__()
        self.feature = "return"  # todo: handle more features
        self.is_test = is_test

    @_null_handle
    def generate_signal(self, event_data):
        sig = np.zeros(event_data.shape[1])

        previous_return = event_data.values[0]

        todays_return = event_data.values[-1]
        todays_market = np.nanmean(todays_return)

        mkt_condition = (todays_market > 0.00)
        stock_condition = (todays_return < -0.01) & (previous_return < 0.0)
        sig[stock_condition & mkt_condition] = 1
        buy_sig_count = len(sig[stock_condition & mkt_condition])

        if sum(sig) <= 2:
            sig[~np.isnan(todays_return)] = 1
            buy_sig_count = 0
        return sig, buy_sig_count


class buy_low_strategy_trade_2(strategy):

    def __init__(self, is_test=False):
        super().__init__()
        self.feature = "return"  # todo: handle more features
        self.is_test = is_test

    @_null_handle
    def generate_signal(self, event_data):
        sig = np.zeros(event_data.shape[1])

        previous_return = event_data.values[0]

        todays_return = event_data.values[-1]
        todays_market = np.nanmean(todays_return)

        mkt_condition = (todays_market > 0.00)
        stock_condition = (todays_return < -0.02) & (previous_return < 0.0)
        sig[stock_condition & mkt_condition] = 1
        buy_sig_count = len(sig[stock_condition & mkt_condition])

        if sum(sig) <= 2:
            sig[~np.isnan(todays_return)] = 1
            buy_sig_count = 0
        return sig, buy_sig_count


class buy_low_strategy_trade_3(strategy):

    def __init__(self, is_test=False):
        super().__init__()
        self.feature = "return"  # todo: handle more features
        self.is_test = is_test

    @_null_handle
    def generate_signal(self, event_data):
        sig = np.zeros(event_data.shape[1])



        two_days_before_return = event_data.values[-3]
        previous_return = event_data.values[-2]

        todays_return = event_data.values[-1]
        todays_market = np.nanmean(todays_return)

        mkt_condition = (todays_market > 0.00)
        stock_condition = (todays_return < -0.01) & (previous_return < 0.0)&(two_days_before_return>0.0)
        sig[stock_condition & mkt_condition] = 1
        buy_sig_count = len(sig[stock_condition & mkt_condition])

        if sum(sig) <= 2:
            sig[~np.isnan(todays_return)] = 1
            buy_sig_count = 0
        return sig, buy_sig_count


class buy_low_strategy_trade_random(strategy):

    def __init__(self, is_test=False):
        super().__init__()
        self.feature = "return"  # todo: handle more features
        self.is_test = is_test

    @_null_handle
    def generate_signal(self, event_data):
        sig = np.zeros(event_data.shape[1])

        random_signal = np.random.choice(np.arange(len(sig)), 10, replace=False)
        sig[random_signal] =1
        buy_sig_count = len(sig[random_signal])
        return sig, buy_sig_count
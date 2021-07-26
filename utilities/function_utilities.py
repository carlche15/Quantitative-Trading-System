import pandas as pd
import numpy as np


def rolling_apply_ext(window ,data, func, *args ,**kwargs):
    """
    pandas' implementation of rolling.apply is such a disappointment!
    :param window:
    :param data:
    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    df_idx = data.index
    result_df = pd.DataFrame().reindex_like(data)

    for i in range(len(df_idx)):
        sub_df = data.loc[df_idx[ i -window +1]:df_idx[i]]
        result_df.loc[df_idx[i] ] =func(sub_df ,*args ,**kwargs)
    return result_df

def rolling_apply_ext_xarray(window ,data, func, *args ,**kwargs):
    """
    pandas' implementation of rolling.apply is such a disappointment!
    :param window:
    :param data:
    :param func:
    :param args:
    :param kwargs:
    :return:
    """
    date_idx = data.eff_date.values

    for i in range(len(date_idx)):
        sub_df = data.loc[:,:,date_idx[ i -window +1]:date_idx[i]]
        func(sub_df,*args ,**kwargs)
    return 0

def xarray2df(xarray, selected_feature):
    df = pd.DataFrame(xarray.loc[:,selected_feature,:].values)
    df.index = xarray.ticker.values
    df.columns = xarray.eff_date.values
    return df


def dropna_ext(data):
    data_tickers = data.ticker.values
    print(f"Raw data dim: {data.shape}")
    a = np.sum(data.values,axis=2) # sum along eff_date, will be nan if any field is nan
    good_tickers = data_tickers[~np.isnan(a).any(axis=1)]
    dropped_tickers = data_tickers[np.isnan(a).any(axis=1)]
    print(f"New data dim: {data.loc[good_tickers,:,:].shape}")
    print(f"Dropped tickers: {dropped_tickers}")
    return data.loc[good_tickers,:,:]

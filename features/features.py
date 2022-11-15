import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from sklearn.linear_model import LinearRegression


def coefficient_column(n, df, indices):
    """
    Creates the {n}_reg column by calculating the regression coefficient for {n} indices
    :param n:
    :param df:
    :param indices:
    :return:
    """

    def linear_regression(_x, _y):
        """
        performs linear regression given x and y. outputs regression coefficient
        """
        lr = LinearRegression()
        lr.fit(_x, _y)

        return lr.coef_[0][0]

    _varname_ = f'{n}_reg'
    df[_varname_] = np.nan

    for index in indices:
        if index >= n:
            y = df['close'][index - n: index].to_numpy()
            x = np.arange(0, n)
            # reshape
            y = y.reshape(y.shape[0], 1)
            x = x.reshape(x.shape[0], 1)
            # calculate regression coefficient
            df.loc[index, _varname_] = linear_regression(x, y)  # add the new value
    return df


def n_day_regression(df, indices):
    """
    This function creates the regression coefficient values for 3, 5, 10, and 20 days
    :param df:
    :param indices:
    :return:
    """
    df = coefficient_column(3, df, indices)
    df = coefficient_column(5, df, indices)
    df = coefficient_column(10, df, indices)
    df = coefficient_column(20, df, indices)
    return df


def local_min_max_columns(data, n):
    """
    Create the local minima and maxima columns
    :param data:
    :param n:
    :return:
    """
    data['loc_min'] = data.iloc[argrelextrema(data.close.values, np.less_equal, order=n)[0]]['close']
    data['loc_max'] = data.iloc[argrelextrema(data.close.values, np.greater_equal, order=n)[0]]['close']
    return data


def normalized_values(high, low, close):
    """
    Calculate the normalized price between 0 and 1
    :param high:
    :param low:
    :param close:
    :return:
    """
    # epsilon to avoid deletion by 0
    epsilon = 10e-10

    #print(x)
    # subtract the lows
    high = high - low
    close = close - low
    return close / (high + epsilon)


def normalized_value_column(data):
    """
    Create the normalized value column
    :param data:
    :return:
    """
    #with pd.option_context('display.max_rows', None, 'display.max_columns', None):  # more options can be specified also
    #    print(data)
    #data = data.dropna()
    #nan_values = data[data['high'].isna()]
    #print(nan_values)
    data = data[(data.high != 'NaN') & (data.low != 'NaN') & (data.open != 'NaN') & (data.close != 'NaN')].copy()
    #data = data[data.high != 'NaN']
    #data = data[data.low != 'NaN']
    #data = data[data.open != 'NaN']
    #data = data[data.close != 'NaN']
    data['normalized_value'] = data.apply(lambda x: normalized_values(x.high, x.low, x.close), axis=1)
    return data


def features_for_production(data, n=10):
    """
    Create production features
    :param data:
    :param n:
    :return:
    """
    data = normalized_value_column(data)
    data = n_day_regression(data, np.arange(0, len(data)))
    data = data[['volume', 'normalized_value', '3_reg', '5_reg', '10_reg', '20_reg']]
    return data.dropna(axis=0)


def features_for_training(data: pd.DataFrame, n=0):
    """
    Create training features
    :param data:
    :param n:
    :return:
    """
    data = normalized_value_column(data)
    data = local_min_max_columns(data, n)
    data = n_day_regression(data, list(np.where(data['loc_min'] > 0)[0]) + list(np.where(data['loc_max'] > 0)[0]))
    data = data[(data['loc_min'] > 0) | (data['loc_max'] > 0)].reset_index(drop=True)

    # create a dummy variable for local_min (0) and max (1)
    data['target'] = [1 if x > 0 else 0 for x in data.loc_max]
    data = data[['date', 'close', 'volume', 'normalized_value', '3_reg', '5_reg', '10_reg', '20_reg', 'target']]
    return data.dropna(axis=0)


def features_for_training_3class(data: pd.DataFrame, order: int = 0) -> pd.DataFrame:
    """

    Parameters
    ----------
    data
        input dataframe
    order
        order parameter to scipy.signal.argrelextrema

    Returns
    -------
    dataframe
        features dataframe

    """
    data = normalized_value_column(data)
    data = local_min_max_columns(data, order)
    data = n_day_regression(data, list(data.index.values))

    # create a dummy variable for
    #   0 neither local minima or local maxima
    #   1 local minima
    #   2 local maxima
    data['t2'] = [2 if x > 0 else 0 for x in data.loc_max]
    data['target'] = [1 if x > 0 else 0 for x in data.loc_min] + data['t2']
    data = data[['date', 'close', 'volume', 'normalized_value', '3_reg', '5_reg', '10_reg', '20_reg', 'target']]
    return data.dropna(axis=0)

import config
import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from matplotlib import pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.seasonal import seasonal_decompose


def data_prep(df):
    if config.USE_TARGET:
        use_target = 0
    else:
        use_target = 1

    X, y = [], []
    for i in range(config.LOOKBACK, len(df) - config.FUTURE + 1):
        X.append(df[i - config.LOOKBACK : i, 0 + use_target : df.shape[1]])
        y.append(df[i + config.FUTURE - 1 : i + config.FUTURE, 0])

    return np.array(X), np.array(y)


def plot_success(predictions, df, training_data_len):
    train = df[: training_data_len + config.LOOKBACK]
    test = df[training_data_len + config.LOOKBACK :]
    test["predictions"] = predictions
    plt.figure(figsize=(16, 6))
    plt.title("Model")
    plt.xlabel("Date", fontsize=18)
    plt.ylabel("Close Price USD ($)", fontsize=18)
    plt.plot(train[f"{config.TARGET_VALUE}"])
    plt.plot(test[[f"{config.TARGET_VALUE}", "predictions"]])
    plt.legend(["Train", "Test", "Predictions"], loc="lower right")
    plt.show()


def make_lag_series(df, lag, column):
    df = df.copy()
    for i in range(1, lag + 1):
        df[f"{column}_lag_{i}"] = df[f"{column}"].shift(i)
    df = df.dropna()
    return df


def extract_target_columns(df):
    first_column = df.pop(f"{config.TARGET_VALUE}")
    df.insert(0, f"{config.TARGET_VALUE}", first_column)
    df = df[[f"{config.TARGET_VALUE}"] + config.TARGET_COLUMNS]
    return df


def make_pct_change(df):
    df = df.pct_change()
    df = df.dropna()
    return df


def find_trend_season(df, column):
    series = df[column]
    try:
        decompose_result_mult = seasonal_decompose(series, model="multiplicative")
    except:
        decompose_result_mult = seasonal_decompose(series, model="additive")

    trend = decompose_result_mult.trend
    seasonal = decompose_result_mult.seasonal
    residual = decompose_result_mult.resid
    df = pd.concat([df, trend, seasonal], axis=1)
    df.rename(
        columns={"trend": f"{column}_trend", "seasonal": f"{column}_seasonal"},
        inplace=True,
    )
    df = df.dropna()
    return df


def adfullertest(df, column):

    print("Dickey-Fuller Test: ")
    data = df[column]
    data = data.values
    data = data.reshape(-1)
    adftest = adfuller(data)
    adfoutput = pd.Series(
        adftest[0:4],
        index=["Test Statistic", "p-value", "Lags Used", "No. of Observations"],
    )
    for key, value in adftest[4].items():
        adfoutput["Critical Value (%s)" % key] = value

    print(adfoutput)


def adfullertest_mulitple_columns(df):
    for column in df.columns:
        adfullertest(df, column)


def make_data_stationary(df):
    df = np.log(df)
    df = df - df.shift(periods=1)
    df = df.dropna()
    return df

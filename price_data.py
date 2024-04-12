import requests
import config
import csv
import pandas as pd
from datetime import datetime
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from matplotlib import pyplot as plt


def get_price_data_csv(ticker, start_date, end_date):
    headers = {"Content-Type": "application/json"}
    requestResponse = requests.get(
        f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&token={config.TIINGO_TOKEN}",
        headers=headers,
    )
    fields = ["date", "close", "high", "low", "open", "volume"]

    with open(f"csv_data/daily_{ticker}_stock_price.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for row in requestResponse.json():
            writer.writerow([row[field] for field in fields])


def get_price_data_csvs(start_date, end_date):
    tickers = list(config.TICKER_ID_DICT.keys())
    for ticker in tickers:
        get_price_data_csv(ticker, start_date, end_date)


def get_single_price_data_df(ticker, time="daily"):
    df = pd.read_csv(f"csv_data/daily_{ticker}_stock_price.csv")
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date")
    df = df.sort_index()
    df = df.asfreq("B")
    df = df.ffill()

    logic = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    df = df.astype(float)

    if time == "weekly":
        df = df.resample("W").apply(logic)
        df.index = df.index - pd.tseries.frequencies.to_offset("6D")

    elif time == "monthly":
        df = df.resample("1ME").apply(logic)

    return df


def get_single_price_data_df_with_spending(ticker):
    df = get_single_price_data_df(ticker, "monthly")
    spending_df = pd.read_csv(f"csv_data/month_{ticker}_spending_over_time.csv")
    spending_df["time_period"] = pd.to_datetime(spending_df["time_period"])
    spending_df = spending_df.set_index("time_period")
    spending_df = spending_df.sort_index()
    spending_df = spending_df.reset_index(drop=True)
    spending_df = spending_df.set_index(df.index)
    df = pd.concat([df, spending_df], axis=1)
    return df


def get_multiple_price_data_df(target_ticker, time="daily"):
    tickers = list(config.TICKER_ID_DICT.keys())
    final_df = pd.DataFrame()
    for ticker in tickers:
        df = get_single_price_data_df(ticker, time)
        df = df[config.TARGET_COLUMNS]
        df.columns = [f"{ticker}_{column}" for column in df.columns]
        final_df = pd.concat([final_df, df], axis=1)

    first_column = final_df.pop(f"{target_ticker}_{config.TARGET_VALUE}")
    final_df.insert(0, f"{target_ticker}_{config.TARGET_VALUE}", first_column)

    return final_df

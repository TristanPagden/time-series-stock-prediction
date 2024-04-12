import requests
import datetime
import config
import pandas as pd
from dateutil.relativedelta import relativedelta
from sklearn.preprocessing import MinMaxScaler
import helper_tools
import numpy as np
import tensorflow as tf


def predict(ticker, time="month"):
    start_date = datetime.datetime.now() - relativedelta(months=120)
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = datetime.datetime.now().strftime("%Y-%m-%d")
    headers = {"Content-Type": "application/json"}
    requestResponse = requests.get(
        f"https://api.tiingo.com/tiingo/daily/{ticker}/prices?startDate={start_date}&endDate={end_date}&token={config.TIINGO_TOKEN}",
        headers=headers,
    )
    price_df = pd.DataFrame(requestResponse.json())
    price_df["date"] = pd.to_datetime(price_df["date"])
    price_df = price_df.set_index("date")
    price_df = price_df.sort_index()
    price_df = price_df.asfreq("B")
    price_df = price_df.ffill()

    logic = {
        "open": "first",
        "high": "max",
        "low": "min",
        "close": "last",
        "volume": "sum",
    }
    price_df = price_df.astype(float)

    if time == "weekly":
        price_df = price_df.resample("W").apply(logic)
        price_df.index = price_df.index - pd.tseries.frequencies.to_offset("6D")

    elif time == "month":
        price_df = price_df.resample("1ME").apply(logic)
    price_df = price_df[:-1]

    filters = {
        "group": time,
        "filters": {
            "recipient_id": config.TICKER_ID_DICT[ticker],
            "time_period": [{"start_date": start_date, "end_date": end_date}],
        },
        "auditTrail": "Recipient Spending Over Time Visualization",
    }
    spendingReq = requests.post(
        "https://api.usaspending.gov/api/v2/search/spending_over_time/", json=filters
    )

    spendingResults = spendingReq.json()["results"]
    for result in spendingResults:
        time_period = result["time_period"]
        year = int(time_period["fiscal_year"])
        month = int(time_period["month"])
        month = month - 3
        if month <= 0:
            month = 12 + month
            year = year - 1
        if str(month).__len__() == 1:
            month = "0" + str(month)
        else:
            month = str(month)
        year = str(year)
        date = ""
        date = date + year
        date = date + "-" + month
        date = date + "-01"
        date = date + "T00:00:00.000Z"
        result["time_period"] = date

    spending_df = pd.DataFrame(spendingResults)
    spending_df["time_period"] = pd.to_datetime(spending_df["time_period"])
    spending_df = spending_df.set_index("time_period")
    spending_df = spending_df.sort_index()
    spending_df = spending_df[:-1]

    spending_df = spending_df.set_index(price_df.index)
    df = pd.concat([price_df, spending_df], axis=1)
    df = helper_tools.find_trend_season(df, config.TARGET_VALUE)
    df = helper_tools.find_trend_season(df, "aggregated_amount")
    df = helper_tools.make_lag_series(df, 2, config.TARGET_VALUE)
    df = helper_tools.make_lag_series(df, 2, "aggregated_amount")
    df = helper_tools.extract_target_columns(df)
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled = scaler.fit_transform(df)
    scaled = scaled.reshape(1, scaled.shape[0], scaled.shape[1])
    scaled = scaled[:, -config.LOOKBACK :, :]
    print(scaled.shape)
    print(scaled)

    lstm = tf.keras.models.load_model("models/lstm.keras")
    predictions = lstm.predict(scaled)
    if config.USE_TARGET:
        predictions = np.repeat(predictions, config.NUM_OF_TIME_SERIES, axis=-1)
    else:
        predictions = np.repeat(predictions, config.NUM_OF_TIME_SERIES + 1, axis=-1)
    predictions = scaler.inverse_transform(predictions)[:, 0]
    print(predictions)


predict("LMT")

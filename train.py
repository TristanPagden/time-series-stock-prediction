import price_data
import spending_data
import model
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import config
import helper_tools
import tensorflow as tf


def train():
    # price_data.get_price_data_csvs(config.START_DATE, conifg.END_DATE)
    # spending_data.get_spending_over_time_csvs(config.START_DATE, config.END_DATE)
    for ticker in config.TICKER_ID_DICT.keys():
        df = price_data.get_single_price_data_df_with_spending(ticker)
        df = helper_tools.find_trend_season(df, config.TARGET_VALUE)
        df = helper_tools.find_trend_season(df, "aggregated_amount")
        df = helper_tools.make_lag_series(df, 2, config.TARGET_VALUE)
        df = helper_tools.make_lag_series(df, 2, "aggregated_amount")
        df = helper_tools.extract_target_columns(df)
        # print(df)
        # df = helper_tools.make_data_stationary(df)
        # helper_tools.adfullertest_mulitple_columns(df)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaled = scaler.fit_transform(df)
        X, y = helper_tools.data_prep(scaled)
        if ticker != list(config.TICKER_ID_DICT.keys())[-1]:
            X_train = X[: int(X.shape[0] * 1)]
            X_test = X[int(X.shape[0] * 1) :]
            y_train = y[: int(X.shape[0] * 1)]
            y_test = y[int(X.shape[0] * 1) :]
        else:
            X_train = X[: int(X.shape[0] * config.TRAINING_SIZE)]
            X_test = X[int(X.shape[0] * config.TRAINING_SIZE) :]
            y_train = y[: int(X.shape[0] * config.TRAINING_SIZE)]
            y_test = y[int(X.shape[0] * config.TRAINING_SIZE) :]

        try:
            lstm = tf.keras.models.load_model("models/lstm.keras")
        except:
            lstm = model.create_model()

        lstm.fit(X_train, y_train, batch_size=1, epochs=1, validation_split=0.1)

        lstm.save("models/lstm.keras")

        if ticker == list(config.TICKER_ID_DICT.keys())[-1]:
            print(X_test)
            print(X_test.shape)
            predictions = lstm.predict(X_test)

            if config.USE_TARGET:
                predictions = np.repeat(predictions, config.NUM_OF_TIME_SERIES, axis=-1)
            else:
                predictions = np.repeat(
                    predictions, config.NUM_OF_TIME_SERIES + 1, axis=-1
                )
            predictions = scaler.inverse_transform(predictions)[:, 0]
            print(predictions)

            helper_tools.plot_success(
                predictions,
                df,
                int(X.shape[0] * config.TRAINING_SIZE),
            )

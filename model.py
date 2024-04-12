from keras.models import Sequential
from keras.layers import Dense, LSTM
import config


# Build the LSTM lstm
def create_model():
    lstm = Sequential()
    lstm.add(
        LSTM(
            128,
            return_sequences=True,
            input_shape=(config.LOOKBACK, config.NUM_OF_TIME_SERIES),
        )
    )
    lstm.add(LSTM(64, return_sequences=True))
    lstm.add(LSTM(64, return_sequences=False))
    lstm.add(Dense(25))
    lstm.add(Dense(1))

    lstm.compile(optimizer="adam", loss="mean_squared_error")
    return lstm

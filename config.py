TIINGO_TOKEN = "7b17b288a139e59b8e5b1796307ad2d72122685c"

TICKER_ID_DICT = {
    "LMT": "b97d19b0-833c-8d8f-3a2c-157d04ea55ef-P",
    "BA": "419ccd27-d6f4-d363-aeaf-b9e2c3ae6f5d-P",
    "RTX": "bb947c1e-56f7-2f71-34d9-b0240c8b117c-P",
    "GD": "f58f9621-d1de-5f11-1041-3c65987927ff-P",
    "NOC": "fbe19298-837a-c0c2-9e1d-ff4c0a5ad25a-P",
}
START_DATE = "2008-01-01"
END_DATE = "2024-01-31"
LOOKBACK = 60
FUTURE = 1
TRAINING_SIZE = 0.5
TARGET_TICKER = "LMT"
USE_TARGET = True
TARGET_COLUMNS = [
    "close_trend",
    "close_seasonal",
    "close_lag_1",
    "close_lag_2",
    "aggregated_amount",
    "aggregated_amount_trend",
    "aggregated_amount_seasonal",
    "aggregated_amount_lag_1",
    "aggregated_amount_lag_2",
]
TARGET_VALUE = "close"
if USE_TARGET:
    NUM_OF_TIME_SERIES = len(TARGET_COLUMNS) + 1
else:
    NUM_OF_TIME_SERIES = len(TARGET_COLUMNS)

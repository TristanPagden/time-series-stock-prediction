import requests
import csv
import config


def get_spending_over_time_csv(
    ticker, start_date, end_date, recipient_id, time="month"
):
    filters = {
        "group": time,
        "filters": {
            "recipient_id": recipient_id,
            "time_period": [{"start_date": start_date, "end_date": end_date}],
        },
        "auditTrail": "Recipient Spending Over Time Visualization",
    }
    spendingReq = requests.post(
        "https://api.usaspending.gov/api/v2/search/spending_over_time/", json=filters
    )

    spendingResults = spendingReq.json()["results"]
    fields = ["aggregated_amount", "time_period"]

    with open(f"csv_data/{time}_{ticker}_spending_over_time.csv", "w") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(fields)
        for row in spendingResults:
            writeableRow = []
            for field in fields:
                if field == "time_period":
                    year = int(row[field]["fiscal_year"])
                    month = int(row[field]["month"])
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
                    writeableRow.append(date)
                else:
                    writeableRow.append(row[field])
            writer.writerow(writeableRow)


def get_spending_over_time_csvs(start_date, end_date, time="month"):
    tickers = list(config.TICKER_ID_DICT.keys())
    for ticker in tickers:
        recipient_id = config.TICKER_ID_DICT[ticker]
        get_spending_over_time_csv(ticker, start_date, end_date, recipient_id, time)


def name_to_ticker(name):
    pass

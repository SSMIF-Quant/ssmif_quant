import sqlite3
import sys
import os
from pathlib import Path
import pandas as pd
import time
import datetime
import json
sys.path.append(os.path.join(Path(__file__).parent.absolute().parent.absolute(), "General_Utility_Functions"))

dbfile = os.path.join(Path(__file__).parent.absolute(), "database/Risk.db")

def getHoldings():

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    holdings = []

    for row in c.execute("""SELECT * FROM current_holdings;"""):
        holdings.append({'Ticker':row[0],
                         'Company':row[1],
                         'Sector':row[2],
                         'Original_Purchase_Date':row[3],
                         'Shares':row[4],
                         'Entry_VWAP':row[5],
                         'Invested_Amount':row[6],
                         'Stop_Loss':row[7],
                         'Current_Value_MTM':row[8],
                         'Year_Open_Price':row[9],
                         'Year_Open_Position_Value':row[10],
                         'Month_Open_Price':row[11],
                         'Month_Open_Position_Value':row[12]
                         })

    return holdings


def getHoldingsByTicker(ticker):

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    holdings = []
    ticker = ticker.upper()

    for row in c.execute("""SELECT * FROM current_holdings WHERE Ticker = '{}';""".format(ticker)):
        holdings.append({'Ticker':row[0],
                         'Company':row[1],
                         'Sector':row[2],
                         'Original_Purchase_Date':row[3],
                         'Shares':row[4],
                         'Entry_VWAP':row[5],
                         'Invested_Amount':row[6],
                         'Stop_Loss':row[7],
                         'Current_Value_MTM':row[8],
                         'Year_Open_Price':row[9],
                         'Year_Open_Position_Value':row[10],
                         'Month_Open_Price':row[11],
                         'Month_Open_Position_Value':row[12]
                         })

    return holdings

def getHoldingsFromCSV():
    holdingscsv = os.path.join(Path(__file__).parent.absolute().parent.absolute(), "General_Utility_Functions/Necessary_Info/Portfolio_Holdings.csv")

    holdings = pd.read_csv(holdingscsv)
    pd.to_datetime(holdings['Original Purchase Date'])
    holdings['Original Purchase Date'] = holdings['Original Purchase Date'].apply(lambda x: int(datetime.datetime.timestamp(datetime.datetime.strptime(x, "%m/%d/%Y"))))
    holdings.rename(columns={'Original Purchase Date':'Original_Purchase_Date', 'Entry VWAP':'Entry_VWAP', 'Invested Amount':'Invested_Amount',
                             'Current Value (Mark-to-Market)':'Current_Value_MTM', 'Year Open Price':'Year_Open_Price',
                             'Year Open Position Value':'Year_Open_Position_Value', 'Month Open Price':'Month_Open_Price', 'Month Open Position Value':'Month_Open_Position_Value'}, inplace=True)

    return json.dumps(holdings.to_json(orient="records"))

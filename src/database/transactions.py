import sqlite3
import sys
import os
from pathlib import Path
import pandas as pd
import time
import datetime
import json

dbfile = os.path.join(Path(__file__).parent.absolute(), "database/Risk.db")

def getTransactions():

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    transactions = []

    for row in c.execute("""SELECT * FROM transactions;"""):
        transactions.append({
                    'Trade_Date':row[0],
                    'Type':row[1],
                    'Symbol':row[2],
                    'Product_Description':row[3],
                    'Units':row[4],
                    'Gross_Amount':row[5],
                    'Transaction_Fee':row[6],
                    'Net_Amount':row[7]
                    })
    return transactions

def getTransactionsAfterDate(time):

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    transactions = []

    for row in c.execute("""SELECT * FROM transactions WHERE Trade_Date > {};""".format(time)):
        transactions.append({
                    'Trade_Date':row[0],
                    'Type':row[1],
                    'Symbol':row[2],
                    'Product_Description':row[3],
                    'Units':row[4],
                    'Gross_Amount':row[5],
                    'Transaction_Fee':row[6],
                    'Net_Amount':row[7]
                    })
    return transactions


def getTransactionsBeforeDate(time):

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    transactions = []

    for row in c.execute("""SELECT * FROM transactions WHERE Trade_Date < {};""".format(time)):
        transactions.append({
                    'Trade_Date':row[0],
                    'Type':row[1],
                    'Symbol':row[2],
                    'Product_Description':row[3],
                    'Units':row[4],
                    'Gross_Amount':row[5],
                    'Transaction_Fee':row[6],
                    'Net_Amount':row[7]
                    })
    return transactions

def getTransactionsFromCSV():
    transactionscsv = os.path.join(Path(__file__).parent.absolute().parent.absolute(), "General_Utility_Functions/Necessary_Info/Transactions.csv")

    trans = pd.read_csv(transactionscsv)
    pd.to_datetime(trans['Trade Date'])
    trans['Trade Date'] = trans['Trade Date'].apply(lambda x: int(datetime.datetime.timestamp(datetime.datetime.strptime(x, "%m/%d/%Y"))))
    trans.rename(columns={"Trade Date":"Trade_Date", 'Product Description':'Product_Description', 'Gross Amount':'Gross_Amount',
                          'Transaction Fee':'Transaction_Fee', 'Net Amount':'Net_Amount'}, inplace=True)

    return json.dumps(trans.to_json(orient="records"))


def newTransaction(trade_date, trade_type, symbol, product_description, units, gross_amount, trans_fee, net_amount):

    conn = sqlite3.connect(dbfile)
    c = conn.cursor()

    dates = trade_date.split('-')
    d = datetime.datetime(year = int(dates[0]), month = int(dates[1]), day = int(dates[2]))

    ex = """INSERT INTO transactions VALUES ({}, '{}', '{}', '{}', {}, {}, {}, {});""".format(datetime.datetime.timestamp(d), trade_type, symbol, product_description, units, gross_amount, trans_fee, net_amount)

    c.execute(ex)

    conn.commit()

    conn.close()

# newTransaction(1546405200, 'Dividend', 'WMT', 'Walmart Inc', 0, 49.92, 0, 49.92)

# print(getTransactions())

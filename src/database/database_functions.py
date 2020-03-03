import sqlite3
import sys
import os
from pathlib import Path
import pandas as pd
import time
import datetime
sys.path.append(os.path.join(Path(__file__).parent.absolute().parent.absolute(), "General_Utility_Functions"))
from GetCurrentPositions import getCurrentPositions

def creatHoldings():

    conn = sqlite3.connect('database/Risk.db')

    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS `current_holdings` (
	`Ticker` VARCHAR(10) NOT NULL,
	`Company` VARCHAR(1000) NOT NULL,
	`Sector` VARCHAR(500) NOT NULL,
	`Original_Purchase_Date` TIMESTAMP NOT NULL,
	`Shares` INT NOT NULL,
	`Entry_VWAP` DECIMAL (10, 2) NOT NULL,
	`Invested_Amount` DECIMAL (10, 2) NOT NULL,
    `Stop_Loss` DECIMAL (10, 2) DEFAULT 0,
	`Current_Value_MTM` DECIMAL (10, 2) NOT NULL,
	`Year_Open_Price` DECIMAL (10, 2) NOT NULL,
	`Year_Open_Position_Value` DECIMAL (10, 2),
	`Month_Open_Price` DECIMAL (10, 2) NOT NULL,
	`Month_Open_Position_Value` DECIMAL (10, 2),
	PRIMARY KEY (`Ticker`));""")

    conn.commit()

    conn.close()

def fillHoldings():
    holdingsFile = os.path.join(Path(__file__).parent.absolute(), "../General_Utility_Functions/Necessary_Info/Portfolio_Holdings.csv")
    holdings = pd.read_csv(holdingsFile)

    conn = sqlite3.connect('database/Risk.db')
    c = conn.cursor()

    for index, row in holdings.iterrows():
        new_date = int(time.mktime(datetime.datetime.strptime(row['Original Purchase Date'], "%m/%d/%Y").timetuple()))
        ticker = row['Ticker']
        company = row['Company']
        sector = row['Sector']
        shares = int(row['Shares'])
        VWAP = float(row['Entry VWAP'])
        Invested_Amount = float(row['Invested Amount'])
        curr_value = float(row['Current Value (Mark-to-Market)'])
        year_price = float(row['Year Open Price'])
        try:
            year_pos = float(row['Year Open Position Value'])
        except:
            year_pos = 'null'
        month_price = float(row['Month Open Price'])
        month_pos = float(row['Month Open Position Value'])
        ex = """INSERT INTO current_holdings VALUES ('{}', '{}', '{}', {}, {}, {}, {}, {}, {}, {}, {}, {}, {});""".format(ticker, company, sector, new_date, shares, VWAP, Invested_Amount, 0, curr_value, year_price, year_pos, month_price, month_pos)
        c.execute(ex)

    conn.commit()

    conn.close()

# fillHoldings()

def transactionsTable():

    conn = sqlite3.connect('database/Risk.db')

    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS `transactions` (
	`Trade_Date` TIMESTAMP NOT NULL,
	`Type` VARCHAR(100) NOT NULL,
	`Symbol` VARCHAR(10) NOT NULL,
	`Product_Description` VARCHAR(1000) NOT NULL,
	`Units` INT DEFAULT '0',
	`Gross_Amount` DECIMAL (10, 2) NOT NULL,
	`Transaction_Fee` DECIMAL (10, 2) DEFAULT '0',
	`Net_Amount` DECIMAL (10, 2) NOT NULL);""")

    conn.commit()

    conn.close()

# transactionsTable()

def fillTransaction():

    transactionsFile = os.path.join(Path(__file__).parent.absolute(), "../General_Utility_Functions/Necessary_Info/Transactions_This_Year.csv")
    transactions = pd.read_csv(transactionsFile)

    conn = sqlite3.connect('database/Risk.db')

    c = conn.cursor()

    for i in range(transactions.shape[0] - 1, -1, -1):
        row = transactions.iloc[i]
        new_date = int(time.mktime(datetime.datetime.strptime(row['Trade Date'], "%m/%d/%Y").timetuple()))
        net_amount = float(row['Net Amount'])

        if(pd.isna(row['Units'])):
            units = 0
        else:
            units = int(row['Units'])


        if(pd.isna(row['Gross Amount'])):
            gross_amount = 0
        else:
            gross_amount = float(row['Gross Amount'])


        if(pd.isna(row['Transaction Fee'])):
            trans_fee = 0
        else:
            trans_fee = float(row['Transaction Fee'])



        ex = """INSERT INTO transactions VALUES ({}, '{}', '{}', '{}', {}, {}, {}, {});""".format(new_date, row['Type'], row['Symbol'], row['Product Description'], units, gross_amount, trans_fee, net_amount)
        # print(ex)
        c.execute(ex)





    conn.commit()

    conn.close()

# fillTransaction()





def selectTransactions():

    conn = sqlite3.connect('database/Risk.db')

    c = conn.cursor()

    for row in c.execute("""SELECT rowid, * FROM transactions;"""):
        print(row[0])

    conn.close()

# selectTransactions()

def accounttable():

    conn = sqlite3.connect('database/Risk.db')

    c = conn.cursor()
    c.execute("""CREATE TABLE `accounts` (
	`username` VARCHAR(20) NOT NULL,
	`password` VARCHAR(20) NOT NULL,
	`analyst` BOOLEAN NOT NULL DEFAULT '1',
	`senior_management` BOOLEAN NOT NULL DEFAULT '0',
	`admin` BOOLEAN NOT NULL DEFAULT '0');""")

    c.execute("""INSERT INTO accounts VALUES ('ssmif', 'quant2019', 1, 0, 0);""")

    conn.commit()

    conn.close()

# accounttable()


def addStopLoss():
    stopLossFile = os.path.join(Path(__file__).parent.absolute(), "../General_Utility_Functions/Necessary_Info/Stop_Losses.csv")
    stopLosses = pd.read_csv(stopLossFile)

    tickers = stopLosses['Ticker'].to_list()
    losses = stopLosses['Stop Loss Price'].to_list()

    conn = sqlite3.connect('database/Risk.db')

    c = conn.cursor()

    for i in range(len(tickers)):
        c.execute("""UPDATE current_holdings SET Stop_Loss = {} WHERE Ticker = '{}'""".format(losses[i], tickers[i]))

    conn.commit()

    conn.close()
# addStopLoss()

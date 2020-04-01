import numpy as np
import pandas_datareader as pdr
import pandas as pd
import matplotlib.pyplot as pt
from datetime import datetime

class BlackLitterman:
    """
    This model will take in three lists, ticker names, investor views, and investor confidence
    Convention - all percentages will be expressed as decimals internally
    """
    def __init__(self, ticker_names, investor_views, investor_confidence, risk_free_rate, basis="Adj Close", benchmark="^GSPC", time_horizon=2):
        self.ticker_names = ticker_names
        self.investor_views = investor_views
        self.investor_confidence = investor_confidence
        self.risk_free_rate = risk_free_rate
        self.BASIS = basis
        self.BENCHMARK = benchmark
        self.TIMEHORIZON = time_horizon

    #Up first, we will need to calculate the implied equilibrium returns
    #We will need to pull in the ticker data, compute a TIMEHORIZON week moving average of the reurns    +
    #We will need to get the market capitalization weights  of a portfolio comprised of the given tickers
    #We will need to calculte the risk aversion coefficient of the portfolio based off of the benchmark 
    #We will need to calculate the variance covariance matrix of the excesss returns +

    def getHistoricalReturns(self, basis="quarterly"):
        """
        TODO:Test
        """
        if basis == "daily":
            frequency = 1
        # elif basis == "weekly":
        #     frequency = 5
        elif basis == "monthly":
            frequency = 20
        elif basis == "quarterly":
            frequency = 62
        elif basis == "semi-annually":
            frequency = 125
        elif basis == "annually":
            frequency = 252
        else:
            raise ValueError
            return 

        dates = self.getDates()
        historical_returns = []
        # used_lead_indexes = []
        # used_tail_indexes = []
        lead_offset = np.arange(0,253)
        tail_offset = np.append(np.arange(0,1), np.arange(0,253))
        # print(lead_offset)
        # print(tail_offset)
        # print(dates)
        for index, ticker in enumerate(self.ticker_names):
            ticker_data = pdr.get_data_yahoo(ticker, start=str(dates[1]), end=str(dates[0]))
            ticker_data = ticker_data[self.BASIS]
            print(ticker_data[252])
            # print(frequency, len(ticker_data), ticker_data[25])
            n = int(len(ticker_data) / frequency)
            temp = []
            # print(n)
            if (basis != "daily"):
                for i in range(n):
                    temp.append((ticker_data[(frequency * (i+1)) + lead_offset[i]] / ticker_data[(frequency * i) + tail_offset[i]]) - 1 )
                    historical_returns.append(temp)
                    # used_lead_indexes.append((frequency * (i+1)) + lead_offset[i])
                    # used_tail_indexes.append((frequency * i) + tail_offset[i])
            else:
                for i in range(n-1):
                    temp.append((ticker_data[i+1] / ticker_data[i]) - 1 )
                    historical_returns.append(temp)
                    # used_lead_indexes.append(i+1)
                    # used_tail_indexes.append(i)

        # return (used_lead_indexes, used_tail_indexes)
        return historical_returns

    def getDates(self):
        """
        Helper function to get "today's" date and return a touple of datetime.date objects (today, last_year)
        """
        today = datetime.date(datetime.now())
        last_year = datetime.date(datetime(datetime.now().year-1, datetime.now().month, datetime.now().day))

        return (today, last_year)

    def getDailyReturns(self):
        """
        This will return a moving average of the daily returns of the tickers in the input list
        """
        #Initialize the dataframe of moving averaged returns with column names as ticker names and get the dates (today and YTD last year)
        returns = pd.DataFrame(columns=self.ticker_names)
        dates = self.getDates()

        #For all tickers, get the ticker data for the past year, get the dialy returns, get the moving average of those daily returns, and 
        #append them to the return dataframe
        for ticker in self.ticker_names:

            ticker_data = pdr.get_data_yahoo(ticker, start=str(dates[1]), end=str(dates[0]))
            ticker_data = ticker_data[self.BASIS]
            daily_returns = []

            for i in range(len(ticker_data)):
                if i == 0:
                    daily_returns.append(0)
                else:
                    daily_returns.append((ticker_data[i] / ticker_data[i-1]) - 1)

            returns[ticker] = daily_returns
        return returns

    def getMovingAverageDailyReturns(self):
        """
        This will return the daily returns of the tickers in the input list
        """
        returns = self.getDailyReturns()
        
        for ticker in self.ticker_names:
            returns[ticker] = returns[ticker].rolling(self.TIMEHORIZON*5, min_periods=1).mean()
        return returns

    def getExpectedReturns(self, basis="quarterly"):
        """
        This will default to calculating quarterly returns for assets 
        TODO: Set this up for calculating returns on all transactions
        TODO:TEST
        """ 
        
        returns = self.getHistoricalReturns(basis=basis)
        # n = len(returns[self.ticker_names])
        print(returns)
        # lol = np.asarray([[0, .15, -.1, .05], [0, .15, -.1, .05], [0, .15, -.1, .05]]).transpose()
        # returns = pd.DataFrame(lol, columns=self.ticker_names)
        # print(returns)
        # n = len(returns[self.ticker_names[0]])
        comp_avg_ret = []
        for ticker in self.ticker_names:
            temp = []
            daily_returns = returns[ticker]
            for i in range(0, n):
                temp.append(daily_returns[i] + 1)
            comp_avg_ret.append(np.prod(temp)**(1.0/(n-1)) - 1)

        return comp_avg_ret
        

    def getVarianceCovarianceMatrix(self, returns):
        #Based off of https://stattrek.com/matrix-algebra/covariance-matrix.aspx
        """
        This will return the variance covariance matrix of the input returns dataframe
        V = (1.0/n) * ((X - (1.0/n) * 11'X)' * (X - (1.0/n) * 11'X))
        where 1 = an n x n matrix of ones
        X = the n x k matrix of returns
        V = k x k matrix 
        """

        X = returns
        columns = returns.columns
        n = len(X[columns[0]])
        ones = np.ones((n,n))
        x = np.subtract(X, np.multiply((1/n), np.matmul(ones, X)))
        xt = x.transpose()
        dev_ss_cp = xt.dot(x)
        V  = np.multiply((1/n), dev_ss_cp)
        #V should be a k x k (num assets x num assets) variance covariance matrix
        return V
        
    #def getRiskAversionCoefficient(self):
        # expected_return = 
if __name__ == "__main__":

    #yet another sanity check
    bl = BlackLitterman(["AAPL", "MSFT", "^GSPC"],4,4,4)
    dates = bl.getDates()
    ticker_data = pdr.get_data_yahoo("^GSPC", start=str(dates[1]), end=str(dates[0]))
    print("hello ",(ticker_data["Adj Close"][252]/ticker_data["Adj Close"][0]) - 1)
    # print(bl.getExpectedReturns(basis="annually"))
    print(bl.getHistoricalReturns(basis="annually"))
    # #Another sanity check
    # bl = BlackLitterman(4, 4, 4, 4)
    # print(bl.getVarianceCovarianceMatrix(pd.DataFrame(np.array([[90,90,60,60,30], [60,90,60,60,30], [90,30,60,90,30]]).T.tolist())))

    # This is a sanity check for the two week moving average and it worked
    # bl = BlackLitterman(4, 4, 4, 4)
    # two_week = bl.getMovingAverageDailyReturns(["AAPL", "MSFT", "^GSPC"])
    # # print(two_week)
    # ph = pdr.get_data_yahoo("^GSPC", start="2019-03-27", end="2020-03-27")["Adj Close"]
    # regular = [0]
    # for i in range(len(ph)):
    #     if i == 0:
    #         continue
    #     else:
    #         regular.append((ph[i] / ph[i-1]) - 1)
    # print(len(regular))
    # index = np.arange(0, 254)
    # pt.plot(index, two_week["AAPL"], 'r')
    # pt.plot(index, two_week["MSFT"], 'g')
    # pt.plot(index, two_week["^GSPC"], 'b')
    # # pt.scatter(index, regular, s = 8)
    # pt.show()

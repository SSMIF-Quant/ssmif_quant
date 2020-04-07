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
    def __init__(self, ticker_names, investor_views, investor_confidence, risk_free_rate, market_cap_weights, basis="Adj Close", benchmark=["^GSPC"], time_horizon=2):
        self.ticker_names = ticker_names
        self.investor_views = investor_views
        self.investor_confidence = investor_confidence
        self.risk_free_rate = risk_free_rate
        self.market_cap_weights = market_cap_weights
        self.BASIS = basis
        self.BENCHMARK = benchmark
        self.TIMEHORIZON = time_horizon

    #Up first, we will need to calculate the implied equilibrium returns
    #We will need to pull in the ticker data, compute a TIMEHORIZON week moving average of the reurns    +
    #We will need to calculate the excess returns of a stock + 
    #We will need to get the market capitalization weights  of a portfolio comprised of the given tickers
    #We will need to calculte the risk aversion coefficient of the portfolio based off of the benchmark 
    #We will need to calculate the variance covariance matrix of the excesss returns +
    def getTickerData(self, ticker, start, end):
        return pdr.get_data_yahoo(ticker, start=start, end=end)[self.BASIS]

    def getHistoricalReturns(self, basis="annually", tickers=None):

        if tickers == None:
            tickers = self.ticker_names
        if basis == "daily":
            frequency = 1
        #weekly doesn't work with numbers because it's weird
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
        lead_offset = np.arange(0,253)
        tail_offset = np.append(np.arange(0,1), np.arange(0,253))
        # print(self.ticker_names)
        for index, ticker in enumerate(tickers):
            ticker_data = self.getTickerData(ticker, start=str(dates[1]), end=str(dates[0]))
            # ticker_data = pdr.get_data_yahoo(ticker, start=str(dates[1]), end=str(dates[0]))
            # ticker_data = ticker_data[self.BASIS]
            # return ticker_data
            n = int(len(ticker_data) / frequency)
            
            temp = []
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
        year_before_that = datetime.date(datetime(datetime.now().year-2, datetime.now().month, datetime.now().day-3))

        # return (today, last_year)
        return (last_year, year_before_that)

    def getDailyReturns(self, tickers=None):
        """
        This will return a moving average of the daily returns of the tickers in the input list
        """
        if tickers == None:
            tickers = self.ticker_names
        #Initialize the dataframe of moving averaged returns with column names as ticker names and get the dates (today and YTD last year)
        returns = pd.DataFrame(columns=tickers)
        dates = self.getDates()

        #For all tickers, get the ticker data for the past year, get the dialy returns, get the moving average of those daily returns, and 
        #append them to the return dataframe
        for ticker in tickers:

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

    def getMovingAverageDailyReturns(self, tickers=None):
        """
        This will return the daily returns of the tickers in the input list
        """
        if tickers == None:
            tickers = self.ticker_names
        returns = self.getDailyReturns()
        
        for ticker in tickers:
            returns[ticker] = returns[ticker].rolling(self.TIMEHORIZON*5, min_periods=1).mean()
        return returns

    def getExpectedReturns(self, basis="annually", tickers=None):
        """
        This will default to calculating quarterly returns for assets 
        TODO: Set this up for calculating returns on all transactions
        TODO:TEST
        """ 
        if tickers == None:
            tickers = self.ticker_names
        returns = self.getHistoricalReturns(basis=basis, tickers=tickers)
        # returns = [[.15, -.1, .05], [.15, -.1, .05], [.15, -.1, .05]]
        # print(returns)
        #just to make sure that everytning is ok
        if (len(tickers) == len(returns)):
            comp_avg_ret = []
            for index, ticker in enumerate(tickers):
                temp = []
                ticker_return = returns[index]
                for i in range(len(ticker_return)):
                    temp.append(ticker_return[i] + 1)
                comp_avg_ret.append(np.prod(temp)**(1.0/len(temp)) - 1)  
        return comp_avg_ret
        
    def getExcessReturns(self, rf=None, basis="annually", tickers=None):
        if (rf == None):
            rf = self.risk_free_rate
        if tickers == None:
            tickers = self.ticker_names

        returns = self.getExpectedReturns(basis=basis, tickers=tickers)
        output = []
        for value in returns:
            output.append(value - rf)
        return output

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
        
    def getRiskAversionCoefficient(self, rf=None):
        """
        TODO: Fix
        """
        if (rf == None):
            rf = self.risk_free_rate
        dates = self.getDates()

        benchmark_daily_returns = self.getTickerData(self.BENCHMARK, start=str(dates[1]), end=str(dates[0])).pct_change()
        benchmark_daily_returns_volatility = benchmark_daily_returns.var()[0]
        benchmark_excess_returns = self.getExcessReturns(tickers=self.BENCHMARK)
        risk_aversion_coefficient = benchmark_excess_returns / benchmark_daily_returns_volatility
        return risk_aversion_coefficient

    def getImpliedEquilibriumReturns(self, market_cap_weights=None):

        if (market_cap_weights == None):
            market_cap_weights = self.market_cap_weights
        
        #PI = risk_aversion_coefficient * variance covariance matrix of returns * market capitalization weights
        risk_aversion_coefficient = self.getRiskAversionCoefficient()
        variance_covariance_matrix = self.getVarianceCovarianceMatrix(self.getDailyReturns()).values
        PI = risk_aversion_coefficient * np.matmul(variance_covariance_matrix, market_cap_weights)
        return PI

if __name__ == "__main__":

    bl = BlackLitterman(["AAPL", "MSFT"], 4, 4, .02, [.477091, .522909])
    # bl = BlackLitterman(["AAPL", "MSFT", "^GSPC"],4,4,4)
    # print("Historical Returns", bl.getHistoricalReturns(tickers=["^GSPC"]))
    # print("Expected Returns", bl.getExpectedReturns(tickers=["^GSPC"]))
    # print("Excess Returns", bl.getExcessReturns(rf=.02,tickers=["^GSPC"]))
    print("Historical Returns: ", bl.getHistoricalReturns())
    print("Expected Returns: ", bl.getExpectedReturns())
    print("Excess Returns: ", bl.getExcessReturns())
    print("Risk Aversion: ", bl.getRiskAversionCoefficient(rf=.02))
    print("Implied Equilibrium Returns: ", bl.getImpliedEquilibriumReturns())
    # print(np.dot(100,bl.getVarianceCovarianceMatrix(bl.getDailyReturns()).values))
    # market_cap_weights = [.477091, .522909]
    # # print(np.matmul(bl.getVarianceCovarianceMatrix(bl.getDailyReturns()).values, market_cap_weights))

    # PI = bl.getRiskAversionCoefficient() * np.matmul(bl.getVarianceCovarianceMatrix(bl.getDailyReturns()).values, market_cap_weights)
    # print(PI)
    # print(bl.getDailyReturns(tickers=["MSFT"]).var())

    # print("PI = :", PI)
    #yet another sanity check
    # bl = BlackLitterman(["AAPL", "MSFT", "^GSPC"],4,4,4)
    # dates = bl.getDates()
    # ticker_data = pdr.get_data_yahoo("^GSPC", start=str(dates[1]), end=str(dates[0]))
    # print("hello ",(ticker_data["Adj Close"][252]/ticker_data["Adj Close"][0]) - 1)
    # # print(bl.getExpectedReturns(basis="annually"))
    # print(bl.getHistoricalReturns(basis="annually"))
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

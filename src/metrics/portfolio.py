# -----------------------------------------------------------
# portfolio object for calculating porfolio risk metrics
#
# Stevens Institute of Technology, Hoboken, New Jersey
# Stevens Student Managed Investment Fund
# -----------------------------------------------------------

import datetime
import pandas as pd
from pandas.tseries.offsets import BDay
from math import sqrt
from src.metrics.risk_metrics import semi_deviation, beta, VaR, CVaR, maximum_drawdown, pain_index
from src.metrics.ssmif_datareader import DataReader


def last_business_day(date):
    date = pd.to_datetime(date).date()
    return (date - BDay(0)).date()


class Portfolio:
    def __init__(self, start='2019-01-01', end=datetime.datetime.today().date()):  # max date period set as default
        self.start = pd.Timestamp(start).date()
        self.end = pd.Timestamp(end).date()
        self.__holdings = None
        self.__current_holdings = None
        self.__NAV = None
        self.__weights = None
        self.__benchmark = None
        self.__marginal_risk_holdings = None

    def holdings(self) -> pd.DataFrame: #or positions
        """Calls the Portfolio_Holdings csv under Necessary_Info to arrive at a df of our positions for every
        business day between start and end date"""
        if self.__holdings is None:
            # calls the csv and stock prices for each day and reindexes the csv dataframe with datetime instead of strings
            port_holdings = pd.read_csv('General_Utility_Functions/Necessary_Info/Portfolio_Positions.csv',
                                        index_col='Unnamed: 0')
            port_holdings = port_holdings.fillna(0)
            holding_prices = DataReader(port_holdings.columns[1:], self.start, self.end)['Close']
            port_holdings.index = port_holdings.index.map(lambda x: datetime.datetime.strptime(x, '%Y-%m-%d').date())
            port_holdings = port_holdings.reindex(holding_prices.index)
            port_holdings = port_holdings.fillna(method='ffill')
            port_holdings = port_holdings.fillna(method='bfill')
            # removes cash from port_holdings to make calcuation of stock positions easier
            cash = port_holdings['CASH']
            port_holdings = port_holdings.drop('CASH', axis=1)
            # calculates our stock positions and adds cash back in
            port_holdings = port_holdings * holding_prices
            port_holdings = pd.concat([cash, port_holdings], axis=1, sort=False)
            self.__holdings = port_holdings
        return self.__holdings

    def current_holdings(self) -> pd.Series:
        """Returns the companies we currently own"""
        return self.holdings()[-1]

    def NAV(self) -> pd.Series:
        """Returns a pandas time series of our Net Asset Value for each day"""
        if self.__NAV is None:
            self.__NAV = self.holdings().sum(axis='columns')  # add along columns, so you'll get the sum for each row
        return self.__NAV

    def weights(self) -> pd.DataFrame:
        """Returns a df our portfolio weights for each day for each stock thats held over the entire period"""
        if self.__weights is None:
            position_weights = self.holdings().divide(self.NAV(), axis=0)
            position_weights.name = 'position weights'
            self.__weights = position_weights
        return self.__weights

    def benchmark(self, benchmark='^GSPC') -> pd.Series:
        """Returns the benchmark level for each given day"""
        if self.__benchmark is None:
            self.__benchmark = DataReader(benchmark, self.start, self.end)['Adj Close']
        return self.__benchmark

    def historic_returns(self, start=None, end=None, benchmark=False) -> float:
        """The returns that our NAV had over the given period"""
        start = self.start if start is None else start
        end = self.end if end is None else end
        if benchmark:
            asset = self.benchmark()[pd.to_datetime(start).date():pd.to_datetime(end).date()]
        else:
            asset = self.NAV()[pd.to_datetime(start).date():pd.to_datetime(end).date()]
        return (asset[-1] / asset[0] - 1) * 100

    def MTD_returns(self, today=datetime.datetime.today().date(), benchmark=False) -> float:
        """Gives returns since the last calender month start"""
        return self.historic_returns(
            start=today,
            end=pd.to_datetime(today).date().replace(day=1),
            benchmark=benchmark
        )

    def YTD_returns(self, today=datetime.datetime.today().date(), benchmark=False) -> float:
        """Gives returns since the last calender year start"""
        return self.historic_returns(
            start=today,
            end=pd.to_datetime(today).date().replace(month=1),
            benchmark=benchmark
        )

    def historic_vol(self, start=None, end=None, benchmark=False, period=252) -> float:
        """The vol that our NAV had over the given period"""
        start = last_business_day(self.start) if start is None else last_business_day(start)
        end = last_business_day(self.end) if end is None else last_business_day(end)
        if benchmark:
            asset = self.benchmark()[start:end]
        else:
            asset = self.NAV()[start:end]
        return asset.pct_change().std() * sqrt(period) * 100

    def current_vol(self, start, end=datetime.datetime.today().date(), period=252) -> float:
        """Our volatility under our current holdings. It is our historic volatility if we had this
        current position for the entire period"""
        df = DataReader(self.current_holdings().index, start=start, end=end)['Adj Close']
        return df.pct_change.dropna().std() * sqrt(period) * 100

    def MTD_vol(self, today=datetime.datetime.today().date(), benchmark=False, period=252) -> float:
        """Gives the volatility since the last calender month start"""
        return self.historic_vol(
            start=today,
            end=pd.to_datetime(today).date().replace(day=1),
            benchmark=benchmark,
            period=period
        )

    def YTD_vol(self, today=datetime.datetime.today().date(), benchmark=False, period=252) -> float:
        """Gives the volatility since the last calender year start"""
        return self.historic_vol(
            start=today,
            end=pd.to_datetime(today).date().replace(month=1),
            benchmark=benchmark,
            period=period
        )

    def historic_semi_deviation(self, start=None, end=None, benchmark=False) -> float:
        """The semi-deviation that our NAV had over the given period"""
        start = last_business_day(self.start) if start is None else last_business_day(start)
        end = last_business_day(self.end) if end is None else last_business_day(end)
        if benchmark:
            asset = self.benchmark()[start:end]
        else:
            asset = self.NAV()[start:end]
        return semi_deviation(asset)

    def historic_beta(self) -> float:
        """The beta that our NAV had with the benchmark over the given period"""
        return beta(self.NAV(), self.benchmark())

    def current_beta(self, start, end=datetime.datetime.today().date()) -> float:
        """Our beta under our current holdings. It is our historic beta if we had this
        current position for the entire period"""
        nav = DataReader(self.current_holdings().index, start=start, end=end)['Adj Close'].sum(axis=1)
        benchmark = DataReader('^GSPC', start=start, end=end)['Adj Close']
        return beta(nav, benchmark)

    def historic_VaR(self, confidence_level=0.05) -> float:
        """The VaR that our NAV had over the given period"""
        return VaR(self.NAV(), confidence_level=confidence_level)

    def historic_CVaR(self, confidence_level=0.05) -> float:
        """The CVaR that our NAV had over the given period"""
        return CVaR(self.NAV(), confidence_level=confidence_level)

    def current_VaR(self, start, end=datetime.datetime.today().date(), confidence_level=0.05) -> float:
        """Our VaR under our current holdings. It is our historic VaR if we had this
        current position for the entire period"""
        nav = DataReader(self.current_holdings().index, start=start, end=end)['Adj Close'].sum(axis=1)
        return VaR(nav, confidence_level=confidence_level)

    def current_CVaR(self, start, end=datetime.datetime.today().date(), confidence_level=0.05) -> float:
        """Our CVaR under our current holdings. It is our historic CVaR if we had this
        current position for the entire period"""
        nav = DataReader(self.current_holdings().index, start=start, end=end)['Adj Close'].sum(axis=1)
        return CVaR(nav, confidence_level=confidence_level)

    def maximum_drawdown(self, window: int) -> float:
        """The maximum drawdown that our NAV had over the given window"""
        return maximum_drawdown(self.NAV(), window=window)

    def pain_index(self, window: int) -> float:
        """The pain index that our NAV had over the given window"""
        return pain_index(self.NAV(), window=window)

    def current_marginal_risk_of_port_holdings(self, start, end) -> pd.Series:
        """Returns how much of our volatility is coming from each stock"""
        if self.__marginal_risk_holdings is None:
            df = DataReader(self.current_holdings().index, start=start, end=end)['Adj Close']
            self.__marginal_risk_holdings = df.pct_change().dropna().cov().sum()
        return self.__marginal_risk_holdings

    def marginal_port_risk(self, ticker: str, start, end) -> float:
        """Returns how much of our volatility the stock is contributing"""
        return self.current_marginal_risk_of_port_holdings(start, end)[ticker]


if __name__ == '__main__':
    pass

# -----------------------------------------------------------
# basic functions for calculating common risk metrics
#
# Stevens Institute of Technology, Hoboken, New Jersey
# Stevens Student Managed Investment Fund
# -----------------------------------------------------------

import numpy as np
import pandas as pd
import statistics as stats
import logging
from math import sqrt
from sklearn.linear_model import LinearRegression


def monthly_vol(price_data: pd.Series) -> float:
	"""Returns the volatility you can expect over a month"""
	return price_data.pct_change().dropna().std() * sqrt(252 / 12)


def semi_deviation(price_data: pd.Series) -> float:
	"""Returns the semi-deviation over the given period. Semi-deviation is just like standard deviation but it only counts
	negative deviations from the mean, so you're not penalizing stock returns that are greater than its average.
	For more information go to https://www.investopedia.com/terms/s/semideviation.asp"""
	returns = price_data.pct_change().dropna()
	return returns[returns < returns.mean()].std()


def beta(price_data: pd.Series, benchmark_data: pd.Series) -> float:
	"""Returns the beta over the given period. Beta tells you the multiple by which you can expect a security's price to
	change relative the percent change of a benchmark.
	For more information go to https://www.investopedia.com/terms/b/beta.asp"""

	# daily returns
	daily = price_data.pct_change().dropna()
	# gets spy data
	benchmark_daily = benchmark_data.pct_change().dropna()

	# calculating beta
	reg = LinearRegression()
	try:
		reg.fit(benchmark_daily.to_numpy().reshape(-1, 1), daily)
		beta = reg.coef_[0]
	except Exception as e:
		logging.warning(e)
		# print("Mismatch array length")
		return 0.0

	return beta


def VaR(price_data: pd.Series, confidence_level=0.05) -> float:
	"""Returns the value-at-risk for the given period. Value-at-risk, or VaR, is the quantile associated with a given
	confidence interval; or, very naively, can be thought of as the most you can expect to lose under a certain
	confidence level. More realistically, it should be thought of as your max price loss excluding the worst case scenarios.
	For more information go to https://www.investopedia.com/terms/v/var.asp"""

	returns = np.array(price_data.pct_change().dropna())
	return np.quantile(returns, confidence_level) * sqrt(252 / 12)


def CVaR(price_data: pd.Series, confidence_level=0.05) -> float:
	"""Returns the conditional value-at-risk for the given period. Conditional value-at-risk, or CVaR,
	gives you the expected price change (loss) when a price change falls outside of its VaR. Its is your expected price
	change in your worst case scenario.
	For more information go to https://www.investopedia.com/terms/c/conditional_value_at_risk.asp"""

	sorted_returns = sorted(price_data.pct_change().dropna())
	cvar = (1 - stats.mean(sorted_returns[0:int(len(sorted_returns) * confidence_level)])) * sqrt(252 / 12)
	return cvar


def maximum_drawdown(price_data: pd.Series, window=252) -> float:
	"""Returns the maximum drawdown for the given period. Maximum drawdown, or MDD, is the spread between an asset's
	maximum and minimum price over a given period as a percent of the maximum price. It is a measure of downside risk.
	For more information go to https://www.investopedia.com/terms/m/maximum-drawdown-mdd.asp"""

	Roll_Max = price_data.rolling(window=window, min_periods=1).max()
	Daily_Drawdown = price_data / Roll_Max - 1.0
	Max_Daily_Drawdown = Daily_Drawdown.rolling(window=window, min_periods=1).min()
	# Daily_Drawdown.plot()
	# Max_Daily_Drawdown.plot()
	# plt.show()
	return Max_Daily_Drawdown[-1]


def pain_index(price_data: pd.Series, window=252) -> float:
	"""Returns the pain_index for the given period. The pain index is the mean of the asset's drawdowns for a
	given period.
	For more information go to https://www.styleadvisor.com/resources/statfacts/pain-index"""

	rolling_max = price_data.rolling(window, min_periods=1).max()
	drawdown = (price_data - rolling_max) / rolling_max
	pain_index = sum((abs(drawdown) / (len(drawdown))))
	return pain_index


def ATR(price_points_data: pd.DataFrame, window=14) -> float:
	"""Returns the average true range for the given period. Average true range, or ATR, is a way of calculating
	stop-losses and how they are reported for SSMIF.
	To see how it is calculated and for more information go to https://www.investopedia.com/terms/a/atr.asp

	price_points_data: a DataFrame with the columns 'High', 'Low', and 'Close'
	"""
	total_true_range = price_points_data[:window].apply( lambda day: max(
		abs(day.High - day.Low),
		abs(day.High - day.Close),
		abs(day.Low - day.Close)
	), axis=1).sum()
	return total_true_range / window


if __name__ == '__main__':
	import pandas_datareader as pdr
	aapl = pdr.DataReader('AAPL', 'yahoo', '2018-01-01', '2019-01-01')['Adj Close']
	print( VaR(aapl) )

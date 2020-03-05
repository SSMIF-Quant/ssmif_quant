#We will need to calculate the covariance matrix of the returns,
#the market caps of each of the assets in consideration
#the risk aversion rate
import pandas as pd
import yfinance as yf
import numpy as np
import seaborn as sns
import pandas_datareader as pdr
import matplotlib.pyplot as pt
from datetime import date

def getDailyReturns(equity_df, basis="Adj Close"):
    returns = []
    basis_columns = []
    #ok, so we have a list of dataframes and we need to get certain columns from each
    for frames in equity_df:
        basis_columns.append(frames[basis])
    
    for col in basis_columns:
        returns.append(col.pct_change().fillna(0))
    
    return returns

def getCovarianceMatrixOfReturns(equities, start, end, basis="Adj Close"):
#This implementation is based off of this example https://stattrek.com/matrix-algebra/covariance-matrix.aspx
    #when printed pandas will round off the output values, in reality they are float64
    #the same thing will happen when you print the .values of V

    equity_df = getTickerStats(equities, start=start, end=end)
    basis_columns = getDailyReturns(equity_df)

########################################TESTING CONTENT############################################
#each sub list represents a different "student's test scores" in math english and art
    # basis_columns = [[90,90,60,60,30], [60,90,60,60,30], [90,30,60,90,30]]
########################################TESTING CONTENT#############################################

    X = np.array(basis_columns).T.tolist()
    X = pd.DataFrame(X, columns=equities)
    #first column of X is the first item in basis columns, second with second, ....
    #time for the math
    #first we will transform the raw data matrix X into deviation scores for matrix x
    #x = X - 11'X (1.0/n) where 
    # X is an n x k matrix of returns, x is an n x k matrix of deviation scores, and 1 is an n x 1 column 
    # vector of ones
    n = len(X.index)
    #one = 11'
    one = np.ones((n,n))
    #x = X - (1.0/n) * 11'X
    x = np.subtract(X, np.multiply( (1/n), np.matmul(one, X) ))
    xt = x.transpose()
    #Then we will compute x'x, the k x k deviation sums of squares and cross products matrix for x
    #pandas dot is a matrix multiplication operation
    dev_ss_cp = xt.dot(x)
    V  = np.multiply((1/n), dev_ss_cp)
    #V should be a k x k (num assets x num assets) variance covariance matrix
    return V

def getTickerStats(tickers, start, end):
        equity_df = []
        for ticker in tickers:
            equity_df.append(yf.download(ticker, start=start, end=end))
        
        return equity_df

def getRiskFreeRate(benchmark=["^IRX"], basis="Adj Close", start=date.today().strftime("%Y-%m-%d"), end=date.today().strftime("%Y-%m-%d")):
    rf = getTickerStats(benchmark, start=start, end=end)
    return rf[0][basis][-1]

def getMarketCapWeights(market_caps):
    market_cap_weights = []
    total_market_cap = sum(market_caps)

    for cap in market_caps:
        market_cap_weights.append(cap/total_market_cap)
    
    return market_cap_weights

def calcImpliedEquilibriumReturns(tickers, start, end, basis="Adj Close"):
    cov_matrix.values = getCovarianceMatrixOfReturns(tickers, start=start, end=end, basis=basis)
    #risk_aversion_coef = getRiskAversionCoef()
    risk_aversion_coef = 3
    market_cap_weights = getMarketCapWeights([1.63, 227.72, 33.64, 904.62, 131.4])
    #PI = l * E * W
    return np.multiply(risk_aversion_coef, np.matmul(cov_matrix, market_cap_weights))

    

if __name__ == "__main__":
    # end = "2020-02-01"
    end = date.today().strftime("%Y-%m-%d")
    start = "2020-01-01"
    # equities = ["HEDJ", "VZ", "STZ", "GOOG", "AMGN", "EMR", "GILD", "FMC"]
    equities = ["HEDJ", "VZ", "STZ", "GOOG", "EMR"]
    #market_caps = [1.63, 227.72, 33.64, 904.62, 131.4, 39.39, 91.18, 11.97]
    market_caps = [1.63, 227.72, 33.64, 904.62, 131.4]
    var_cov_matrix = getCovarianceMatrixOfReturns(equities, start=start, end=end, basis="Adj Close")
    print("##############VARIANCE COVARIANCE MATRIX ###################\n")
    print(var_cov_matrix)
    print()
    print(var_cov_matrix.values)
    print()
    print(var_cov_matrix.values[0][0])
    print("\n###################################################\n")

    # rf = getRiskFreeRate()
    # print(rf)
    # print(getMarketCapWeights([1.63, 227.72, 33.64, 904.62, 131.4]))
    # print(sum(getMarketCapWeights([1.63, 227.72, 33.64, 904.62, 131.4])))
    # print(calcImpliedEquilibriumReturns(equities, start=start, end=end, basis="Adj Close") * 100)








# def getCovarianceMatrixOfReturns2(equities, start, end, basis="Adj Close"):
#     basis_df = pdr.DataReader(["HEDJ"], 'yahoo', start=start, end=end)[basis]
#     #V = np.multiply(basis_df.pct_change().dropna().cov(), (len(basis_df) - 1) / len(basis_df))
#     #print(V)
#     basis_col = basis_df["HEDJ"]
#     change = basis_col.pct_change()
#     variance = (change.std() * (len(change)-1)/(len(change)))**2
#     print(variance)    
#     #return V

# def getCovarianceMatrixOfReturns3(equities, start, end, basis="Adj Close"):
# #This implementation is based off of this example https://stattrek.com/matrix-algebra/covariance-matrix.aspx
#     equity_df = getTickerStats(equities, start=start, end=end)
#     basis_columns = getDailyReturns(equity_df)

# ########################################TESTING CONTENT############################################
# #each sub list represents a different "student's test scores" in math english and art
#     # basis_columns = [[90,90,60,60,30], [60,90,60,60,30], [90,30,60,90,30]]
# ########################################TESTING CONTENT#############################################

#     X = np.array(basis_columns).T.tolist()
#     n = len(X)
#     #one = 11'
#     one = np.ones((n,n))

#     #x = X - (1.0/n) * 11'X
#     x = np.subtract(X, np.multiply( (1/n), np.matmul(one, X) ))
#     dev_ss_cp = np.matmul(x.transpose(), x)
#     V  = np.multiply((1/n), dev_ss_cp)
#     return pd.DataFrame(V, columns=equities, index=equities)
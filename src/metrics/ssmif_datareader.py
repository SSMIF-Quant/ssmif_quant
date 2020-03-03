# -----------------------------------------------------------
# Overrides pandas_datareader functions with our own for faster results
#
# (C) 2020 Juan Amezquita, Hoboken, New Jersey
# Released under GNU Public License (GPL)
# email jamezqui@stevens.edu
# -----------------------------------------------------------


def DataReader(ticker, start, end):
    """A wrapper for the ssmif api call that gets stock data, the effect is to override the pandas_datareader
    function DataReader. Used in exact same way as pandas_datareader.DataReader, only
    difference is that it pulls stock data from our database for faster results."""

    #for now it'll just be a wrapper for pandas_datareader.DataReader
    import pandas_datareader as pdr
    return pdr.DataReader(ticker, 'yahoo', start=start, end=end)


if __name__ == '__main__':
    pass

import sys
import os
from datetime import date
import pandas_datareader as pdr
import logging
import json

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from Metrics import *
from changelog import changelog
from Risk_API import holdings, transactions, accounts

app = Flask(__name__)
app.secret_key = 'quantgang2019'

app.config.from_object(__name__)


@app.route('/')
def screen():
    # will check if a user has logged in by checking if the session variable is not none. If it is none, no user has login, so redirect to login page
    if session.get('username') != None:
        # loads the screen.html template and passes in the latest version number to be presented on the risk screen page
        return render_template("screen.html", version = changelog[0]['version'])
    else:
        # if session username not set, run the login() fucntion
        return redirect(url_for('login'))

@app.route('/changelog')
def view_changelog():
    # returns the changelog list and the length of it to be used on the changelog page
    return render_template("changelog.html", changes = changelog, changeslen = len(changelog))

@app.route('/holdings')
def holdingspage():
    # will check if a user has logged in by checking if the session variable is not none. If it is none, no user has login, so redirect to login page
    if session.get('username') != None:
        return render_template("holdings.html")
    else:
        return redirect(url_for('login'))


# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    session.pop('username', None)
    session.pop('perms', (0, 0, 0))
    if request.method == 'POST':
        authenticated, perms = accounts.auth(request.form['username'], request.form['password'])
        if not authenticated:
            error = 'Invalid Credentials. Please try again.'
        else:
            session['username'] = request.form['username']
            session['perms'] = perms
            return redirect(url_for('screen'))
    return render_template('login.html', error=error)



# API Endpoints


# Holdings
@app.route('/api/holdings/getHoldings')
def returnHoldings():
    return jsonify(holdings.getHoldings())

@app.route('/api/holdings/getHoldings/<ticker>')
def returnHoldingsByTicker(ticker):
    return jsonify(holdings.getHoldingsByTicker(ticker))

@app.route('/api/holdings/getHoldingsFromCSV')
def returnHoldingsFromCSV():
    return json.loads(holdings.getHoldingsFromCSV())




# Transactions
@app.route('/api/transactions/getTransactions')
def returnTransactions():
    return jsonify(transactions.getTransactions())

@app.route('/api/transactions/getTransactionsFromCSV')
def returnTransactionsFromCSV():
    return json.loads(transactions.getTransactionsFromCSV())

@app.route('/api/transactions/getTransactionsBefore/<inputtime>')
def returnTransactionsBefore(inputtime):
    return jsonify(transactions.getTransactionsBeforeDate(int(inputtime)))

@app.route('/api/transactions/getTransactionsAfter/<inputtime>')
def returnTransactionsAfter(inputtime):
    return jsonify(transactions.getTransactionsAfterDate(int(inputtime)))

@app.route('/api/transactions/newTransaction', methods=['POST'])
def addNewTransactions():
    transactions.newTransaction(request.form['transDate'], request.form['transType'], request.form['symbol'], request.form['prodDesc'], request.form['units'], request.form['grossAmt'], request.form['transFee'], request.form['netAmt'])
    return 'success'




@app.route('/screen-backend', methods=['POST'])
def backend():
    """The backend end to the form on screen.html. The form data gets POSTed here via AJAX and creates a list of metric values which gets sent back in JSON in the form of {[],[]...}."""
    metric_data = []

    # global status
    # num_metrics = 11
    # status = {'metric':'None', 'num':-1, 'total':num_metrics, 'status':'start'}

    try:
        # status = {'metric':'Data Collection', 'num':0, 'total': num_metrics, 'status':'ok'}
        today = date.today()
        ticker_data = pdr.get_data_yahoo(request.form['ticker'], str(today.replace(year = today.year - int(request.form['years']))))
        sector_data = pdr.get_data_yahoo(request.form['sector'], str(today.replace(year = today.year - int(request.form['years']))))
        spy_data = pdr.get_data_yahoo("^GSPC", str(today.replace(year = today.year - int(request.form['years']))))
    except Exception as e:
        metric_data.append("Error")
        logging.info(e)
        # status = {'metric':'Error', 'num':-2, 'total':num_metrics, 'status':'error'}
        return jsonify(metric_data)


    try:
        # status = {'metric':'Portfolio VaR', 'num':1, 'total': num_metrics, 'status':'ok'}
        value = CalcPortfolioVar.calcPortfolioVar(timeRange = int(request.form['years']), marginalTicker = request.form['ticker']) * 100
        if(value > 15):
            pf = "fail"
        else:
            pf = "pass"
        metric_data.append({'metric': 'Portfolio VaR w/ ' + request.form['ticker'], 'value' : '{0:.3g}%'.format(value), 'pf':pf})
    except Exception as e:
        metric_data.append({'metric': 'Portfolio VaR w/ ' + request.form['ticker'], 'value' : "Error", 'pf':""})
        logging.info('Portfolio VaR: ')
        logging.info(e)

    try:
        # status = {'metric':'Portfolio CVaR', 'num':2, 'total': num_metrics, 'status':'ok'}
        value = CalcPortfolioCvar.calcPortfolioCvar(timeRange = int(request.form['years']), marginalTicker = request.form['ticker']) * 100
        metric_data.append({'metric': 'Portfolio CVaR w/ ' + request.form['ticker'], 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Portfolio CVaR w/ ' + request.form['ticker'], 'value' : "Error", 'pf':""})
        logging.info('Portfolio CVaR: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly VaR', 'num':3, 'total': num_metrics, 'status':'ok'}
        value = CalcVar.calcVar(ticker_data) * 100
        metric_data.append({'metric': 'Monthly VaR', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly VaR', 'value' : "Error", 'pf':""})
        logging.info('Monthly VaR: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly CVaR', 'num':4, 'total': num_metrics, 'status':'ok'}
        value = CalcCvar.calcCvar(ticker_data) * 100
        metric_data.append({'metric': 'Monthly CVaR', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly CVaR', 'value' : "Error", 'pf':""})
        logging.info('Monthly CVaR: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly Semi Dev', 'num':5, 'total': num_metrics, 'status':'ok'}
        value = semi_deviation.semi_deviation(ticker_data) * 100
        metric_data.append({'metric': 'Monthly Semi Dev', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly Semi Dev', 'value' : "Error", 'pf':""})
        logging.info('Monthly Semi Dev: ')
        logging.info(e)

    try:
        # status = {'metric':'Daily Max Drawdown', 'num':6, 'total': num_metrics, 'status':'ok'}
        value = maximum_drawdown.max_drawdown(ticker_data) * 100
        metric_data.append({'metric': 'Daily Max Drawdown', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Daily Max Drawdown', 'value' : "Error", 'pf':""})
        logging.info('Daily Max Drawdown: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly Pain Index', 'num':7, 'total': num_metrics, 'status':'ok'}
        value = pain_index.pain_index(ticker_data, spy_data) * 100
        metric_data.append({'metric': 'Monthly Pain Index', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly Pain Index', 'value' : "Error", 'pf':""})
        logging.info('Monthly Pain Index: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly Beta', 'num':8, 'total': num_metrics, 'status':'ok'}
        value = beta.beta(ticker_data, spy_data)
        metric_data.append({'metric': 'Monthly Beta', 'value' : '{0:.3g}'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly Beta', 'value' : "Error", 'pf':""})
        logging.info('Monthly Beta: ')
        logging.info(e)

    try:
        # status = {'metric':'Sector Beta', 'num':9, 'total': num_metrics, 'status':'ok'}
        value = sector_beta.call_sector_beta(ticker_data, request.form['ticker'], int(request.form['years']), sector_data)
        metric_data.append({'metric': 'Sector Beta', 'value' : '{0:.3g}'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Sector Beta', 'value' : "Error", 'pf':""})
        logging.info('Sector Beta: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly Variance', 'num':10, 'total': num_metrics, 'status':'ok'}
        value = monthly_variance.call_monthly_variance(ticker_data) * 100
        metric_data.append({'metric': 'Monthly Variance', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly Variance', 'value' : "Error", 'pf':""})
        logging.info('Monthly Variance: ')
        logging.info(e)

    try:
        # status = {'metric':'Monthly Historical Volatility', 'num':11, 'total': num_metrics, 'status':'ok'}
        value = CalcMonthlyVolatility.calcMonthlyVolatility(ticker_data) * 100
        metric_data.append({'metric': 'Monthly Historical Volatility', 'value' : '{0:.3g}%'.format(value), 'pf':""})
    except Exception as e:
        metric_data.append({'metric': 'Monthly Historical Volatility', 'value' : "Error", 'pf':""})
        logging.info('Historical Volatility: ')
        logging.info(e)

    # try:
    #     metric_data.append({'metric': 'GICS Sector', 'value' : get_sector(request.form['ticker']), 'pf':""})
    # except:
    #     metric_data.append({'metric': 'GICS Sector', 'value' : "Error", 'pf':""})

    # status = {'metric':'Done', 'num':-1, 'total': num_metrics, 'status':'finish'}
    return jsonify(metric_data)

if __name__ == '__main__':
    app.run()
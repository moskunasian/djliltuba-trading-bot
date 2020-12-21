import uuid
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.feeds as btfeeds
from PermuteStrategy import PermuteStrategy
from itertools import chain, combinations


def indicator_powerset(indicators):
    s = list(indicators)
    return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1)))


def get_sptickers():
    sp_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return list(sp_table[0]['Symbol'])


def get_tickerdata(cer_obj, curr_ticker, start_date, end_date, pset):
    cer_obj.addstrategy(PermuteStrategy, ta_set=pset)
    ticker_data = yf.Ticker(curr_ticker)
    ticker_data = ticker_data.history(start=start_date, end=end_date)
    ticker_data = bt.feeds.PandasData(dataname=ticker_data)
    cer_obj.adddata(ticker_data)
    return cer_obj


def run_backtest(cer_obj, start_cash, stake_sizer):
    cer_obj.broker.setcash(start_cash)
    cer_obj.addsizer(bt.sizers.FixedSize, stake=stake_sizer)
    account_start = cer_obj.broker.getvalue()
    cer_obj.run()
    account_end = cer_obj.broker.getvalue()
    return round(float(account_end - account_start), 2)


def save_backtest(curr_ticker, potential, pset, date_range):
    inner_perf = {}
    inner_perf["final_profit"] = potential
    inner_perf["ta_set"] = [str(x) for x in pset]
    inner_perf["ticker"] = curr_ticker
    inner_perf["backtest_range"] = date_range
    inner_perf["backtest_id"] = str(uuid.uuid4())
    return inner_perf


def ticker_backtest(tickers=[], start_date="2005-01-01", end_date="2020-10-31", start_cash=100000, stake_sizer=10):
    indicator_fxns = [PermuteStrategy.retrieve_rsi, PermuteStrategy.retrieve_macd]
    powerset = indicator_powerset(indicator_fxns)
    top_perf = []

    for ticker in tickers:
        for pset in powerset:
            inner_perf = {}
            cer = bt.Cerebro()
            cer = get_tickerdata(cer, ticker, start_date, end_date, pset)
            potential = run_backtest(cer, start_cash, stake_sizer)
            top_perf.append(save_backtest(ticker, potential, pset, [start_date, end_date]))
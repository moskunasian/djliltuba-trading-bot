# powerset_backtests.py
# 11.01.2020

import ta
import sys
import os.path
import datetime
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.feeds as btfeeds
from itertools import chain, combinations

START_CASH = 100000.0

class PermuteStrategy(bt.Strategy):
    params = (
        ('ta_set', None),
    )


    def __init__(self):
        self.date_close =   self.datas[0].close
        self.date_high =    self.datas[0].high
        self.date_low =     self.datas[0].low
        self.date_volume =  self.datas[0].volume
        self.order =        None
        self.buy_price =    None


    def retrieve_rsi(self):
        # ta.momentum.RSIIndicator(close)
        return


    def retrieve_macd(self):
        # ta.trend.MACD(close)
        return

    
    def retrieve_bbands(self):
        # ta.volatility.bollinger_hband_indicator(close)
        # ta.volatility.bollinger_lband_indicator(close)
        return

    
    def retrieve_vwap(self):
        # ta.volume.VolumeWeightedAveragePrice(high, low, close, volume)
        return


    def log_event(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print("%s, %s" % (dt.isoformat(), txt))


    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log_event(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f" % 
                    (order.executed.price,
                     order.executed.value))
                self.buy_price = order.executed.price
            else:
                self.log_event(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f" % 
                    (order.executed.price,
                     order.executed.value))
            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log_event("Order Canceled/Margin/Rejected")

        self.order = None


        def notify_trade(self, trade):
            if not trade.isclosed:
                return

            self.log_event("Operation Profit, Gross %.2f, NET %.2f" %
                    (trade.pnl, trade.pnl_comm))


    # this will be holding the strategy, once available to be referenced
    def next(self):
        self.log_event("Close, %.2f" % self.date_close[0])

        if self.order:
            return

        if not self.position:
            # placeholder buy strat for initial testing
            # if all in current set return true, buy
            if self.date_close[0] < self.date_close[-1]:
                if self.date_close[-1] < self.date_close[-2]:
                    self.log_event("BUY CREATE, %.2f" % self.date_close[0])
                    self.order = self.buy()
        else:
            # placeholder sell strat for initial testing
            if len(self) >= (self.bar_executed + 5):
                self.log_event("SELL CREATE, %.2f" % self.date_close[0])
                self.order = self.sell()


def indicator_powerset(indicators):
    s = list(indicators)
    return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1)))


def retrieve_sptickers():
    sp_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return list(sp_table[0]['Symbol'])


if __name__ == '__main__':
    indicator_fxns = [PermuteStrategy.retrieve_rsi, 
                      PermuteStrategy.retrieve_macd, 
                      PermuteStrategy.retrieve_bbands, 
                      PermuteStrategy.retrieve_vwap]
    powerset = indicator_powerset(indicator_fxns) 
    # for pset in powerset:
    # will loop and try strategy per each pset, will test just one starting out, then all

    cer = bt.Cerebro()
    cer.addstrategy(PermuteStrategy, ta_set=[])

    data = yf.Ticker("MSFT")
    data = data.history(start="2005-01-01", end="2020-12-31")

    data = bt.feeds.PandasData(dataname=data)
    cer.adddata(data)
    
    cer.broker.setcash(START_CASH)
    cer.addsizer(bt.sizers.FixedSize, stake=10)
    start_cash = cer.broker.getvalue()
    cer.run()
    end_cash = cer.broker.getvalue()

    # initial storage will be something along the lines of:
    # {ticker: {final_profit: x, ta_set: []}, ticker2: { ... }}

    print("Final Profit Potential: $%.2f" % (float(end_cash) - float(start_cash)))

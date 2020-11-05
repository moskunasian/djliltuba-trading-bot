# powerset_backtests.py
# 11.01.2020

import ta 
import sys
import uuid
import os.path
import datetime
import pandas as pd
import yfinance as yf
import backtrader as bt
import backtrader.feeds as btfeeds
from itertools import chain, combinations

START_CASH = 100000.0
RSI_SELL_FLAG = 70
RSI_BUY_FLAG = 30
START_DATE = "2005-01-01"
END_DATE = "2020-12-31"

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

        # indicators being pre calculated, although not always used
        self.macd = bt.indicators.MACD(self.datas[0])
        self.m_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.rsi = bt.talib.RSI(self.datas[0])


    def retrieve_rsi(self):
        if self.rsi[0] <= RSI_BUY_FLAG:
            return 1
        elif self.rsi[0] >= RSI_SELL_FLAG:
            return -1
        return 0


    def retrieve_macd(self):
        if self.m_cross[0] > 0:
            return 1
        elif self.m_cross[0] < 0:
            return -1
        return 0


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
        

    def next(self):
        if self.order:
            return

        flag_sum = 0
        for fxn in self.params.ta_set:
            flag_sum += fxn(self)
    
        if not self.position:
            if flag_sum == len(self.params.ta_set):
                self.log_event("BUY CREATE, %.2f" % self.date_close[0])
                self.order = self.buy()
        else:
            if flag_sum == (len(self.params.ta_set) * -1):
                self.log_event("SELL CREATE, %.2f" % self.date_close[0])
                self.order = self.sell()


def indicator_powerset(indicators):
    s = list(indicators)
    return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1)))


def retrieve_sptickers():
    sp_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return list(sp_table[0]['Symbol'])


if __name__ == '__main__':
    indicator_fxns = [PermuteStrategy.retrieve_rsi, PermuteStrategy.retrieve_macd]
    powerset = indicator_powerset(indicator_fxns) 
    performance_dict = {}

    for ticker in retrieve_sptickers()[:2]:
        for pset in powerset:
            inner_perf = {}

            cer = bt.Cerebro()
            cer.addstrategy(PermuteStrategy, ta_set=pset)
            data = yf.Ticker("MSFT")
            data = data.history(start="2005-01-01", end="2020-12-31")
            data = bt.feeds.PandasData(dataname=data)
            cer.adddata(data)
            
            cer.broker.setcash(START_CASH)
            cer.addsizer(bt.sizers.FixedSize, stake=10)
            start_cash = cer.broker.getvalue()
            cer.run()
            end_cash = cer.broker.getvalue()

            inner_perf["final_profit"] = round(float(end_cash) - float(start_cash), 2)
            inner_perf["ta_set"] = [str(x) for x in pset]
            inner_perf["ticker"] = ticker
            inner_perf["backtest_range"] = [START_DATE, END_DATE]
            performance_dict[str(uuid.uuid4())] = inner_perf
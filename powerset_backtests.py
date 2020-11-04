# powerset_backtests.py
# 11.01.2020

import sys
import os.path
import datetime
import pandas as pd
import backtrader as bt
import backtrader.feeds as btfeeds
from itertools import chain, combinations


class PermuteStrategy(bt.Strategy):

    def __init__(self):
        self.date_close = self.datas[0].close
        self.order = None
        self.buy_price = None
        self.ta_set = None

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
                self.log(
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

        self.log("Operation Profit, Gross %.2f, NET %.2f" %
                 (trade.pnl, trade.pnl_comm))

    # this will be holding the strategy, once available to be referenced
    def next(self):
        self.log_event("Close, %.2f" % self.date_close[0])

    if self.order:
        return

    if not self.position:
        # not in the market, could possibly buy
    else:
        # already in the market, might sell for checking


def indicator_powerset(indicators):
    s = list(indicators)
    return list(chain.from_iterable(combinations(s, r) for r in range(1, len(s) + 1)))


def retrieve_sptickers():
    sp_table = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    return list(sp_table[0]['Symbol'])


if __name__ == '__main__':
    cer = bt.Cerebro()
    cer.addstrategy(PermuteStrategy)
import ta 
import sys
import os.path
import datetime
import backtrader as bt


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

        self.macd = bt.indicators.MACD(self.datas[0])
        self.m_cross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
        self.rsi = bt.indicators.RelativeStrengthIndex(self.datas[0])


    def retrieve_rsi(self):
        if self.rsi[0] <= 30:
            return 1
        elif self.rsi[0] >= 70:
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
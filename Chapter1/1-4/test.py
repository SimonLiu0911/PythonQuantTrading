import backtrader as bt
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf


class SMAStrategy(bt.Strategy):
    def __init__(self):
        self.dataclose = self.data.close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.sma = bt.indicators.SimpleMovingAverage(self.data.close, period=14)

    def next(self):
        if not self.position:
            if self.dataclose[0] > self.sma[0]:
                self.buy()
        else:
            if self.dataclose[0] < self.sma[0]:
                self.sell()

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if self.isbuy():
                self.log(
                    (
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    )
                )
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:
                self.log(
                    (
                        order.executed.price,
                        order.executed.value,
                        order.executed.comm,
                    )
                )
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")
        self.order = None

    def notify_order(self, trade):
        if not trade.isclosed:
            return
        self.log("OPERATION PROFIT")

    # def log(self, txt, dt=None, doprint=False)


cerebro = bt.Cerebro()
asset = "2335.TW"
data = bt.feeds.PandasData(
    dataname=yf.download(asset, "2011-01-01", "2025-11-24").droplevel("Ticker", axis=1)[
        ["Open", "High", "Low", "Close", "Volume"]
    ]
)
cerebro.adddata(data)



# %%
import pandas as pd
stock_data = pd.DataFrame({
    "Close": [10.5, None, None, 11.0, None, 12.0],
    "Volume": [1000, 1200, None, None, 1500, None],
})
stock_data_filled = stock_data.ffill()
print(stock_data_filled)

# %%
from finlab import data
factor_data = data.get(f"fundamental_features:{"營業利益"}").deadline()
# factor_data = data.get(f"fundamental_features:ROA稅後息前").deadline()
# Ndhv3Iwte6ie9K9mXiVdIvTaSpjgEJbclXgWS3p9HKf3iOcbWAOQoCGXt33a5o9H
print(factor_data.columns)
# %%

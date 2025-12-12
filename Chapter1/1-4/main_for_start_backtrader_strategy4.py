"""範例策略四：移動平均交叉策略"""

# %%
import backtrader as bt
import numpy as np
import yfinance as yf
import pandas as pd


class MovingAverageCrossStrategy(bt.Strategy):
    # 定義策略的參數：短期移動平均線週期和長期移動平均線週期
    params = (("short_period", 5), ("long_period", 20))

    def __init__(self):
        # 5日均線作為短期移動平均線
        self.short_sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.short_period
        )
        # 20日均線作為長期移動平均線
        self.long_sma = bt.indicators.SimpleMovingAverage(
            self.data.close, period=self.params.long_period
        )
        # 初始化訂單狀態，用來追蹤當前的訂單
        self.order = None

    def next(self):
        # 紀錄當日的均線與持倉狀態，方便觀察為何當天是否產生訊號
        short_val = float(self.short_sma[0])
        long_val = float(self.long_sma[0])
        pos_size = np.round(self.position.size, 2)
        action = "hold"
        if not self.position:  # 當下沒有任何持倉
            # 如果短期移動平均線高於長期移動平均線，則買入股票
            if self.short_sma[0] > self.long_sma[0]:
                self.buy()
                action = "buy signal"
        else:  # 當下已經有倉位
            # 如果短期移動平均線低於長期移動平均線，則賣出股票
            if self.short_sma[0] < self.long_sma[0]:
                self.order = self.sell()  # 賣出股票
                action = "sell signal"
        self.log(
            f"短均線：{short_val:.2f}，長均線：{long_val:.2f}，倉位：{pos_size}，動作：{action}"
        )

    def log(self, txt, dt=None):
        """記錄策略日誌的函數"""
        # 如果沒有指定日期，則預設為當前交易日日期
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        """訂單通知處理"""
        if order.status in [order.Completed]:
            executed_price = np.round(order.executed.price, 3)
            executed_comm = np.round(order.executed.comm, 3)
            
            if order.isbuy():
                self.log(
                    f"訂單完成：買入執行，價格：{executed_price}，手續費：{executed_comm}"
                )
            elif order.issell():
                self.log(
                    f"訂單完成：賣出執行，價格：{executed_price}，手續費：{executed_comm}"
                )


cerebro = bt.Cerebro()
cerebro.addstrategy(MovingAverageCrossStrategy)
asset = "00631L.TW"
raw = yf.download(asset, "2025-10-01", "2025-11-27", auto_adjust=True)
# yfinance 可能回傳 MultiIndex 欄位，扁平化並轉為小寫以符合 Backtrader 預期
if isinstance(raw.columns, pd.MultiIndex):
    raw.columns = raw.columns.get_level_values(0)
raw = raw.rename(columns=str.lower)
data = bt.feeds.PandasData(dataname=raw[["open", "high", "low", "close", "volume"]])
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.0015)
cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="SharpeRatio")
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="DrawDown")
cerebro.addsizer(bt.sizers.PercentSizer, percents=90)


results = cerebro.run()


print("夏普比率：", results[0].analyzers.SharpeRatio.get_analysis()["sharperatio"])
print("最大回撤：", results[0].analyzers.DrawDown.get_analysis()["max"]["drawdown"])

cerebro.plot()

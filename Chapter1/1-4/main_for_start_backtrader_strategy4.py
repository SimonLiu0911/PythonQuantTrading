"""範例策略四：移動平均交叉策略"""
import backtrader as bt
import numpy as np
import yfinance as yf

# Backtrader 內建常用的指標韓式使用範例
"""簡單移動平均(SMA)"""
# bt.indicators.SimpleMovingAverage(self.data.close.period=20)
"""指數移動平均(EMA)"""
# bt.indicators.ExponentialMovingAverage(self.data.close, period=20)

"""相對強弱指數(RSI)"""
# bt.indicators.RSI(self.data.close, period=14)

"""指數平滑異同移動平均(MACD)"""
# bt.indicators.MACD(self.data.close, period_me1=12, period_me=2, period_singl=9)

"""布林帶(Bollinger Bands)"""
# bt.indicators.BollingerBands(self.data.close, period=20, devfactor=2.0)

"""動量指標(Momentum)"""
# bt.indicators.Momentum(self.data.close, period=12)


class MovingAverageCrossStrategy(bt.Strategy):
    # 定義策略的參數：短期移動平均線週期和長期移動平均線週期
    params = (("short_period", 5), ("long_period", 20))
    def __init__(self):
        # 5日均線作為短期移動平均線
        self.short_sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.short_period)
        # 20日均線作為長期移動平均線
        self.long_sma = bt.indicators.SimpleMovingAverage(self.data.close, period=self.params.long_period)
        # 初始化訂單狀態，用來追蹤當前的訂單
        self.order = None
    def next(self):
        # 紀錄當日的均線與持倉狀態，方便觀察為何當天是否產生訊號
        short_val = float(self.short_sma[0])
        long_val = float(self.long_sma[0])
        pos_size = self.position.size
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
                self.log(f"訂單完成：買入執行，價格：{executed_price}，手續費：{executed_comm}")
            elif order.issell():
                self.log(f"訂單完成：賣出執行，價格：{executed_price}，手續費：{executed_comm}")

cerebro = bt.Cerebro()
cerebro.addstrategy(MovingAverageCrossStrategy)
asset = "00631L.TW"
data = bt.feeds.PandasData(
    dataname=yf.download(asset, "2025-01-01", "2025-11-24").droplevel("Ticker", axis=1)[
        ["Open", "High", "Low", "Close", "Volume"]
    ]
)
cerebro.adddata(data)
cerebro.broker.setcash(100000)
cerebro.broker.setcommission(commission=0.0015)
results = cerebro.run()
print(results)


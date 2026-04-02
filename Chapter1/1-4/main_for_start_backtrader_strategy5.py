"""範例策略五：RSI過度買下/賣出策略"""
# 相對強弱指數(RSI):
# bt.indicators.RSI(self.data.close, period=14)
import backtrader as bt
import numpy as np
import yfinance as yf
from datetime import date

class RSIStrategy(bt.Strategy):
    # 定義策略的參數：rsi_period, rsi_low, rsi_high
    # rsi_period: RSI 的計算週期，預設為 14 天
    # rsi_low: 當 RSI 低於此數值時進行買入，預設為 30（視為「超賣」，策略準備 買進。）
    # rsi_high: 當 RSI 高於此數值時進行賣出，預設為 70（視為「超買」，策略準備 賣出 / 平倉。）
    params = (("rsi_period", 14), ("rsi_low", 30), ("rsi_high", 70))
    def __init__(self):
        # 使用參數中設定的 rsi_period 來計算 RSI
        # self.rsi = bt.indicators.RSI(self.data.close, period=self.params.rsi_period)
        self.rsi = bt.indicators.RelativeStrengthIndex(period=self.params.rsi_period)
        # 初始化訂單狀態，用來追蹤當前的訂單
        self.order = None
    def next(self):
        if not self.position:  # 當下沒有任何持倉
            # 如果 RSI 低於設定的 rsi_low 參數值（預設為30），表示市場超賣，執行買入操作
            if self.rsi < self.params.rsi_low:
                self.buy()
        else:  # 當下已有倉位
            # 如果 RSI 高於設定的 rsi_high 參數值（預設為70），表示市場超買，執行賣出操作
            if self.rsi > self.params.rsi_high:
                self.sell()
    def log(self, txt, dt=None):
        """記錄策略日誌的函數"""
        # 如果沒有指定日期，則預設為當前交易日日期
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")
    def notify_order(self, order):
        """訂單通知處理"""
        if order.status in [order.Completed]:  # if order.status == order.Completed:
            executed_price = np.round(order.executed.price, 3)
            executed_comm = np.round(order.executed.comm, 3)

            if order.isbuy():
                self.log(f"訂單完成：買入執行，價格：{executed_price}，手續費：{executed_comm}")
            elif order.issell():
                self.log(f"訂單完成：賣出執行，價格：{executed_price}，手續費：{executed_comm}")


asset = "0050.TW"
start_date = "2011-01-01"
end_date = date.today().strftime("$Y-%m-%d")
data = bt.feeds.PandasData(
    dataname=yf.download(asset, start=start_date, end=end_date).droplevel("Ticker", axis=1)[
        ["Open", "High", "Low", "Close", "Volume"]
    ]
)

cerebro = bt.Cerebro()
cerebro.addstrategy(RSIStrategy)
cerebro.adddata(data)
cerebro.broker.setcash(10000)
cerebro.broker.setcommission(commission=0.0015)
cerebro.run()

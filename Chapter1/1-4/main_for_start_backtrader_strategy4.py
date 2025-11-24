"""範例策略四：移動平均交叉策略"""
import backtrader as bt
import numpy as np

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
        if not self.position:  # 當下沒有任何持倉
            # 如果短期移動平均線高於長期移動平均線，則買入股票
            if self.short_sma[0] > self.long_sma[0]:
                self.buy()
        else:  # 當下已經有倉位
            # 如果短期移動平均線低於長期移動平均線，則賣出股票
            if self.short_sma[0] < self.long_sma[0]:
                self.order = self.sell()  # 賣出股票
    def log(self, txt, dt=None):
        """記錄策略日誌的函數"""
        # 如果沒有指定日期，則預設為當前交易日日期
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")


# optimize
# class MovingAverageCrossStrategy(bt.Strategy):
#     # 定義策略的參數：短期移動平均線週期和長期移動平均線週期
#     params = (("short_period", 5), ("long_period", 20))

#     def __init__(self):
#         # 基本參數驗證：短期應小於長期
#         if self.params.short_period >= self.params.long_period:
#             raise ValueError("short_period 必須小於 long_period")
#         # 5日均線作為短期移動平均線
#         self.short_sma = bt.indicators.SimpleMovingAverage(
#             self.data.close, period=self.params.short_period
#         )
#         # 20日均線作為長期移動平均線
#         self.long_sma = bt.indicators.SimpleMovingAverage(
#             self.data.close, period=self.params.long_period
#         )
#         # 交叉指標：>0 為金叉，<0 為死叉
#         self.crossover = bt.indicators.CrossOver(self.short_sma, self.long_sma)
#         # 初始化訂單狀態，用來追蹤當前的訂單
#         self.order = None

#     def next(self):
#         # 若有掛單尚未處理，先等待
#         if self.order:
#             return
#         if not self.position:  # 當下沒有任何持倉
#             # 金叉買入
#             if self.crossover[0] > 0:
#                 self.order = self.buy()
#         else:  # 當下已經有倉位
#             # 死叉賣出
#             if self.crossover[0] < 0:
#                 self.order = self.sell()

#     def notify_order(self, order):
#         # 訂單完成後清除掛單狀態
#         if order.status in [order.Completed, order.Canceled, order.Rejected]:
#             self.order = None

#     def log(self, txt, dt=None):
#         """記錄策略日誌的函數"""
#         # 如果沒有指定日期，則預設為當前交易日日期
#         dt = dt or self.datas[0].datetime.date(0)
#         print(f"{dt.isoformat()} {txt}")

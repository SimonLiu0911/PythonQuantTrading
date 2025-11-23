import backtrader as bt
import yfinance as yf
import pandas as pd

# 1) 準備資料（用 yfinance 取 OHLCV）
df = yf.download("2330.TW", start="2022-01-01", end="2025-11-21", auto_adjust=True)

# Flatten MultiIndex columns (if present) and lowercase for Backtrader
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)
df = df.rename(columns=str.lower)

df.index = pd.to_datetime(df.index)
data = bt.feeds.PandasData(dataname=df)  # 欄位名已符合 Open/High/Low/Close/Volume


# 2) 定義策略：SMA 金叉做多、死叉平倉
class SmaCross(bt.Strategy):
    params = dict(pfast=10, pslow=30)

    def __init__(self):
        # SMA: Simple Moving Average, 把最近N根K的收盤價取平均
        sma_fast = bt.ind.SMA(self.data.close, period=self.p.pfast)
        sma_slow = bt.ind.SMA(self.data.close, period=self.p.pslow)
        self.crossover = bt.ind.CrossOver(sma_fast, sma_slow)

    def next(self):
        if not self.position and self.crossover > 0:
            self.buy()  # 金叉→做多（下根K開盤成交）
        elif self.position and self.crossover < 0:
            self.close()  # 死叉→平倉


# 3) 建立 Cerebro，引擎裝配
cerebro = bt.Cerebro()
cerebro.adddata(data, name="2330")
cerebro.addstrategy(SmaCross, pfast=10, pslow=30)
cerebro.broker.setcash(1000000)  # 初始資金
cerebro.broker.setcommission(commission=0.001)  # 單邊千分之一


# 4) 加入常用分析器
cerebro.addanalyzer(
    bt.analyzers.SharpeRatio, _name="sharpe", timeframe=bt.TimeFrame.Days
)
cerebro.addanalyzer(bt.analyzers.DrawDown, _name="dd")
cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")


# 5) 執行
res = cerebro.run()
strat = res[0]
print()
print("Final Value:", cerebro.broker.getvalue())
print("Sharpe     :", strat.analyzers.sharpe.get_analysis().get("sharperatio"))
print("Drawdown   :", strat.analyzers.dd.get_analysis()["max"]["drawdown"])

# 6) 視覺化（需 matplotlib）
# cerebro.plot(style='candlestick')

"""範例策略三：每月定期定額0050"""

import backtrader as bt
import numpy as np

"""夏普比率 Sharpe Ratio"""
# cerebro.addanalyzer(bt.analyzers.SharpeRatio)
# results = cerebro.run()
# strat = results[0]
# strat.analyzers.sharperatio.get_analysis()
# strat.analyzers.sharperatio.get_analysis()['sharperatio']

"""回撤 Drawdown"""
# cerebro.addanalyzer(bt.analyzers.DrawDown)
# results = cerebro.run()
# strat = results[0]
# strat.analyzers.drawdown.get_analysis()
# strat.analyzers.drawdown.get_analysis()['drawdown']

"""收益 Returns"""
# cerebro.addanalyzer(bt.analyzers.Returns)
# results = cerebro.run()
# strat = results[0]
# strat.analyzers.returns.get_analysis()

"""Pyfolio"""
# cerebro.addanalyzer(bt.analyzers.Pyfolio)
# results = cerebro.run()
# strat = results[0]
# strat.analyzers.pyfolio.get_analysis()

"""取得當前帳戶的現金餘額"""
# cerebro.broker.getcash()

"""取得當前帳戶的總額（包含現金和持倉的市值）"""
# cerebro.broker.getvalue()

"""取得持倉的價格"""
# cerebro.broker.getposition(data).price

"""取得持倉的數量"""
# cerebro.broker.getposition(data).size


class MonthlyInvestmentStrategy(bt.Strategy):
    # 定義策略的參數
    params = (
        ("cash_to_invest", 10000),  # 每月計劃投資的金額
        ("investment_day", 1),  # 每月的投資日（哪一天執行定期投資）
    )

    def __init__(self):
        # 確保投資日有設定
        if self.params.investment_day is None:
            raise ValueError("必須設定 investment_day (每月投資日)")
        # 初始化一個定時器，設置在每個月的指定投資日執行操作
        self.add_timer(
            when=bt.Timer.SESSION_START,  # 在指定交易日開始觸發
            monthdays=[self.params.investment_day],  # 每月的指定投資日
        )
        # 初始化訂單狀態為 None，用來追蹤當前的訂單
        self.order = None
    
    def log(self, txt, dt=None):
        """記錄策略日誌的函數"""
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        """訂單通知處理"""
        if order.status in [order.Completed]:
            # 取得成交價格
            executed_price = np.round(order.executed.price, 2)
            # 取得手續費
            executed_comm = np.round(order.executed.comm, 2)
            self.log(f"訂單完成：買入執行，價格：{executed_price}, 手續費：{executed_comm}")

    def notify_timer(self, timer, when, *args, **kwargs):
        """定時器觸發時執行的操作"""
        self.log("定投日，執行買入訂單")
        # 取當前帳戶可用的現金金額
        cash_available = self.broker.getcash()
        # 取得當前收盤價
        price = self.data.close[0]
        # 根據每月計劃投資的金額(self.params.cash_to_invest)和可用的現金
        # 計算可以買入的股票數量 size
        size = min(self.params.cash_to_invest, cash_available) // price
        if size > 0:
            # 如果計算出可以買的股票數量大於0，則執行買入訂單
            self.order = self.buy(size=size)
    # next 是在每個交易日都會被使用的方法，但這個範例中不做任何事，全部交由定時器控制交易
    def next(self):
        pass

data = bt.feeds.GenericCSVData(
    dataname="Chapter1/1-4/stock_data_examples.csv",
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1,
    dtformat=("%Y/%m/%d"),
    headers=True,
)

cerebro = bt.Cerebro()  # 初始化回測引擎
cerebro.adddata(data)  # 加載數據
cerebro.addstrategy(MonthlyInvestmentStrategy)  # 加載策略
cerebro.broker.setcash(100000)  # 設置初始資金
cerebro.broker.setcommission(commission=0.0015)  # 設置交易手續費
results = cerebro.run()  # 執行回測

# %%
"""範例策略三：每日定期定額0050"""

import os
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


class DailyInvestmentStrategy(bt.Strategy):
    # 定義策略的參數
    """
    params 放在類別層級才能被 Backtrader 掃描並允許外部透過 addstrategy 覆寫
    放 __init__ 只是普通實例屬性，框架不會當成參數處理，也無法從外部傳入覆蓋。

    """
    params = (
        ("cash_to_invest", 10000),  # 每日計劃投資的金額
    )

    def __init__(self):
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
        # 訂單處理完畢後清除掛單狀態
        if order.status in [order.Completed, order.Canceled, order.Rejected, order.Expired]:
            self.order = None

    def next(self):
        """每日定投：每個交易日開盤/收盤後依照設定金額買入"""
        if self.order:
            return  # 等待掛單完成
        cash_available = self.broker.getcash()
        price = self.data.close[0]
        size = min(self.params.cash_to_invest, cash_available) // price
        if size > 0:
            self.order = self.buy(size=size)
            self.log(f"每日定投買入 size={size}, 價格={np.round(price, 2)}")
current_folder = os.path.dirname(__file__)
data = bt.feeds.GenericCSVData(
    dataname=os.path.join(current_folder, "stock_data_examples.csv"),
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
cerebro.addstrategy(DailyInvestmentStrategy)  # 加載策略
cerebro.broker.setcash(100000)  # 設置初始資金
cerebro.broker.setcommission(commission=0.0015)  # 設置交易手續費
cerebro.run()  # 執行回測

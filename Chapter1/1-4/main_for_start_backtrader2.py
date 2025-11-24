"""範例策略一：印出教日當天和前一天的開盤價和收盤價"""

import backtrader as bt
import numpy as np

# 定義一個策略類別，印出交易日當天和前一天的開盤價和收盤價


class PrintDataStrategy(bt.Strategy):
    # next 方法會在每個時間點被執行
    def next(self):
        # self.datas[0] 代表第一個數據集（即第一隻股票）
        date = self.datas[0].datetime.date(0)  # 取得當前交易日的日期
        close = self.datas[0].close[0]  # 取得當前交易日的收盤價
        open = self.datas[0].open[0]  # 取得當前交易日的開盤價
        # len(self.datas[0]) 對應當前是第幾個交易日
        # 隨著每個交易日的進行，len(self.datas[0]) 會不斷增加
        # 每當 next() 方法被調用時，len(self.datas[0]) 會+1
        print(
            f"Day-{len(self.datas[0])}, "
            + f"Date: {date}, "
            + f"Close: {close}, "
            + f"Open: {open}, "
        )
        
        # 檢查數據集中是否有前一天的資料
        # 這個檢查是為了避免存取不存在的前一天資料
        if len(self.datas[0]) > 1:
            # 索引 [-1] 表示前一個時間點的數據
            # 取得前一個交易日的日期、收盤價和開盤價
            yesterday_date = self.datas[0].datetime.date(-1)
            yesterday_close = self.datas[0].close[-1]
            yesterday_open = self.datas[0].open[-1]
            print(
                f"Yesterday Date: {yesterday_date}, "
                + f"Close: {yesterday_close}, "
                + f"Open: {yesterday_open}"
            )
            print("----")

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

cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(PrintDataStrategy)
results = cerebro.run()
print(results)

print("回測結束")


"""範例策略二：收盤價小於開盤價時買入，收盤價高於開盤價時賣出"""
# 邏輯：當收盤價低於開盤價時買入一股，當收盤價高於開盤價時，賣出一股；如果收盤價等於開盤價，則不進行操作

"""
收盤價 < 開盤價 => 買入
收盤價 > 開盤價 => 賣出
收盤價 = 開盤價 => 無操作
"""

class OpenCloseStrategy(bt.Strategy):
    def __init__(self):
        self.order = None  # 初始化訂單狀態為 None，訂單狀態會隨著交易變更
        self.close = self.datas[0].close  # 取得第一個數據集的收盤價
        self.open = self.datas[0].open  # 取得第一個數據集的開盤價資料

    def log(self, txt, dt=None):
        """記錄策略日誌的函數"""
        # 如果沒有指定日期，則預設為當前交易日日期
        dt = dt or self.datas[0].datetime.date(0)
        print(f"{dt.isoformat()} {txt}")

    def notify_order(self, order):
        if order.status in [order.Submitted]:
            self.log("訂單已成交")
        if order.status in [order.Accepted]:
            self.log("訂單已接受")
        if order.status in [order.Canceled]:
            self.log("訂單已取消")
        if order.status in [order.Margin]:
            self.log("保證金不足")
        if order.status in [order.Rejected]:
            self.log("訂單被拒絕")
        if order.status in [order.Completed]:
            executed_price = np.round(order.executed.price, 3)
            executed_comm = np.round(order.executed.comm, 3)
            if order.isbuy():
                self.log(
                    "訂單已完成：買入執行,"
                    + f"價格：{executed_price}"
                    + f"手續費：{executed_comm}"
                )
            elif order.issell():
                self.log(
                    "訂單已完成：賣出執行,"
                    + f"價格：{executed_price}"
                    + f"手續費：{executed_comm}"
                )
                
    def notify_trade(self, trade):
        """交易通知處理"""
        if trade.isclosed:  # 交易結束時
            trade_pnl = np.round(trade.pnl, 2)
            trade_pnlcomm = np.round(trade.pnlcomm, 2)
            self.log(f"考慮手續費利潤：{trade_pnlcomm}")
            self.log(f"不考慮手續費利潤：{trade_pnl}")

    def next(self):
        today_open = np.round(self.open[0], 2)
        today_close = np.round(self.close[0], 2)
        self.log(f"當前收盤價：{today_close}, 當前開盤價：{today_open}")
        if self.close[0] < self.open[0]:
            # 如果收盤價小於開盤價，表示當日收黑，則執行買入操作
            self.buy(size=1)  # 買入一股
            self.log("收盤價小於開盤價，執行買入")
        elif self.close[0] > self.open[0]:
            # 如果收盤價大於開盤價，表示當日收紅，則執行賣出操作
            self.sell(size=1)  # 賣出一股
            self.log("收盤價大於開盤價，執行賣出")

# 加載數據
data = bt.feeds.GenericCSVData(
    dataname="Chapter1/1-4/stock_data_examples.csv",  # 指定 CSV 檔案的路徑
    datetime=0,  # 設定 datetime 欄位的位置
    open=1,  # 設定 open 欄位的位置
    high=2,  # 設定 high 欄位的位置
    low=3,  # 設定 low 欄位的位置
    close=4,  # 設定 close 欄位的位置
    volume=5,  # 設定 volume 欄位的位置
    openinterest=-1,  # 設定 open interest 欄位，這裡不使用所以設為-1
    dtformat=("%Y/%m/%d"),  # 指定日期格式，原始資料為 2020/1/2
)

cerebro = bt.Cerebro()  # 初始化回測引擎
cerebro.adddata(data)  # 加載數據
cerebro.addstrategy(OpenCloseStrategy)  # 加載策略
cerebro.broker.setcash(100000)  # 設置初始資金
cerebro.broker.setcommission(commission=0.0015)  # 設置交易手續費
results = cerebro.run()  # 執行回測


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



"""範例策略三：每月定期定額0050"""
class MonthlyInvestmentStrategy(bt.Strategy):
    # 定義策略的參數
    params = (
        ("cash_to_invest", None),  # 每月計劃投資的金額
        ("investment_day", None),  # 每月的投資日（哪一天執行定期投資）
    )

    def __init__(self):
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
            self.order = self.but(size=size)
    # next 是在每個交易日都會被使用的方法，但這個範例中不做任何事，全部交由定時器控制交易
    def next(self):
        pass
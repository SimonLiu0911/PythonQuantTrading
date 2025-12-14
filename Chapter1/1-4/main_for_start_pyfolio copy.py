# %%
import backtrader as bt
import pyfolio as pf
import yfinance as yf
from datetime import date

# 設定要取得的數據區間：2015/1/1 ~ today
start_date = "2015-01-01"
end_date = date.today().strftime("%Y-%m-%d")

data = bt.feeds.PandasData(
    dataname=yf.download(
        "0050.TW",
        start_date,
        end_date,
        auto_adjust=False,  # keep raw prices to avoid yfinance auto-adjust warning
    ).droplevel("Ticker", axis=1)
)

# 定義每月定期定額策略
class MonthlyInvestmentStrategy(bt.Strategy):
    params = (
        ("cash_to_invest", None),
        ("investment_day", None),
    )

    def __init__(self):
        self.add_timer(
            when=bt.Timer.SESSION_START,
            monthdays=[self.params.investment_day],
        )
        self.order = None

    def notify_timer(self, timer, when, *args, **kwargs):
        """定時器觸發時執行操作"""
        cash_available = self.broker.getcash()
        price = self.data.close[0]
        size = min(self.params.cash_to_invest, cash_available) // price
        if size > 0:
            self.order = self.buy(size=size)

    def next(self):
        pass


cerebro = bt.Cerebro()
cerebro.adddata(data)
cerebro.addstrategy(
    MonthlyInvestmentStrategy,
    cash_to_invest=10000,
    investment_day=1,
)

cerebro.broker.setcash(9 * 12 * 10000)  # 設定初始資金
cerebro.broker.setcommission(commission=0.0015)  # 設定交易手續費
# 添加 PyFolio 分析器，用於在回測後進行分析
cerebro.addanalyzer(bt.analyzers.PyFolio, _name="pyfolio")
results = cerebro.run()
strat = results[0]  # 取得第一個策略的結果
# 從策略中心取得 PyFolio 分析器，用來進行投資組合績效分析
pyfoliozer = strat.analyzers.getbyname("pyfolio")
# 取得回測結果的四個主要部分，用來進一步分析投資組合的表現
# returns: 投資組合的收益率數據序列（例如每日收益率）
# positions: 投資組合在不同時間點的持倉情況（例如每個時間點持有多少股票）
# transactions: 投資組合的交易紀錄，詳細記錄買入和賣出的每筆交易
# grass_lev: 投資組合的總槓桿率
returns, positions, transactions, gross_lev = pyfoliozer.get_pf_items()

# 使用 PyFolio 生成完整的投資報告，涵蓋收益、持倉、交易等方面的分析
pf.create_full_tear_sheet(returns, positions, transactions)

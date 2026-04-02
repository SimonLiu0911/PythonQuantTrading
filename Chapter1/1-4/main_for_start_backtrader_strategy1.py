# %%
"""範例策略一：印出交易日當天和前一天的開盤價和收盤價"""

"""
此策略的功能是每天印出「當天和前一天的開盤價與收盤價」
"""

import backtrader as bt
from pathlib import Path

# 定義一個策略類別，印出交易日當天和前一天的開盤價和收盤價
class PrintDataStrategy(bt.Strategy):
    # # 初始化方法，在策略開始時執行，用於設置指標，包含定義策略會使用到的參數
    # def __init__(self):
    #     d=self.datas[0]
    #     print(
    #         d.datetime.date(0), # 2020-01-08
    #         d.open[0], # 74.29
    #         d.high[0], # 76.11
    #         d.low[0], # 74.29
    #         d.close[0], # 75.8
    #         d.volume[0], # 132079200.0
    #     )
    # # next 方法會在每個時間點被執行
    def next(self):
        # self.datas[0] 代表第一個數據集（即第一支股票）
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
    dataname=str(Path(__file__).parent / "stock_data_examples.csv"),
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=5,
    openinterest=-1,
    dtformat=("%Y/%m/%d"),
    headers=True, # 第一行是標題列，不算資料，讀檔時會跳過
)

cerebro = bt.Cerebro()  # 初始化回測引擎
cerebro.adddata(data)  # 加載數據
cerebro.addstrategy(PrintDataStrategy)  # 加載策略
results = cerebro.run()
# print(results)

print("回測結束")

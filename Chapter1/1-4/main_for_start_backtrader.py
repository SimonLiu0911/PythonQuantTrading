"""
Backtrader 預設的資料結構包涵：
datetime(日期)
open(開盤價)
high(最高價)
low(最低價)
close(收盤價)
volume(成交量)
openinterest(未平倉合約數)
等欄位。
若欄位不存在，就要將其設置為-1。
"""

import os
import backtrader as bt
import pandas as pd

# cerebro = bt.Cerebro()
# cerebro.adddata(data)
# cerebro.addstrategy(strategy)
# cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name="sharpe")
# cerebro.broker.setcash(100000.0)
# cerebro.broker.setcommission(commission=0.001)
# results = cerebro.run()

"""加載回測數據一：從 CSV 下載資料"""
# csv_path = os.path.join(os.path.dirname(__file__), "stock_data_examples.csv")

# data = bt.feeds.GenericCSVData(
#     dataname=csv_path,  # 指定 CSV 檔案的路徑
#     datetime=0,  # 設定 datetime 欄位的位置
#     open=1,  # 設定 open 欄位的位置
#     high=2,  # 設定 high 欄位的位置
#     low=3,  # 設定 low 欄位的位置
#     close=4,  # 設定 close 欄位的位置
#     volume=5,  # 設定 volume 欄位的位置
#     openinterest=-1,  # 設定 open interest 欄位，這裡設為-1 表示沒有此欄位
#     dtformat=("%Y/%m/%d"),  # 指定日期格式
#     headers=True,  # 指定 CSV 檔案是否包含標題列
# )

# cerebro = bt.Cerebro()  # 初始化 Cerebro 引擎
# cerebro.adddata(data)  # 將數據添加到 Cerebro 中
# results = cerebro.run()  # 執行回測


"""加載回測數據二：從 yfinance 下載資料"""
# # 使用 PandasData 方法載入 yfinance 股票數據
# import yfinance as yf

# data_2330 = bt.feeds.PandasData(
#     dataname=yf.download("2330.TW", start="2020-01-01", end="2023-01-01").droplevel(
#         "Ticker", axis=1
#     )[
#         ["Open", "High", "Low", "Close", "Volume"]
#     ]  # 下載 2330.TW 的股票在指定日期範圍內的數據
# )

# data_2317 = bt.feeds.PandasData(
#     dataname=yf.download("2317.TW", "2020-01-01", "2023-01-01").droplevel(
#         "Ticker", axis=1
#     )[
#         ["Open", "High", "Low", "Close", "Volume"]
#     ]  # 下載 2317.TW 的股票在指定日期範圍內的數據
# )

# cerebro = bt.Cerebro()  # 初始化 Cerebro 引擎
# cerebro.adddata(data_2330)  # 將 2330.TW 數據添加到 Cerebro 中
# cerebro.adddata(data_2317)  # 將 2317.TW 數據添加到 Cerebro 中
# results = cerebro.run()  # 執行回測

# print(results)


"""加載回測數據三：自訂資料格式"""
# 生成一個自訂的資料集，包含日期、價格和自訂義因子
data = [
    ["2023-01-02", 74.06, 75.15, 73.80, 75.09, 135480400, 1, 11],
    ["2023-01-03", 74.29, 75.14, 73.13, 74.36, 146322800, 2, 12],
    ["2023-01-06", 74.29, 76.03, 74.13, 75.93, 140843800, 3, 13],
    ["2023-01-07", 76.89, 77.61, 76.55, 77.34, 125911600, 4, 14],
    ["2023-01-08", 77.52, 78.75, 77.06, 78.52, 172014600, 5, 15],
]
data = pd.DataFrame(data)  # 將資料轉換為 DataFrame 格式
data.columns = [  # 設定 DataFrame 的欄位名稱
    "datetime",
    "Open",
    "High",
    "Low",
    "Close",
    "Volume",
    "factor1",
    "factor2",
]
data["datetime"] = pd.to_datetime(
    data["datetime"]
)  # 將 datetime 欄位轉換為日期時間格式


class PandasDataWithFactor(bt.feeds.PandasData):
    params = (
        ("datetime", "datetime"),  # 對應 datetime 欄位
        ("open", "Open"),  # 對應 open 欄位
        ("high", "High"),  # 對應 high 欄位
        ("low", "Low"),  # 對應 low 欄位
        ("close", "Close"),  # 對應 close 欄位
        ("volume", "Volume"),  # 對應 volume 欄位
        ("factor1", "factor1"),  # 定義自訂因子 factor1，對應第 6 欄位
        ("factor2", "factor2"),  # 定義自訂因子 factor2，對應第 7 欄位
        ("openinterest", -1),  # 不使用 open interest，設為 -1
    )


data = PandasDataWithFactor(dataname=data)  # 初始化 PandasDataWithFactor
cerebro = bt.Cerebro()  # 初始化 Cerebro 引擎
cerebro.adddata(data)  # 將數據添加到 Cerebro 中
results = cerebro.run()  # 執行回測






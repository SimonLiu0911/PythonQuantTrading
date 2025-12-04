import os
import sys
from pathlib import Path
import backtrader as bt
import pandas as pd
import pyfolio as pf

# project_root = Path(__file__).resolve().parents[2]
# if str(project_root) not in sys.path:
#     sys.path.append(str(project_root))

utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(utils_folder_path)

from Chapter1 import utils as chap1_utils # 這是讀取 Chapter1 下面的 utils

chap1_utils.finlab_login()

analysis_period_start_date = "2021-03-16"
analysis_period_end_date = "2021-05-15"

top_N_stocks = chap1_utils.get_top_stocks_by_market_value(
    excluded_industry=[
        "金融業",
        "金融保險業",
        "存托憑證",
        "建材營造",
    ],
    pre_list_date="2017-01-03",
)

# 取得指定股票代碼列表在給定日期範圍內的每日 OHLCV 數據(get_daily_price_and_volume_data)
all_stock_data = chap1_utils.get_daily_OHLCV_data(
    stock_symbols=top_N_stocks,
    start_date=analysis_period_start_date,
    end_date=analysis_period_end_date,
)
print(all_stock_data)
all_stock_data["datetime"] = all_stock_data["datetime"].astype(str)
all_stock_data["asset"] = all_stock_data["asset"].astype(str)
# 指定各個季度下要使用來排序的因子
# name 對應的是每個季度的因子名稱
# corr 對應的是因子值與未來收益的關係（根據單因子 Alphalens 分析結果）
select_rank_factor_dict = {
    "2017-Q1": {"name": "稅後淨利成長率", "corr": True},
    "2017-Q2": {"name": "稅後淨利成長率", "corr": True},
    "2017-Q3": {"name": "稅後淨利成長率", "corr": True},
    "2017-Q4": {"name": "稅後淨利成長率", "corr": True},
    "2018-Q1": {"name": "稅前淨利成長率", "corr": True},
    "2018-Q2": {"name": "稅前淨利成長率", "corr": True},
    "2018-Q3": {"name": "稅前淨利成長率", "corr": True},
    "2018-Q4": {"name": "稅前淨利成長率", "corr": True},
    "2019-Q1": {"name": "稅後淨利成長率", "corr": True},
    "2019-Q2": {"name": "稅後淨利成長率", "corr": True},
    "2019-Q3": {"name": "稅後淨利成長率", "corr": True},
    "2019-Q4": {"name": "稅後淨利成長率", "corr": True},
    "2020-Q1": {"name": "稅前淨利成長率", "corr": True},
    "2020-Q2": {"name": "稅前淨利成長率", "corr": True},
    "2020-Q3": {"name": "稅前淨利成長率", "corr": True},
    "2020-Q4": {"name": "稅前淨利成長率", "corr": True},
}
# 準備因子數據，將個季度的因子數據進行排序。
all_factor_data = pd.DataFrame()

print(11111, all_factor_data)
print(22222, all_stock_data)
for quarter, factor in select_rank_factor_dict.items():
    # 將季度字串轉換為起始和結束日期
    start_date, end_date = chap1_utils.convert_quarter_to_dates(quarter)
    # 生成該季度的交易日範圍
    trading_days = pd.date_range(start=start_date, end=end_date)
    # 取得因子數據，並按股票代碼和日期進行排序與填補
    quarter_factor_data = (
        chap1_utils.get_factor_data(
            stock_symbols=top_N_stocks,
            factor_name=factor["name"],
            trading_days=list(trading_days),
        )
        .reset_index()
        .assign(factor_name=factor["name"])
        .sort_values(by=["asset", "datetime"])
        .groupby("asset", group_keys=False)
        .apply(lambda group: group.ffill())
        .dropna()
    )
    # 根據因子值進行股票排序：由小到大(positive_corr=True) or 由大到小(positive_corr=False)
    quarter_factor_data = chap1_utils.rank_stocks_by_factor(
        factor_df=quarter_factor_data,
        positive_corr=factor["corr"],  # 根據因子相關性決定的排序方向
        rank_column="value",  # 用來排序的欄位名稱
        rank_result_column="rank",  # 儲存排序結果的欄位名稱
    ).drop(columns=["value"])
    # 合併該季度的因子數據
    all_factor_data = pd.concat([all_factor_data, quarter_factor_data])
# 重設索引並將日期與股票代碼轉換為字串格式
all_factor_data = all_factor_data.reset_index(drop=True)
all_factor_data["datetime"] = all_factor_data["datetime"].astype(str)
all_factor_data["asset"] = all_factor_data["asset"].astype(str)
# 將因子數據與股價數據進行合併
all_stock_and_all_factor_data = pd.merge(
    all_stock_data, all_factor_data, on=["datetime", "asset"], how="outer"
)
# 站股票代碼和日期排序並填補遺失值
all_stock_and_all_factor_data = (
    all_stock_and_all_factor_data.sort_values(by=["asset", "datetime"])
    .groupby("asset", group_keys=False)
    .apply(lambda group: group.ffill())
    .reset_index(drop=True)
)
# 定義回測資料格式，新增排名資料
class PanadasDataWithRank(bt.feeds.PandasData):
    params = (
        ("datetime", "datetime"),  # 日期欄位
        ("open", "Open"),  # 開盤價欄位
        ("high", "High"),  # 最高價欄位
        ("low", "Low"),  # 最低價欄位
        ("close", "Close"),  # 收盤價欄位
        ("volume", "Volume"),  # 成交量欄位
        ("rank", "rank"),  # 排名欄位
        ("openinterest", -1),  # 持倉量欄位（不使用）
    )
    # 新增因子排名這條數據線
    lines = ("rank",)
# 定義策略：根據因子排名買入和賣出股票
class FactorRankStrategy(bt.Strategy):
    pass # 請參考前面內容
    # ////
    # params = dict(buy_n=20, sell_n=20, each_cash=100000)

    # def __init__(self):
    #     self.last_rebalance = None  # 上次進行調倉的日期(None代表未調倉)

    # def next(self):
    #     current_date = self.datas[0].datetime.date(0)
    #     # 每月第一次交易日才重新調倉，避免每天重複下單
    #     if self.last_rebalance and (
    #         self.last_rebalance.year == current_date.year
    #         and self.last_rebalance.month == current_date.month
    #     ):
    #         return
        
    #     self.last_rebalance = current_date

    #     ranked = []
    #     for data in self.datas:
    #         rank = data.rank[0]
    #         if pd.isna(rank):
    #             continue
    #         ranked.append((rank, data))
    #     if not ranked:
    #         return
    #     ranked.sort(key=lambda x: x[0])  # rank 值愈小代表排名愈前面

    #     top_to_hold = {d._name for _, d in ranked[: self.p.buy_n]}

    #     # 先賣出：持有但不在前 buy_n，且位於最末的 sell_n 名
    #     held_with_rank = [
    #         (data.rank[0], data)
    #         for data in self.datas
    #         if self.getposition(data).size != 0 and not pd.isna(data.rank[0])
    #     ]
    #     held_with_rank.sort(key=lambda x: x[0], reverse=True)  # 排名越大越差
    #     for rank, data in held_with_rank[: self.p.sell_n]:
    #         if data._name not in top_to_hold:
    #             self.close(data=data)

    #     # 再買入：補齊前 buy_n 名中尚未持有的股票
    #     for _, data in ranked[: self.p.buy_n]:
    #         if self.getposition(data).size != 0:
    #             continue
    #         price = data.close[0]
    #         if price <= 0:
    #             continue
    #         size = int(self.p.each_cash / price)
    #         if size <= 0:
    #             continue
    #         self.buy(data=data, size=size)
    # ////

# 設定回測引擎
cerebro = bt.Cerebro()
# 加入交易策略 FactorRankStrategy，設定策略參數：
# buy_n: 每次要買入的股票數量（20檔）
# sell_n: 每次要賣出的股票數量（20檔）
# each_cash: 每檔股票的交易金額，這裡是總資金的90%除以40檔股票，確保每檔股票有足夠資金配置
cerebro.addstrategy(
    FactorRankStrategy, buy_n=20, sell_n=20, each_cash=2000_0000 * 0.9 / 40
)
# 依序加入每檔股票的數據到回測引擎中
stock_list = list(set(all_stock_and_all_factor_data["asset"]))
for stock in stock_list:
    data = all_stock_and_all_factor_data[all_stock_and_all_factor_data["asset"] == stock]
    data = data.drop(columns=["asset", "factor_name"])  # 移除不必要欄位
    data["datetime"] = pd.to_datetime(data["datetime"])  # 日期欄位轉為 datetime 格式
    data = data.dropna().sort_values(by=["datetime"]).reset_index(drop=True)
    if data.empty:
        # 無資料的股票不加入，避免 backtrader 在分析器階段索引越界
        continue
    data = PanadasDataWithRank(dataname=data)  # 使用自訂的數據格式 PanadasDataWithRank
    cerebro.adddata(data, name=stock)  # 加入數據到回測引擎

# 設定初始資金為 200 萬元
cerebro.broker.set_cash(200_0000)
# 設定每筆交易的手續費為 0.1%
cerebro.broker.setcommission(commission=0.001)
# 加入 PyFolio 分析器，用於生成投資組合的性能分析報告
cerebro.addanalyzer(bt.analyzers.PyFolio)
# 運行策略
results = cerebro.run()
# 取得策略結果並生成投資組合分析報告
strat = results[0]  # 取得回測結果中的第一個策略
pyfoliozer = strat.analyzers.getbyname("pyfolio")
(
    returns,
    positions,
    transactions,
    gross_lev,
) = pyfoliozer.get_pf_items()
# 使用 PyFolio 生成完整的投資組合表現分析報告
pf.create_full_tear_sheet(returns)

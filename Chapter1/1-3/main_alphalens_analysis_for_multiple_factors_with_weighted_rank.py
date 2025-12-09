# %%
import os, sys
from itertools import combinations
from alphalens.tears import create_full_tear_sheet
from alphalens.utils import get_clean_factor_and_forward_returns

utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(utils_folder_path)

from Chapter1 import utils as chap1_utils

chap1_utils.finlab_login()

# 涵蓋 2017 第一季到 2020 第四季的財報數據
analysis_period_start_date = "2017-05-16"
analysis_period_end_date = "2021-05-15"

top_N_stocks = chap1_utils.get_top_stocks_by_market_value(
    excluded_industry=[
        "金融業",
        "金融保險單",
        "存托憑證",
        "建材營造",
    ],
    pre_list_date="2017-01-03",
)
# 獲取指定股票代碼列表在給定日期範圍內的每日收盤價資料。
# 對應到財報資料時間 2017-Q1~2020-Q4
close_price_data = chap1_utils.get_daily_close_prices_data(
    stock_symbols=top_N_stocks,
    start_date=analysis_period_start_date,
    end_date=analysis_period_end_date,
)
# 列舉和收益呈正相關的因子（根據先前單因子分析結果）
pos_corr_factors = [
    "營業利益",
    "歸屬母公司淨利",
    "ROE稅後",
    "營業毛利成長率",
    "營業利益成長率",
    "稅前淨利成長率",
    "稅後淨利成長率",
]
# 從 FinLab 取得多個因子資料，並將這些資料儲存在 factors_data_dict 字典中，字典的鍵是因子名稱，值是對應的因子資料。
factors_data_dict = {}
for factor in pos_corr_factors:
    factor_data = (
        chap1_utils.get_factor_data(
            stock_symbols=top_N_stocks,
            factor_name=factor,
            trading_days=list(close_price_data.index),
        )
        .reset_index()
        .assign(factor_name=factor)
    )
    factors_data_dict[factor] = factor_data
# 根據各個因子（欄位：value）對股票進行排序，排序後的結果存放在 ranked_factors_data_dict 字典中，字典的鍵是因子名稱，值為排名結果。
rank_factors_data_dict = {}
for factor in factors_data_dict:
    rank_factors_data_dict[factor] = chap1_utils.rank_stocks_by_factor(
        factor_df=factors_data_dict[factor],
        positive_corr=True,
        rank_column="value",
        rank_result_column="rank",
    )

# 根據多個因子的排名和對應的權重，計算加權排名後．再依據加權排名結果將股票進行排序
pos_corr_factor_pair = list(combinations(pos_corr_factors, 5))
print(f"總計有 {len(pos_corr_factors)} 組五因子組合")

# combined_df_dict 用來儲存每個五因子組合的排續結果。
combined_df_dict = {}
for pair in pos_corr_factor_pair:
    combined_df_dict[pair] = chap1_utils.calculate_weighted_rank(
        ranked_dfs=[
            rank_factors_data_dict[pair[0]],
            rank_factors_data_dict[pair[1]],
            rank_factors_data_dict[pair[2]],
            rank_factors_data_dict[pair[3]],
            rank_factors_data_dict[pair[4]],
        ],
        weights=[0.2, 0.2, 0.2, 0.2, 0.2], # 等權重
        positive_corr=True,
        rank_column="rank",
    ).set_index(['datetime', 'asset'])

# 使用 Alphalens 進行因子分析
for pair in combined_df_dict:
    print(f"pair: {pair}")
    alphalens_factor_data = get_clean_factor_and_forward_returns(
        factor=combined_df_dict[pair].squeeze(),
        prices=close_price_data,
        periods=(1,),
    )
    create_full_tear_sheet(alphalens_factor_data)
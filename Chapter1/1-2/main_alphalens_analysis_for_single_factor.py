# 載入需要的套件
import json, os, sys
from alphalens.tears import create_full_tear_sheet
from alphalens.utils import get_clean_factor_and_forward_returns

# get_clean_factor_and_forward_returns: 可以根據 period 參數來設置分析的時間範圍

utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(utils_folder_path)
# 載入 Chapter1 資料夾中的 utils.py 模組，並命名為 chap1_utils
from Chapter1 import utils as chap1_utils  # 這是讀取 Chapter1 下面的 utils

# 使用 FinLab API token 登入 FinLab 平台，取得資料訪問權限
chap1_utils.finlab_login()

analysis_period_start_date = "2017-05-16"
analysis_period_end_date = "2021-05-15"

"""排除指定產業（金融業、金融保險業、存托憑證、建材營造）的股票，並排除上市日期晚於 2017-01-03 的股票"""
top_N_stocks = chap1_utils.get_top_stocks_by_market_value(
    excluded_industry=[
        "金融業",
        "金融保險單",
        "存托憑證",
        "建材營造",
    ],
    pre_list_date="2017-01-03",
)
# print(f"列出市值前 10 大的股票代號：{ top_N_stocks[:10] }")
# print(f"列出市值前 10 大的股票代號：{ top_N_stocks }")
# print(f"股票數量：{len(top_N_stocks)}")  # 798

"""獲取指定股票代碼列表在給定日期範圍內的每日收盤價資料。"""
close_price_data = chap1_utils.get_daily_close_prices_data(
    stock_symbols=top_N_stocks,
    start_date=analysis_period_start_date,
    end_date=analysis_period_end_date,
)
close_price_data.head() # 直接 close_price_data 是一樣的意思，因為head()裡面沒放參數，所以是全取
# print(f"股票代碼（欄位名稱）：{close_price_data.columns}")
# print(f"日期（索引）：{close_price_data.index}")

"""針對市值前 300 大的股票，獲取指定因子（營業利益）的資料，並根據每日的交易日將因子資料擴展成日頻資料（時間間隔是「一天一次」的資料）。"""
factor_data = chap1_utils.get_factor_data(
    stock_symbols=top_N_stocks,
    factor_name="營業利益",
    trading_days=sorted(list(close_price_data.index)),
)
factor_data = factor_data.dropna()
factor_data.head()
# print(f"列出欄位名稱{factor_data.columns}")
# print(f"列出索引名稱（日期，股票代碼）：{factor_data.index}")

# # 使用 Alphalens 將因子數據與收益數據結合。
# # 生成 Alphalens 分析所需的數據表格。
# alphalens_factor_data = get_clean_factor_and_forward_returns(
#     factor=factor_data.squeeze(), prices=close_price_data, quantiles=5
# )
# """
# 「Dropped 1% entries from factor data: 1.0% in forward returns computation. max_loss is 35.0%, not exceeded: OK!」
# Dropped 1% entries from factor data: 表示處理因子數據時，有1.0%的數據被丟棄了。通常是因為因子的數據或價格有缺失或不完整的情況，導致這部分數據無法使用，因而被剔除。
# 1.0% in forward returns computation: 說明這 1.0% 的數據是在計算未來收益(forward returns)的過程中被丟棄的。這些數據可能缺失對應的未來收益數據，通常是因為某些日期的價格數據有問題或缺失。
# max_loss is 35.0%, not exceeded: OK!: 這表示設置的 max_loss 參數值是 35.0%，即允許最多丟棄 35% 的數據。由於實際丟棄的數據比例沒有超過這個設定值，因此顯示「OK!」，說明數據處理過程在可接受範圍內並且是正常的
# """

# # 使用 Alphalens 生成完整的因子分析圖表報告
# create_full_tear_sheet(alphalens_factor_data)

# ### Part 2 ###
# with open(
#     utils_folder_path + "/Chapter1/1-2/factors_list.json",
#     "r",
#     encoding="utf-8",
# ) as file:
#     result = json.load(file)

# # 從載入的 JSON 文件中提取因子名稱列表，準備進行分析。
# fundamental_features_list = result["fundamental_features"]
# print(f"將要分析的因子清單：{fundamental_features_list}")
# print(f"總計有{len(fundamental_features_list)}個因子")
# # 使用 for 迴圈從 FinLab 獲取多個因子的資料。
# # 將所有因子資料儲存到字典 factors_data_dict 中，鍵為因子名稱，值為對應的因子資料。
# factors_data_dict = {}
# for factor in fundamental_features_list:
#     factor_data = chap1_utils.get_factor_data(
#         stock_symbols=top_N_stocks,
#         factor_name=factor,
#         trading_days=list(close_price_data.index),
#     )
#     factors_data_dict[factor] = factor_data
# # 使用 Alphalens 進行因子分析
# for fsctor in fundamental_features_list[41:]:
#     print(f"factor: {factor}")
#     alphalens_factor_data = get_clean_factor_and_forward_returns(
#         factor=factors_data_dict[factor].squeeze(),
#         prices=close_price_data,
#         periods=(1,),
#     )
# create_full_tear_sheet(alphalens_factor_data)

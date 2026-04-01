import os, sys
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from alphalens.tears import create_full_tear_sheet
from alphalens.utils import get_clean_factor_and_forward_returns

utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(utils_folder_path)
from Chapter1 import utils as chap1_utils

chap1_utils.finlab_login()

analysis_period_start_date = "2017-05-16"
analysis_period_end_date = "2021-05-15"

top_N_stocks = chap1_utils.get_top_stocks_by_market_value(
    excluded_industry=[
        "金融業",
        "金融保險單",
        "存托憑證",
        "建材營造",
    ],
    pre_list_date="2016-01-01",
)
close_price_data = chap1_utils.get_daily_close_prices_data(
    stock_symbols=top_N_stocks,
    start_date=analysis_period_start_date,
    end_date=analysis_period_end_date,
)

# 要進行主成份分析的因子列表
all_factors_list = [
    "ROE稅後",
    "應收帳款週轉率",
    "歸屬母公司淨利",
    "營業利益",
    "營業利益成長率",
    "營運現金流",
    "稅前淨利成長率",
    "稅後淨利成長率",
    "經常稅後淨利",
]
# 取得 FinLab 多個因子資料
# 將多個因子資料整合(concat)成一個資料集
factors_data_dict = {}
for factor in all_factors_list:
    # factor_data = chap1_utils.get_factor_data(
    #     stock_symbols=top_N_stocks,
    #     factor_name=factor,
    #     trading_days=list(close_price_data.index),
    # )
    # factor_data = factor_data.reset_index()
    # factor_data = factor_data.assign(factor_name=factor)

    # 下方優化上方程式碼，直接在一行內完成資料的取得、重置索引和新增因子名稱欄位的操作
    factor_data = (
        chap1_utils.get_factor_data(
            stock_symbols=top_N_stocks,
            factor_name=factor,
            trading_days=list(close_price_data.index),
        )
        .reset_index()
        .assign(factor_name=factor)
        # .dropna()
    )
    factors_data_dict[factor] = factor_data
    print(f"已取得因子 {factor} 的資料，資料的前 5 行：\n{factor_data.head()}\n")

# 將所有因子資料合併成一個 DataFrame
concat_factors_data = pd.concat(factors_data_dict.values(), ignore_index=True)
# 將資料格式轉換為索引是 datetime 和 asset，欄位名稱是因子名稱
# pivot_table 用於將長格式的資料展開轉換為寬格式(P1-101)
concat_factors_data = concat_factors_data.pivot_table(
    index=["datetime", "asset"],
    columns="factor_name",
    values="value",
)
# 處理異常值和遺失值，將無窮大的值替換為 NaN，並透過向前填補的方法填補遺失值
concat_factors_data.replace([np.inf, -np.inf], np.nan, inplace=True)

# 進行主成份分析。
# 首先對因子數據進行標準化處理，以保證每個因子的尺度相同。
# 這個標準化過程會將每個因子數據的平均值調整為0，標準差調整為1。
scaler = StandardScaler()
# 將 concat_factors_data.dropna().values 裡的每個欄位都做標準化(確保每個變數再降維過程中具有享童的尺度)
scale_concat_factors_data = scaler.fit_transform(concat_factors_data.dropna().values)
# 設置要提取的主成份數量為 8，這裡選擇了比財報因子數少一個的主成份數量
pac_components_num = len(all_factors_list) - 1
# print(pac_components_num)
pca = PCA(n_components=pac_components_num)

# 對標準化後的資料進行 PCA 分析(PCA 是一種降維技術。它透過線性組合，把原本多個可能互相關聯的變數，轉換成一組新的、彼此獨立的變數，稱為主成分（Principal Components）)。
"""
對標準化後的資料做 PCA，實際上是在分析資料的相關係數矩陣(Correlation Matrix)。
這樣做的目的是：
公平比較：確保不同單位的特徵（如：金額、百分比、溫度）能被平等對待。
簡化模型：用少數幾個新變數來解釋大部分的資料特徵，方便後續的視覺化或機器學習
"""
principal_components = pca.fit_transform(scale_concat_factors_data)
# 將原始資料轉換成主成份分析結果表。每一行代表一個主成份。
principal_df = pd.DataFrame(
    data=principal_components,
    index=concat_factors_data.dropna().index,
    columns=[f"PC{i}" for i in range(1, pac_components_num + 1)],
)
# 將 asset 索引重命名為帶 .TW 的格式，與 close_price_data 對齐
principal_df.index = principal_df.index.set_levels(
    principal_df.index.levels[1].map(lambda x: f"{x}.TW"),
    level=1
)
# 產生主成份係數表
loadings = pd.DataFrame(
    pca.components_,
    columns=concat_factors_data.columns,
    index=[f"PC{i+1}" for i in range(pca.n_components_)],
)
print(f"主成份係數表，index 是第 i 個主成份， columns 是第 j 個財報因子：{loadings}")

# 產生主成份的資訊保留比例表
explained_variance_ratio = pd.DataFrame(
    pca.explained_variance_ratio_,
    index=[f"PC{i+1}" for i in range(pca.n_components_)],
    columns=["可解釋比例"],
)
print(f"主成份各自可解釋比例：{explained_variance_ratio}")

# 產生主成份的資訊保留累積比例表
cumulative_variance_ratio = pd.DataFrame(
    np.cumsum(pca.explained_variance_ratio_),
    index=[f"使用前 {i+1} 個主成份" for i in range(pca.n_components_)],
    columns=["累積可解釋比例"],
)
print(f"累積可解釋比例：{cumulative_variance_ratio}")

# 使用 Alphalens 進行第一主成份的因子分析。
alphalens_factor_data = get_clean_factor_and_forward_returns(
    factor=principal_df[["PC1"]].squeeze(),
    prices=close_price_data,
    quantiles=5,
    periods=(1,),
)
create_full_tear_sheet(alphalens_factor_data)

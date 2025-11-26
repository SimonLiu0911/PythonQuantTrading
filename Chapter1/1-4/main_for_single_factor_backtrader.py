# %%
import os
import sys
import backtrader as bt
import pandas as pd
import pyfolio as pf

utils_folder_path = os.path.dirname(os.path.dirname(__file__))
sys.path.append(utils_folder_path)

# import Chapter1.utils as chap1_utils
from Chapter1 import utils as chap1_utils

chap1_utils.finlab_login()

analysis_period_start_date = "2017-05-16"
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

# 取得指定股票代碼列表在給定日期範圍內的每日 OHLCV 數據
all_stock_data = chap1_utils.get_daily_OHLCV_data(
    stock_symbols=top_N_stocks,
    start_date=analysis_period_start_date,
    end_date=analysis_period_end_date,
)

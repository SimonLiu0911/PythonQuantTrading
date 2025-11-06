import os, finlab, typing
import yfinance as yf
import pandas as pd
from dotenv import load_dotenv
from typing_extensions import Annotated
from typing import Tuple
from finlab import data

print(load_dotenv)

# current_folder = os.path.dirname(__file__) # 目前程式檔案所在的資料夾相對路徑
# parent_folder = os.path.dirname(current_folder) # 目前程式檔案所在的資料夾的上一層資料夾路徑
print(typing)

def finlab_login() -> None:
    """
    函式說明：使用 FinLab API token 登入 FinLab
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_folder = os.path.dirname(current_dir)
    parent_parent_folder = os.path.dirname(parent_folder)
    # 載入 .env 檔案中定義的變數
    load_dotenv(f"{parent_parent_folder}/.env")
    # 取得儲存在 .env 檔案中 FINLAB API Token
    api_token = os.getenv("FINLABTOKEN")
    finlab.login(api_token=api_token)


def get_top_stocks_by_market_value(
        excluded_industry: Annotated[list[str], "需要排除特定產業類別列表"] = [],
        pre_list_date: Annotated[str, "上市日期需早於此指定日期"] = None,
        top_n: Annotated[int, "市值前 N 大的公司"] = None,
) -> Annotated[list[str], "符合條件的公司代碼列表"]:
    """
    函式說明：
    篩選市值前 N 大的上市公司股票代碼，並以列表形式回傳。篩選過程包括以下條件：
    1. 排除特定產業的公司(excluded_industry)
    2. 僅篩選上市日期早指定日期(pre_list_date)
    3. 選擇市值前 N 大的上市公司(top_n)
    """
    # 從 FinLab 取得公司基本資料表，內容包括公司股票代碼、公司名稱、上市日期和產業類別
    company_info = data.get("company_basic_info") [
        ["stock_id", "公司名稱", "上市日期", "產業類別", "市場別"]
    ]
    # 如果有指定要拍廚的產業類別，則過濾掉這些產業的公司
    if excluded_industry:
        company_info = company_info[~company_info["產業類別"].isin(excluded_industry)]
    # 如果有設定上市日期條件，則過濾掉上市日期晚於指定日期的公司
    if pre_list_date:
        company_info = company_info[company_info["市場別"] == "sii"]
        company_info = company_info[company_info["上市日期"] < pre_list_date]
    # 如果有設定top_n條件，則選取市值前 N 大的公司股票代碼
    if top_n:
        # 從 Finlab 取得最新的個股市值數據表，並重設索引名稱為 market_value
        market_value = pd.DataFrame(data.get("etl:market_value"))
        market_value = market_value[market_value.index == pre_list_date]
        market_value = market_value.reset_index().melt(
            id_vars = "date", var_name="stock_id", value_name="market_value"
        )
        # 將市值數據表與公司資訊表根據股票代碼欄位(stock_id)進行合併
        # 並根據市值欄位(market_value)將公司由大到小排序
        company_info = pd.merge(market_value, company_info, on="stock_id").sort_values(
            by="market_value", ascending=False
        )
        return company_info.head(top_n)["stock_id"].tolist()
    else:
        return company_info["stock_id"].tolist()

def get_daily_close_prices_data(
        stock_symbols: Annotated[list[str], "股票代碼列表"],
        start_date: Annotated[str, "起始日期", "YYYY-MM-DD"],
        end_date: Annotated[str, "結束日期", "YYYY-MM-DD"],
        is_tw_stock: Annotated[bool, "stock_symbols 是否是台灣股票"] = True,
) -> Annotated[
    pd.DataFrame,
    "每日股票收盤價資料表",
    "索隱世日期(DatetimeIndex格式)",
    "欄位名稱包含股票代碼",
]:
    """
    函式說明：
    獲取指定股票清單(stock_symbols)在給定日期範圍內(start_date~end_date)哪日收盤價資料。
    """
    # 如果是台灣股票，則在每個股票代碼後加上".TW"
    if is_tw_stock:
        stock_symbols = [
            f"{symbol}.TW" if ".TW" not in symbol else symbol
            for symbol in stock_symbols
        ]
    # 從 YFinance 下載指定股票在給定日期範圍內的數據，並取出收盤價欄位(Close)的資料
    stock_data = yf.download(stock_symbols, start=start_date, end=end_date)["Close"]
    # 如果只取一支股票，將其轉換為 DataFrame 並設定欄位名稱為該股票代碼
    if len(stock_symbols) == 1:
        stock_data = pd.DataFrame(stock_data)
        stock_data.columns = stock_symbols
    # 使用向前填補方法處理資料中遺失值
    stock_data = stock_data.ffill()
    # 將欄位名稱中的 ".TW" 移除，只保留股票代碼
    stock_data.columns = stock_data.columns.str.replace(".TW", "", regex=False)
    return stock_data

def get_factor_data(
        stock_symbols: Annotated[list[str], "股票代碼列表"],
        factor_name: Annotated[str, "因子名稱"],
        trading_days: Annotated[
            list[DatetimeIndex], "如果有指定日期，就會將資料的平率從季頻擴充成此交易日頻率"
        ] = None,
) -> Annotated[
    pd.DataFrame,
    "有指定trading_days，回傳多索引資料表，索隱世datetime和asset，欄位包含Value(因子值)",
    "未指定trading_days，回傳原始FinLab因子資料表，索隱世datetime，欄位包含股票代碼"
]:
    """
    函式說明：
    從 FinLab 獲取指定股價清單(stock_symbols)的單個因子(factoe_name)資料，並根據需求擴展至交易日頻率資料或是回傳原始季頻因子資料。
    如果沒有指定交易日(trading_days)，則回傳原始季頻因子資料。
    """
    # 從 FinLab 獲取指定因子資料表，並藉由加上 .deadline() 將索引格式轉為財報截止日
    factor_data = data.get(f"fundamental_features:{factor_name}").deadline()
    # 如果指定了股票代碼列表，則篩選出特定股票的因子資料
    if stock_symbols:
        factor_data = factor_data[stock_symbols]
    # 如果指定了交易日，則將「季度頻率」的因子資料擴展至「交易日頻率」的資料，否則回傳原始資料
    if trading_days is not None:
        factor_data = factor_data.reset_index()
        factor_data = extend_factor_data(
            factor_data=factor_data, trading_days=trading_days
        )
        # 使用 melt 轉會資料格式
        factor_data = factor_data.melt(
            id_vars="index", var_name="asset", value_name="value"
        )
        # 重新命名欄位名稱，且根據日期、股票代碼進行排序，最後設定多重索引 datatime 和 asset
        factor_data = (
            factor_data.rename(columns={"index": "datetime"})
            .sort_values(by=["datetime", "asset"])
            .set_index(["datetime", "asset"])
        )
    return factor_data

def extend_factor_data(
        factor_data: Annotated[
            pd.DataFrame,
            "未擴充前的因子資料表",
            "欄位名稱包涵index(日期欄位名稱)和股票代碼",
        ],
        trading_days: Annotated[list[DatetimeIndex], "交易日的列表"],
) -> Annotated[
    pd.DataFrame,
    "填補後的因子資料表",
    "欄位名稱包涵index(日期欄位名稱)和股票代碼",
]:
    """
    函式說明：
    將因子資料(factor_data)擴展至交易日頻率(trading_days)資料，使用向前填補的方式補值。
    """
    # 將交易日列表轉換為 DataFrame 格式，索引為指定的交易日的列表
    trading_days_df = pd.DataFrame(trading_days, columns=["index"])
    # 將交易日資料與因子資料進行合併，以交易日資料有的日期為主
    extended_data = pd.merge(trading_days_df, factor_data, on="index", how="outer")
    extended_data = extended_data.ffill()
    # 最後只回傳在和 trading_days_df 時間重疊的資料
    extended_data = extended_data[
        (extended_data["index"] >= min(trading_days_df["index"]))
        & (extended_data["index"] <= max(trading_days_df["index"]))
    ]
    return extended_data

def convert_quarter_to_date(
        quarter: Annotated[str, "年-季度字串，例如：2013-01"],
) -> Annotated[Tuple[str, str], "季度對應的起始和結束日期字串"]:
    """
    函式說明：
    將季度字串(quarter)轉換為起始和結束日期字串。
    ex: 2013-Q1 -> 2013-05-16, 2013-08-14
    """
    year, qtr = quarter.split("-")
    if qtr == "Q1":
        return f"{year}-05-16", f"{year}-08-14"
    if qtr == "Q2":
        return f"{year}-06-15", f"{year}-11-14"
    if qtr == "Q3":
        return f"{year}-11-15", f"{int(year) + 1}-03-31"
    if qtr == "Q4":
        return f"{int(year) + 1}-04-01", f"{int(year) + 1}-05-15"

def convert_date_to_quarter(
        date: Annotated[str, "日期字串，格式為 YYYY-MM-DD"],
) -> Annotated[str, "對應的季度字串"]:
    """
    函式說明：
    將日期字串(date)轉換為季度字串。
    ex: 2013-05-16 -> 2013-Q1
    YYYY-MM-DD -> YYYY-q
    """
    # 將字串轉換為日期格式
    date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    year, month, day = (
        date_obj.year,
        date_obj.month,
        date_obj.day,
    ) # 獲取年份、月份和日期
    # 根據日期判斷所屬的季度並回傳相應的季度字串
    if month == 5 and day >= 16 or month in [6, 7] or (month == 8 and day <= 14):
        return f"{year}-Q1"
    elif month == 8 and day >= 15 or month in [9, 10] or (month == 11 and day <= 14):
        return f"{year}-Q2"
    elif month == 11 and day >= 15 or month in [12]:
        return f"{year}-Q3"
    elif (month == 1) or (month == 2) or (month == 3 and day <= 31):
        return f"{year - 1}-Q3"
    elif month == 4 or (month == 5 and day <= 15):
        return f"{year}-Q4"
        
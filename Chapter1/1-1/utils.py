import os, finlab
from dotenv import load_dotenv
from typing_extensions import Annotated
import pandas as pd

print(load_dotenv)


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
        excluded_industry: Annotated[List[str], "需要排除特定產業類別列表"] = [],
        pre_list_date: Annotated[str, "上市日期需早於此指定日期"] = None,
        top_n: Annotated[int, "市值前 N 大的公司"] = None,
) -> Annotated[List[str], "符合條件的公司代碼列表"]:
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
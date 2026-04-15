#%%
# 載入需要的套件
import os, sys
from pathlib import Path
from dotenv import load_dotenv
from finlab import data


# # 載入.env檔案中定義的變數
# def get_parent_dir(levels=1):
#     return Path(__file__).parent.relative_to(Path(__file__).anchor) if levels == 0 else Path(__file__).parents[levels - 1]

# parent_folder = get_parent_dir(3)
# load_dotenv(f"{parent_folder}/.env")
# FINLABTOKEN = os.getenv("FINLABTOKEN")
# finlab.login(api_token=FINLABTOKEN)


utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(utils_folder_path)
# 載入 Chapter1 資料夾中的 utils.py 模組，並命名為 chap1_utils
from Chapter1 import utils as chap1_utils  # 這是讀取 Chapter1 下面的 utils

# 使用 FinLab API token 登入 FinLab 平台，取得資料訪問權限
chap1_utils.finlab_login()

# 以取得「現金及約當現金」的財務報表數據為例
# 對應的使用方法為 [financial_statement:現金及約當現金]
# 可以用 data.search('營業') 搜尋跟「營業」相關的所有欄位 or 用 data.search() 列出所有台股欄位
# 使用 .deadline() 將索引從季別「年度－季度」格式轉為財報截止日「yyyy-mm-dd」
# 公司財報截止日對應為: {'Q1': '05-15', 'Q2': '08-14', 'Q3': '11-14', 'Q4': '02-14'}
# 公司財報截止日對應為: {'Q1': '5-15', 'Q2': '8-14', 'Q3': '11-14', 'Q4': '3-31'}
df = data.get("financial_statement:現金及約當現金").deadline()
print("取得「現金及約當現金」的財務報表數據：")
print(df)

import os, finlab
from dotenv import load_dotenv


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


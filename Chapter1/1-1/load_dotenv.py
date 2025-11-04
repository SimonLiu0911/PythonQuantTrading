# %%
# # 載入需要的套件
# import os, finlab
# from dotenv import load_dotenv
# from finlab import data

# load_dotenv("Chapter1/.env")

# # 取得FINLABTOKEN
# FINLABTOKEN = os.getenv("FINLABTOKEN")

# finlab.login(api_token=FINLABTOKEN)

# df = data.get("financial_statement:現金及約當現金").deadline()
# print("取得「現金及當約現金」的財務報表數據")
# print(df)


#%%
import yfinance as yf

# 以取得台積電 2330.TW 的財報資料為例
stock = yf.Ticker("2330.TW")
print(stock.quarterly_financials)

# %%
# Alphalens主要功能是幫助我們深入分析音子策略的表現，評估這些策略是否能在實際操作中實現超越大盤的收益
# 套件（版本）：alphalens-reloaded==0.4.4


# %%
# 註解工具 typing_extensions 中的 Annotated
from typing import Tuple
from typing_extensions import Annotated

def Annotated_example(
      n1: Annotated[int, "這個數字會被加1"],
      n2: Annotated[int, "這個數字會被加2"],
    ) -> Tuple[Annotated[str, "轉成數文字的 n1 + 1"], Annotated[str, "轉成數文字的 n2 + 2"]]:
  return str(n1 + 1), str(n2 + 2)

print(f"輸出結果：{Annotated_example(3, 4)}")




# %%

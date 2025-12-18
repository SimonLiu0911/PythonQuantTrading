# %%
import talib
import yfinance as yf
import pandas as pd
from talib import abstract

# 取得 TALIB 支援的所有技術指標名稱列表
all_ta_indicators = talib.get_functions()
print(f"TALIB支援的技術指標總數量：{len(all_ta_indicators)}個")

# 取得依類別分組後的技術指標名稱列表，例如分成動量指標、Cycle指標等
all_group_ta_indicators = talib.get_function_groups()
print(f"TALIB 所有技術指標分類的名稱：{list(all_group_ta_indicators.keys())}")

# 先嘗試從本地 CSV 檔案載入（支援多種命名），再 fallback 到 yfinance 下載
import os
import glob
from pathlib import Path
# 可能的檔名（包含 singular / plural 變體）
names = ["finlab_price_2015_today.csv", "finlab_prices_2015_today.csv"]
csv_path = None
# 先檢查：1) script 目錄 2) 工作目錄 3) 常見子資料夾，並向上搜尋父目錄（最多 5 層）
script_dir = Path(__file__).resolve().parent
candidates = []
for n in names:
    candidates.append(str(script_dir / n))
    candidates.append(str(Path.cwd() / n))
    candidates.append(str(Path.cwd() / "data" / n))
    candidates.append(str(Path.cwd() / "data" / "finlab" / n))
# 向上搜尋父目錄（最多 5 個層級）以處理不同的工作目錄
parent = Path.cwd()
for _ in range(5):
    for n in names:
        candidates.append(str(parent / n))
    if parent.parent == parent:
        break
    parent = parent.parent
# 再用 glob 在工作目錄中遞迴搜尋相符檔案
for pattern in ["**/finlab*2015*.csv", "**/*finlab*2015*.csv"]:
    matches = glob.glob(str(Path.cwd() / pattern), recursive=True)
    for m in matches:
        if m not in candidates:
            candidates.append(m)
# 找到第一個存在的路徑
for p in candidates:
    if os.path.exists(p):
        csv_path = p
        break


if csv_path:
    # 讀取 CSV，嘗試處理常見欄位命名差異
    data = pd.read_csv(csv_path)
    # 統一欄位名稱（小寫轉大寫首字母）
    col_map = {}
    for col in data.columns:
        lc = col.lower()
        if lc == "date" or lc == "datetime":
            col_map[col] = "Date"
        elif lc == "open":
            col_map[col] = "Open"
        elif lc == "high":
            col_map[col] = "High"
        elif lc == "low":
            col_map[col] = "Low"
        elif lc == "close":
            col_map[col] = "Close"
        elif lc == "volume":
            col_map[col] = "Volume"
        elif lc == "ticker":
            col_map[col] = "Ticker"
    if col_map:
        data = data.rename(columns=col_map)
    # 若有 Date 欄，轉為 datetime 並排序
    if "Date" in data.columns:
        data["Date"] = pd.to_datetime(data["Date"]) 
        data = data.sort_values("Date").reset_index(drop=True)
    # 若有多支股票（Ticker 欄位），篩選 1101 或 1101.TW
    if "Ticker" in data.columns:
        ticker_candidates = ["1101.TW", "1101.Tw", "1101", "1101.tw"]
        for t in ticker_candidates:
            if t in data["Ticker"].unique():
                data = data.loc[data["Ticker"] == t].reset_index(drop=True)
                break
    # 最後補值
    data = data.ffill()
else:
    print('no csv')
    # data = (
    #   pd.DataFrame(yf.download("1101.TW", start="2022-01-01", end="2022-12-31"))
    #   .droplevel("Ticker", axis=1)
    #   .reset_index()
    #   .ffill()
    # )


# 方法一：使用標準 TALIB 函數進行技術指標計算
# 計算 30 天的簡單移動平均線（SMA），並將結果存入新的欄位"SMA"
data["SMA"] = talib.SMA(real=data["Close"], timeperiod=30)

# 計算 14 天的相對強弱指標（RSI），並將結果存入新的欄位 “RSI"
data["RSI"] = talib.RSI(data["Close"], timeperiod=14)

# 查看隨機指標（STOCH）的參數和使用說明
# print(f"STOCH 函數說明：{help(talib.STOCH)}")

# 計算隨機指標（STOCH），包括名K線和%D線，並將結果存入對應欄位
# %K 和 %D 是隨機指標的兩條線，快線(fast %K)和慢線(slow %D)
data["STOCH_K"], data["STOCH_D"] = talib.STOCH(
    high=data["High"],
    low=data["Low" ],
    close=data["Close"],
    fastk_period=5,  # 快線 %K 的週期為 5
    slowk_period=3,  # 慢線 %K 的週期為 3
    slowk_matype=0,  # 慢線 %K 的移動平均類型為簡單移動平均
    slowd_period=3,  # 慢線 %D 的週期為 3
    slowd_matype=0,  # 慢線 %D 的移動平均類型為簡單移動平均
)

# 計算移動平均收斂發散指標（MACD），包括 MACD 線、訊號線和柱狀圖，並將結果存入對應欄位
data["MACD"], data["MACDSignal"], data["MACDHist"] = talib.MACD(
    data["Close"],
    fastperiod=12,  # 快線的週期為 12
    slowperiod=26,  # 慢線的週期為 26
    signalperiod=9,  # 訊號線的週期為 9
)

# 計算隨機指標（STOCH），包括名K線和$D線，並將結果存入對應欄位
# %K 和 %D 是隨機指標的兩條線，快線（fast %K）和慢線（slow %D）
data["STOCH_K"], data["STOCH_D"] = talib.STOCH(
    high=data["High"],
    low=data["Low"],
    close=data["Close"],
    fastk_period=5,  # 快線 %K 的週期為 5
    slowk_period=3,  # 慢線 &K 的週期為 3
    slowk_matype=0,  # 慢線 &K 的移動平均類型為簡單移動平均
    slowd_period=3,  # 慢線 %D的週期為 3
    slowd_matype=0,  # 慢線 %D 的移動平均類型為簡單移動平均
)

# 計算移動平均收斂發散指標（MACD），包括 MACD 線、訊號線和柱狀圖，並將結果存入對應欄位
data["MACD"], data["MACDSignal"], data["MACDHist"] = talib.MACD(
    data["Close"],
    fastperiod=12, # 快線的週期為 12
    slowperiod=26, # 慢線的週期為 26
    signalperiod=9, # 訊號線的週期為 9
)

# 計算布林帶（Bollinger Bands），包括上軌線、中軌線和下軌線，並將結果存入對應欄位
data["BBANDS_upper"], data["BBANDS_middle"], data["BBANDS_lower"] = talib.BBANDS(
    data["Close"],
    timeperiod=5,  # 布林帶的週期為 5
    nbdevup=2.0,  # 上軌線與中軌線之間的標準差為 2
    nbdevdn=2.0,  # 下軌線與中軌線之間的標準差為 2
    matype=0,  # 移動平均的類型為簡單移動平均
)

""""""

# 方法二：：使用 TALIB 的 abstract 模組進行技術指標計算
# 使用 abstract 模組時，資料欄位必須符合 TALIB 所需的格式
# TALIB 要求的資料欄位名稱為“open"，“high"，"low"，"close"
# 重新命名資料欄位名稱，使其符合 TALIB 所需的格式
data = data.rename(
    columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close"
    }
)
# 使用 TALIB 的 abstract 模組計算 30 天的簡單移動平均線（SMA），並將結果存入“SMA”欄位
data["SMA-2"] = talib.abstract.SMA(data, timeperiod=30)

# 使用 TALIB 的 abstract 模組計算 14 天的相對強弱指標（RSI），並將結果存入 "RSI" 欄位
data["RSI-2"] = talib.abstract.RSI(data, timeperiod=14)
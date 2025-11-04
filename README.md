# PythonQuantTrading

Necessary Plugin:
python-dotenv
yfinance
finlab

如何使用 Alphalens
1. 準備數據：首先，需要準備好股價資料和因子資料，這些資料將作為後續分析的基礎
2. 整理數據：將取得的資料整理成符合 Alphalens 規定的格式，以便能夠進行有效分析
3. 計算因子數值與未來收益：使用 get_clean_factor_and_forward_returns 韓式還計算因子數值及其對應的未來收益表
  這一部會產生 Alphalens 後續分析所需的清理過的因子數據和收益數據
4. 生成因子分析報表：最後，使用 create_full_tear_sheet 函式來生成最終的因子分系報表該報表提供完整的因子表現評估，幫助我們理解因子的有效性及其對投資收益的影響
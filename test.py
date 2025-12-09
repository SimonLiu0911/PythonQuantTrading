# %%
import pandas as pd
stock_data = pd.DataFrame({
    "Close": [10.5, None, None, 11.0, None, 12.0],
    "Volume": [1000, 1200, None, None, 1500, None],
})
stock_data_filled = stock_data.ffill()
print(stock_data_filled)

# %%
from finlab import data
factor_data = data.get(f"fundamental_features:{"營業利益"}").deadline()
# factor_data = data.get(f"fundamental_features:ROA稅後息前").deadline()
# Ndhv3Iwte6ie9K9mXiVdIvTaSpjgEJbclXgWS3p9HKf3iOcbWAOQoCGXt33a5o9H
print(factor_data.columns)
# %%
import pandas as pd
df = pd.DataFrame({
    'value': [1,2],
    'date': ['10/1', '10/2']
})
print(df.squeeze())
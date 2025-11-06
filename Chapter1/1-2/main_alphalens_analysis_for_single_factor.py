# 載入需要的套件
import json
import os
import sys
from alphalens.tears import create_full_tear_sheet
from alphalens.utils import get_clean_factor_and_forward_returns

utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(utils_folder_path)
# 載入 Chapter1 資料夾中的 utils.py 模組，並命名為 chap1_utils
# import Chapter1.utils as chap1_utils
from Chapter1 import utils as chap1_utils
# from .. import utils as chap1_utils

print(chap1_utils)
# 使用 FinLab API token 登入 FinLab 平台，取得資料訪問權限
# chap1_utils.finlab_login()

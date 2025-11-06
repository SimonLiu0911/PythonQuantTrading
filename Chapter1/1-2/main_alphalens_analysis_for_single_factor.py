# 載入需要的套件
import json
import os
import sys
from alphalens.tears import create_full_tear_sheet
from alphalens.utils import get_clean_factor_and_forward_returns

utils_folder_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

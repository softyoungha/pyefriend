from enum import Enum
from pyefriend.const import *


class How(str, Enum):
    """ 매수/매도시 가격 결정 방법 """
    MARKET = 'market'  # 시장가격에 매수/패도
    N_DIFF = 'n_diff'  # 호가 단위 x n 원 아래에서 매수/ 위에서 매도
    REGRESSION = 'regression'  # linear regression


class OrderType(str, Enum):
    BUY = '매수'
    SELL = '매도'


__all__ = [
    'System',
    'Market',
    'Service',
    'MarketCode',
    'ProductCode',
    'Currency',
    'Unit',
    'How',
    'OrderType',
    'DWM',
]



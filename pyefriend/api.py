from typing import List, Dict, Union, Optional
from PyQt5.QAxContainer import QAxWidget
from PyQt5.QtWidgets import QMainWindow, QPushButton

from pyefriend.core import Core
from utils.const import PROGID, Service
from utils.config import User


Session: Optional[Core] = None


def create_session():
    global Session

    if Session is None:
        Session = Core()


class StockAPI(QMainWindow):
    def __init__(self):
        super().__init__()
        create_session()

    @staticmethod
    def _parse_account(account: str):
        """입력받은 계좌번호를 종합계좌번호와 상품코드로 파싱해서 반환한다"""
        account_num = account[:8]  # 종합계좌번호 (계좌번호 앞 8자리)
        product_code = account[8:]  # 계좌상품코드(종합계좌번호 뒷 부분에 붙는 번호)
        return account_num, product_code

    @property
    def all_accounts_(self) -> List[str]:
        """ 모든 계좌 반환 """
        return [Session.GetAccount(i)
                for i in range(Session.GetAccountCount())]

    @property
    def encrypted_password_(self):
        return Session.GetEncryptPassword(User.PASSWORD)

    @property
    def is_connected_(self) -> bool:
        """ 접속여부 판단(Accounts 갯수) """
        return len(self.all_accounts_) > 0

    def set_account_info(self, account: str):
        account_num, product_code = self._parse_account(account=account)

        self.set_data(0, account_num)
        self.set_data(1, product_code)
        self.set_data(2, self.encrypted_password_)

    @staticmethod
    def set_data(field_index: int, value: str):
        Session.SetSingleData(field_index, value)

    @staticmethod
    def get_data(field_index: int, multiple: bool = False, columns: List[Dict] = None) -> Union[str, List[Dict]]:
        """
        columns: example)
                [
            {"key": "주문일자", "index": 0},
            {"key": "주문번호", "index": 2},
            ...
        ]
        """
        if multiple:
            assert columns is not None, "columns must be set"

            # set empty list
            data_list = []

            # 총 갯수
            record_ct = Session.GetMultiRecordCount(0)

            for record_idx in range(record_ct):
                # record마다 data get
                data = {}
                for column in columns:
                    key = column.get('key')
                    index = column.get('index')

                    data[key] = Session.GetMultiData(0, record_idx, index)

                data_list.append(data)

            return data_list
        else:
            return Session.GetSingleData(field_index, 0)

    @staticmethod
    def request_data(service: str):
        Session.RequestData(service=service)


class DomesticStock(StockAPI):
    def get_stock_price(self, stock_code: str) -> int:

        # set
        self.set_data(0, 'J')           # 0: 시장분류코드 / J: 주식, ETF, ETN
        self.set_data(1, stock_code)    # 1: 종목코드

        # request
        self.request_data(Service.SCP)

        # response
        return int(self.get_data(11))   # 11: 주식 현재가

    def get_total_cash(self, account: str):
        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(5, '01')

        # request
        self.request_data(Service.SCAP)


    def get_total_evaluated_price(self, account: str):
        deposit = self.GetCashKR(account)



class OverSeasStock(StockAPI):
    pass




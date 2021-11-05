from typing import List, Dict, Union, Optional
from datetime import datetime

from PyQt5.QtWidgets import QMainWindow

from pyefriend.core import Core
from utils.const import System, Service
from utils.config import User


class API(QMainWindow):
    def __init__(self, target_account: str = None):
        super().__init__()
        self._encrypted_password = None
        self.target_account = target_account
        self.session = self.create_session()

    def create_session(self):
        session = Core()

        def send_log_when_error():
            if session.GetRtCode() != '0':
                print(f'[ERROR] {session.GetReqMessage()}')

        session.set_receive_data_event_handler(send_log_when_error)
        session.set_receive_error_data_handler(send_log_when_error)

        return session

    @staticmethod
    def _parse_account(account: str):
        """입력받은 계좌번호를 종합계좌번호와 상품코드로 파싱해서 반환한다"""
        account_num = account[:8]  # 종합계좌번호 (계좌번호 앞 8자리)
        product_code = account[8:]  # 계좌상품코드(종합계좌번호 뒷 부분에 붙는 번호)
        return account_num, product_code

    @property
    def all_accounts(self) -> List[str]:
        """ 모든 계좌 반환 """
        return [self.session.GetAccount(i)
                for i in range(self.session.GetAccountCount())]

    @property
    def encrypted_password(self):
        if self._encrypted_password is None:
            self._encrypted_password = self.session.GetEncryptPassword(User.PASSWORD)
        return self._encrypted_password

    @property
    def is_connected(self) -> bool:
        """ 접속여부 판단(Accounts 갯수) """
        return len(self.all_accounts) > 0

    def set_account_info(self, account: str = None):
        if account is None:
            account = self.target_account

        account_num, product_code = self._parse_account(account=account)

        self.set_data(0, account_num)
        self.set_data(1, product_code)
        self.set_data(2, self.encrypted_password)

    def set_data(self, field_index: int, value: str):
        self.session.SetSingleData(field_index, value)

    def get_data(self, field_index: int = None, multiple: bool = False, columns: List[Dict] = None) -> Union[str, List[Dict]]:
        """
        columns: example)
                [
            {"key": "주문일자", "index": 0, 'dtype': str},
            {"key": "주문번호", "index": 2, 'dtype': str, 'pk': True},
            ...
        ]
        """
        if multiple:
            assert columns is not None, "columns must be set"

            # set empty list
            data_list = []

            # 총 갯수
            record_ct = self.session.GetMultiRecordCount(0)

            for record_idx in range(record_ct):

                data = {}
                for column in columns:
                    key = column.get('key')
                    index = column.get('index')
                    dtype = column.get('dtype', 'str')
                    pk = column.get('pk', False)
                    value = self.session.GetMultiData(0, record_idx, index)

                    if pk and data == '':
                        # pk column의 값이 ''일 경우 break
                        break

                    data[key] = int(value) if dtype == int else value

                data_list.append(data)

            return data_list
        else:
            return self.session.GetSingleData(field_index, 0)

    def request_data(self, service: str):
        self.session.RequestData(service=service)


class DomesticAPI(API):
    def get_stock_price(self, stock_code: str) -> int:
        # set
        self.set_data(0, 'J')  # 0: 시장분류코드 / J: 주식, ETF, ETN
        self.set_data(1, stock_code)  # 1: 종목코드

        # request
        self.request_data(Service.SCP)

        # response
        return int(self.get_data(11))  # 11: 주식 현재가

    def get_total_cash(self, account: str = None) -> int:
        """ 총 주문가능현금 """
        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(5, '01')  # 01: 시장가로 계산

        # request
        self.request_data(Service.SCAP)

        # response
        return int(self.get_data(0))  # 0: 주문가능현금

    def get_stocks(self, account: str = None) -> List[Dict]:
        """ 주식별 정보 """
        # 계정 정보
        self.set_account_info(account=account)

        # request
        self.request_data(Service.SATPS)

        # get table
        columns = [
            {'index': 0, 'key': '종목코드', 'pk': True},
            {'index': 1, 'key': '종목명'},
            {'index': 11, 'key': '현재가', 'dtype': int},
            {'index': 7, 'key': '보유수량', 'dtype': int},
            {'index': 12, 'key': '평가금액', 'dtype': int},
        ]
        return self.get_data(multiple=True, columns=columns)

    def get_total_evaluated_price(self, account: str = None):
        deposit = self.get_total_cash(account)
        stocks = self.get_stocks(account)

        # 총합
        return deposit + sum([stock['평가금액'] for stock in stocks])

    def buy_stock(self, product_code: str, amount: int, price: int = 0, account: str = None) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 시장가로 매수
        :return 주문번호
        """
        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(3, product_code)
        self.set_data(4, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
        self.set_data(5, str(amount))  # 주문수량
        self.set_data(6, str(price))  # 주문단가

        # request
        self.request_data(Service.SCABO)

        return self.get_data(1)  # 1: 주문번호

    def sell_stock(self, product_code: str, amount: int, price: int = 0, account: str = None) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 매도
        :return 주문번호
        """
        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(3, product_code)
        self.set_data(4, '01')  # 매도유형(고정값)
        self.set_data(5, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
        self.set_data(6, str(amount))  # 주문수량
        self.set_data(7, str(price))  # 주문단가

        # request
        self.request_data(Service.SCAAO)

        return self.get_data(1)  # 1: 주문번호

    def get_processed_orders(self, start_date: str = None, account: str = None) -> List[Dict]:
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(3, start_date)
        self.set_data(4, today)
        self.set_data(5, '00')  # 매도매수구분코드  전체: 00 / 매도: 01 / 매수: 02
        self.set_data(6, '00')  # 조회구분        역순: 00 / 정순: 01
        self.set_data(8, '01')  # 체결구분        전체: 00 / 체결: 01 / 미체결: 02

        # request
        self.request_data(Service.SDOC)

        # get table
        columns = [
            {'index': 1, 'key': '주문번호', 'pk': True},
            {'index': 2, 'key': '원주문번호'},
            {'index': 4, 'key': '상품번호'},
            {'index': 13, 'key': '매수매도구분코드명'},
            {'index': 7, 'key': '주문수량'},
        ]
        return self.get_data(multiple=True, columns=columns)

    def get_unprocessed_orders(self, account: str = None) -> List[Dict]:
        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(5, '0')       # 조회구분      주문순: 0 / 종목순 1

        # request
        self.request_data(Service.SMCP)

        # get table
        columns = [
            {'index': 0, 'key': '주문일자', 'pk': True},
            {'index': 2, 'key': '주문번호'},
            {'index': 3, 'key': '원주문번호'},
            {'index': 7, 'key': '상품번호'},
            {'index': 6, 'key': '매수매도구분코드명'},
            {'index': 9, 'key': '주문수량'},
        ]
        return self.get_data(multiple=True, columns=columns)

    def cancel_order(self, order_num: str, amount: int, account: str = None) -> str:
        # 계정 정보
        self.set_account_info(account=account)

        # set
        self.set_data(4, order_num)
        self.set_data(5, "00")  # 주문 구분, 취소인 경우는 00
        self.set_data(5, "02")  # 정정취소구분코드. 02: 취소, 01: 정정
        self.set_data(7, str(amount))  # 주문수량

        self._core.RequestData("SMCO")  # 국내 주식 주문 정정 취소

        return self.get_data(1)  # 1: 주문번호

    def cancel_all_unprocessed_orders(self, account: str = None) -> List[str]:
        unprocessed_orders = self.get_unprocessed_orders(account=account)

        results = []

        for order in unprocessed_orders:
            order_num = order.get('원주문번호') or order.get('주문번호')
            amount = order.get('주문수량')

            result = self.cancel_order(order_num=order_num, amount=amount, account=account)

            results.append(result)

        return results


class OverSeasAPI(API):
    def get_stock_price(self, stock_code: str) -> int:
        pass


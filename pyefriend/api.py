from typing import List, Dict, Union, Optional
from datetime import datetime

from .const import Service, MarketCode
from .exceptions import UnExpectedException, UnAuthorizedAccountException, NotConnectedException
from .log import logger
from .connection import Conn

# [Section] Variables

conn: Optional[Conn] = None


# [Section] Constants


# [Section] Modules

def get_or_create_conn(raise_error: bool = True):
    global conn

    if conn is None:
        conn = Conn()

        def send_log_when_error():
            return_code = conn.GetRtCode()
            msg_code = conn.GetReqMsgCode()

            if return_code != '0':
                msg = conn.GetReqMessage()

                if raise_error:
                    if msg_code == '40910000':
                        raise UnAuthorizedAccountException(msg)

                    else:
                        raise UnExpectedException(msg)

                else:
                    logger.error(f'[{msg_code}] {conn.GetReqMessage()}')

        conn.set_receive_data_event_handler(send_log_when_error)
        conn.set_receive_error_data_handler(send_log_when_error)

    return conn


class Api:
    """ High Level API """

    def __init__(self,
                 target_account: str,
                 password: str):
        self.target_account = target_account
        self._encrypted_password = self.conn.GetEncryptPassword(password)

        if not self.is_connected:
            raise NotConnectedException()

        if self.conn.IsVTS():
            logger.info(f"모의투자에 성공적으로 연결되었습니다. 타겟 계좌: '{self.target_account}'")
        else:
            logger.warning(f"실제계좌에 성공적으로 연결되었습니다. 타겟 계좌: '{self.target_account}'")

    @property
    def conn(self):
        return get_or_create_conn()

    @staticmethod
    def _parse_account(account: str):
        """입력받은 계좌번호를 종합계좌번호와 상품코드로 파싱해서 반환한다"""
        account_num = account[:8]  # 종합계좌번호 (계좌번호 앞 8자리)
        product_code = account[8:]  # 계좌상품코드(종합계좌번호 뒷 부분에 붙는 번호)
        return account_num, product_code

    @property
    def all_accounts(self) -> List[str]:
        """ 모든 계좌 반환 """
        return [self.conn.GetAccount(i)
                for i in range(self.conn.GetAccountCount())]

    @property
    def encrypted_password(self):
        return self._encrypted_password

    @property
    def is_connected(self) -> bool:
        """ 접속여부 판단(Accounts 갯수) """
        return len(self.all_accounts) > 0

    def set_account_info(self, account: str = None):
        if account is None:
            account = self.target_account

        account_num, product_code = self._parse_account(account=account)

        return (
            self.set_data(0, account_num)
                .set_data(1, product_code)
                .set_data(2, self.encrypted_password)
        )

    def set_data(self, field_index: int, value: str):
        self.conn.SetSingleData(field_index, value)
        return self

    def get_data(self,
                 field_index: int = None,
                 multiple: bool = False,
                 columns: List[Dict] = None) -> Union[str, List[Dict]]:
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
            record_ct = self.conn.GetMultiRecordCount(0)

            for record_idx in range(record_ct):

                data = {}
                for column in columns:
                    key = column.get('key')
                    index = column.get('index')
                    dtype = column.get('dtype', 'str')
                    pk = column.get('pk', False)
                    value = self.conn.GetMultiData(0, record_idx, index)

                    if pk and data == '':
                        # pk column의 값이 ''일 경우 break
                        break

                    data[key] = int(value) if dtype == int else value

                data_list.append(data)

            return data_list
        else:
            return self.conn.GetSingleData(field_index, 0)

    def request_data(self, service: str):
        self.conn.RequestData(service=service)
        return self


class DomesticApi(Api):
    def get_stock_name(self, product_code: str):
        return self.conn.GetSingleDataStockMaster(product_code, 2)

    def get_stock_price(self, product_code: str, market_code: str = None) -> int:
        # set
        (
            self.set_data(0, 'J')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, product_code)  # 1: 종목코드
                .request_data(Service.SCP)
        )

        # response
        return int(self.get_data(11))  # 11: 주식 현재가

    def get_total_cash(self, account: str = None) -> int:
        """ 총 주문가능현금 """
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(5, '01')  # 01: 시장가로 계산
                .request_data(Service.SCAP)
        )

        # response
        return int(self.get_data(0))  # 0: 주문가능현금

    def get_stocks(self, account: str = None) -> List[Dict]:
        """ 주식별 정보 """

        (
            self.set_account_info(account=account)  # 계정 정보
                .request_data(Service.SATPS)  # request
        )

        # response as table
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

        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, product_code)
                .set_data(4, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
                .set_data(5, str(amount))  # 주문수량
                .set_data(6, str(price))  # 주문단가
                .request_data(Service.SCABO)
        )

        return self.get_data(1)  # 1: 주문번호

    def sell_stock(self, product_code: str, amount: int, price: int = 0, account: str = None) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 매도
        :return 주문번호
        """
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, product_code)
                .set_data(4, '01')  # 매도유형(고정값)
                .set_data(5, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
                .set_data(6, str(amount))  # 주문수량
                .set_data(7, str(price))  # 주문단가
                .request_data(Service.SCAAO)
        )

        return self.get_data(1)  # 1: 주문번호

    def get_processed_orders(self, start_date: str = None, account: str = None) -> List[Dict]:
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, start_date)
                .set_data(4, today)
                .set_data(5, '00')  # 매도매수구분코드  전체: 00 / 매도: 01 / 매수: 02
                .set_data(6, '00')  # 조회구분        역순: 00 / 정순: 01
                .set_data(8, '01')  # 체결구분        전체: 00 / 체결: 01 / 미체결: 02
                .request_data(Service.TC8001R)
        )

        # response as table
        columns = [
            {'index': 1, 'key': '주문번호', 'pk': True},
            {'index': 2, 'key': '원주문번호'},
            {'index': 4, 'key': '상품번호'},
            {'index': 13, 'key': '매수매도구분코드명'},
            {'index': 7, 'key': '주문수량'},
        ]
        return self.get_data(multiple=True, columns=columns)

    def get_unprocessed_orders(self, account: str = None) -> List[Dict]:
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(5, '0')  # 조회구분      주문순: 0 / 종목순 1
                .request_data(Service.SMCP)
        )

        # response as table
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
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(4, order_num)
                .set_data(5, "00")  # 주문 구분, 취소인 경우는 00
                .set_data(5, "02")  # 정정취소구분코드. 02: 취소, 01: 정정
                .set_data(7, str(amount))  # 주문수량
                .request_data(Service.SMCO)
        )

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


class OverSeasApi(Api):
    def set_auth(self, index: int = 0):
        return self.set_data(index, self.conn.GetOverSeasStockSise())

    def get_currency(self, account: str = None):
        """
        1 달러 -> 원으로 환전할때의 현재 기준 예상환율을 반환
        예상환율은 최초고시 환율로 매일 08:15시경에 당일 환율이 제공됨
        """
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, '512')  # 미국: 512
                .request_data(Service.OS_OS3004R)
        )

        # response
        return float(self.conn.GetMultiData(3, 0, 4))

    def get_stock_price(self, product_code: str, market_code: str = MarketCode.NASD) -> float:
        (
            self.set_auth(0)  # 권한 확인
                .set_data(1, MarketCode.as_short(market_code))
                .set_data(2, product_code)  # 1: 종목코드
                .request_data(Service.OS_ST01)
        )

        # response
        print(market_code, product_code, self.get_data(4))
        return float(self.get_data(4))  # 4: 현재가

    def get_total_cash(self, account: str = None) -> float:
        """ 총 주문가능현금 """
        (
            self.set_account_info(account=account)  # 계정 정보
                .request_data(Service.OS_US_DNCL)
        )

        # response: get table
        columns = [
            {'index': 0, 'key': '통화코드'},
            {'index': 4, 'key': '외화주문가능금액'},
        ]
        data = self.get_data(multiple=True, columns=columns)

        # filter USD
        data = [item for item in data if item['통화코드'] == 'USD']

        if len(data) > 0:
            return float(data[0])

        else:
            return 0.0

    def get_stocks(self, account: str = None) -> List[Dict]:
        (
            self.set_account_info(account=account)  # 계정 정보
                .request_data(Service.OS_US_CBLC)
        )

        # response as table
        columns = [
            {'index': 14, 'key': '해외거래소코드'},
            {'index': 3, 'key': '종목코드', 'pk': True},
            {'index': 4, 'key': '종목명', 'dtype': int},
            {'index': 12, 'key': '현재가', 'dtype': int},
            {'index': 8, 'key': '보유수량', 'dtype': int},
            {'index': 11, 'key': '평가금액', 'dtype': int},
        ]
        return self.get_data(multiple=True, columns=columns)

    def get_total_evaluated_price(self, account: str = None):
        deposit = self.get_total_cash(account)
        stocks = self.get_stocks(account)

        # 총합
        return deposit + sum([stock['평가금액'] for stock in stocks])

    def buy_stock(self,
                  product_code: str,
                  amount: int,
                  price: int = 0,
                  market_code: str = MarketCode.NASD,
                  account: str = None) -> str:
        """
        미국주식 매수

        :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
        :return 주문번호
        """

        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, str(amount))
                .set_data(6, f"{price:.2f}")  # 소숫점 2자리까지로 설정해야 오류가 안남
                .set_data(9, '0')  # 주문서버구분코드, 0으로 입력
                .set_data(10, '00')  # 주문구분, 00: 지정가
        )

        # request
        self.request_data(Service.OS_US_BUY)  # 미국매수 주문

        # response
        return self.get_data(1)  # 1: 주문번호

    def sell_stock(self,
                   product_code: str,
                   amount: int,
                   price: int = 0,
                   market_code: str = MarketCode.NASD,
                   account: str = None) -> str:
        """
        미국주식 매도

        :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
        :return 주문번호
        """
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, str(amount))
                .set_data(6, str(price))
                .set_data(9, '0')  # 주문서버구분코드, 0으로 입력
                .set_data(10, '00')  # 주문구분, 00: 지정가
                .request_data(Service.OS_US_SEL)  # 미국매도 주문
        )

        # response
        return self.get_data(1)  # 1: 주문번호

    def get_processed_orders(self,
                             market_code: str = MarketCode.NASD,
                             start_date: str = None,
                             account: str = None) -> List[Dict]:
        """
        미국주식 체결 내역 조회

        :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
        """
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        # 계정 정보
        (
            self.set_account_info(account=account)
                .set_data(4, start_date)
                .set_data(5, today)
                .set_data(6, '00')  # 매도매수구분코드  전체: 00 / 매도: 01 / 매수: 02
                .set_data(7, '01')  # 체결구분        전체: 00 / 체결: 01 / 미체결: 02
                .set_data(8, market_code)
                .request_data(Service.OS_US_CCLD)
        )

        # response as table
        columns = [
            {'index': 0, 'key': "주문일자"},
            {'index': 2, 'key': "주문번호"},
            {'index': 3, 'key': "원주문번호"},
            {'index': 12, 'key': "상품번호"},
            {'index': 10, 'key': "주문수량"},
            {'index': 13, 'key': "체결단가"},
        ]
        return self.get_data(multiple=True, columns=columns)

    def get_unprocessed_orders(self, market_code: str = MarketCode.NASD, account: str = None) -> List[Dict]:
        """
        미국 주식 미체결 내역 조회

        :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
        """
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, market_code)
                .request_data(Service.OS_US_NCCS)
        )

        # response as table
        columns = [
            {'index': 0, 'key': "주문일자"},
            {'index': 2, 'key': "주문번호"},
            {'index': 3, 'key': "원주문번호"},
            {'index': 5, 'key': "상품번호"},
            {'index': 17, 'key': "주문수량"},
        ]
        return self.get_data(multiple=True, columns=columns)

    def cancel_order(self,
                     product_code: str,
                     order_num: str,
                     amount: int,
                     market_code: str = MarketCode.NASD,
                     account: str = None) -> str:
        """
        미국 주식 주문 취소

        :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
        """
        (
            self.set_account_info(account=account)  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, order_num)
                .set_data(6, '02')  # 02 : 취소, 01 : 정정
                .set_data(7, str(amount))
                .request_data(Service.OS_US_CNC)
        )

        # response
        return self.get_data(1)  # 1: 주문번호

    def cancel_all_unprocessed_orders(self, market_code: str = MarketCode.NASD, account: str = None) -> List[str]:
        """
        미체결 국내 주식 주문을 모두 취소

        :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
        :return:
        """
        unprocessed_orders = self.get_unprocessed_orders(market_code=market_code, account=account)

        results = []

        for order in unprocessed_orders:
            order_num = order.get('원주문번호') or order.get('주문번호')
            product_code = order.get('상품번호')
            amount = order.get('주문수량')

            result = self.cancel_order(market_code=market_code,
                                       product_code=product_code,
                                       order_num=order_num,
                                       amount=amount,
                                       account=account)

            results.append(result)

        return results

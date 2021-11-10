from logging import Logger
from typing import List, Dict, Union, Optional, Tuple
from datetime import datetime
import requests

from .const import Service, MarketCode, Currency, ProductCode
from .log import logger as pyefriend_logger
from .connection import Conn
from .exceptions import *

# [Section] Variables

conn: Optional[Conn] = None


# [Section] Modules

def get_or_create_conn(logger=None, raise_error: bool = True):
    global conn

    if conn is None:
        conn = Conn(logger)

        def send_log_when_error():
            return_code = conn.GetRtCode()
            msg_code = conn.GetReqMsgCode()

            if return_code != '0':
                msg = f'[{msg_code}] {conn.GetReqMessage()}'

                if raise_error:
                    if msg_code == '40910000':
                        raise UnAuthorizedAccountException(msg)

                    elif msg_code == '40580000':
                        raise MarketClosingException(msg)

                    else:
                        raise UnExpectedException(msg)

                else:
                    logger.error(msg)

        conn.set_receive_data_event_handler(send_log_when_error)
        conn.set_receive_error_data_handler(send_log_when_error)

    return conn


class Api:
    """
    High Level API

    :param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
    :param product_code: 종목 코드
    :param order_num: 주문번호
    """

    def __init__(self,
                 target_account: str,
                 password: str = None,
                 encrypted_password: str = None,
                 logger=None):
        if not logger:
            logger = pyefriend_logger
        self.logger: Logger = logger

        self.target_account = target_account
        self._all_accounts = None

        assert password or encrypted_password, "password 혹은 암호화된 password 둘 중 하나는 입력해야 합니다."

        if encrypted_password:
            self._encrypted_password = self.conn.GetEncryptPassword(password)

        if not self.is_connected:
            raise NotConnectedException()

        logger.info(f"계좌가 존재하는 지 확인합니다.: '{self.target_account}'")

        if not self.is_account_exist:
            raise AccountNotExistsException()

        if self.conn.IsVTS():
            logger.info(f"모의투자에 성공적으로 연결되었습니다. 타겟 계좌: '{self.target_account}'")
        else:
            logger.warning(f"실제계좌에 성공적으로 연결되었습니다. 타겟 계좌: '{self.target_account}'")

    @property
    def conn(self):
        """ connection load """
        return get_or_create_conn(self.logger)

    @property
    def account(self):
        """ 입력받은 계좌번호를 (종합계좌번호, 상품코드)로 파싱해서 반환 """
        account_num = self.target_account[:8]  # 종합계좌번호 (계좌번호 앞 8자리)
        product_code = self.target_account[8:]  # 계좌상품코드(종합계좌번호 뒷 부분에 붙는 번호)
        return account_num, product_code

    @property
    def all_accounts(self) -> List[str]:
        """ 모든 계좌 반환 """
        if self._all_accounts is None:
            self._all_accounts = [
                self.conn.GetAccount(i)
                for i in range(self.conn.GetAccountCount())
            ]

        return self._all_accounts

    @property
    def encrypted_password(self):
        """ 암호화된 패스워드 반환 """
        return self._encrypted_password

    @property
    def is_connected(self) -> bool:
        """ 접속여부 판단(Accounts 갯수) """
        return len(self.all_accounts) > 0

    @property
    def is_account_exist(self) -> bool:
        """ target_account 존재여부 계산 """
        return self.target_account in self.all_accounts

    def set_data(self,
                 field_index: int,
                 value: str,
                 block_index: int = None):
        """ set data """
        if block_index is not None:
            self.conn.SetSingleDataEx(block_index=block_index, field_index=field_index, value=value)
        else:
            self.conn.SetSingleData(field_index, value)
        return self

    def get_data(self,
                 field_index: int = None,
                 multiple: bool = False,
                 columns: List[Dict] = None,
                 block_index: int = 0,
                 as_type=None) -> Union[str, List[Dict]]:
        """
        pk = True인 column은 value가 ''인 것을 체크하여 for문을 나가므로 columns의 맨 앞에 위치해야합니다.

        :param multiple: 테이블형태로 데이터를 get해올 경우 True, 단일 로그일 경우 False
        :param columns: example)
                [
            {"key": "주문일자", "index": 0, 'dtype': str},
            {"key": "주문번호", "index": 2, 'dtype': str, 'pk': True},
            ...
        ]
        :param block_index: output이 multi block인 경우 block input를 선택해서 선택해주어야함.
        """
        if multiple:
            assert columns is not None, "columns must be set"

            # set empty list
            data_list = []

            # 총 갯수
            record_ct = self.conn.GetMultiRecordCount(block_index)

            for record_idx in range(record_ct):
                skip = False
                data = {}
                for column in columns:
                    key = column.get('key')
                    index = column.get('index')
                    dtype = column.get('dtype', str)
                    pk = column.get('pk', False)
                    value = self.conn.GetMultiData(block_index=block_index,
                                                   record_index=record_idx,
                                                   field_index=index)

                    if pk and value == '':
                        # pk column의 값이 ''일 경우 break
                        break

                    data[key] = value if dtype == str else dtype(value)

                if len(data) > 0:
                    data_list.append(data)

            return data_list
        else:
            data = self.conn.GetSingleData(field_index, 0)
            if as_type:
                return as_type(data)
            else:
                return data

    def set_account_info(self):
        """ request 0, 1, 2에 계정 정보 입력 """
        account_num, product_code = self.account

        return (
            self.set_data(0, account_num)
                .set_data(1, product_code)
                .set_data(2, self.encrypted_password)
        )

    def request_data(self, service: str):
        """ Transaction 요청 """
        self.conn.RequestData(service=service)
        return self

    def get_kospi_histories(self, standard: str = 'D'):
        columns = [
            dict(index=0, key='standard_date', pk=True),
            dict(index=3, key='minimum', dtype=float),
            dict(index=2, key='maximum', dtype=float),
            dict(index=1, key='opening', dtype=float),
            dict(index=4, key='closing', dtype=float),
            dict(index=5, key='volume', dtype=int),
        ]

        # response
        return (
            self.set_data(0, 'U')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, ProductCode.KOSPI)  # 1: 종목코드
                .set_data(2, standard)  # D: 일/ W: 주/ M: 월
                .request_data(Service.SCPD)
                .get_data(multiple=True, columns=columns)
        )

    def get_sp500_histories(self, standard: str = 'D'):
        if standard == 'D':
            standard = '0'
        elif standard == 'W':
            standard = '1'
        elif standard == 'M':
            standard = '2'

        columns = [
            dict(index=0, key='standard_date', pk=True),
            dict(index=7, key='minimum', dtype=float),
            dict(index=6, key='maximum', dtype=float),
            dict(index=5, key='opening', dtype=float),
            dict(index=1, key='closing', dtype=float),
            dict(index=8, key='volume', dtype=float),
        ]

        return (
            self.set_data(0, 'N')  # 0: 시장 분류 코드, 'N': 기본
                .set_data(1, ProductCode.SPX)  # 1: 종목코드
                .set_data(2, standard)
                .request_data(Service.PFX06910000)
                .get_data(multiple=True, columns=columns)
        )

    @property
    def deposit(self) -> Union[int, float]:
        """ 예수금 전체 금액 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    @property
    def stocks(self) -> List[Dict]:
        """
        현재 보유한 주식 리스트 반환
        :return: [
            {
            'product_code': str
            'product_name': str
            'current': int
            'count': int
            'price': int
            },
            ...
        ]
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def evaluate_amount(self, product_codes: List[str] = None):
        """
        전체 금액 반환(deposit + stocks 전체 금액)
        :param product_codes: 포함된 종목 코드들에 대해서만 금액 계산(포함되지 않은 종목들은 예산에서 제외)
        """
        deposit = self.deposit
        stocks = self.stocks

        if product_codes is not None:
            stocks = [stock
                      for stock in self.stocks
                      if stock['product_code'] in product_codes]

        # sum
        total_amount = self.deposit + sum([stock['price'] for stock in stocks])
        return deposit, stocks, total_amount

    def get_stock_name(self, product_code: str):
        """ 종목명 반환 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_stock_info(self, product_code: str, market_code: str = None):
        """
        입력한 종목의 현재가, 최저가, 최고가, 시가, 전일종가 로드
        :return 현재가, 최저가, 최고가, 시가, 전일종가 (Tuple)
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_stock_histories(self, product_code: str, standard: str = 'W', market_code: str = None) -> List[Dict]:
        """
        일자별 상세 정보 로드
        :param standard: D: 일/ W: 주/ M: 월
        :return [
            {
                'standard_date': 'YYYYMMDD'
                'minimum': number
                'maximum': number
                'opening': number
                'closing': number
            },
            ...
        ]
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def buy_stock(self, product_code: str, count: int, price: int = 0, market_code: str = None) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 시장가로 매수
        :return 주문번호
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def sell_stock(self, product_code: str, count: int, price: int = 0, market_code: str = None) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 매도
        :return 주문번호
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_processed_orders(self, start_date: str = None, market_code: str = None) -> List[Dict]:
        """ start_date 이후의 체결된 주문 리스트 반환 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_unprocessed_orders(self, market_code: str = None) -> List[Dict]:
        """ 미체결된 주문 리스트 반환 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def cancel_order(self, order_num: str, count: int, product_code: str = None, market_code: str = None) -> str:
        """ 주문 취소 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def cancel_all_unprocessed_orders(self, market_code: str = None) -> List[str]:
        """ 미체결된 모든 리스트 취소 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')


class DomesticApi(Api):
    @property
    def unit(self):
        return 'KRW'

    @property
    def deposit(self) -> int:
        return int(
            self.set_account_info()  # 계정 정보
                .set_data(5, '01')  # 01: 시장가로 계산
                .request_data(Service.SCAP)
                .get_data(0)  # 0: 주문가능현금
        )

    @property
    def stocks(self) -> List[Dict]:
        columns = [
            dict(index=0, key='product_code', pk=True),
            dict(index=1, key='product_name'),
            dict(index=11, key='current', dtype=int),
            dict(index=7, key='count', dtype=int),
            dict(index=12, key='price', dtype=int),
        ]
        return (
            self.set_account_info()  # 계정 정보
                .request_data(Service.SATPS)  # request
                .get_data(multiple=True, columns=columns)
        )

    def get_stock_name(self, product_code: str):
        return self.conn.GetSingleDataStockMaster(product_code, 2)

    def get_stock_info(self, product_code: str, market_code: str = None) -> Tuple[int, int, int, int, int]:
        # set
        (
            self.set_data(0, 'J')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, product_code)  # 1: 종목코드
                .request_data(Service.SCP)
        )

        current = int(self.get_data(11))  # 11: 주식 현재가
        minimum = int(self.get_data(20))  # 19: 주식 최저가
        maximum = int(self.get_data(19))  # 20: 주식 최고가
        opening = int(self.get_data(18))  # 19: 주식 시가
        base = int(self.get_data(23))  # 23: 주식 기준가(전일 종가)

        # response
        return current, minimum, maximum, opening, base

    def get_stock_histories(self,
                            product_code: str,
                            standard: str = 'D',
                            market_code: str = None) -> List[Dict]:

        columns = [
            dict(index=0, key='standard_date', pk=True),
            dict(index=3, key='minimum', dtype=int),
            dict(index=2, key='maximum', dtype=int),
            dict(index=1, key='opening', dtype=int),
            dict(index=4, key='closing', dtype=int),
            dict(index=5, key='volume', dtype=int),
        ]

        return (
            self.set_data(0, 'J')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, product_code)  # 1: 종목코드
                .set_data(2, standard)  # D: 일/ W: 주/ M: 월
                .request_data(Service.SCPD)
                .get_data(multiple=True, columns=columns)
        )

    def buy_stock(self, product_code: str, count: int, price: int = 0, market_code: str = None) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, product_code)
                .set_data(4, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
                .set_data(5, str(count))  # 주문수량
                .set_data(6, str(price))  # 주문단가
                .request_data(Service.SCABO)
                .get_data(1)  # 1: 주문번호
        )

    def sell_stock(self, product_code: str, count: int, price: int = 0, market_code: str = None) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, product_code)
                .set_data(4, '01')  # 매도유형(고정값)
                .set_data(5, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
                .set_data(6, str(count))  # 주문수량
                .set_data(7, str(price))  # 주문단가
                .request_data(Service.SCAAO)
                .get_data(1)  # 1: 주문번호
        )

    def get_processed_orders(self, start_date: str = None, market_code: str = None) -> List[Dict]:
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        columns = [
            dict(index=1, key='주문번호', pk=True),
            dict(index=2, key='원주문번호'),
            dict(index=4, key='상품번호'),
            dict(index=13, key='매수매도구분코드명'),
            dict(index=7, key='주문수량'),
        ]

        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, start_date)
                .set_data(4, today)
                .set_data(5, '00')  # 매도매수구분코드  전체: 00 / 매도: 01 / 매수: 02
                .set_data(6, '00')  # 조회구분        역순: 00 / 정순: 01
                .set_data(8, '01')  # 체결구분        전체: 00 / 체결: 01 / 미체결: 02
                .request_data(Service.TC8001R)
                .get_data(multiple=True, columns=columns)
        )

    def get_unprocessed_orders(self, market_code: str = None) -> List[Dict]:
        columns = [
            dict(index=0, key='주문일자', pk=True),
            dict(index=2, key='주문번호'),
            dict(index=3, key='원주문번호'),
            dict(index=7, key='상품번호'),
            dict(index=6, key='매수매도구분코드명'),
            dict(index=9, key='주문수량'),
        ]

        return (
            self.set_account_info()  # 계정 정보
                .set_data(5, '0')  # 조회구분      주문순: 0 / 종목순 1
                .request_data(Service.SMCP)
                .get_data(multiple=True, columns=columns)
        )

    def cancel_order(self,
                     order_num: str,
                     count: int,
                     product_code: str = None,
                     market_code: str = None) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(4, order_num)
                .set_data(5, "00")  # 주문 구분, 취소인 경우는 00
                .set_data(6, "02")  # 정정취소구분코드. 02: 취소, 01: 정정
                .set_data(7, str(count))  # 주문수량
                .request_data(Service.SMCO)
                .get_data(1)  # 1: 주문번호
        )

    def cancel_all_unprocessed_orders(self, market_code: str = None) -> List[str]:
        unprocessed_orders = self.get_unprocessed_orders()

        results = []

        for order in unprocessed_orders:
            order_num = order.get('원주문번호') or order.get('주문번호')
            count = order.get('주문수량')

            result = self.cancel_order(order_num=order_num, count=count)

            results.append(result)

        return results


class OverSeasApi(Api):
    @property
    def unit(self):
        return 'USD'

    def set_auth(self, index: int = 0):
        return self.set_data(index, self.conn.GetOverSeasStockSise())

    @property
    def deposit(self) -> float:
        columns = [
            dict(index=0, key='currency_code'),
            dict(index=4, key='available_amount'),
        ]

        data = (
            self.set_account_info()  # 계정 정보
                .request_data(Service.OS_US_DNCL)
                .get_data(multiple=True, columns=columns)
        )

        # filter USD
        data = [item for item in data if item['currency_code'] == 'USD']

        if len(data) > 0:
            return float(data[0].get('available_amount', 0))

        else:
            return 0.0

    @property
    def stocks(self) -> List[Dict]:
        columns = [
            dict(index=14, key='market_code', pk=True),
            dict(index=3, key='product_code', pk=True),
            dict(index=4, key='product_name', dtype=str),
            dict(index=12, key='current', dtype=float),
            dict(index=8, key='count', dtype=int),
            dict(index=11, key='price', dtype=float),
        ]

        return (
            self.set_account_info()  # 계정 정보
                .request_data(Service.OS_US_CBLC)
                .get_data(multiple=True, columns=columns)
        )

    @property
    def currency(self):
        """
        1 달러 -> 원으로 환전할때의 현재 기준 예상환율을 반환
        예상환율은 최초고시 환율로 매일 08:15시경에 당일 환율이 제공됨
        """
        (
            self.set_account_info()  # 계정 정보
                .set_data(3, '512')  # 미국: 512
                .request_data(Service.OS_OS3004R)
        )

        # get data
        currency = self.conn.GetMultiData(3, 0, 4)

        # 값을 불러오지 못할 때가 있음
        if currency != '':
            return float(currency)

        try:
            # requests 모듈로 타 사이트에서 로드해옴
            response = requests.get(Currency.URL)
            data = response.json()
            return data[0]['basePrice']

        except Exception as e:
            self.logger.error('환율 정보를 불러오는 데 실패하였습니다.'
                              '설정된 환율을 사용합니다.')
            return Currency.BASE

    def get_stock_info(self,
                       product_code: str,
                       market_code: str = None) -> Tuple[float, float, float, float, float]:
        (
            self.set_auth(0)  # 권한 확인
                .set_data(1, MarketCode.as_short(market_code))
                .set_data(2, product_code)  # 1: 종목코드
                .request_data(Service.OS_ST02)
        )

        current = float(self.get_data(7))  # 7: 현재가
        minimum = float(self.get_data(6))  # 6: 저가
        maximum = float(self.get_data(5))  # 5: 고가
        opening = float(self.get_data(4))  # 4: 시가
        base = float(self.get_data(3))  # 3: 전일종가

        # response
        return current, minimum, maximum, opening, base

    def get_stock_histories(self,
                            product_code: str,
                            standard: str = 'D',
                            market_code: str = None) -> List[Dict]:
        if standard == 'D':
            standard = '0'
        elif standard == 'W':
            standard = '1'
        elif standard == 'M':
            standard = '2'

        columns = [
            dict(index=0, key='standard_date', pk=True),
            dict(index=7, key='minimum', dtype=float),
            dict(index=6, key='maximum', dtype=float),
            dict(index=5, key='opening', dtype=float),
            dict(index=1, key='closing', dtype=float),
            dict(index=8, key='volume', dtype=int),
        ]

        return (
            self.set_auth(0)  # 권한 확인
                .set_data(1, MarketCode.as_short(market_code))
                .set_data(2, product_code)  # 1: 종목코드
                .set_data(3, standard)
                .request_data(Service.OS_ST03)
                .get_data(multiple=True, columns=columns, block_index=1)
        )

    def buy_stock(self,
                  product_code: str,
                  count: int,
                  price: int = 0,
                  market_code: str = None) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, str(count))
                .set_data(6, f"{price:.2f}")  # 소숫점 2자리까지로 설정해야 오류가 안남
                .set_data(9, '0')  # 주문서버구분코드, 0으로 입력
                .set_data(10, '00')  # 주문구분, 00: 지정가
                .request_data(Service.OS_US_BUY)  # 미국매수 주문
                .get_data(1)  # 1: 주문번호
        )

    def sell_stock(self,
                   product_code: str,
                   count: int,
                   price: int = 0,
                   market_code: str = None) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, str(count))
                .set_data(6, str(price))
                .set_data(9, '0')  # 주문서버구분코드, 0으로 입력
                .set_data(10, '00')  # 주문구분, 00: 지정가
                .request_data(Service.OS_US_SEL)  # 미국매도 주문
                .get_data(1)  # 1: 주문번호
        )

    def get_processed_orders(self,
                             start_date: str = None,
                             market_code: str = None) -> List[Dict]:
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        columns = [
            dict(index=0, key="주문일자"),
            dict(index=2, key="주문번호"),
            dict(index=3, key="원주문번호"),
            dict(index=12, key="상품번호"),
            dict(index=10, key="주문수량"),
            dict(index=13, key="체결단가"),
        ]

        return (
            self.set_account_info()
                .set_data(4, start_date)
                .set_data(5, today)
                .set_data(6, '00')  # 매도매수구분코드  전체: 00 / 매도: 01 / 매수: 02
                .set_data(7, '01')  # 체결구분        전체: 00 / 체결: 01 / 미체결: 02
                .set_data(8, market_code)
                .request_data(Service.OS_US_CCLD)
                .get_data(multiple=True, columns=columns)
        )

    def get_unprocessed_orders(self, market_code: str = None) -> List[Dict]:
        columns = [
            dict(index=0, key="주문일자"),
            dict(index=2, key="주문번호"),
            dict(index=3, key="원주문번호"),
            dict(index=5, key="상품번호"),
            dict(index=17, key="주문수량"),
        ]

        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, market_code)
                .request_data(Service.OS_US_NCCS)
                .get_data(multiple=True, columns=columns)
        )

    def cancel_order(self,
                     order_num: str,
                     count: int,
                     product_code: str = None,
                     market_code: str = None) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, order_num)
                .set_data(6, '02')  # 02 : 취소, 01 : 정정
                .set_data(7, str(count))
                .request_data(Service.OS_US_CNC)
                .get_data(1)  # 1: 주문번호
        )

    def cancel_all_unprocessed_orders(self, market_code: str = None) -> List[str]:
        unprocessed_orders = self.get_unprocessed_orders(market_code=market_code)

        results = []

        for order in unprocessed_orders:
            order_num = order.get('원주문번호') or order.get('주문번호')
            product_code = order.get('상품번호')
            count = order.get('주문수량')

            result = self.cancel_order(market_code=market_code,
                                       product_code=product_code,
                                       order_num=order_num,
                                       count=count)

            results.append(result)

        return results

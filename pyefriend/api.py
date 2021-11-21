"""
# API Class

:var controller: controller.py 내 Controller class instance를 단 하나만 생성(get_or_create_controller)

# 주요 parameters

:param market_code: 해외거래소코드(NASD / NYSE / AMEX 등 4글자 문자열)
:param product_code: 종목 코드
:param order_num: 주문번호
"""
import pandas as pd
from logging import Logger
from typing import List, Dict, Union, Optional, Tuple, Any
from datetime import datetime, date
import requests

from .exceptions import *
from .const import *
from .log import logger as pyefriend_logger
from .controller import Controller

# [Section] Variables

controller: Optional[Controller] = None


# [Section] Modules

def get_or_create_controller(logger=None, raise_error: bool = True):
    global controller

    if controller is None:
        controller = Controller(logger)

        def send_log_when_error():
            return_code = controller.GetRtCode()
            msg_code = controller.GetReqMsgCode()

            if return_code != '0':
                msg = f'[{msg_code}] {controller.GetReqMessage()}'

                if raise_error:
                    if msg_code == '40910000':
                        raise UnAuthorizedAccountException(msg)

                    elif msg_code == '40580000':
                        raise MarketClosingException(msg)

                    elif msg_code == '90000000':
                        raise NotInVTSException(msg)

                    else:
                        raise UnExpectedException(msg)

                else:
                    logger.error(msg)

        controller.set_receive_data_event_handler(send_log_when_error)
        controller.set_receive_error_data_handler(send_log_when_error)

    return controller


def encrypt_password_by_efriend_expert(raw_password: str):
    return get_or_create_controller().GetEncryptPassword(raw_password)


class Api:
    """ High Level API """

    def __init__(self,
                 account: str,
                 password: str = None,
                 encrypted_password: str = None,
                 logger=None):
        if not logger:
            logger = pyefriend_logger
        self.logger: Logger = logger

        self.account = account
        self._all_accounts = None
        self.last_service = None

        assert password or encrypted_password, "password 혹은 암호화된 password 둘 중 하나는 입력해야 합니다."

        if encrypted_password:
            self._encrypted_password = encrypted_password
        else:
            self._encrypted_password = encrypt_password_by_efriend_expert(password)

        if not self.is_connected:
            raise NotConnectedException()

        logger.info(f"계좌가 존재하는 지 확인합니다.: '{self.account}'")

        if not self.is_account_exist:
            raise AccountNotExistsException()

        if self.controller.IsVTS():
            logger.info(f"모의투자에 성공적으로 연결되었습니다. 타겟 계좌: '{self.account}'")
        else:
            logger.warning(f"실제계좌에 성공적으로 연결되었습니다. 타겟 계좌: '{self.account}'")

    @property
    def controller(self):
        """ get or create controller """
        return get_or_create_controller(logger=self.logger)

    @property
    def splitted_account(self):
        """ 입력받은 계좌번호를 (종합계좌번호, 상품코드)로 파싱해서 반환 """
        account_num = self.account[:8]  # 종합계좌번호 (계좌번호 앞 8자리)
        product_code = self.account[8:]  # 계좌상품코드(종합계좌번호 뒷 부분에 붙는 번호)
        return account_num, product_code

    @property
    def all_accounts(self) -> List[str]:
        """ 모든 계좌 반환 """
        if self._all_accounts is None:
            self._all_accounts = [
                self.controller.GetAccount(i)
                for i in range(self.controller.GetAccountCount())
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
        """ account 존재여부 계산 """
        return self.account in self.all_accounts

    def set_data(self,
                 field_index: int,
                 value: str,
                 block_index: int = None):
        """ set data """
        if block_index is not None:
            self.controller.SetSingleDataEx(block_index=block_index, field_index=field_index, value=value)
        else:
            self.controller.SetSingleData(field_index, value)
        return self

    def get_data(self,
                 field_index: int = None,
                 multiple: bool = False,
                 columns: List[Dict] = None,
                 block_index: int = 0,
                 as_type=None,
                 default: Any = None) -> Union[str, List[Dict]]:
        """
        pk = True인 column은 value가 ''인 것을 체크하여 for문을 나가므로 columns의 맨 앞에 위치해야합니다.

        :param multiple: 테이블형태로 데이터를 get해올 경우 True, 단일 로그일 경우 False
        :param columns: example)
                [
            {"key": "주문일자", "index": 0, 'dtype': str},
            {"key": "주문번호", "index": 2, 'dtype': str, 'not_null': True},
            ...
        ]
        :param block_index: output이 multi block인 경우 block input를 선택해서 선택해주어야함.
        """
        if multiple:
            assert columns is not None, "columns must be set"

            # set empty list
            data_list = []

            # 총 갯수
            record_ct = self.controller.GetMultiRecordCount(block_index)

            for record_idx in range(record_ct):
                # skip 여부: not_null=True인 column이 ''일 경우 skip
                skip = False
                data = {}
                for column in columns:
                    key = column.get('key')
                    index = column.get('index')
                    dtype = column.get('dtype', str)
                    not_null = column.get('not_null', False)
                    value = self.controller.GetMultiData(block_index=block_index,
                                                         record_index=record_idx,
                                                         field_index=index)

                    if not_null and value == '':
                        # pk column의 값이 ''일 경우 break
                        skip = True
                        break

                    data[key] = value if dtype == str else dtype(value)

                if len(data) > 0 and not skip:
                    data_list.append(data)

            return data_list
        else:
            if block_index is not None:
                data = self.controller.GetSingleDataEx(block_index, field_index, 0)
            else:
                data = self.controller.GetSingleData(field_index, 0)

            if data:
                if as_type:
                    return as_type(data)
                else:
                    return data
            else:
                return default

    def set_account_info(self):
        """ request 0, 1, 2에 계정 정보 입력 """
        account_num, product_code = self.splitted_account

        return (
            self.set_data(0, account_num)
                .set_data(1, product_code)
                .set_data(2, self.encrypted_password)
        )

    def request_data(self, service: str):
        """ Transaction 요청 """
        self.last_service = service
        self.controller.RequestData(service=service)
        return self

    @property
    def currency(self) -> float:
        """
        1 달러 -> 원으로 환전할때의 현재 기준 예상환율을 반환
        예상환율은 최초고시 환율로 매일 08:15시경에 당일 환율이 제공됨
        """
        try:
            (
                self.set_account_info()  # 계정 정보
                    .set_data(3, '512')  # 미국: 512
                    .request_data(Service.OS_OS3004R)
            )

            # get data
            currency = self.controller.GetMultiData(3, 0, 4)

            # 값을 불러오지 못할 때가 있음
            if currency != '':
                return float(currency)

        except Exception as e:
            self.logger.warning(f'{e.__class__.__name__}: {str(e)}')
            pass

        try:
            # requests 모듈로 타 사이트에서 로드해옴
            response = requests.get(Currency.URL)
            data = response.json()
            return data[0]['basePrice']

        except Exception as e:
            self.logger.warning('환율 정보를 불러오는 데 실패하였습니다.'
                                '설정된 환율을 사용합니다.')
            return Currency.BASE

    @property
    def domestic_deposit(self) -> int:
        return int(
            self.set_account_info()  # 계정 정보
                .set_data(5, '01')  # 01: 시장가로 계산
                .request_data(Service.SCAP)
                .get_data(0)  # 0: 주문가능현금
        )

    @property
    def domestic_stocks(self) -> List[Dict]:
        columns = [
            dict(index=0, key='product_code', not_null=True),
            dict(index=1, key='product_name'),
            dict(index=11, key='current', dtype=int),
            dict(index=7, key='count', dtype=int),
            dict(index=12, key='price', dtype=int),
        ]

        stocks = (
            self.set_account_info()  # 계정 정보
                .request_data(Service.SATPS)  # request
                .get_data(multiple=True, columns=columns)
        )

        return [dict(**stock, unit=Unit.KRW) for stock in stocks]

    @property
    def overseas_deposit(self) -> float:
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
        data = [item for item in data if item['currency_code'] == Unit.USD]

        if len(data) > 0:
            return float(data[0].get('available_amount', 0))

        else:
            return 0.0

    @property
    def overseas_stocks(self) -> List[Dict]:
        columns = [
            dict(index=14, key='market_code', not_null=True),
            dict(index=3, key='product_code', not_null=True),
            dict(index=4, key='product_name', dtype=str),
            dict(index=12, key='current', dtype=float),
            dict(index=8, key='count', dtype=int),
            dict(index=11, key='price', dtype=float),
        ]

        stocks = (
            self.set_account_info()  # 계정 정보
                .request_data(Service.OS_US_CBLC)
                .get_data(multiple=True, columns=columns)
        )

        return [dict(**stock, unit=Unit.USD) for stock in stocks]

    def get_deposit(self, overall: bool = True) -> Union[int, float]:
        """ 예수금 전체 금액 """
        if overall:
            return self.domestic_deposit + self.overseas_deposit

        if self.is_domestic:
            return self.domestic_deposit
        else:
            return self.overseas_deposit

    def get_stocks(self, overall: bool = True) -> List[Dict]:
        """
        현재 보유한 주식 리스트 반환
        :return: [
            {
                'product_code': str
                'product_name': str
                'current': Union[int, float]
                'count': Union[int, float]
                'price': Union[int, float],
                'unit': 'KRW' or 'USD'
            },
            ...
        ]
        """
        if overall:
            return self.domestic_stocks + self.overseas_stocks

        if self.is_domestic:
            return self.domestic_stocks
        else:
            return self.overseas_stocks

    def evaluate_amount(self,
                        product_codes: List[str] = None,
                        overall: bool = True,
                        currency: float = None):
        """
        전체 금액 반환(deposit + stocks 전체 금액)
        :param product_codes: 포함된 종목 코드들에 대해서만 금액 계산(포함되지 않은 종목들은 예산에서 제외)
        :param overall: 국내/해외 합산 여부
        :param currency: 환율
        """
        deposit = self.get_deposit(overall=overall)
        stocks = self.get_stocks(overall=overall)

        if product_codes is not None:
            stocks = [
                stock
                for stock in stocks
                if stock['product_code'] in product_codes
            ]

        if overall:
            if currency is None:
                currency = self.currency

            # 환율 계산
            amount_stock = sum([stock['price'] * currency if stock['unit'] == Unit.USD else stock['price']
                                for stock in stocks])

        else:
            amount_stock = sum([stock['price'] for stock in stocks])

        # sum
        total_amount = deposit + amount_stock
        return deposit, stocks, total_amount

    def get_kospi_histories(self, standard: DWM = DWM.D):
        columns = [
            dict(index=0, key='standard_date', not_null=True),
            dict(index=3, key='minimum', dtype=float),
            dict(index=2, key='maximum', dtype=float),
            dict(index=1, key='opening', dtype=float),
            dict(index=4, key='closing', dtype=float),
            dict(index=5, key='volume', dtype=int),
        ]

        # response
        return (
            self.set_data(0, 'U')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, SectorCode.KOSPI)  # 1: 종목코드
                .set_data(2, standard)  # D: 일/ W: 주/ M: 월
                .request_data(Service.SCPD)
                .get_data(multiple=True, columns=columns)
        )

    def get_sp500_histories(self, standard: DWM = DWM.D):
        if standard == DWM.D:
            standard = '0'
        elif standard == DWM.W:
            standard = '1'
        elif standard == DWM.M:
            standard = '2'

        columns = [
            dict(index=0, key='standard_date', not_null=True),
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
    def unit(self):
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    @property
    def is_domestic(self):
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_product_prices(self, product_code: str, **kwargs):
        """
        입력한 종목의 현재가, 최저가, 최고가, 시가, 전일종가 로드
        :return 현재가, 최저가, 최고가, 시가, 전일종가 (Tuple)
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def list_product_histories(self, product_code: str, standard: DWM = DWM.W, **kwargs) -> List[Dict]:
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

    def buy_stock(self, product_code: str, count: int, price: int = 0, **kwargs) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 시장가로 매수
        :return 주문번호
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def sell_stock(self, product_code: str, count: int, price: int = 0, **kwargs) -> str:
        """
        설정한 price보다 낮으면 product_code의 종목 매도
        :return 주문번호
        """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_processed_orders(self, start_date: str = None, **kwargs) -> List[Dict]:
        """ start_date 이후의 체결된 주문 리스트 반환 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def get_unprocessed_orders(self, **kwargs) -> List[Dict]:
        """ 미체결된 주문 리스트 반환 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def cancel_order(self, order_num: str, count: int, product_code: str = None, market_code: str = None) -> str:
        """ 주문 취소 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')

    def cancel_all_unprocessed_orders(self, **kwargs) -> List[str]:
        """ 미체결된 모든 리스트 취소 """
        raise NotImplementedError('해당 함수가 설정되어야 합니다.')


class DomesticApi(Api):

    @property
    def is_domestic(self):
        return True

    @property
    def unit(self):
        return Unit.KRW

    def get_product_info(self, product_code: str, **kwargs) -> dict:
        mapping = [
            (2, 'product_name'),
            (6, 'sector_code')
        ]

        return {
            name: self.controller.GetSingleDataStockMaster(product_code, index)
            for index, name in mapping
        }

    def get_product_prices(self, product_code: str, **kwargs) -> Tuple[int, int, int, int, int, int]:
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
        total_volume = int(self.get_data(16))  # 16: 누적 거래량

        # response
        return current, minimum, maximum, opening, base, total_volume

    def list_product_histories(self,
                               product_code: str,
                               standard: DWM = DWM.D,
                               **kwargs) -> List[Dict]:
        columns = [
            dict(index=0, key='standard_date', not_null=True),
            dict(index=3, key='minimum', dtype=int),
            dict(index=2, key='maximum', dtype=int),
            dict(index=1, key='opening', dtype=int),
            dict(index=4, key='closing', dtype=int),
            dict(index=5, key='volume', dtype=int),
        ]

        return (
            self.set_data(0, 'J')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, product_code)  # 1: 종목코드
                .set_data(2, standard.value)  # D: 일/ W: 주/ M: 월
                .request_data(Service.SCPD)
                .get_data(multiple=True, columns=columns)
        )

    def list_product_histories_daily(self,
                                     product_code: str,
                                     start_date: Union[date, str],
                                     end_date: Union[date, str],
                                     **kwargs):
        """ 일자별 현/시/고/체결량 제공 """

        if isinstance(start_date, date):
            start_date = start_date.strftime('%Y%m%d')

        if isinstance(end_date, date):
            end_date = end_date.strftime('%Y%m%d')

        (
            self
                .set_data(0, 'J')
                .set_data(1, product_code)  # 1: 종목코드
                .set_data(0, 'J', 1)
                .set_data(1, product_code, 1)
                .set_data(2, start_date, 1)
                .set_data(3, end_date, 1)
                .request_data(Service.KST03010100)
        )

        columns = [
            dict(index=0, key='standard_date', not_null=True),
            dict(index=4, key='minimum', type=float),
            dict(index=3, key='maximum', type=float),
            dict(index=2, key='opening', type=float),
            dict(index=1, key='closing', not_null=True),
            dict(index=5, key='volume', type=int),
        ]
        data = self.get_data(multiple=True, columns=columns, block_index=1)
        return data

    def get_sector_info(self, sector_code: str, **kwargs) -> dict:
        mapping = [
            (0, 'current', float),
            (6, 'opening', float),
            (8, 'minimum', float),
            (7, 'maximum', float),
            (1, 'compared_yesterday_amount', float),
            (2, 'compared_yesterday_sign', str),
            (9, 'last_volume', int),
            (4, 'total_volume', int),
            (10, 'increase_product_count', int),
            (11, 'decrease_product_count', int),
            (12, 'nochange_product_count', int),
            (13, 'maximum_product_count', int),
            (14, 'minimum_product_count', int),
        ]

        (
            self.set_data(0, 'U')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, sector_code)  # 1: 종목코드
                .request_data(Service.PUP02120000)
        )

        return {
            name: type_(self.get_data(index))
            for index, name, type_ in mapping
        }

    def list_sector_histories(self,
                              sector_code: str,
                              start_date: str = None,
                              standard: DWM = DWM.D):
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        columns = [
            dict(index=0, key='standard_date', not_null=True),
            dict(index=7, key='minimum', dtype=float),
            dict(index=6, key='maximum', dtype=float),
            dict(index=5, key='opening', dtype=float),
            dict(index=1, key='closing', dtype=float),
            dict(index=9, key='volume', dtype=int),
        ]

        return (
            self.set_data(0, 'U', 0)
                .set_data(1, sector_code, 0)
                .set_data(0, 'U', 1)  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, sector_code, 1)  # 1: 종목코드
                .set_data(2, start_date, 1)
                .set_data(3, standard.value, 1)  # D: 일/ W: 주/ M: 월
                .request_data(Service.PUP02120000)
                .get_data(multiple=True, columns=columns, block_index=1)
        )

    def buy_stock(self,
                  product_code: str,
                  count: int,
                  price: int = 0,
                  **kwargs) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, product_code)
                .set_data(4, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
                .set_data(5, str(count))  # 주문수량
                .set_data(6, str(int(price)))  # 주문단가
                .request_data(Service.SCABO)
                .get_data(1)  # 1: 주문번호
        )

    def sell_stock(self,
                   product_code: str,
                   count: int,
                   price: int = 0,
                   **kwargs) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, product_code)
                .set_data(4, '01')  # 매도유형(고정값)
                .set_data(5, '01' if price <= 0 else '00')  # 00: 지정가 / 01: 시장가
                .set_data(6, str(count))  # 주문수량
                .set_data(7, str(int(price)))  # 주문단가
                .request_data(Service.SCAAO)
                .get_data(1)  # 1: 주문번호
        )

    def get_processed_orders(self, start_date: str = None, **kwargs) -> List[Dict]:
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        columns = [
            dict(index=0, key='order_date', not_null=True),
            dict(index=1, key='order_num', not_null=True),
            dict(index=2, key='origin_order_num'),
            dict(index=7, key='product_code'),
            dict(index=5, key='order_type'),
            dict(index=6, key='order_type_name'),
            dict(index=9, key='count'),
            dict(index=15, key='price'),
            dict(index=12, key='executed_count'),
            dict(index=15, key='executed_amount'),
            dict(index=14, key='is_cancel'),
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

    def get_unprocessed_orders(self, **kwargs) -> List[Dict]:
        columns = [
            dict(index=0, key='order_date', not_null=True),
            dict(index=1, key='order_num', not_null=True),
            dict(index=2, key='origin_order_num'),
            dict(index=13, key='order_type'),
            dict(index=6, key='order_type_name'),  # efriend Expert에 정정취소구분명으로 등록되어있음
            dict(index=4, key='product_code'),
            dict(index=7, key='count'),
            dict(index=10, key='executed_count'),
            dict(index=11, key='executed_amount'),
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
                     **kwargs) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(4, order_num)
                .set_data(5, "00")  # 주문 구분, 취소인 경우는 00
                .set_data(6, "02")  # 정정취소구분코드. 02: 취소, 01: 정정
                .set_data(7, str(count))  # 주문수량
                .request_data(Service.SMCO)
                .get_data(1)  # 1: 주문번호
        )

    def cancel_all_unprocessed_orders(self, **kwargs) -> List[str]:
        unprocessed_orders = self.get_unprocessed_orders()

        results = []

        for order in unprocessed_orders:
            order_num = order.get('origin_order_num') or order.get('order_num')
            count = order.get('count')

            result = self.cancel_order(order_num=order_num, count=count)

            results.append(result)

        return results

    def get_spread(self, product_code: str, **kwargs):
        """ 종목 현재시간 기준 매수/매도호가 정보 """
        (
            self
                .set_data(0, 'J')
                .set_data(1, product_code)
                .request_data(Service.SCPH)
        )

        columns = [
            dict(index=0, key='accepted_time'),
            dict(index=61, key='total_ask_count', type=int),
            dict(index=62, key='total_bid_count', type=int),
            dict(index=63, key='total_ask_count_icdc', type=int),
            dict(index=64, key='total_bid_count_icdc', type=int),
            *[dict(index=i, key=f'ask_price_{order}', type=int) for order, i in enumerate(range(1, 11))],
            *[dict(index=i, key=f'bid_price_{order}', type=int) for order, i in enumerate(range(11, 21))],
            *[dict(index=i, key=f'ask_count_{order}', type=int) for order, i in enumerate(range(21, 31))],
            *[dict(index=i, key=f'bid_count_{order}', type=int) for order, i in enumerate(range(31, 41))],
            *[dict(index=i, key=f'ask_count_icdc_{order}', type=int) for order, i in enumerate(range(41, 51))],
            *[dict(index=i, key=f'bid_count_icdc_{order}', type=int) for order, i in enumerate(range(51, 61))],
        ]
        data = self.get_data(multiple=True, columns=columns)[0]
        return {
            'accepted_time': data['accepted_time'],
            'total_ask_count': data['total_ask_count'],
            'total_bid_count': data['total_bid_count'],
            'total_ask_count_icdc': data['total_ask_count_icdc'],
            'total_bid_count_icdc': data['total_bid_count_icdc'],
            'asks': [
                {
                    'price': data[f'ask_price_{order}'],
                    'count': data[f'ask_count_{order}'],
                    'icdc': data[f'ask_count_icdc_{order}']
                }
                for order in range(10)
            ],
            'bids': [
                {
                    'price': data[f'bid_price_{order}'],
                    'count': data[f'bid_count_{order}'],
                    'icdc': data[f'bid_count_icdc_{order}']
                }
                for order in range(10)
            ]
        }

    def get_product_chart(self, product_code: str, interval: int = 60, **kwargs):
        """ interval별 현/시/고/체결량 제공 """
        (
            self
                .set_data(0, 'J')
                .set_data(1, product_code)
                .set_data(2, str(interval))
                .request_data(Service.PST01010300)
        )

        columns = [
            dict(index=0, key='executed_date', not_null=True),
            dict(index=1, key='executed_time', not_null=True),
            dict(index=2, key='current', type=float),
            dict(index=4, key='maximum', type=float),
            dict(index=5, key='minimum', type=float),
            dict(index=3, key='opening', type=float),
            dict(index=7, key='volume', type=int),
            dict(index=6, key='total_volume', type=int),
        ]
        data = self.get_data(multiple=True, columns=columns)
        return data

    def get_sector_chart(self, sector_code: str, interval: int = 60, **kwargs):
        """ interval별 현/시/고/체결량 제공 """
        (
            self
                .set_data(0, 'U')
                .set_data(1, sector_code)
                .set_data(2, str(interval))
                .request_data(Service.PUP02100200)
        )

        columns = [
            dict(index=0, key='executed_time', not_null=True),
            dict(index=1, key='current', type=float, not_null=True),
            dict(index=5, key='total_volume', type=int),
            dict(index=6, key='volume', type=int),
        ]
        data = self.get_data(multiple=True, columns=columns)

        return [row for row in data if row['executed_time'] < '153001']

    def list_popular_products(self,
                              direction: Direction = Direction.INCREASE,
                              index_code: IndexCode = IndexCode.TOTAL,
                              last_day: bool = False,
                              **kwargs):
        if index_code == IndexCode.TOTAL:
            index_code = '0000'
        elif index_code == IndexCode.KOSPI:
            index_code = '0001'
        elif index_code == IndexCode.KOSDAQ:
            index_code = '1001'

        if direction == Direction.MAXIMUM:
            direction_num = '0'
        elif direction == Direction.INCREASE:
            direction_num = '1'
        elif direction == Direction.NOCHANGE:
            direction_num = '2'
        elif direction == Direction.DECREASE:
            direction_num = '3'
        elif direction == Direction.MINIMUM:
            direction_num = '4'
        else:
            raise ValueError('direction must be set')

        if last_day:
            date = '1'  # 전일
        else:
            date = '0'  # 당일

        (
            self
                .set_data(0, 'J')
                .set_data(1, '11302')
                .set_data(2, direction_num)
                .set_data(3, date)
                .set_data(4, index_code)
                .request_data(Service.KST13020000)
        )

        columns = [
            dict(index=0, key='product_code', not_null=True),
            dict(index=1, key='product_status', not_null=True),
            dict(index=2, key='product_name'),
            dict(index=3, key='current', type=int),
            dict(index=4, key='compared_yesterday_amount', type=int),
            dict(index=5, key='compared_yesterday_sign', type=str),
            dict(index=7, key='total_volume', type=int),
            dict(index=8, key='total_amount', type=int),
            dict(index=13, key='continuous_maximum_days', type=int),
            dict(index=14, key='continuous_minimum_days', type=int),
            dict(index=15, key='continuous_increase_days', type=int),
            dict(index=16, key='continuous_decrease_days', type=int),
            dict(index=17, key='continuous_nochange_days', type=int),
        ]
        data = self.get_data(multiple=True, columns=columns)
        return data

    def list_foreigner_net_buy_or_sell(self,
                                       net_buy_sell: NetBuySell,
                                       index_code: IndexCode = IndexCode.TOTAL,
                                       **kwargs):
        if index_code == IndexCode.TOTAL:
            index_code = '0000'
        elif index_code == IndexCode.KOSPI:
            index_code = '1001'
        elif index_code == IndexCode.KOSDAQ:
            index_code = '2001'
        else:
            raise ValueError('index_code must be set')

        if net_buy_sell == NetBuySell.SIM_NET_BUY:
            net_buy_sell = '00'
        if net_buy_sell == NetBuySell.SIM_NET_SELL:
            net_buy_sell = '01'
        if net_buy_sell == NetBuySell.SUM_NET_BUY:
            net_buy_sell = '02'
        if net_buy_sell == NetBuySell.SUM_NET_SELL:
            net_buy_sell = '03'
        if net_buy_sell == NetBuySell.TOTAL:
            net_buy_sell = '04'

        (
            self
                .set_data(0, net_buy_sell)
                .set_data(1, index_code)
                .request_data(Service.PST045600C0)
        )

        columns = [
            dict(index=0, key='rank', not_null=True),
            dict(index=1, key='product_code', not_null=True),
            dict(index=2, key='product_name'),
            dict(index=3, key='closing_price', type=int),
            dict(index=14, key='foreigner_total_ask', type=int),
            dict(index=15, key='foreigner_total_bid', type=str),
            dict(index=7, key='total_volume', type=int),
            dict(index=10, key='net_quantity', type=int),
            dict(index=13, key='fake_net_quantity', type=int),
        ]
        data = self.get_data(multiple=True, columns=columns)
        return data


class OverSeasApi(Api):

    @property
    def is_domestic(self):
        return False

    @property
    def unit(self):
        return Unit.USD

    def set_auth(self, index: int = 0):
        return self.set_data(index, self.controller.GetOverSeasStockSise())

    def get_product_prices(self,
                           product_code: str,
                           market_code: str = None,
                           **kwargs) -> Tuple[float, float, float, float, float, int]:
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

        (
            self.set_auth(0)  # 권한 확인
                .set_data(1, MarketCode.as_short(market_code))
                .set_data(2, product_code)  # 1: 종목코드
                .request_data(Service.OS_ST02)
        )

        total_volume = int(self.get_data(8))

        # response
        return current, minimum, maximum, opening, base, total_volume

    def list_product_histories(self,
                               product_code: str,
                               standard: DWM = DWM.D,
                               market_code: str = None,
                               **kwargs) -> List[Dict]:
        if standard == DWM.D:
            standard = '0'
        elif standard == DWM.W:
            standard = '1'
        elif standard == DWM.M:
            standard = '2'

        columns = [
            dict(index=0, key='standard_date', not_null=True),
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
                  price: float = 0,
                  market_code: str = None,
                  **kwargs) -> str:
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
                   price: float = 0,
                   market_code: str = None,
                   **kwargs) -> str:
        return (
            self.set_account_info()  # 계정 정보
                .set_data(3, market_code)
                .set_data(4, product_code)
                .set_data(5, str(count))
                .set_data(6, f"{price:.2f}")
                .set_data(9, '0')  # 주문서버구분코드, 0으로 입력
                .set_data(10, '00')  # 주문구분, 00: 지정가
                .request_data(Service.OS_US_SEL)  # 미국매도 주문
                .get_data(1)  # 1: 주문번호
        )

    def get_processed_orders(self, start_date: str = None, market_code: str = None, **kwargs) -> List[Dict]:
        today = datetime.today().strftime('%Y%m%d')

        if start_date is None:
            start_date = today

        columns = [
            dict(index=0, key='order_date', not_null=True),
            dict(index=2, key='order_num', not_null=True),
            dict(index=3, key='origin_order_num'),
            dict(index=12, key='product_code'),
            dict(index=4, key='order_type'),
            dict(index=5, key='order_type_name'),
            dict(index=10, key='count'),
            dict(index=13, key='price'),
            dict(index=12, key='executed_count'),
            dict(index=14, key='executed_amount'),
            dict(index=16, key='is_cancel'),
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

    def get_unprocessed_orders(self, market_code: str = None, **kwargs) -> List[Dict]:
        columns = [
            dict(index=0, key='order_date', not_null=True),
            dict(index=2, key='order_num', not_null=True),
            dict(index=3, key='origin_order_num'),
            dict(index=6, key='order_type'),
            dict(index=7, key='order_type_name'),
            dict(index=5, key='product_code'),
            dict(index=17, key='count'),
            dict(index=18, key='executed_count'),
            dict(index=22, key='executed_amount'),
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

    def cancel_all_unprocessed_orders(self, market_code: str = None, **kwargs) -> List[str]:
        unprocessed_orders = self.get_unprocessed_orders(market_code=market_code)

        results = []

        for order in unprocessed_orders:
            order_num = order.get('origin_order_num') or order.get('order_num')
            product_code = order.get('product_code')
            count = order.get('count')

            result = self.cancel_order(market_code=market_code,
                                       product_code=product_code,
                                       order_num=order_num,
                                       count=count)

            results.append(result)

        return results

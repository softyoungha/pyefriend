import os
import time
from datetime import datetime
import pandas as pd
import logging
from typing import Union, Dict, List
from IPython.display import display, Markdown
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean

from pyefriend import load_api, encrypt_password_by_efriend_expert
from pyefriend.const import MarketCode, Market, Unit

from rebalancing.exceptions import ReportNotFoundException
from rebalancing.settings import IS_JUPYTER_KERNEL
from rebalancing.config import Config, HOME_PATH
from rebalancing.utils.const import How, OrderType
from rebalancing.utils.log import get_logger, remove_logger
from rebalancing.utils.orm_helper import provide_session
from rebalancing.models import Product, Portfolio, ProductHistory, Setting
from .base import Base, Length


def display_only_jupyter(data: Union[str, pd.DataFrame]):
    if IS_JUPYTER_KERNEL:
        if isinstance(data, pd.DataFrame):
            display(data)
        else:
            display(Markdown(data))


class Status:
    """ Report 상태 """
    CREATED = 'CREATED'
    PLANNING = 'PLANNING'
    EXECUTED = 'EXECUTED'


class Report(Base):
    __tablename__ = 'report'

    # columns
    id = Column(Integer(), primary_key=True, autoincrement=True)
    report_name = Column(String(Length.ID), comment='리포트명')
    created_time = Column(String(Length.TYPE), comment='Report 생성일자')
    market = Column(String(Length.TYPE), comment="국내/해외 여부('domestic', 'overseas')")
    account = Column(String(Length.ID), comment='계좌명')
    encrypted_password = Column(String(Length.DESC), comment='암호화된 비밀번호')
    status = Column(String(Length.TYPE), default=Status.CREATED, comment='상태')

    __table_args__ = (
        Index('idx_report', market, report_name, created_time, unique=True),
    )

    def __init__(self,
                 market: Market,
                 account: str = None,
                 password: str = None,
                 encrypted_password: str = None,
                 created_time: str = None,
                 prompt: bool = False,
                 status: str = Status.CREATED,
                 **kwargs):
        """
        re-balancing 실행 후 자동 리포트 생성

        :param market:          'domestic', 'overseas'
        :param account:         setting 테이블 에 있는 계좌가 아닌 입력된 계좌를 사용
        :param password:        account를 직접 입력했을 경우 사용할 password
        :param created_time:   [%Y%m%d_%H_%M_%S, str] 입력될 경우 해당 시간에 계산된 rebalancing 결과를 바라봅니다.
                                입력되지 않을 경우 Executor가 실행된 시간으로 저장합니다(report_path의 폴더구분으로 사용됩니다)
        :param prompt:          True일 경우 report_name을 직접 입력할 수 있습니다. False일 경우 계좌명을 report_name으로 사용합니다.
        """
        super().__init__(**kwargs)

        # initialize
        self._init()

        # set created_time
        if created_time:
            try:
                # format 확인
                datetime.strptime(created_time, '%Y%m%d_%H_%M_%S')
            except Exception as e:
                raise e

            self.created_time = created_time

        else:
            self.created_time = datetime.now().strftime('%Y%m%d_%H_%M_%S')

        # set market
        assert market in (Market.DOMESTIC, Market.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."
        self.market: Market = market

        # set account & encrypted_password
        if account:
            assert password is not None, "account가 입력되면 password도 입력되어야 합니다."

        else:
            # 실제 계정
            account = Setting.get_value('ACCOUNT', 'ACCOUNT')
            password = Setting.get_value('ACCOUNT', 'PASSWORD')

        # 계정 set
        self.account = account

        # 비밀번호는 암호화된 것만 저장 set
        if encrypted_password:
            self.encrypted_password = encrypted_password
        else:
            self.encrypted_password = encrypt_password_by_efriend_expert(password)

        # set report_name
        if prompt:
            # report prompt
            display_only_jupyter('##### 리밸런싱 생성시 결과 및 로그를 저장할 폴더명을 정합니다.')
            print('입력하지 않을 경우 계좌명으로 설정됩니다')
            self.report_name = input('report_name = ') or self.account

        else:
            self.report_name = self.account

        display_only_jupyter(f'##### 다음 경로에 report가 저장됩니다. \n{self.report_dir}')

        # set status
        self.status = status

    def __repr__(self):
        return f"<Report(code='{self.report_name}')>"

    def _init(self):
        """ logger, api, report_dir 초기화 """
        self._report_dir = None
        self._logger = None
        self._api = None
        return self

    @provide_session
    def delete(self, session=None):
        """ 삭제 """
        session.delete(self)

    @provide_session
    def save(self, delete_if_exists: bool = False, session=None):
        """ 저장 """
        if delete_if_exists:
            report = Report.get(report_name=self.report_name,
                                created_time=self.created_time,
                                raise_if_not_exists=False,
                                session=session)
            if report:
                report.delete()

        session.add(self)

    @classmethod
    @provide_session
    def get(cls,
            report_name: str,
            created_time: str = None,
            statuses: List[str] = None,
            raise_if_not_exists: bool = True,
            session=None):
        """
        테이블 내 report_name 조회
        created_time=None일 경우 report_name 기준 마지막으로 생성된 report 검색

        :param statuses: 필터링 조건이 되는 상태 리스트
        :param raise_if_not_exists: 존재하지 않을 경우 error raise
        """
        query = session.query(cls).filter(cls.report_name == report_name)

        if statuses:
            query = query.filter(cls.status.in_(statuses))

        if created_time:
            query = (
                query
                    .filter(cls.created_time == created_time)
                    .order_by(cls.created_time.desc())
            )

        row: Report = query.first()

        if row:
            return row._init()
        else:
            if raise_if_not_exists:
                raise ReportNotFoundException()
            else:
                return None

    @provide_session
    def update_status(self, status: str, session=None):
        """ report status 업데이트 """
        report = session.query(Report).filter(Report.id == self.id).first()
        report.status = status
        return self

    @property
    def api(self):
        """ get or create api """
        if self._api is None:
            self._api = load_api(market=self.market,
                                 account=self.account,
                                 encrypted_password=self.encrypted_password,
                                 logger=self.logger)
        return self._api

    @property
    def is_domestic(self):
        """ 국내/해외 여부 """
        return self.market == Market.DOMESTIC

    @property
    def unit(self):
        """ KRW/USD 단위 """
        return self.api.unit

    @property
    def report_dir(self):
        """ report 저장 디렉토리 """
        if not self._report_dir:
            # get
            report_dir = os.path.join(HOME_PATH, Config.get('core', 'REPORT_DIR', default='report'))

            # expand ~ -> HOME path
            report_dir = os.path.expanduser(report_dir)

            # abspath
            report_dir = os.path.abspath(report_dir)

            # join
            report_dir = os.path.join(report_dir, self.report_name, f'{self.market}_{self.created_time}')

            # create tree
            os.makedirs(report_dir, exist_ok=True)

            # set
            self._report_dir = report_dir

        return self._report_dir

    def path(self, file_name: str):
        return os.path.join(self.report_dir, file_name)

    @property
    def summary_path(self):
        """ report summary 저장 경로 """
        return self.path('summary.csv')

    @property
    def plan_path(self):
        """ report 리밸런싱 plan 저장 경로 """
        return self.path('plan.csv')

    @property
    def order_path(self):
        """ report 리밸런싱 plan 저장 경로 """
        return self.path('order.txt')

    @property
    def name(self):
        """ report instance 명칭(logger_name, api file response 파일명으로 사용) """
        return f'{self.market}_{self.report_name}_{self.created_time}'

    @property
    def logger(self):
        """ get or create logger """
        if not self._logger:
            self._logger = get_logger(name=self.name, path=self.path('log.txt'))
        return self._logger

    def remove_logger(self):
        """ logger handler 제거 """
        remove_logger(logger=self.logger)

    @provide_session
    def refresh_prices(self, session=None):
        """ DB 내 종목 가격 최신화('product' table) """
        products = Product.list(is_domestic=self.is_domestic, session=session)

        # update 'Product'
        self.logger.info('종목 리스트를 최신화합니다.')
        product_infos = [(product.code,
                          self.api.get_product_prices(product_code=product.code,
                                                      market_code=product.market_code))
                         for product in products]

        product_infos = [
            {
                'code': code,
                'current': current,
                'minimum': minimum,
                'maximum': maximum,
                'opening': opening,
                'base': base,
            }
            for code, (current, minimum, maximum, opening, base) in product_infos
        ]

        # update
        Product.bulk_update(product_infos)
        self.logger.info(f'종목 리스트가 최신화되었습니다: {len(product_infos)}')

        # update 'ProductHistory'
        self.logger.info('종목 History를 최신화합니다.')
        product_histories = [(product.name,
                              self.api.list_product_histories(product_code=product.code,
                                                              market_code=product.market_code))
                             for product in products]
        product_histories = [
            {
                'product_name': name,
                'standard_date': record['standard_date'],
                'minimum': record['minimum'],
                'maximum': record['maximum'],
                'opening': record['opening'],
                'closing': record['closing']
            }
            for name, records in product_histories
            for record in records
        ]

        # truncate
        ProductHistory.truncate()

        # insert
        ProductHistory.bulk_insert(product_histories)

        self.logger.info('종목 History가 최신화되었습니다.')

        return self

    def get_prices(self) -> List[Dict]:
        """ DB 내 종목 가격 조회('product' table) """

        # 사용하는 포트폴리오 종목 리스트
        used_product_names = [
            portfolio.product_name
            for portfolio in Portfolio.list(is_domestic=self.is_domestic, as_tuple=False)
        ]

        # 사용하는 상품 정보 리스트
        used_products = [
            product.as_dict
            for product in Product.list(is_domestic=self.is_domestic)
            if product.name in used_product_names
        ]
        return used_products

    def _print_log_save(self, df: pd.DataFrame, index_name: str, title: str, filepath: str):
        """ 반복 작업 최소화 """
        df.index.name = index_name
        self.logger.info(f'{title}: \n{df.to_string()}')
        display_only_jupyter(f'### {title}')
        display_only_jupyter(df)
        df.to_csv(filepath,
                  encoding='utf-8',
                  index=True)
        print(f"# '{title}' Successfully saved in '{filepath}'")

    def make_plan(self, overall: bool = False):
        """
        최신화된 가격을 토대로 리밸런싱 플랜 생성
        이미 매수된 종목이면서 포트폴리오에 포함되지 않은 종목은 제외됩니다.
        현재 모의투자에서는 해외 잔고를 확인할 수가 없으므로

        # plan result dataframe
        :keyword deposit:                   총 예수금
        :keyword total_amount:              총 예수금 + 포트폴리오 포함 & 매수된 종목들의 평가 금액 전체 합
        :keyword available_total_amount:    전체 금액 중 사용할 금액(total_amount * [AVAILABLE percent in setting table])
        :keyword asis_total_amount:         포트폴리오 포함 & 매수된 종목들의 평가 금액 전체 합
        :keyword planned_budge:             국내/해외 투자에 사용할 금액
        :keyword tobe_total_amount:         rebalancing 후 계산된 실제 전체 금액

        # plan detail dataframe
        :keyword current:                   현재가
        :keyword weight:                    리밸런싱의 기준이 되는 가중치
        :keyword asis_count:                [리밸런싱 전] 현재 매수 수량
        :keyword asis_amount:               [리밸런싱 전] 평가금액
        :keyword planned_rate:              [리밸런싱 계산] 가중치 비중 * planned_budge
        :keyword planned_amount:            [리밸런싱 계산] 리밸런싱되어 매수되어야할 금액(planned_rate * planned_budge)
        :keyword tobe_count:                [리밸런싱 후] 최종 매수 수량
        :keyword tobe_amount:               [리밸런싱 후] 현재가 기준 최종 매수된 후 전체 금액
        :keyword difference:                TOBE - ASIS 수량 차이
        """
        # unit(overall=True일 경우 원단위)
        u = Unit.KRW if overall else self.unit

        # 숫자 타입(overall=True일 경우 float, 그 외 국내 조회일 경우에만 int)
        num_type = float if overall or not self.is_domestic else int

        # get currency
        currency = self.api.currency

        # available_percent: 사용할 금액 %
        available_percent = Setting.get_value('REBALANCE', 'AVAILABLE_LIMIT', dtype=float)

        # additional_amount: 전체 금액 합산시 추가할 금액
        additional_amount = Setting.get_value('REBALANCE', 'ADDITIONAL_AMOUNT', dtype=float)

        # percent: 국내/해외 주식 비율 %
        if self.is_domestic:
            percent = Setting.get_value('REBALANCE', 'DOMESTIC_LIMIT', dtype=float)

        else:
            percent = Setting.get_value('REBALANCE', 'OVERSEAS_LIMIT', dtype=float)

        # list all portfolio with use_yn = True
        portfolios = Portfolio.list(is_domestic=self.is_domestic, only_y=True, as_tuple=True)

        # product_codes_in_portfolio: 포트폴리오에 포함된 product_code
        product_codes_in_portfolio = [portfolio[0] for portfolio in portfolios]

        # total_weights: 전체 weight(5번째 -> 4)
        total_weights = sum([portfolio[4] for portfolio in portfolios])

        # 현재 주식 금액: 예수금, 주식들, 계좌 내 전체 금액
        deposit, stocks, account_amount = self.api.evaluate_amount(product_codes_in_portfolio,
                                                                   overall=overall,
                                                                   currency=currency)

        # 타계좌 금액
        total_amount = additional_amount + account_amount

        self.logger.info(f"{'deposit':>25}{deposit:>15,.2f} {u} (총 예수금)")
        self.logger.debug(f"{'stocks':>25}(현재 매수한 주식 리스트)\n{stocks} ")
        self.logger.info(f"{'account_amount':>25}{account_amount:>15,.2f} {u} "
                         f"(추가로 더할 금액)")
        self.logger.info(f"{'total_amount':>25}{total_amount:>15,.2f} {u} "
                         f"(총 예수금 + 포트폴리오 포함 & 매수된 종목들의 평가 금액 전체 합)")

        # stocks: list -> dict
        stocks = {stock['product_code']: stock for stock in stocks}

        # available_total_amount: 전체 금액 중 사용할 금액
        available_total_amount = total_amount * available_percent
        self.logger.info(f"{'available_total_amount':>25}{available_total_amount:>15,.2f} {u} (전체 금액 중 사용할 금액)")

        # planned_budge: 국내/해외 투자에 사용할 금액
        planned_budge = available_total_amount * percent
        self.logger.info(f"{'planned_budge':>25}{planned_budge:>15,.2f} {u} (투자에 사용할 금액)")

        # init list & sum
        plan_index = []
        plan_data = []
        asis_total_amount = 0

        for product_code, product_name, market_code, current, weight, quote_unit, unit in portfolios:

            # create empty row
            row = {}

            # get stock
            stock = stocks.get(product_code, {})

            # 다음 조건을 만족하면 환율 곱해서 계산: overall(전체금액 합산시 단위가 USD인 경우)
            if overall and unit == Unit.USD:
                row.update(us_current=current)
                current = current * currency

            # calculate
            asis_count = stock.get('count', 0)
            asis_amount = stock.get('price', 0)
            planned_rate = weight / total_weights
            planned_amount = planned_budge * planned_rate
            tobe_count = round(planned_amount / current)
            tobe_amount = current * tobe_count
            difference = int(tobe_count - asis_count)

            row.update(market_code=market_code,
                       product_name=product_name,
                       unit=u,
                       current=num_type(current),
                       weight=weight,
                       quote_unit=quote_unit,
                       asis_count=asis_count,
                       asis_amount=num_type(asis_amount),
                       planned_rate=planned_rate,
                       planned_amount=num_type(planned_amount),
                       tobe_count=tobe_count,
                       tobe_amount=num_type(tobe_amount),
                       difference=difference)

            # append
            plan_index.append(product_code)
            plan_data.append(row)

            asis_total_amount += asis_amount

        tobe_total_amount = sum([portfoilo.get('tobe_amount') for portfoilo in plan_data])
        self.logger.info(f"{'asis_total_amount':>25}{asis_total_amount:>15,.2f} {u} (리밸런싱 전 전체 금액)")
        self.logger.info(f"{'tobe_total_amount':>25}{tobe_total_amount:>15,.2f} {u} (리밸런싱 후 전체 금액)")
        self.logger.info(f"{'리밸런싱 후 감소 금액':>25}: {planned_budge - tobe_total_amount:>15,.2f} {u} ")

        # 결과 집계
        results = {}
        results['deposit'] = deposit
        results['total_amount'] = total_amount
        results['available_total_amount'] = available_total_amount
        results['planned_budge'] = planned_budge
        results['asis_total_amount'] = asis_total_amount
        results['tobe_total_amount'] = tobe_total_amount

        # result dataframe
        df_results = pd.DataFrame([results], index=[self.created_time])
        self._print_log_save(df=df_results,
                             index_name='created_time',
                             title='Rebalance Result',
                             filepath=self.summary_path)

        # plan dataframe
        df_plan = pd.DataFrame(plan_data, index=plan_index)
        self._print_log_save(df=df_plan,
                             index_name='product_code',
                             title='Rebalance Detail',
                             filepath=self.plan_path)

        # 상태 변경 -> PLANNING
        self.update_status(Status.PLANNING)

        return self

    def adjust_plan(self):
        """ 최신화된 가격을 토대로 리밸런싱 플랜 생성 """
        return self

    def _calculate_appropriate_price(self, portfolio: dict, how: str = How.MARKET, n_diff: int = 3):
        if how == How.MARKET:
            # 시장가에 판매
            return 0

        elif how == How.N_DIFF:
            # 매수시에는 (현재가) - quote_unit * n_diff 에서 매수(-)
            # 매도시에는 (현재가) + quote_unit * n_diff 에서 매도(+)
            print(portfolio)
            sign = -1 if portfolio['difference'] > 0 else 1
            return portfolio['current'] + portfolio['quote_unit'] * n_diff * sign

        elif how == How.REGRESSION:
            # TBD
            return 0
        else:
            pass

        return 0

    def execute_plan(self, how: str = How.MARKET, n_diff: int = 3) -> List[str]:
        """ 리밸런싱 플랜 실행 """
        dtype = {
            'product_code': str,
            'market_code': str,
            'difference': int,
            'current': float,
            'quote_unit': float,
        }

        planned_portfoilos = (
            pd.read_csv(self.plan_path,
                        sep=',',
                        dtype=dtype,
                        usecols=list(dtype.keys()))
                .to_dict(orient='records')
        )

        # create empty orders
        orders = []

        for portfolio in planned_portfoilos:

            params = portfolio.copy()

            # 매수/매도 값 계산difference
            difference: int = params.pop('difference')

            if difference == 0:
                continue

            # count: 양수
            params.bulk_update(count=abs(difference))

            # price: 계산
            price = self._calculate_appropriate_price(portfolio=dict(**params,
                                                                     difference=difference),
                                                      how=how,
                                                      n_diff=n_diff)
            params.bulk_update(price=price)

            if difference > 0:
                order_num: str = self.api.buy_stock(**params)
                params['order_type'] = OrderType.BUY

            else:
                order_num: str = self.api.buy_stock(**params)
                params['order_type'] = OrderType.SELL

            params['order_num'] = order_num

            orders.append(params)

        # save order data
        pd.DataFrame(orders).to_csv(self.order_path, sep=',', index=False)

        # 상태 변경 -> EXECUTED
        self.update_status(Status.EXECUTED)

        return orders

    def get_order_status(self) -> List[Dict]:
        dtype = {
            'product_code': str,
            'market_code': str,
            'count': int,
            'order_num': str,
            'order_type': str,
        }

        if os.path.exists(self.order_path):
            report_orders = pd.read_csv(self.order_path, sep=',', dtype=dtype).to_dict(orient='records')
        else:
            raise ReportNotFoundException(f'Report의 order_path에 파일이 없습니다: {self.order_path}')

        created_date = datetime.strptime(self.created_time, '%Y%m%d_%H_%M_%S').strftime('%Y%m%d')

        if self.is_domestic:
            processed_orders = [
                order_result.get('order_num')
                for order_result in self.api.get_processed_orders(start_date=created_date)
            ]
            unprocessed_orders = [
                order_result.get('order_num')
                for order_result in self.api.get_unprocessed_orders()
            ]

        else:
            # 거래소 코드 리스트
            market_codes = [order['market_code'] for order in report_orders]

            # 거래소 코드마다 조회
            processed_orders = [
                order_result.get('order_num')
                for market_code in market_codes
                for order_result in self.api.get_processed_orders(start_date=created_date,
                                                                  market_code=market_code)
            ]
            unprocessed_orders = [
                order_result.get('order_num')
                for market_code in market_codes
                for order_result in self.api.get_unprocessed_orders(market_code=market_code)
            ]

        for report_order in report_orders:
            order_num = report_order['order_num']

            # 상태 업데이트(체결/미체결)
            if order_num in processed_orders:
                report_order.bulk_update('process', True)
            elif order_num in unprocessed_orders:
                report_order.bulk_update('process', False)
            else:
                report_order.bulk_update('process', None)

        return report_orders

    def wait_for_all_orders_to_be_processed(self,
                                            timeout: int = None,
                                            retries: int = None,
                                            retry_delay: int = 60) -> List[Dict]:
        """
        order_path에 위치한 주문 리스트가 모두 체결될때까지 기다림

        :param timeout: 초과시 TimeoutError 발생(분).
        :param retries: 재시도 횟수 제한
        :param retry_delay: while문 재실행시 delay(초)
        :return: 주문 리스트
        """
        start_time = datetime.now()
        count = 0

        while True:
            count += 1

            # 처음 실행부터 걸린 시간(분)
            elapsed_minutes = (datetime.now() - start_time).seconds / 60

            if elapsed_minutes > timeout * 60:
                raise TimeoutError(f'설정된 Timeout을 초과하였습니다.: {timeout}s')

            orders = self.get_order_status()

            # get orders
            order_processes = [order
                               for order in orders
                               if not order['process']]

            # all processes True -> break
            if len(order_processes) == 0:
                break

            if retries:
                if count > retries:
                    return orders

            # sleep
            time.sleep(retry_delay)

        return orders

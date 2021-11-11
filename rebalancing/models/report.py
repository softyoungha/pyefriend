import os
from datetime import datetime
import pandas as pd
import logging
from typing import Union, Dict, List
from IPython.display import display, Markdown
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean

from pyefriend import load_api, encrypt_password_by_efriend_expert
from pyefriend.const import MarketCode, Target

from rebalancing.exceptions import ReportNotFoundException
from rebalancing.settings import IS_JUPYTER_KERNEL
from rebalancing.config import REPORT_DIR
from rebalancing.models import Product, Portfolio, ProductHistory, Setting
from rebalancing.utils.log import get_logger
from rebalancing.utils.orm_helper import provide_session
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


class How:
    """ 매수/매도시 가격 결정 방법 """
    MARKET = 'market'   # 시장가격에 매수/패도
    N_DIFF = 'n_diff'   # 호가 단위 x n 원 아래에서 매수/ 위에서 매도
    REGRESSION = 'regression'   # linear regression


class Report(Base):
    __tablename__ = 'report'

    # columns
    id = Column(Integer(), primary_key=True, autoincrement=True)
    report_name = Column(String(Length.ID), comment='리포트명')
    created_time = Column(String(Length.TYPE), comment='Report 생성일자')
    target = Column(String(Length.TYPE), comment="국내/해외 여부('domestic', 'overseas')")
    account = Column(String(Length.ID), comment='계좌명')
    encrypted_password = Column(String(Length.DESC), comment='암호화된 비밀번호')
    status = Column(String(Length.TYPE), default=Status.CREATED, comment='상태')

    __table_args__ = (
        Index('idx_report', target, report_name, created_time, unique=True),
    )

    def __init__(self,
                 target: str,
                 test: bool = True,
                 account: str = None,
                 password: str = None,
                 encrypted_password: str = None,
                 created_time: str = None,
                 prompt: bool = False,
                 status: str = Status.CREATED,
                 **kwargs):
        """
        re-balancing 실행 후 자동 리포트 생성

        :param target:          'domestic', 'overseas'
        :param test:            setting 테이블 내의 모의주문 계정 사용여부(account, password)
        :param account:         setting 테이블 에 있는 계좌가 아닌 입력된 계좌를 사용
        :param password:        account를 직접 입력했을 경우 사용할 password
        :param created_time:   [%Y%m%d_%H_%M_%S, str] 입력될 경우 해당 시간에 계산된 rebalancing 결과를 바라봅니다.
                                입력되지 않을 경우 Executor가 실행된 시간으로 저장합니다(report_path의 폴더구분으로 사용됩니다)
        :param prompt:          True일 경우 report_name을 직접 입력할 수 있습니다. False일 경우 계좌명을 report_name으로 사용합니다.
        """
        super().__init__(**kwargs)

        # initialize
        self.init()

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

        # set target
        assert target in (Target.DOMESTIC, Target.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."
        self.target = target

        # set account & encrypted_password
        if account:
            assert password is not None, "account가 입력되면 password도 입력되어야 합니다."

        elif test:
            # 모의주문 계정
            account = Setting.get_value('ACCOUNT', 'TEST_ACCOUNT')
            password = Setting.get_value('ACCOUNT', 'TEST_PASSWORD')
        else:
            # 실제 계정
            account = Setting.get_value('ACCOUNT', 'REAL_ACCOUNT')
            password = Setting.get_value('ACCOUNT', 'REAL_PASSWORD')

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

        display_only_jupyter(f'##### 다음 경로에 report가 저장됩니다. \n{self.report_path}')

        # set status
        self.status = status

    def __repr__(self):
        return f"<Report(code='{self.report_name}')>"

    def init(self):
        self._report_path = None
        self._logger = None
        self._api = None
        return self

    @provide_session
    def delete(self, session=None):
        session.delete(self)

    @provide_session
    def save(self, delete_if_exists: bool = False, session=None):
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
        query = session.query(cls).filter(cls.report_name == report_name)

        if statuses:
            query = query.filter(cls.status.in_(statuses))

        if created_time:
            query = (
                query
                    .filter(cls.created_time == created_time)
                    .order_by(cls.created_time.desc())
            )

        row = query.first()

        if row:
            return row.init()
        else:
            if raise_if_not_exists:
                raise ReportNotFoundException()
            else:
                return None

    @provide_session
    def update_status(self, status: str, session=None):
        report = session.query(Report).filter(Report.id==self.id).first()
        report.status = status

    @property
    def api(self):
        if self._api is None:
            self._api = load_api(target=self.target,
                                 account=self.account,
                                 encrypted_password=self.encrypted_password,
                                 logger=self.logger)
        return self._api

    @property
    def is_domestic(self):
        return self.target == Target.DOMESTIC

    @property
    def unit(self):
        return self.api.unit

    @property
    def report_path(self):
        if not self._report_path:
            # get
            report_dir = REPORT_DIR

            # expand ~ -> HOME path
            report_dir = os.path.expanduser(report_dir)

            # abspath
            report_dir = os.path.abspath(report_dir)

            # join
            report_path = os.path.join(report_dir, self.report_name, f'{self.target}_{self.created_time}')

            # create tree
            os.makedirs(report_path, exist_ok=True)

            # set
            self._report_path = report_path

        return self._report_path

    def path(self, file_name: str):
        return os.path.join(self.report_path, file_name)

    @property
    def summary_path(self):
        return self.path('summary.csv')

    @property
    def plan_path(self):
        return self.path('plan.csv')

    @property
    def name(self):
        return f'{self.target}_{self.report_name}_{self.created_time}'

    @property
    def logger(self):
        if not self._logger:
            self._logger = get_logger(name=self.name, path=self.path('log.txt'))
        return self._logger

    def remove_logger(self):
        while self.logger.hasHandlers():
            self.logger.removeHandler(self.logger.handlers[0])

    @provide_session
    def refresh_prices(self, session=None):
        if self.is_domestic:
            products = Product.list(MarketCode.KRX, session=session)

        else:
            products = Product.list(only_oversea=True, session=session)

        # update 'Product'
        self.logger.info('종목 리스트를 최신화합니다.')
        product_infos = [(product.code,
                          self.api.get_stock_info(product_code=product.code,
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
        Product.update(product_infos)
        self.logger.info(f'종목 리스트가 최신화되었습니다: {len(product_infos)}')

        # update 'ProductHistory'
        self.logger.info('종목 History를 최신화합니다.')
        product_histories = [(product.name,
                              self.api.get_stock_histories(product_code=product.code,
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
        ProductHistory.insert(product_histories)

        self.logger.info('종목 History가 최신화되었습니다.')

        return self

    def get_prices(self) -> List[Dict]:
        
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

    def make_plan(self):
        """
        이미 매수된 종목이면서 포트폴리오에 포함되지 않은 종목은 제외됩니다.

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

        :return:
        """

        # available_percent: 사용할 금액 %
        available_percent = Setting.get_value('AMOUNT_LIMIT', 'AVAILABLE', dtype=float)

        # percent: 국내/해외 주식 비율 %
        if self.is_domestic:
            percent = Setting.get_value('AMOUNT_LIMIT', 'DOMESTIC', dtype=float)
            numeric_type = int

        else:
            percent = Setting.get_value('AMOUNT_LIMIT', 'OVERSEAS', dtype=float)
            numeric_type = float

        # list all portfolio with use_yn = True
        portfolios = Portfolio.list(is_domestic=self.is_domestic, only_y=True)

        # product_codes_in_portfolio: 포트폴리오에 포함된 product_code
        product_codes_in_portfolio = [product_code
                                      for product_code, _, _, _, _ in portfolios]

        # 현재 주식 금액: 예수금, 주식들, 전체 금액
        deposit, stocks, total_amount = self.api.evaluate_amount(product_codes_in_portfolio)
        self.logger.info(f"{'deposit':>25}{deposit:>15,} {self.unit} "
                         f"(총 예수금)")
        self.logger.debug(f"{'stocks':>25}(현재 매수한 주식 리스트)\n{stocks} ")
        self.logger.info(f"{'total_amount':>25}{total_amount:>15,} {self.unit} "
                         f"(총 예수금 + 포트폴리오 포함 & 매수된 종목들의 평가 금액 전체 합)")

        # stocks: list -> dict
        stocks = {stock['product_code']: stock for stock in stocks}

        # available_total_amount: 전체 금액 중 사용할 금액
        available_total_amount = total_amount * available_percent
        self.logger.info(f"{'available_total_amount':>25}{int(available_total_amount):>15,} {self.unit} "
                         f"(전체 금액 중 사용할 금액)")

        # planned_budge: 국내/해외 투자에 사용할 금액
        planned_budge = available_total_amount * percent
        self.logger.info(f"{'planned_budge':>25}{int(planned_budge):>15,} {self.unit} "
                         f"(투자에 사용할 금액)")

        # total_weights: 전체 weight
        total_weights = sum([weight for _, _, _, weight, _ in portfolios])

        # init list & sum
        plan_index = []
        plan_data = []
        asis_total_amount = 0

        for product_code, product_name, current, weight, quote_unit in portfolios:
            # get stock
            stock = stocks.get(product_code, {})

            # calculate
            asis_count = stock.get('count', 0)
            asis_amount = stock.get('price', 0)
            planned_rate = weight / total_weights
            planned_amount = planned_budge * planned_rate
            tobe_count = round(planned_amount / current)
            tobe_amount = numeric_type(current * tobe_count)
            difference = int(tobe_count - asis_count)

            # append
            plan_index.append(product_code)
            plan_data.append(
                dict(product_name=product_name,
                     current=numeric_type(current),
                     weight=weight,
                     quote_unit=quote_unit,
                     asis_count=asis_count,
                     asis_amount=asis_amount,
                     planned_rate=planned_rate,
                     planned_amount=numeric_type(planned_amount),
                     tobe_count=tobe_count,
                     tobe_amount=tobe_amount,
                     difference=difference)
            )

            asis_total_amount += asis_amount

        tobe_total_amount = sum([portfoilo.get('tobe_amount') for portfoilo in plan_data])
        self.logger.info(f"{'asis_total_amount':>25}{asis_total_amount:>15,} {self.unit} "
                         f"(리밸런싱 전 전체 금액)")
        self.logger.info(f"{'tobe_total_amount':>25}{tobe_total_amount:>15,} {self.unit} "
                         f"(리밸런싱 후 전체 금액)")
        self.logger.info(f"{'리밸런싱 후 감소 금액':>25}: {(numeric_type(planned_budge) - tobe_total_amount):>15,} {self.unit} ")

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
                             index_name='결과생성일자',
                             title='Rebalance Result',
                             filepath=self.summary_path)

        # plan dataframe
        df_plan = pd.DataFrame(plan_data, index=plan_index)
        self._print_log_save(df=df_plan,
                             index_name='product_code',
                             title='Rebalance Detail',
                             filepath=self.plan_path)

        if not self.is_domestic:
            # 환율 계산
            currency = self.api.currency

            # result dataframe(WON)
            df_results_won = df_results.copy()
            for column in results.keys():
                df_results_won[column] = [int(value * currency) for value in df_results_won[column]]
            self._print_log_save(df=df_results_won,
                                 index_name='결과생성일자',
                                 title='Rebalance Result(WON)',
                                 filepath='summary_won.csv')

            # plan dataframe(WON)
            df_plan_won = df_plan.copy()
            for column in ['current', 'asis_amount', 'planned_amount', 'tobe_amount']:
                df_plan_won[column] = [int(value * currency) for value in df_plan_won[column]]
            self._print_log_save(df=df_plan_won,
                                 index_name='결과생성일자',
                                 title='Rebalance Detail(WON)',
                                 filepath='plan_won.csv')

        self.update_status(Status.PLANNING)

        return self

    def adjust_plan(self):
        return self

    def execute_plan(self, how: str = How.MARKET):
        dtype = {
            'market_code': str,
            'product_name': str,
            'product_code': str,
            'weight': float
        }

        df = pd.read_csv(self.plan_path, sep=',', dtype=dtype)

        self.update_status(Status.EXECUTED)
        return self

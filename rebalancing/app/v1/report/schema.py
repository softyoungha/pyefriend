from typing import Optional
from pydantic import BaseModel, Field
from rebalancing.utils.const import OrderType


ReportNameField = Field(...,
                        title='리포트명',
                        description='리포트 생성 기준')
CreatedTimeField = Field(None,
                         title='Report 실행시간',
                         description='Report 생성시간(실행시간)',
                         example='20211109_07_19_39')


class ReportInput(BaseModel):
    target: str = Field(...,
                        title='타겟장',
                        description="국내/해외 여부('domestic', 'overseas')",
                        example='domestic')
    account: Optional[str] = Field(None,
                                   title='계좌명',
                                   description='config.yml에 있는 계좌가 아닌 입력된 계좌를 사용',
                                   example='5005775101')
    password: Optional[str] = Field(None,
                                    title='비밀번호',
                                    description='account를 직접 입력했을 경우 사용할 password',
                                    example='password')
    created_time: Optional[str] = CreatedTimeField


class ReportOutput(BaseModel):
    report_name: str = ReportNameField
    created_time: str = CreatedTimeField


class CreateReportOutput(ReportOutput):
    account: str = Field(..., title='테스트 성공시 사용될 계좌명')
    is_vts: bool = Field(..., title='모의투자여부')


class PricesOutput(BaseModel):
    product_code: str = Field(..., title='종목코드')
    product_name: str = Field(..., title='종목명')
    market_code: str = Field(..., title='거래소(KRX: 한국거래소/NASD/NYSE/AMEX')
    current: float = Field(..., title='현재가')
    minimum: float = Field(..., title='최저가')
    maximum: float = Field(..., title='최고가')
    opening: float = Field(..., title='시가')
    base: float = Field(..., title='종가')


class OrderBase(BaseModel):
    product_code: str = Field(..., title='종목코드')
    market_code: str = Field(..., title='거래소(KRX: 한국거래소/NASD/NYSE/AMEX')
    count: str = Field(..., title='매도/매수 수량')
    order_num: str = Field(..., title='주문번호')
    order_type: OrderType = Field(..., title='매도/매수 구분')


class ExecuteReportOutput(OrderBase):
    quote_unit: str = Field(..., title='호가단위')
    price: str = Field(..., title='매도/매수 가격')


class GetOrderOutput(OrderBase):
    process: Optional[str] = Field(..., title='주문 상태')

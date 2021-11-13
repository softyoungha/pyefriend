from typing import Optional, Union, List
from pydantic import BaseModel, Field

from rebalancing.utils.const import Market

# vars
Number = Union[int, float]
MarketField = Field(None,
                    title='장 구분 코드',
                    description='해외주식일 경우'
                                '해외거래소코드(NASD/ NYSE / AMEX 등 4글자 문자열) 입력 필수')


class LoginInput(BaseModel):
    """ 로그인 정보 """
    market: Market = Field(...,
                           title='타겟장',
                           description="국내/해외 여부('domestic', 'overseas')",
                           example=Market.DOMESTIC)
    account: str = Field(None,
                         title='계좌명',
                         description='config.yml에 있는 계좌가 아닌 입력된 계좌를 사용',
                         example='5005775101')
    password: str = Field(None,
                          title='비밀번호',
                          description='account를 직접 입력했을 경우 사용할 password',
                          example='password')


class LoginOutput(LoginInput):
    account: str = Field(..., title='테스트 성공시 사용될 계좌명')
    is_vts: bool = Field(..., title='모의투자여부')


class Deposit(BaseModel):
    deposit: Number = Field(..., title='예수금')


class Stock(BaseModel):
    product_code: str = Field(..., title='종목코드')
    product_name: str = Field(..., title='종목명')
    current: Number = Field(..., title='현재가')
    count: int = Field(..., title='수량')
    price: Number = Field(..., title='총 평가금액')
    unit: str = Field(..., title='단위')


class Amount(Deposit):
    stocks: List[Stock] = Field(None, title='주식리스트')
    total_amount: Number = Field(..., title='주식 전체 평가금액 + 예수금')


class Currency(BaseModel):
    currency: float = Field(..., title='환율')


class ProductHistory(BaseModel):
    standard_date: str = Field(..., title='영업일자')
    minimum: Number = Field(..., title='저가')
    maximum: Number = Field(..., title='고가')
    opening: Number = Field(..., title='시가')
    closing: Number = Field(..., title='종가')
    volume: int = Field(..., title='체결량')


class BuyOrSellInput(LoginInput):
    product_code: str = Field(..., title='종목코드')
    market_code: Optional[Market] = MarketField
    count: int = Field(..., title='매수/매도수량')
    price: Number = Field(..., title='매수/매도가격')


class OrderNum(BaseModel):
    order_num: str = Field(..., title='주문번호')


class UnProcessedOrdersInput(LoginInput):
    market_code: Optional[Market] = MarketField


class UnProcessedOrdersOutput(OrderNum):
    order_date: str = Field(..., title='주문일자(YYmmdd)')
    origin_order_num: str = Field(..., title='원주문번호')
    product_code: str = Field(..., title='종목코드')
    count: int = Field(..., title='주문수량')
    order_type: str = Field(..., title='매도매수구분')


class ProcessedOrdersInput(UnProcessedOrdersInput):
    start_date: Optional[str] = Field(None, title='조회시작기간(YYmmdd)')


class ProcessedOrdersOutput(UnProcessedOrdersOutput):
    price: str = Field(..., title='체결금액')


class CancelInput(LoginInput, OrderNum):
    count: int = Field(..., title='주문수량')
    market_code: Optional[Market] = MarketField
    product_code: Optional[str] = Field(None, title='종목코드')


class CancelAllInput(LoginInput):
    market_code: Optional[Market] = MarketField

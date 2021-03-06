from typing import Optional, Union, List

from pydantic import BaseModel, Field

from pyefriend_api.utils.const import Market

# vars
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
    deposit: float = Field(..., title='예수금')


class Stock(BaseModel):
    product_code: str = Field(..., title='종목코드')
    product_name: str = Field(..., title='종목명')
    current: float = Field(..., title='현재가')
    count: int = Field(..., title='수량')
    price: float = Field(..., title='총 평가금액')
    my_price: float = Field(..., title='매입금액')
    unit: str = Field(..., title='단위')


class Amount(Deposit):
    stocks: List[Stock] = Field(None, title='주식리스트')
    total_amount: float = Field(..., title='주식 전체 평가금액 + 예수금')


class Currency(BaseModel):
    currency: float = Field(..., title='환율')


class PriceHistory(BaseModel):
    standard_date: str = Field(..., title='영업일자')
    minimum: float = Field(..., title='저가')
    maximum: float = Field(..., title='고가')
    opening: float = Field(..., title='시가')
    closing: float = Field(..., title='종가')
    volume: int = Field(..., title='체결량')


class BuyOrSellInput(LoginInput):
    product_code: str = Field(..., title='종목코드')
    market_code: Optional[str] = MarketField
    count: int = Field(..., title='매수/매도수량')
    price: float = Field(..., title='매수/매도가격')


class OrderNum(BaseModel):
    order_num: str = Field(..., title='주문번호')


class UnProcessedOrderInput(LoginInput):
    market_code: Optional[str] = MarketField


class UnProcessedOrderOutput(OrderNum):
    order_date: str = Field(..., title='주문일자(YYmmdd)')
    origin_order_num: Optional[str] = Field(None, title='원주문번호')
    product_code: str = Field(..., title='종목코드')
    count: int = Field(..., title='주문수량')
    order_type: str = Field(..., title='매도매수구분')
    order_type_name: Optional[str] = Field(None, title='매도매수구분명')
    executed_count: Optional[int] = Field(None, title='총체결수량')
    executed_amount: Optional[int] = Field(None, title='총체결금액')


class ProcessedOrderInput(UnProcessedOrderInput):
    start_date: Optional[str] = Field(None, title='조회시작기간(YYmmdd)')


class ProcessedOrderOutput(OrderNum):
    order_date: str = Field(..., title='주문일자(YYmmdd)')
    origin_order_num: Optional[str] = Field(None, title='원주문번호')
    product_code: str = Field(..., title='종목코드')
    count: int = Field(..., title='주문수량')
    price: float = Field(..., title='체결금액')
    order_type: str = Field(..., title='매도매수구분')
    order_type_name: Optional[str] = Field(None, title='매도매수구분명')
    executed_count: Optional[int] = Field(None, title='총체결수량')
    executed_amount: Optional[float] = Field(None, title='총체결금액')
    is_cancel: Optional[str] = Field(None, title='취소여부')


class CancelInput(OrderNum, LoginInput):
    count: int = Field(..., title='주문수량')
    market_code: Optional[str] = MarketField
    product_code: Optional[str] = Field(None, title='종목코드')


class CancelAllInput(LoginInput):
    market_code: Optional[str] = MarketField


class GetProductInput(LoginInput):
    product_code: str = Field(..., title='종목코드')
    market_code: Optional[str] = MarketField


class ProductInfo(BaseModel):
    product_name: str = Field(..., title='품목명')
    price: float = Field(..., title='현재가')
    market_code: Optional[str] = MarketField
    sector_code: Optional[str] = Field(None, title='업종 중유형 코드')
    per: Optional[float] = Field(None, title='PER')
    eps: Optional[float] = Field(None, title='EPS')


class ProductPrice(BaseModel):
    current: float = Field(..., title='주식 현재가')
    minimum: float = Field(..., title='주식 최저가')
    maximum: float = Field(..., title='주식 최고가')
    opening: float = Field(..., title='주식 시가')
    base: float = Field(..., title='주식 기준가(전일 종가)')
    total_volume: int = Field(..., title='누적 거래량')


class ProductChart(BaseModel):
    executed_date: str = Field(..., title='체결일자(YYYYmmdd)')
    executed_time: str = Field(..., title='체결시간(HHMMSS)')
    current: float = Field(..., title='현재가')
    minimum: float = Field(..., title='저가')
    maximum: float = Field(..., title='고가')
    opening: float = Field(..., title='시가')
    volume: int = Field(..., title='체결량')
    total_volume: int = Field(..., title='누적 체결량')


class SectorChart(BaseModel):
    executed_time: str = Field(..., title='체결시간(HHMMSS)')
    current: float = Field(..., title='현재가')
    volume: int = Field(..., title='체결량')
    total_volume: int = Field(..., title='누적 체결량')


class GetSpreadInput(GetProductInput):
    pass


class AskBid(BaseModel):
    price: float = Field(..., title='매수/매도 가격')
    count: int = Field(..., title='매수/매도 잔량')
    icdc: int = Field(..., title='매수/매도 잔량 증감(increase or decrease)')


class ProductSpread(BaseModel):
    accepted_time: str = Field(..., title='호가 접수시간')
    total_ask_count: int = Field(..., title='총 매도호가 잔량')
    total_bid_count: int = Field(..., title='총 매수호가 잔량')
    total_ask_count_icdc: int = Field(..., title='총 매도호가 잔량 증감')
    total_bid_count_icdc: int = Field(..., title='총 매수호가 잔량 증감')
    asks: List[AskBid] = Field(..., title='매도호가 정보 리스트')
    bids: List[AskBid] = Field(..., title='매수호가 정보 리스트')


class PopularProduct(BaseModel):
    product_code: str = Field(..., title='종목코드')
    product_name: str = Field(..., title='종목명')
    product_status: str = Field(..., title='종목상태')
    current: float = Field(..., title='현재가')
    compared_yesterday_amount: int = Field(..., title='전일 대비 금액')
    compared_yesterday_sign: str = Field(..., title='전일 대비 부호')
    total_volume: int = Field(..., title='누적 거래량')
    total_amount: float = Field(..., title='누적 거래 대금')
    continuous_maximum_days: int = Field(..., title='연속 상한 일수')
    continuous_increase_days: int = Field(..., title='연속 상승 일수')
    continuous_nochange_days: int = Field(..., title='연속 보합 일수')
    continuous_decrease_days: int = Field(..., title='연속 하락 일수')
    continuous_minimum_days: int = Field(..., title='연속 하한 일수')


class GetSectorInput(LoginInput):
    sector_code: str = Field(..., title='업종 코드')


class SectorInfo(BaseModel):
    current: float = Field(..., title='현재가')
    opening: float = Field(..., title='시가')
    minimum: float = Field(..., title='최저가')
    maximum: float = Field(..., title='최고가')
    compared_yesterday_amount: float = Field(..., title='전일 대비')
    compared_yesterday_sign: str = Field(..., title='전일 대비 부호')
    last_volume: int = Field(..., title='전일 거래량')
    total_volume: int = Field(..., title='누적 거래량')
    increase_product_count: int = Field(..., title='상승 종목 수')
    decrease_product_count: int = Field(..., title='하락 종목 수')
    nochange_product_count: int = Field(..., title='보합 종목 수')
    maximum_product_count: int = Field(..., title='상한 종목 수')
    minimum_product_count: int = Field(..., title='하한 종목 수')


class GetSectorChartInput(GetSectorInput):
    pass


class ForeignerNetBuySell(BaseModel):
    rank: int = Field(..., title='순위')
    product_code: str = Field(..., title='종목코드')
    product_name: str = Field(..., title='종목명')
    closing_price: float = Field(..., title='종가')
    foreigner_total_ask: int = Field(..., title='외국인총매도수량')
    foreigner_total_bid: int = Field(..., title='외국인총매수수량')
    total_volume: int = Field(..., title='거래량')
    net_quantity: int = Field(..., title='합산수량')
    fake_net_quantity: int = Field(..., title='합산수량(가집계)')

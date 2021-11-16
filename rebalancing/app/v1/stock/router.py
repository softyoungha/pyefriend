import os
from typing import Optional, List
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException

from pyefriend import load_api
from pyefriend.exceptions import NotConnectedException, AccountNotExistsException
from rebalancing.utils.const import DWM
from rebalancing.app.auth import login_required
from .schema import *

r = APIRouter(prefix='/stock',
              tags=['stock'])


@r.post('/', response_model=LoginOutput)
async def test_api(request: LoginInput, user=Depends(login_required)):
    """### API 테스트 """
    try:
        context = request.dict()

        # create api
        api = load_api(**context)

        # get context
        context.update(account=api.account,
                       is_vts=api.controller.IsVTS())

        return context

    except NotConnectedException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=str(e))

    except AccountNotExistsException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=str(e))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f'{e.__class__.__name__}: \n{str(e)}')


@r.post('/account', response_model=Amount)
async def evaluate_total_amount(request: LoginInput,
                                overall: bool = True,
                                user=Depends(login_required)):
    """### 계좌 전체 금액  """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    deposit, stocks, total_amount = api.evaluate_amount(overall=overall, currency=False)
    return {
        'deposit': deposit,
        'stocks': stocks,
        'total_amount': total_amount
    }


@r.post('/account/deposit', response_model=Deposit)
async def get_deposit_amount(request: LoginInput,
                             overall: bool = False,
                             user=Depends(login_required)):
    """### 예수금 전체 금액 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return {
        'deposit': api.get_deposit(overall=overall)
    }


@r.post('/account/stocks', response_model=List[Stock])
async def get_stocks_list(request: LoginInput,
                          overall: bool = False,
                          user=Depends(login_required)):
    """### 현재 보유한 주식 리스트 반환 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_stocks(overall=overall)


@r.post('/info/currency', response_model=Currency)
async def get_currency(request: LoginInput, user=Depends(login_required)):
    """ 1 달러 -> 원으로 환전할때의 현재 기준 예상환율을 반환 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return {
        'currency': api.currency
    }


@r.post('/info/kospi', response_model=List[ProductHistory])
async def get_kospi_histories(request: LoginInput,
                              standard: DWM = DWM.D,
                              user=Depends(login_required)):
    """ kospi 히스토리 반환 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_kospi_histories(standard=standard)


@r.post('/info/sp500', response_model=List[ProductHistory])
async def get_sp500_histories(request: LoginInput,
                              standard: DWM = DWM.D,
                              user=Depends(login_required)):
    """ SP&500 히스토리 반환 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_sp500_histories(standard=standard)


@r.post('/trade/buy', response_model=OrderNum)
async def buy_stock(request: BuyOrSellInput, user=Depends(login_required)):
    """### 설정한 price보다 낮으면 product_code의 종목 시장가로 매수 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    order_num = api.buy_stock(product_code=request.product_code,
                              count=request.count,
                              price=request.price,
                              market_code=request.market_code)

    return {
        'order_num': order_num
    }


@r.post('/trade/sell', response_model=OrderNum)
async def sell_stock(request: BuyOrSellInput, user=Depends(login_required)):
    """### 설정한 price보다 낮으면 product_code의 종목 매도 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    order_num = api.sell_stock(product_code=request.product_code,
                               count=request.count,
                               price=request.price,
                               market_code=request.market_code)

    return {
        'order_num': order_num
    }


@r.post('/order/processed', response_model=List[ProcessedOrderOutput])
async def get_processed_orders(request: ProcessedOrderInput, user=Depends(login_required)):
    """### start_date 이후의 체결된 주문 리스트 반환 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_processed_orders(start_date=request.start_date,
                                    market_code=request.market_code)


@r.post('/order/unprocessed', response_model=List[UnProcessedOrderOutput])
async def get_unprocessed_orders(request: UnProcessedOrderInput, user=Depends(login_required)):
    """### 미체결된 주문 리스트 반환 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_unprocessed_orders(market_code=request.market_code)


@r.post('/order/cancel', response_model=OrderNum)
async def cancel_order(request: CancelInput, user=Depends(login_required)):
    """### 주문 취소 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return {
        'order_num': api.cancel_order(order_num=request.order_num,
                                      count=request.count,
                                      product_code=request.product_code,
                                      market_code=request.market_code)
    }


@r.post('/order/cancel-all', response_model=List[str])
async def cancel_unprocessed_order(request: CancelAllInput, user=Depends(login_required)):
    """### 미체결된 모든 리스트 취소 """
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.cancel_all_unprocessed_orders(market_code=request.market_code)


@r.post('/product/chart', response_model=List[ProductChart])
async def get_chart(request: GetChartInput,
                    user=Depends(login_required)):
    """### interval별 종목의 현/시/고/체결량 제공  """
    if request.market != Market.DOMESTIC:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='해당 URI는 국내(domestic)만 가능합니다.')

    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_chart(product_code=request.product_code,
                         interval=request.interval)


@r.post('/product/spread', response_model=ProductSpread)
async def get_spread(request: GetSpreadInput,
                     user=Depends(login_required)):
    """### 종목 현재시간 기준 매수/매도호가 정보  """
    if request.market != Market.DOMESTIC:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='해당 URI는 국내(domestic)만 가능합니다.')

    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_spread(product_code=request.product_code)


@r.post('/product/popular', response_model=List[PopularProduct])
async def list_popular_products(request: LoginInput,
                                direction: Direction = Direction.INCREASE,
                                index: IndexCode = IndexCode.TOTAL,
                                last_day: bool = False,
                                user=Depends(login_required)):
    """
    ### 상승 하락 종목 리스트
    - direction: 'MAXIMUM' 상한, 'INCREASE' 상승, 'NOCHANGE' 보합, 'DECREASE' 하락, 'MINIMUM' 하한
    - index_code: '0000' 전체, '0001' 코스피, '1001' 코스닥
    """
    if request.market != Market.DOMESTIC:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail='해당 URI는 국내(domestic)만 가능합니다.')

    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.list_popular_products(direction=direction,
                                     index_code=index,
                                     last_day=last_day)

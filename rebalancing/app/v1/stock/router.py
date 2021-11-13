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
async def evaluate_amount(request: LoginInput,
                          overall: bool = False,
                          user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    deposit, stocks, total_amount = api.evaluate_amount(overall=overall, currency=False)
    return {
        'deposit': deposit,
        'stocks': stocks,
        'total_amount': total_amount
    }


@r.post('/account/deposit', response_model=Deposit)
async def evaluate_amount(request: LoginInput,
                          overall: bool = False,
                          user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return {
        'deposit': api.get_deposit(overall=overall)
    }


@r.post('/account/stocks', response_model=List[Stock])
async def evaluate_amount(request: LoginInput,
                          overall: bool = False,
                          user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_stocks(overall=overall)


@r.post('/info/currency', response_model=Currency)
async def get_currency(request: LoginInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return {
        'currency': api.currency
    }


@r.post('/info/kospi', response_model=List[ProductHistory])
async def get_kospi_histories(request: LoginInput,
                              standard: DWM = DWM.D,
                              user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_kospi_histories(standard=standard)


@r.post('/info/sp500', response_model=List[ProductHistory])
async def get_kospi_histories(request: LoginInput,
                              standard: DWM = DWM.D,
                              user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_sp500_histories(standard=standard)


@r.post('/trade/buy', response_model=OrderNum)
async def buy_stock(request: BuyOrSellInput, user=Depends(login_required)):
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
async def buy_stock(request: BuyOrSellInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    order_num = api.sell_stock(product_code=request.product_code,
                               count=request.count,
                               price=request.price,
                               market_code=request.market_code)

    return {
        'order_num': order_num
    }


@r.post('/order/processed', response_model=List[ProcessedOrdersOutput])
async def get_processed_orders(request: ProcessedOrdersInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_processed_orders(start_date=request.start_date,
                                    market_code=request.market_code)


@r.post('/order/unprocessed', response_model=List[UnProcessedOrdersOutput])
async def get_unprocessed_orders(request: UnProcessedOrdersInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.get_unprocessed_orders(market_code=request.market_code)


@r.post('/order/cancel', response_model=OrderNum)
async def cancel_order(request: CancelInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.cancel_order(order_num=request.order_num,
                            count=request.count,
                            product_code=request.product_code,
                            market_code=request.market_code)


@r.post('/order/cancel', response_model=OrderNum)
async def cancel_order(request: CancelInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.cancel_order(order_num=request.order_num,
                            count=request.count,
                            product_code=request.product_code,
                            market_code=request.market_code)


@r.post('/order/cancel-all', response_model=List[str])
async def cancel_unprocessed_order(request: CancelAllInput, user=Depends(login_required)):
    # create api
    api = load_api(**request.dict(include={'market', 'account', 'password'}))
    return api.cancel_all_unprocessed_orders(market_code=request.market_code)

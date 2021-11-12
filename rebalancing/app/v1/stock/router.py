import os
from typing import Optional, List
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException

from pyefriend import load_api
from rebalancing.app.auth import login_required
from .schema import LoginTest, LoginTestOutput

r = APIRouter(prefix='/stock',
              tags=['stock'])
from pyefriend.exceptions import NotConnectedException, AccountNotExistsException


@r.get('/', response_model=LoginTestOutput)
async def test_api(request: LoginTest, user=Depends(login_required)):
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


from fastapi import APIRouter, Response, status, Depends

from pyefriend_api.app.auth import login_required
from pyefriend_api.utils.db import init_db, reset_db

r = APIRouter(prefix='/database',
              tags=['database'])


@r.post('/init-db', status_code=status.HTTP_200_OK)
async def initialize_database(user=Depends(login_required)):
    """### database 내 모든 테이블들 생성(이미 존재하는 테이블은 Skip) """
    init_db()

    return Response('Success', status_code=status.HTTP_200_OK)


@r.post('/reset-db', status_code=status.HTTP_200_OK)
async def reset_database(user=Depends(login_required)):
    """### database 내 모든 테이블들 삭제 후 재생성 """
    reset_db()

    return Response('Success', status_code=status.HTTP_200_OK)

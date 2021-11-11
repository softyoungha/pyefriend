import os
from typing import Optional, List
from fastapi import APIRouter, Request, Response, status, HTTPException, File
from fastapi.responses import FileResponse

from rebalancing.process.db import init_db, reset_db, init_data


r = APIRouter(prefix='/database',
              tags=['v1'])


@r.post('/init-db', status_code=status.HTTP_200_OK)
async def initialize_database():
    """ database 내 모든 테이블들 생성(이미 존재하는 테이블은 Skip) """
    init_db()

    return Response('Success', status_code=status.HTTP_200_OK)


@r.post('/reset-db', status_code=status.HTTP_200_OK)
async def reset_database():
    """ database 내 모든 테이블들 삭제 후 재생성 """
    reset_db()

    return Response('Success', status_code=status.HTTP_200_OK)


@r.post('/init-db', status_code=status.HTTP_200_OK)
async def initialize_data(upload: File):
    """ product, portfolio 초기화 """
    init_data()

    return Response('Success', status_code=status.HTTP_200_OK)

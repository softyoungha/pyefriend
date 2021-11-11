from io import StringIO
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Request, Response, status, UploadFile, File, Depends

from rebalancing.app.auth import login_required
from rebalancing.process.db import init_db, reset_db, init_data, insert_data

r = APIRouter(prefix='/database',
              tags=['v1-database'])


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


FileClass = File(None,
                 media_type='text/csv',
                 title='products',
                 description='업로드한 파일이 존재할 경우 해당 파일 내의 종목들을 저장.\n\n'
                             '파일은 csv 파일만 가능하며, '
                             'market_code, product_name, product_code, weight 를 column으로 가져야함\n\n'
                             "- market_code: 한국거래소('KRX') 혹은 해외거래소코드('NASD'/'NYSE'/'AMEX')의 4글자 문자열)\n\n"
                             "- product_code: 종목명('005930'/'AAPL')\n\n"
                             "- product_name: 종목코드('삼성전자'/'애플')\n\n"
                             "- weight: 종목 가중치(상대값 혹은 국민연금 포트폴리오 투자 요금 등이 될 수 있음)")


@r.post('/insert-data', status_code=status.HTTP_200_OK)
async def insert_data_to_database(file: Optional[UploadFile] = FileClass,
                                  user=Depends(login_required)):
    """### product, portfolio data 생성"""
    if file is not None:
        contents = await file.read()

        products = (
            pd.read_csv(StringIO(str(contents, 'utf-8')), encoding='utf-8')
                .to_dict(orient='records')
        )

        # insert
        insert_data(products=products)

    else:
        # insert data
        init_data()

    return Response('Success', status_code=status.HTTP_200_OK)

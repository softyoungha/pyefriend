import os
import pandas as pd
from typing import Dict, List
from sqlalchemy.orm import Session

from rebalancing.settings import BASE_DIR, logger
from rebalancing.models.base import metadata
from rebalancing.models import Product, Portfolio, Setting


def init_db():
    metadata.create_all()
    logger.info('create_all: Done')

    Setting.initialize()
    logger.info('create_all: Done')


def reset_db():
    # drop tables
    metadata.drop_all()
    logger.info('drop_all: Done')

    # create tables
    init_db()


def insert_data(products: List[Dict] = None, data_path: str = None):
    assert products is not None or data_path is not None, "둘 중 하나는 None이 아니여야 합니다."

    # data type
    dtype = {
        'market_code': str,
        'product_name': str,
        'product_code': str,
        'weight': float
    }

    if data_path:
        if not os.path.exists(data_path):
            raise FileNotFoundError(data_path)

        products: List[Dict] = (
            pd.read_csv(data_path, sep=',', dtype=dtype)
                .to_dict(orient='records')
        )

    else:
        products = [
            {
                'market_code': str(product['market_code']),
                'product_name': str(product['product_name']),
                'product_code': str(product['product_code']),
                'weight': float(product['weight']),
            }
            for product in products
        ]

    # initialize
    Product.insert([{'code': product.get('product_code'),
                     'name': product.get('product_name'),
                     'market_code': product.get('market_code')}
                    for product in products])
    Portfolio.insert([{'product_name': product.get('product_name'),
                       'weight': product.get('weight')}
                      for product in products])


def init_data():
    # domestic
    insert_data(data_path=os.path.join(BASE_DIR, 'data', 'init_data_domestic.csv'))
    logger.info('Domestic: successfully inserted')

    # domestic
    insert_data(data_path=os.path.join(BASE_DIR, 'data', 'init_data_overseas.csv'))
    logger.info('Overseas: successfully inserted')

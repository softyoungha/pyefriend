import os
import pandas as pd
from typing import Dict, List
from sqlalchemy.orm import Session

from pyefriend.settings import BASE_DIR, logger
from pyefriend.models.base import metadata
from pyefriend.models import Product, Portfolio
from pyefriend.utils.orm_helper import provide_session


def init_db():
    metadata.create_all()
    logger.info('create_all: Done')


def reset_db():
    # drop tables
    metadata.drop_all()
    logger.info('drop_all: Done')

    # create tables
    init_db()


def load_data(data_path: str):

    if not os.path.exists(data_path):
        raise FileNotFoundError(data_path)

    # data type
    dtype = {
        'market_code': str,
        'product_name': str,
        'product_code': str,
        'weight': float
    }

    products: List[Dict] = (
        pd.read_csv(data_path, sep=',', dtype=dtype)
            .to_dict(orient='records')
    )

    # initialize
    save_products(products)
    save_portfolios(products)


@provide_session
def save_products(products: List[Dict], session: Session = None):
    product_instances = [
        Product(code=product.get('product_code'),
                name=product.get('product_name'),
                market_code=product.get('market_code'))
        for product in products
    ]

    session.bulk_save_objects(product_instances)


@provide_session
def save_portfolios(products: List[Dict], session: Session = None):
    portfolio_instances = [
        Portfolio(product_name=product.get('product_name'),
                  weight=product.get('weight'))
        for product in products
    ]

    session.bulk_save_objects(portfolio_instances)


def init_data():
    # domestic
    load_data(os.path.join(BASE_DIR, 'data', 'init_data_domestic.csv'))
    logger.info('Domestic: successfully inserted')

    # domestic
    load_data(os.path.join(BASE_DIR, 'data', 'init_data_overseas.csv'))
    logger.info('Overseas: successfully inserted')
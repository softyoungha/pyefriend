from pyefriend import api_context
from pyefriend.const import MarketCode, Target

from rebalancing.settings import logger
from rebalancing.config import Config
from rebalancing.utils.orm_helper import provide_session
from rebalancing.models import Product, Portfolio, ProductHistory


class Main:
    def __init__(self, target: str, test: bool = True):
        self._target = target

        if test:
            self._account_info = {
                'account': Config.get('user', 'TEST_ACCOUNT'),
                'password': Config.get('user', 'TEST_PASSWORD')
            }
        else:
            self._account_info = {
                'account': Config.get('user', 'REAL_ACCOUNT'),
                'password': Config.get('user', 'REAL_PASSWORD')
            }

    @property
    def target(self):
        return self._target

    @property
    def account_info(self):
        return self._account_info

    @provide_session
    def refresh_price(self, session=None):
        with api_context(target=self.target, **self.account_info) as api:
            logger.info('가격 리스트를 최신화합니다.')

            if self.target == Target.DOMESTIC:
                products = Product.list(MarketCode.KRX, session=session)

            elif self.target == Target.OVERSEAS:
                products = Product.list(only_oversea=True, session=session)

            # update 'Product'
            product_infos = [(product.code,
                              api.get_stock_info(product_code=product.code,
                                                 market_code=product.market_code))
                             for product in products]
            product_infos = [
                {
                    'code': code,
                    'current': current,
                    'minimum': minimum,
                    'maximum': maximum,
                    'opening': opening,
                    'base': base,
                }
                for code, (current, minimum, maximum, opening, base) in product_infos
            ]

            # update
            Product.update(product_infos)

            # update 'ProductHistory'
            product_histories = [(product.name,
                                  api.get_stock_histories(product_code=product.code,
                                                          market_code=product.market_code))
                                 for product in products]
            product_histories = [
                {
                    'product_name': name,
                    'standard_date': record['영업일자'],
                    'mininum': record['최저가'],
                    'maximum': record['최고가'],
                    'opening': record['시가'],
                    'closing': record['종가']
                }
                for name, records in product_histories
                for record in records
            ]

            # truncate
            ProductHistory.truncate()

            # insert
            ProductHistory.insert(product_histories)

            logger.info('가격 리스트가 최신화되었습니다.')

    def planning_re_balancing(self):
        pass


    def re_balance(self):
        pass

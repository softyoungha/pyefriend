from pyefriend import api_context
from pyefriend.const import MarketCode, Target

from rebalancing.settings import logger
from rebalancing.config import Config
from rebalancing.utils.orm_helper import provide_session
from rebalancing.models import Product, Portfolio


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
            if self.target == Target.DOMESTIC:
                products = Product.list(MarketCode.KRX, session=session)

            elif self.target == Target.OVERSEAS:
                products = Product.list(only_oversea=True, session=session)

            products_with_price = [
                {
                    'product_name': product.name,
                    'last_price': api.get_stock_price(product_code=product.code,
                                                      market_code=product.market_code)
                }
                for product in products
            ]

            Portfolio.update_price(products_with_price)

    def planning_re_balancing(self):
        pass


    def re_balance(self):
        pass

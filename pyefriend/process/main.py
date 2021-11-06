from pyefriend.utils.const import Target, MarketCode
from pyefriend.utils.orm_helper import provide_session
from pyefriend.core import api_context
from pyefriend.models import Product, Portfolio


@provide_session
def refresh_price(target: str, account: str = None, test: bool = True, session=None):
    with api_context(target=target, account=account, test=test) as api:
        if target == Target.DOMESTIC:
            products = Product.list(MarketCode.KRX, session=session)

        elif target == Target.OVERSEAS:
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

def planning_re_balancing():
    pass


def re_balance():
    pass

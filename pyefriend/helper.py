"""
# Helper

- API
- api를 with절로 활용하거나, 단일 api를 불러오는 데에 용이
"""

from contextlib import contextmanager
from typing import Union

from .api import DomesticApi, OverSeasApi
from .const import Market
from .log import logger


# [Section] Modules

def load_api(market: Market,
             account: str,
             password: str = None,
             encrypted_password: str = None,
             logger=None) -> Union[DomesticApi, OverSeasApi]:
    """
    api 로드
    :param market: 'domestic' / 'overseas'
    """
    assert market in (Market.DOMESTIC, Market.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."

    if market == Market.DOMESTIC:
        return DomesticApi(account=account,
                           password=password,
                           encrypted_password=encrypted_password,
                           logger=logger)

    elif market == Market.OVERSEAS:
        return OverSeasApi(account=account,
                           password=password,
                           encrypted_password=encrypted_password,
                           logger=logger)


@contextmanager
def api_context(market: Market,
                account: str,
                password: str = None,
                encrypted_password: str = None,
                logger=logger) -> Union[DomesticApi, OverSeasApi]:
    """
    api 생성
    :param market: 'domestic' / 'overseas'
    """
    assert market in (Market.DOMESTIC, Market.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."

    try:
        # api
        if market == Market.DOMESTIC:
            api = DomesticApi(account=account,
                              password=password,
                              encrypted_password=encrypted_password,
                              logger=logger)

        elif market == Market.OVERSEAS:
            api = OverSeasApi(account=account,
                              password=password,
                              encrypted_password=encrypted_password,
                              logger=logger)

        yield api

    except Exception as e:
        raise

    finally:
        logger.info('exit context')


def domestic_context(account: str,
                     password: str = None,
                     encrypted_password: str = None,
                     logger=None) -> DomesticApi:
    return api_context(market=Market.DOMESTIC,
                       account=account,
                       password=password,
                       encrypted_password=encrypted_password,
                       logger=logger)


def overseas_context(account: str,
                     password: str = None,
                     encrypted_password: str = None,
                     logger=None) -> OverSeasApi:
    return api_context(market=Market.OVERSEAS,
                       account=account,
                       password=password,
                       encrypted_password=encrypted_password,
                       logger=logger)

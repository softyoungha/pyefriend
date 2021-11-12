"""
# Helper

- API
- api를 with절로 활용하거나, 단일 api를 불러오는 데에 용이
"""

from contextlib import contextmanager
from typing import Union

from .api import DomesticApi, OverSeasApi
from .const import Target
from .log import logger


# [Section] Modules

def load_api(target: Target,
             account: str,
             password: str = None,
             encrypted_password: str = None,
             logger=None) -> Union[DomesticApi, OverSeasApi]:
    """
    api 로드
    :param target: 'domestic' / 'overseas'
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."

    if target == Target.DOMESTIC:
        return DomesticApi(account=account,
                           password=password,
                           encrypted_password=encrypted_password,
                           logger=logger)

    elif target == Target.OVERSEAS:
        return OverSeasApi(account=account,
                           password=password,
                           encrypted_password=encrypted_password,
                           logger=logger)


@contextmanager
def api_context(target: Target,
                account: str,
                password: str = None,
                encrypted_password: str = None,
                logger=logger) -> Union[DomesticApi, OverSeasApi]:
    """
    api 생성
    :param target: 'domestic' / 'overseas'
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), "target은 'domestic', 'overseas' 둘 중 하나만 입력 가능합니다."

    try:
        # api
        if target == Target.DOMESTIC:
            api = DomesticApi(account=account,
                              password=password,
                              encrypted_password=encrypted_password,
                              logger=logger)

        elif target == Target.OVERSEAS:
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
    return api_context(target=Target.DOMESTIC,
                       account=account,
                       password=password,
                       encrypted_password=encrypted_password,
                       logger=logger)


def overseas_context(account: str,
                     password: str = None,
                     encrypted_password: str = None,
                     logger=None) -> OverSeasApi:
    return api_context(target=Target.OVERSEAS,
                       account=account,
                       password=password,
                       encrypted_password=encrypted_password,
                       logger=logger)

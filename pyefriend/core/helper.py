import sys
from typing import Tuple, Union, Optional
from contextlib import contextmanager
from PyQt5.QtWidgets import QApplication

from pyefriend.settings import logger
from pyefriend.utils.const import Target
from .api import DomesticApi, OverSeasApi


app: Optional[QApplication] = None


def run_app():
    global app

    if app is None:
        app = QApplication(sys.argv)
        logger.info('Start APP')

    return app


def load_api(target: str = Target.DOMESTIC,
             account: str = None,
             test: bool = True) -> Union[DomesticApi, OverSeasApi]:
    # run app
    run_app()

    if target == Target.DOMESTIC:
        return DomesticApi(target_account=account, test=test)

    elif target == Target.OVERSEAS:
        return OverSeasApi(target_account=account, test=test)


@contextmanager
def api_context(target: str, account: str = None, test: bool = True):
    """
    session생성

    :param target: 'domestic' / 'overseas'
    :return: session
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), ""

    # run app
    run_app()

    try:
        # api
        if target == Target.DOMESTIC:
            api = DomesticApi(target_account=account, test=test)

        elif target == Target.OVERSEAS:
            api = OverSeasApi(target_account=account, test=test)

        yield api

    except Exception as e:
        raise

    finally:
        logger.info('exit context')


def domestic_context(account: str = None, test: bool = True) -> DomesticApi:
    return api_context(target=Target.DOMESTIC,
                       account=account,
                       test=test)


def overseas_context(account: str = None, test: bool = True) -> OverSeasApi:
    return api_context(target=Target.OVERSEAS,
                       account=account,
                       test=test)

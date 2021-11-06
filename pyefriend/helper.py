import sys
from typing import Tuple, Union
from contextlib import contextmanager

from utils.const import Target
from .api import DomesticApi, OverSeasApi

from PyQt5.QtWidgets import QApplication


def load_api(target: str = Target.DOMESTIC,
             account: str = None,
             test: bool = False) -> Tuple[QApplication,
                                          Union[DomesticApi, OverSeasApi]]:
    app = QApplication(sys.argv)

    if target == Target.DOMESTIC:
        return app, DomesticApi(target_account=account, test=test)

    elif target == Target.OVERSEAS:
        return app, OverSeasApi(target_account=account, test=test)


@contextmanager
def api_context(target: str = Target.DOMESTIC,
                account: str = None,
                test: bool = False):
    """
    session생성

    :param target: 'domestic' / 'overseas'
    :return: session
    """
    assert target in (Target.DOMESTIC, Target.OVERSEAS), ""

    # create app
    QApplication(sys.argv)
    print('[INFO] Start APP')

    try:
        # api
        if target == Target.DOMESTIC:
            api = DomesticApi(target_account=account, test=test)

        elif target == Target.OVERSEAS:
            api = OverSeasApi(target_account=account, test=test)

        yield api

    except Exception as e:
        # session.close()
        raise

    finally:
        print('[INFO] exit')
        # app.exec_()


def domestic_context(account: str = None, test: bool = False) -> DomesticApi:
    return api_context(target=Target.DOMESTIC,
                       account=account,
                       test=test)


def overseas_context(account: str = None, test: bool = False) -> OverSeasApi:
    return api_context(target=Target.OVERSEAS,
                       account=account,
                       test=test)

""" Exceptions """


class UnExpectedException(Exception):
    """ 예상치못한 에러 """
    def __init__(self, detail: str):
        self.detail = detail


class NotConnectedException(Exception):
    """ 접속 오류 """
    def __init__(self):
        msg = "'efriend expert'를 찾을 수 없습니다." \
              "\n\t1. Python 32bit를 사용하세요." \
              "\n\t2. Python을 관리자 권한으로 실행하세요(cmd 혹은 Pycharm)" \
              "\n\t3. efriend expert를 관리자 권한으로 실행하세요."
        super().__init__(msg)


class AccountNotExistsException(UnExpectedException):
    """ 입력한 계좌가 존재하지 않습니다. """
    def __init__(self, detail: str = "입력한 계좌가 존재하지 않습니다."):
        super().__init__(detail)


class UnAuthorizedAccountException(UnExpectedException):
    """ 계좌 권한 관련 에러 """


class MarketClosingException(UnExpectedException):
    """ 장 종료 """


class NotInVTSException(UnExpectedException):
    """ 모의투자에서는 제공되지 않는 서비스 """


class BiddingException(UnExpectedException):
    """ 모의투자 주문처리 불가(매매불가 종목) """

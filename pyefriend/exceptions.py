
class ConfigException(Exception):
    """ Config 관련 에러 """


# about PyQt5 connection
class UnExpectedException(Exception):
    """ 예상치못한 에러 """


class NotConnectedException(Exception):
    """ 접속 오류 """
    def __init__(self):
        msg = "Python 32bit를 사용하거나 python와 efriend expert를 관리자 권한으로 실행해야 합니다."
        super().__init__(msg)


class UnAuthorizedAccountException(Exception):
    """ 계좌 권한 관련 에러 """

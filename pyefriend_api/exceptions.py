from fastapi import HTTPException, status


class ConfigException(Exception):
    """ Config 관련 에러 """


class CredentialException(HTTPException):
    """ 로그인 에러 """
    def __init__(self):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED,
                         detail="Could not validate credentials",
                         headers={"WWW-Authenticate": "Bearer"})


class ReportNotFoundException(HTTPException):
    """ Report 없음 """
    def __init__(self, detail='조건을 만족하는 Report가 없습니다.'):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail=detail)


class MarketClosedException(HTTPException):
    """ Report 없음 """
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST,
                         detail=detail)


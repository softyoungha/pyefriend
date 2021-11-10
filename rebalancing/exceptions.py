from fastapi import HTTPException, status


class ConfigException(Exception):
    """ Config 관련 에러 """


class ReportNotFound(HTTPException):
    """ Report 없음 """
    def __init__(self):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND,
                         detail="조건을 만족하는 Report가 없습니다.")
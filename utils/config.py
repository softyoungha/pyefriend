""" Configuration 설정 파일 """

#####################################
#           USER Section            #
#####################################
class TestUser:
    DEFAULT_ACCOUNT = '5005775101'
    PASSWORD = 'Dmazhffk1'


class User:
    DEFAULT_ACCOUNT = '7289926901'
    PASSWORD = '3685'


#####################################
#         Database Section          #
#####################################
class Database:
    SQLALCHEMY_CONN_STR = 'sqlite:///database.db'
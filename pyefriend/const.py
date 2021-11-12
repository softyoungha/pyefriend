from enum import Enum


class System:
    """ 시스템 정보 """
    CSLID = '08E39D09-206D-43D1-AC78-D1AE3635A4E9'
    PROGID = 'ITGExpertCtl.ITGExpertCtlCtrl.1'


class Target(str, Enum):
    """ 타겟 """
    DOMESTIC = 'domestic'  # 국내
    OVERSEAS = 'overseas'  # 해외(미국)


class Service:
    """ 한국투자증권 서비스 """

    # 국내
    SCP = 'SCP'  # 주식 현재가 시세
    SCPD = 'SCPD'  # 주식 현재가 일자별
    SCAP = 'SCAP'  # 주식 현금 금액 잔고 조회
    SATPS = 'SATPS'  # 주식 계좌 당일 잔고 현황 조회
    SCABO = 'SCABO'  # 주식 현금 매수 주문
    SCAAO = 'SCAAO'  # 주식 현금 매도 주문
    TC8001R = 'TC8001R'  # 주식 일별 주문 체결 조회(3개월 이내)
    SMCP = 'SMCP'  # 주식 정정 취소 가능 주문 조회
    SMCO = 'SMCO'  # 주식 정정 취소 주문

    # 미국(모의투자에서 제공되지 않을 수 있음)
    OS_ST01 = 'OS_ST01'  # 해외주식 현재가 체결
    OS_ST02 = 'OS_ST02'  # 해외주식 현재가 10호가(?)
    OS_ST03 = 'OS_ST03'  # 해외주식 일,주,월 종가 시세
    OS_US_DNCL = 'OS_US_DNCL'  # 야간 외화예수금
    OS_US_CBLC = 'OS_US_CBLC'  # 미국 잔고
    OS_OS3004R = 'OS_OS3004R'  # 해외 증거금 조회
    OS_US_BUY = 'OS_US_BUY'  # 미국 매수 주문
    OS_US_SEL = 'OS_US_SEL'  # 미국 매도 주문
    OS_US_CCLD = 'OS_US_CCLD'  # 미국 체결 내역 조회
    OS_US_NCCS = 'OS_US_NCCS'  # 미국 미체결 내역 조회
    OS_US_CNC = 'OS_US_CNC'  # 미국 주식 주문 취소
    PFX06910200 = 'PFX06910200'  # 해외증시 시간별 조회
    PFX06910000 = 'PFX06910000'  # 해외증시 일주월별 조회


class MarketCode(str, Enum):
    # 한국증시
    KRX = 'KRX'

    # 해외거래소코드
    NASD = 'NASD'
    NYSE = 'NYSE'
    AMEX = 'AMEX'

    @classmethod
    def as_short(cls, code: str):
        if code == cls.NASD:
            return 'NAS'
        elif code == cls.NYSE:
            return 'NYS'
        elif code == cls.AMEX:
            return 'AMS'
        else:
            raise KeyError(f'no such code: {code}')

    @classmethod
    def us_list(cls):
        return [cls.NASD, cls.NYSE, cls.AMEX]


class ProductCode:
    # 업종 코드: 'U'
    KOSPI = '0001'
    KOSDAQ = '1001'
    KOSPI200 = '2001'

    # S&P 500
    SPX = 'SPX'

    # 시장분류코드: 'J'
    SAMSUNG = '005930'
    APPLE = 'AAPL'  # NASD


class Currency:
    """ 환율 정보 """
    URL = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    BASE = 1186.50  # 2021-11-06 기준


class Unit(str, Enum):
    KRW = 'KRW'
    USD = 'USD'

from enum import Enum


class System:
    """ 시스템 정보 """
    CSLID = '08E39D09-206D-43D1-AC78-D1AE3635A4E9'
    PROGID = 'ITGExpertCtl.ITGExpertCtlCtrl.1'


class Market(str, Enum):
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
    SCPH = 'SCPH'  # 주식 현재가 호가
    PST01010300 = 'PST01010300'  # 현재가(분별)
    KST13020000 = 'KST13020000'  # 상승 하락 종목
    PUP02120000 = 'PUP02120000'  # 업종 지수정보

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
    # S&P 500
    SPX = 'SPX'

    # 시장분류코드: 'J'
    SAMSUNG = '005930'
    APPLE = 'AAPL'  # NASD


class SectorCode(str, Enum):
    """ 업종 코드 """
    KOSPI = '0001'  # KOSPI
    KOSDAQ = '1001'  # KOSDAQ
    KOSPI200 = '2001'  # KOSPI200

    LARGE = '0002'  # 대형주
    MEDIUM = '0003'  # 중형주
    SMALL = '0004'  # 소형주유통회사
    FOOD = '0005'  # 음식료품
    CLOTHES = '0006'  # 섬유, 의복
    PAPER = '0007'  # 종이, 목재
    CHEMISTRY = '0008'  # 화학
    MEDICINE = '0009'  # 의약품
    NONMETAL = '0010'  # 비금속광물
    STEEL = '0011'  # 철강, 금속
    MACHINE = '0012'  # 기계
    ELECTRONIC = '0013'  # 전기, 전자
    MEDICAL = '0014'  # 의료정밀
    EQUIPMENT = '0015'  # 운수, 장비
    DISTRIBUTION = '0016'  # 유통업
    GAS = '0017'  # 전기, 가스업
    CONSTRUCTION = '0018'  # 건설업
    WAREHOUSE = '0019'  # 운수, 창고
    TELECOM = '0020'  # 통신업
    FINANCE = '0021'  # 금융업
    BANK = '0022'  # 은행
    STOCK = '0024'  # 증권
    INSURANCE = '0025'  # 보험
    SERVICE = '0026'  # 서비스업
    MANUFACTURING = '0027'  # 제조업


class Currency:
    """ 환율 정보 """
    URL = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    BASE = 1186.50  # 2021-11-06 기준


class Unit(str, Enum):
    KRW = 'KRW'
    USD = 'USD'


class DWM(str, Enum):
    D = 'D'  # 날짜 기준
    W = 'W'  # 주 기준
    M = 'M'  # 월 기준


class Direction(str, Enum):
    MAXIMUM = 'MAXIMUM'
    INCREASE = 'INCREASE'
    NOCHANGE = 'NOCHANGE'
    DECREASE = 'DECREASE'
    MINIMUM = 'MINIMUM'


class IndexCode(str, Enum):
    TOTAL = '0000'
    KOSPI = '0001'
    KOSDAQ = '1001'

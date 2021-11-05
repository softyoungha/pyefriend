
# system
class System:
    CSLID = '08E39D09-206D-43D1-AC78-D1AE3635A4E9'
    PROGID = 'ITGExpertCtl.ITGExpertCtlCtrl.1'


# 환율 정보
class Currency:
    URL = 'https://quotation-api-cdn.dunamu.com/v1/forex/recent?codes=FRX.KRWUSD'
    BASE = 1186.50  # 2021-11-06 기준


class Service:
    # 국내
    SCP = 'SCP'                     # 주식 현재가 시세
    SCAP = 'SCAP'                   # 주식 현금 금액 잔고 조회
    SATPS = 'SATPS'                 # 주식 계좌 당일 잔고 현황 조회
    SCABO = 'SCABO'                 # 주식 현금 매수 주문
    SCAAO = 'SCAAO'                 # 주식 현금 매도 주문
    SDOC = 'SDOC'                   # 주식 일별 주문 체결 조회
    SMCP = 'SMCP'                   # 주식 정정 취소 가능 주문 조회
    SMCO = 'SMCO'                   # 주식 정정 취소 주문

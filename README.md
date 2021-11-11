# pyefriend

##### By Youngha Park

## Description

pyefriend는 한국투자증권 OpenAPI(**efriend Expert**)과 연동하여 
주식 가격 조회, 종목 매수/매도 등 가능하도록 구성한 High/Low-Level Python 패키지입니다.
국내/해외 주식의 가격 종목 리스트 관리 및 조회를 할 수 있으며,
추가적으로 입력한 계좌에 대한 리밸런싱 리포트를 자동 생성하여 Next plan을 결정할 수 있도록 도와줍니다.  

패키지는 **pyefriend**와 **rebalancing** 두가지 모듈로 구성되어 있습니다.
pyefriend 모듈은 PyQt5 패키지를 사용하여 efriend Expert와 상호작용하여 종목 조회/매수/매도할 수 있으며,
Low-level(**pyefriend/controller.py**), High-level(**pyefriend/api.py**) API를 제공합니다.
그리고 rebalancing 모듈에 대한 dependency를 가지고 있지 않기 때문에 별도의 설정 없이 단독으로 사용할 수 있습니다.

rebalancing 모듈은 pyefriend 모듈을 활용하여 설정한 계좌에 대해 
국내/해외 총 예수금, 종목별 시/종/저/고/기준가, KOSPI/SP&500 지수 등을 조회할 수 있고 
이를 토대로 **리밸런싱(Re-balancing)** 포트폴리오, 플랜을 생성합니다. 
리밸런싱에 대한 이론은 구글 검색을 참고하시기 바랍니다.

* pyefriend 모듈은 [eFriendPy](https://github.com/pjueon/eFriendPy)를 참고하여 만든 코드를 재해석하여 구성하였습니다.


**Table of contents**
- [Warning](##warning)
- [Requirements](##requirements)
- [Getting started](##getting-started)
- [Rebalancing](##rebalancing)
- [Process](##process)
- [ETC](##etc)
- [Links](##links)


## Warning

- pyefriend, rebalancing 코드는 개인 투자 목적으로 사용하거나 스터디 용도로만 사용하실 수 있습니다. 
- pyefriend는 [한국투자증권 Expert 표준 API Reference Guide](https://new.real.download.dws.co.kr/download/expert_manual.pdf)
  (2021-11-09 기준)를 참고하여 작성하였습니다.

## Requirements

- pyefriend 코드는 Window 환경에서만 작동합니다.(Window 10에서 개발 진행)
- 한국투자증권 공식홈페이지에서 OpenAPI 신청 후 eFriend Expert를 다운받아 **관리자 권한**으로 실행해야 정상 작동합니다.
- Python 3의 32bit 버전에서만 정상 작동합니다.
  - python3.x-32bit를 공식홈페이지에서 설치한 후 해당 python을 통해 가상환경(`virtualenv`)를 구성하여 설치하는 것을 권장합니다.
- Python도 마찬가지로 **관리자 권한**으로 실행해야 합니다.
  - `cmd`를 관리자 권한으로 실행한 후 가상환경을 활성화한 후 실행(`jupyter notebook`)
  - Pycharm을 사용할 경우 Pycharm을 관리자 권한으로 실행한 뒤 Terminal에서 실행 가능합니다.

|                      | version                   |
| -------------------- | ------------------------- |
| PyQt5                | 5.15.6                    |
| pywinpty             | <1,>=0.5                  |
| jupyter              | 1.0.0                     |
| notebook             | 6.4.5                     |
| ipython              | 7.29.0                    |
| numpy                | 1.21.4                    |
| pandas               | 1.3.4                     |
| sqlalchemy           | 1.4.26                    |

## Installation

현재 PyPi 에 pyefriend를 업로드해놓았습니다.([Pypi: pyefriend](https://pypi.org/project/pyefriend/1.0/))

```shell
pip install pyefriend
```

* 어느정도 안정화될 때까지는 github repo에서 pull 받아서 사용하길 권장합니다.(현재 수정이 잦습니다.)



## Getting started

pyefriend, rebalancing 모듈 모두 다음의 조건에서 정상작동됩니다. 

- Python 32bix **관리자** 모드 실행
- efriend expert **관리자** 모드 후 로그인 완료(모의투자일 경우는 비밀번호만, 운영일 경우 공인인증서 입력 후 로그인까지 완료) 

### pyefriend

pyefriend에서 High-level로 API를 활용하는 방법은 다음과 같습니다.

```python
# 국내 조회/매수/매도시 사용법 """

from pyefriend import load_api
# or from pyefriend.helper import load_api

""" api instance 생성 """
# target: 'domestic'(국내)/'overseas'(해외)
# account: efriend Expert 로그인한 계정 내에 존재하는 계좌
# password: 한국투자증권 매수/매도시 입력 비밀번호
api = load_api(target='domestic',   
               account='5005775101',
               password='password')

# 삼성전자 종목코드
product_code: str = '005930'

""" 종목 조회 """
# return: 현재가, 저가, 고가, 시가, 기준가
current, minimum, maximum, opening, base = api.get_stock_info(product_code=product_code)

""" 종목 매수 """
# count: 수량
# price: 매수가격
# return: 주문번호
buy_order_num: str = api.buy_stock(product_code=product_code, count=3, price=50000)

""" 종목 매도 """
sell_order_num: str = api.sell_stock(product_code=product_code, count=2, price=90000) # 9만전자 가자

""" 매수/매도 취소 """
api.cancel_order(order_num=buy_order_num, count=3)
```

get_stock_info, buy_stock, sell_stock, cancel_order 와 같이 High-level 사용이 가능합니다.

국내 주식 API와 해외 주식 API를 직접 호출해서 다음과 같이 사용할 수 있습니다.

```python
""" 국내 주식 API """
from pyefriend.api import DomesticApi

api = DomesticApi(account='5005775101', password='password')

""" 해외 주식 API """
from pyefriend.api import OverSeasApi

api = OverSeasApi(account='5005775101', password='password')
```

> helper.py의 load_api 함수에서 **target** 입력값에 대한 분기를 통해 
> 국내 주식 API(**DomesticApi**), 해외 주식 API(**OverSeasApi**)를 사용하도록 결정합니다.

함수 리스트는 다음과 같습니다.
parameter, return type 등의 자세한 내용은 api.py 내에서 주석과 함께 확인할 수 있습니다.

#### property
  - deposit
  - stocks
  - unit

#### common functions
  - evaluate_amount
  - get_stock_name
  - get_stock_info
  - get_stock_histories
  - buy_stock
  - sell_stock
  - get_processed_orders
  - get_unprocessed_orders
  - cancel_order
  - cancel_all_unprocessed_orders
  - get_kospi_histories
  - get_sp500_histories

#### only OverseasApi
  - set_auth
  - currency(property)

같은 함수명을 가지고 parameter명도 같지만 내부에서 요청하는 efriend Service는 다릅니다.
직접 커스텀 서비스 요청을 만드는 방법은 [Custom API Control](#custom-api-control) Section을 참고하세요.


## Custom API Control

efriend Service 리스트는 efriend Expert 프로그램 실행시 도움말에서 인터페이스 정의서를 확인하거나, 
혹은 [Expert 표준 API Guide](https://new.real.download.dws.co.kr/download/expert_manual.pdf)를 참고하세요.)

다음은 국내 주식 정보를 조회하는 함수입니다.

```python
class DomesticApi(Api):
    # 국내 주식 조회 API
    ...
    def get_stock_info(self, product_code: str, market_code: str = None) -> Tuple[int, int, int, int, int]:
        # set
        (
            self.set_data(0, 'J')  # 0: 시장분류코드 / J: 주식, ETF, ETN
                .set_data(1, product_code)  # 1: 종목코드
                .request_data(Service.SCP)
        )
        
        # get
        current = int(self.get_data(11))  # 11: 주식 현재가
        minimum = int(self.get_data(20))  # 19: 주식 최저가
        maximum = int(self.get_data(19))  # 20: 주식 최고가
        opening = int(self.get_data(18))  # 19: 주식 시가
        base = int(self.get_data(23))  # 23: 주식 기준가(전일 종가)

        # as response
        return current, minimum, maximum, opening, base
```

API 내의 모든 함수는 set -> request_data -> get 순서를 따릅니다.

* `self.set_data` 함수는 `self`를 return하기 때문에 계속해서 `.`으로 계속 이어서 적을 수 있습니다.
* set_data Chain 마지막에는 `request_data(service)`를 통해 모인 데이터를 
  efriend 내 특정 서비스로 전송합니다.
* request_data 이후 Controller(Low-level)는 전송 결과 반환받은 데이터를 저장해놓은 상태이고,
  이를 `self.get_data` 함수를 통해 가져올 수 있습니다.
* 이 데이터는 request_data를 실행하기 전까지 유지됩니다.


다음과 같이 Api를 상속받아서 새로운 Api class를 생성할 수 있습니다.
set -> request -> get 의 순서만 지키면 커스텀 함수를 생성하는 것이 어렵지 않습니다.

```python
class MyApi(DomesticApi):
    # 커스텀 API(국내 주식 API 상속)
    def get_something_new(self, param: str):
        # set chain
        (
          self.set_data(0, ...)
              .set_data(1, ...)
              .set_data(2, ...)
              # ...
              .request_data('SERVICE_IN_EFRIEND_DOCUMENT')
        )
        
        # get
        my_param1 = self.get_data(0)
        my_param2 = self.get_data(1)
        ...
        
        return my_param1, my_param2, ...
```


---

# Rebalancing

- pyefriend를 활용하여 투자 리밸런싱을 진행하는 모듈입니다.

- config.yml 에서 계정

## Process

1. refresh: DB 주식 시세 최신화

2. planning: 매수, 매도 수량 책정

3. re-balance: 현재 수량과 비교하여 주문

4. visualize: 

## ETC

[국민연금 포트폴리오](https://fund.nps.or.kr/jsppage/fund/mpc/mpc_03.jsp)

## Links

- [Github](https://github.com/softyoungha)

- [Github blog](https://softyoungha.github.io/)

- [Pypi: pyefriend](https://pypi.org/project/pyefriend/1.0/)

- [한국투자증권 Expert 표준 API Reference Guide](https://new.real.download.dws.co.kr/download/expert_manual.pdf)
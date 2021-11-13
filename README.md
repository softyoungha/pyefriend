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
- [Warning](#warning)
- [Requirements](#requirements)
- [Getting started](#getting-started)
- [Rebalancing](#rebalancing)
- [Process](#process)
- [ETC](#etc)
- [Links](#links)


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
| fastapi              | 0.70.0                    |
| uvicorn[standard]    | 0.15.0                    |

<br/>

## Installation

현재 PyPi 에 pyefriend를 업로드해놓았습니다.([Pypi: pyefriend](https://pypi.org/project/pyefriend/1.0/))

```shell
pip install pyefriend
```

* 어느정도 안정화될 때까지는 github repo에서 pull 받아서 사용하길 권장합니다.    
  (현재 수정이 잦습니다.)
  
Python 32bit 설치 이후 해당 python을 통해 가상환경을 만들어서 사용하는 것을 추천합니다.

```shell
# venv 생성
python -m venv venv

# activate 방법 1: 직접 타이핑
.\venv\Scripts\activate

# activate 방법 2: 직접 타이핑
call venv\Scripts\activate.bat

# activate 방법 3: git source에 포함된 .bat 파일 사용(추천)
activate.bat
```


<br/>

## Getting started

pyefriend, rebalancing 모듈 모두 다음의 조건에서 정상작동됩니다. 

- Python 32bix **관리자** 모드 실행
- efriend expert **관리자** 모드 후 로그인 완료(모의투자일 경우는 비밀번호만, 운영일 경우 공인인증서 입력 후 로그인까지 완료) 

### Module: pyefriend

pyefriend에서 High-level로 API를 활용하는 방법은 다음과 같습니다.

```python
# 국내 조회/매수/매도시 사용법 """

from pyefriend import load_api
# or from pyefriend.helper import load_api

""" api instance 생성 """
# market: 'domestic'(국내)/'overseas'(해외)
# account: efriend Expert 로그인한 계정 내에 존재하는 계좌
# password: 한국투자증권 매수/매도시 입력 비밀번호
api = load_api(market='domestic',   
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

> helper.py의 load_api 함수에서 **market** 입력값에 대한 분기를 통해 
> 국내 주식 API(**DomesticApi**), 해외 주식 API(**OverSeasApi**)를 사용하도록 결정합니다.

함수 리스트는 다음과 같습니다.
parameter, return type 등의 자세한 내용은 api.py 내에서 주석과 함께 확인할 수 있습니다.

#### Property
  - deposit
  - stocks
  - unit

#### Common functions
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

#### Only OverseasApi
  - set_auth
  - currency(property)

같은 함수명을 가지고 parameter명도 같지만 내부에서 요청하는 efriend Service는 다릅니다.
직접 커스텀 서비스 요청을 만드는 방법은 [Custom API Control](#custom-api-control) Section을 참고하세요.

<br/>

### Module: rebalancing

1. rebalancing의 초기 설정을 위해서는 먼저 환경변수 설정을 해야합니다.

    ```shell
    # 실행 경로
    set REBAL_HOME=.
    
    # config.yml 위치(입력하지 않을 경우 %REBAL_HOME%/config.yml 로 자동 설정)
    set REBAL_CONF=./config.yml
    
    # FastAPI 실행시 관리자 로그인을 위한 계정 비밀번호
    set REBAL_PASSWORD=password
    ```
    
    > Windows cmd.exe에서는 `set`으로 해당 cmd 세션에 대해서 환경변수를 설정할 수 있습니다.
    > 
    > 새로운 cmd에서는 새롭게 설정해주어야 합니다.
    > 
    > 환경변수를 유지하고 싶다면 컴퓨터 환경변수로 등록하거나 Pycharm 세팅을 활용하시면 됩니다.   
    
2. REBAL_CONF 위치에 `config.template.yml`을 복사하여 설정값을 변경합니다.

    config.yml은 다음과 같이 section/key/value 형식으로 구성되어 있습니다.
    ```yaml
    # .../config.yml (%REBAL_CONF%)
    section:  
      # key description
      key: value
      ...
    ```

3. database를 생성합니다.
   
    config.yml -> `database` section -> `sqlalchemy_conn_str` 에서
    이미 생성되어 있는 다른 database connection을 설정할 수 있습니다.
    혹은, sqlite3(config.template.yml) 경로를 사용자 경로에 맞춰 변경한 뒤 다음의 코드를 실행하면
       
    ```shell
    # cmd terminal: run ipython
    ipython
    ```
    ```python
    # ipython 
    from rebalancing.utils.db import init_db
    
    # database 생성
    init_db()
    ```
    
    `init_db` 함수 실행과 동시에 sqlite3 database 파일(ex. database.db)이 생성되며
    rebalancing에서 사용하는 모든 테이블들이 생성됩니다.
    
    > rebalancing 내에서 사용하는 database 작업이 개인 사용 목적이므로 많은 세션을 요구하지 않고, 
      잦은 transaction이 일어나지 않으므로 sqlite3만으로도 충분합니다.
      
    > database 내에 'setting' 테이블이 init_db 실행과 함께 값이 insert됩니다.

4. db table 내에 data를 insert합니다.

    ```python
    from rebalancing.utils.db import init_data
    
    # 초기 데이터 insert
    init_data()
    ```
    
    생성되는 초기 데이터는 국민연금기관의 국내/해외 투자 포트폴리오를 기반으로 계산된 데이터입니다.
    ([국민연금 포트폴리오](https://fund.nps.or.kr/jsppage/fund/mpc/mpc_03.jsp))
    
    - rebalancing/data/init_data_domestic.csv
    - rebalancing/data/init_data_overseas.csv
    
    weight 국민연금기관이 투자한 금액으로, 리밸런싱할 비율을 계산하는 값입니다.

5. 생성된 'portfolio' 테이블에서 포트폴리오에서 사용할 종목만 use_yn = 1 로 변경

    가진 예산이 50만원일 때 모든 종목을 use_yn = 1로 하여도 개별 종목들이 비싸기 때문에
    리밸런싱으로 계산할 수 없습니다.(엔씨소프트 주식 현재가 70만원)
    따라서 예산에 감안해서 리밸런싱을 진행할 종목들을 선택해야 하고, 
    예산도 어느정도 확보한 상태에서 분산투자가 가능합니다. 
    
    > DBeaver와 같은 DB 접속 Tool을 사용하여 변경하는 것을 권장합니다.  

6. 리밸런싱 실행

    리밸런싱을 실행하는 방법은 총 세가지가 있습니다.
  
    ### 방법1: cmd에서 python 프로그램으로 실행
      
    `python -m rebalancing -h` 커맨드를 입력하면 다음과 같이 help 메시지가 출력됩니다.
    
    > cmd.exe가 역시 관리자 모드로 실행되어야 하며, 이후 `activate.bat`을 통해 venv가 activate 되어야 합니다.
    
    ```text
    (venv) C:\...\rebalancing> python -m rebalancing -h
    usage: __main__.py [-h] --market {domestic,overseas} [--created CREATED] [--test] [--account ACCOUNT] [--password] [--skip-refresh]
    
    Re-balancing 모듈 실행
    
    optional arguments:
      -h, --help            show this help message and exit
      --market {domestic,overseas}, -t {domestic,overseas}
                            domestic: 국내 투자 선택
                            overseas: 해외 투자 선택
      --created CREATED, -c CREATED
                            Report 생성이력(YYYYmmdd_HH_MM_SS format)
      --account ACCOUNT, -a ACCOUNT
                            계좌명('-' 제외), 입력하지 않을 경우 config.yml에서 사용
      --password, -p        계좌 매수/매도시 입력 비밀번호
                            입력하지 않을 경우 config.yml에서 사용
                            -p/--password 입력 후 별도로 입력
      --skip-refresh, -s    입력시 종목 최신화 skip
    
    ```

    ### 방법2: jupyter notebook에서 모듈 임포트 후 커스텀 코드로 실행
    
    rebalancing_example.ipynb를 참고하세요.

    ### 방법3: FastAPI 실행 후 request

    다음의 커맨드로 FastAPI를 실행합니다.
    
    > cmd.exe가 관리자 모드로 실행되어야 하며, 이후 `activate.bat`을 통해 venv가 activate 되어야 합니다.
    
    ```shell
    uvicorn rebalancing.api:app --reload
    ```
    
    브라우저에서 `http://localhost:8000`로 접속하면 **Re-balancing App** 화면이 나옵니다.
    
    > fastapi 기본포트는 8000입니다.
    >
    > 타 컴퓨터에서 접속이 가능하게 하려면 `--host 0.0.0.0`, 포트를 변경하려면 `--port xxxx`를 추가합니다.
    >
    > --reload 옵션이 있으면 python source code가 변경되었을 때 다시 리로딩합니다.
    > 
    > 프로젝트 폴더 내 config.template.yml 이나 md 파일, csv 파일이 변경되어도 리로딩되지 않으므로 참고하세요.
    
    ```shell
    uvicorn rebalancing.api:app --host 0.0.0.0 --port 8080 --reload
    ```
    
    Re-balancing App 에 관한 내용은 App 실행시 상단 Description, 혹은 rebalancing/DESCRIPTION.md를 확인하세요.

<br/>

## Custom API Control

efriend Service 리스트는 efriend Expert 프로그램 실행시 도움말에서 인터페이스 정의서를 확인하거나, 
혹은 [Expert 표준 API Guide](https://new.real.download.dws.co.kr/download/expert_manual.pdf)를 참고하세요.

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
                .request_data(Service.SCP)  # Service.SCP = 'SCP' (상수)
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

API 내의 모든 함수는 `set -> request_data -> get` 순서를 따릅니다.

* `self.set_data` 함수는 `self`를 return하도록 되어있어 `.`으로 이어서 Chain을 만들 수 있습니다.
* set_data Chain 마지막에는 `request_data(service)`를 통해 모인 데이터를 
  efriend 내 특정 서비스로 전송합니다.
* request_data 이후 Controller(Low-level)는 전송 결과 반환받은 데이터를 저장해놓은 상태이고,
  이를 `self.get_data` 함수를 통해 가져올 수 있습니다.
* 이 데이터는 request_data를 실행하기 전까지 유지됩니다.


다음과 같이 Api를 상속받아서 새로운 Api class를 생성할 수 있습니다.
`set -> request_data -> get` 의 맥락만 지키면 커스텀 함수를 생성하는 것이 어렵지 않습니다.

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

## Process

1. refresh: DB 주식 시세 최신화

2. planning: 매수, 매도 수량 책정

3. re-balance: 현재 수량과 비교하여 주문

## ETC

[국민연금 포트폴리오](https://fund.nps.or.kr/jsppage/fund/mpc/mpc_03.jsp)

## Links

- [Github](https://github.com/softyoungha)

- [Github blog](https://softyoungha.github.io/)

- [Pypi: pyefriend](https://pypi.org/project/pyefriend/1.0/)

- [한국투자증권 Expert 표준 API Reference Guide](https://new.real.download.dws.co.kr/download/expert_manual.pdf)
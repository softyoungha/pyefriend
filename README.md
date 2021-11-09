# pyefriend

python을 이용하여 한국투자증권 OpenAPI에 연동하여 트레이딩이 가능한 모듈입니다. 
[eFriendPy](https://github.com/pjueon/eFriendPy)를 참고하여 만든 코드를 재해석하여 구성하였습니다.

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
- pyefriend는 [한국투자증권 Expert 표준 API Reference Guide(2021-11-09 업데이트)](https://new.real.download.dws.co.kr/download/expert_manual.pdf))를
참고하여 작성하였습니다.
- pyefriend 코드는 Window 환경에서만 작동합니다.(Window 10에서 개발 진행)
- 한국투자증권 공식홈페이지에서 OpenAPI 신청 후 eFriend Expert를 다운받아 **관리자 권한**으로 실행해야 정상 작동합니다.
- Python 3의 32bit 버전에서만 정상 작동합니다.
  - python3.x-32bit를 공식홈페이지에서 설치한 후 해당 python을 통해 가상환경(`virtualenv`)를 구성하여 설치하는 것을 권장합니다.
- Python도 마찬가지로 **관리자 권한**으로 실행해야 합니다.
  - `cmd`를 관리자 권한으로 실행한 후 가상환경을 활성화한 후 실행(`jupyter notebook`)
  - Pycharm을 사용할 경우 Pycharm을 관리자 권한으로 실행한 뒤 Terminal에서 실행 가능합니다.

## Requirements

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

## Getting started

```shell
pip install pyefriend
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

#### 2021-08 기준 국민연금

- 국내주식: 19.0%/해외주식: 26.7%


## Links

- [Pypi](https://pypi.org/project/pyefriend/1.0/)

- [Github](https://github.com/softyoungha)

- [Github blog](https://softyoungha.github.io/))
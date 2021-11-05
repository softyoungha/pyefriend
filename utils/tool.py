import requests
from .const import Currency


def get_currency(raise_error: bool = False):
    try:
        response = requests.get(Currency.URL)
        data = response.json()
        return data[0]['basePrice']
    except Exception as e:
        print('환율 정보를 불러오는 데 실패하였습니다.')
        if raise_error:
            raise e
        print('설정된 환율을 사용합니다.')
        return Currency.BASE



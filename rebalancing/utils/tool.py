import os
import yaml
import requests
import ipykernel


def load_yaml(file_path: str) -> dict:
    with open(file_path, encoding='utf-8') as f:
        _dict = yaml.load(f, Loader=yaml.FullLoader)

    return _dict


def get_jupyter_id() -> str:
    connection_file = os.path.basename(ipykernel.get_connection_file())
    kernel_id = connection_file.split('-', 1)[1].split('.')[0]

    return kernel_id


def is_jupyter_kernel(raise_error: bool = False):
    try:
        jupyter_id = get_jupyter_id()
        print(f'using jupyter kernel now: {jupyter_id}')
        return True

    except RuntimeError as e:
        if raise_error:
            raise e
        else:
            pass
    except Exception as e:
        if raise_error:
            raise e
        else:
            pass




# def get_currency(raise_error: bool = False):
#     try:
#         response = requests.get(Currency.URL)
#         data = response.json()
#         return data[0]['basePrice']
#     except Exception as e:
#         print('환율 정보를 불러오는 데 실패하였습니다.')
#         if raise_error:
#             raise e
#         print('설정된 환율을 사용합니다.')
#         return Currency.BASE

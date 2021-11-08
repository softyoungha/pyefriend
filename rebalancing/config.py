""" Configuration 설정 파일 """
import os
from typing import Any, Optional, List

from rebalancing.exceptions import ConfigException
from rebalancing.utils.tool import load_yaml


HOME_PATH = os.getenv("REBALANCING_HOME", '.')


def get_config_yaml():
    # config
    config_path = os.path.join(HOME_PATH, 'config.yml')

    if os.path.exists(config_path):
        # get from config.yml
        return load_yaml(config_path)

    else:
        raise FileNotFoundError(f"can't find config.yml: {config_path}")


class Config:
    """
    # priority
    1. environment variables
    2. config.yml
    """
    conf = get_config_yaml()

    @classmethod
    def get(cls,
            section: str,
            key: str,
            default: Any = None,
            error_if_not_exists: bool = False,
            **kwargs) -> Optional[Any]:

        # try to get from config.yml
        option: Any = cls.conf.get(str(section).lower(), {}).get(str(key).lower(), None)

        if option is None:
            if default is not None:
                return default
            else:
                if error_if_not_exists:
                    raise ConfigException(f"Section '{section}' 내에 '{key}'가 존재하지 않습니다.")
                else:
                    return None

        else:
            return option

    @classmethod
    def has_option(cls, section: str, key: str) -> bool:
        try:
            option = cls.get(section, key, error_if_not_exists=True)
            return option is not None

        except ConfigException as e:
            return False

    @classmethod
    def get_boolean(cls, section: str, key: str, **kwargs) -> Optional[bool]:
        val = str(cls.get(section, key, **kwargs)).lower().strip()

        if '#' in val:
            val = val.split('#')[0].strip()
        if val in ('t', 'true', '1'):
            return True
        elif val in ('f', 'false', '0'):
            return False
        else:
            raise ConfigException(
                f'Failed to convert value to bool. Please check "{key}" key in "{section}" section. '
                f'Current value: "{val}".'
            )

    @classmethod
    def get_int(cls, section: str, key: str, **kwargs) -> Optional[int]:
        val = cls.get(section, key, **kwargs)

        try:
            return int(val)
        except ValueError:
            raise ConfigException(
                f'Failed to convert value to int. Please check "{key}" key in "{section}" section. '
                f'Current value: "{val}".'
            )

    @classmethod
    def get_float(cls, section: str, key: str, **kwargs) -> Optional[float]:
        val = cls.get(section, key, **kwargs)

        try:
            return float(val)
        except ValueError:
            raise ConfigException(
                f'Failed to convert value to float. Please check "{key}" key in "{section}" section. '
                f'Current value: "{val}".'
            )

    @classmethod
    def get_list(cls, section: str, key: str, **kwargs) -> Optional[List[str]]:
        val = cls.get(section, key, **kwargs)

        if isinstance(val, str):
            return val.split(';')

        elif isinstance(val, list):
            return val

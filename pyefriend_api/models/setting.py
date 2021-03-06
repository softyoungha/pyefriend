from typing import Optional
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import Session

from pyefriend_api.utils.orm_helper import provide_session
from pyefriend_api.config import Config
from .base import Base, Length


# section - key - default value
SETTING_LIST = {
    'ACCOUNT': {
        'ACCOUNT': (Config.get('core', 'ACCOUNT'), '계좌번호'),
    },
    'REBALANCE': {
        'AVAILABLE_LIMIT': (0.9, r'계좌 전체 금액 중 사용할 금액 비율'),
        'DOMESTIC_LIMIT': (0.19, r'AVAILABLE_LIMIT 중 국내 주식 비율'),
        'OVERSEAS_LIMIT': (0.27, r'AVAILABLE_LIMIT 중 외국 주식 비율'),
        'ADDITIONAL_AMOUNT': (0.0, r'계좌 전체 금액 계산시 추가할 금액(타 계좌에 존재하는 자본금)'),
    },
}


class Setting(Base):
    __tablename__ = 'setting'

    # columns
    section = Column(String(Length.TYPE), primary_key=True, comment='Section')
    key = Column(String(Length.ID), primary_key=True, comment='Key')
    value = Column(String(5000), comment='Value')
    comment = Column(String(Length.DESC), comment='코멘트')

    def __init__(self, section: str, key: str, **kwargs):
        super().__init__(**kwargs)

        # upper
        section = section.upper()
        key = key.upper()

        # assertion
        assert section in SETTING_LIST.keys(), f"해당 section이 없습니다: {section}"
        assert key in SETTING_LIST[section].keys(), f"'{section}' section 내에 해당 key가 없습니다: {key}"

        self.section = section
        self.key = key

    @classmethod
    @provide_session
    def get(cls, section: str, key: str, session=None):
        # upper
        section = section.upper()
        key = key.upper()

        row: Optional[cls] = (
            session
                .query(cls)
                .filter(cls.section == section, cls.key == key)
                .first()
        )
        return row

    @provide_session
    def update(self, section: str, key: str, value: str, session: Session = None):
        obj = Setting.get(section=section, key=key, session=session)
        obj.value = value

    @provide_session
    def save(self, session=None):
        session.add(self)

    @classmethod
    @provide_session
    def list(cls, session: Session = None):
        return session.query(cls).all()

    @classmethod
    def get_value(cls, section: str, key: str, with_comment: bool = False, dtype=None):
        row: Setting = cls.get(section=section, key=key)

        if row:
            value = row.value
            if dtype:
                value = dtype(value)

            if with_comment:
                return value, row.comment
            else:
                return value
        else:
            return None

    @classmethod
    @provide_session
    def truncate(cls, session: Session = None):
        session.query(cls).delete()

    @classmethod
    @provide_session
    def initialize(cls, first: bool = False, session: Session = None):
        items = [dict(section=section, key=key, value=value, comment=comment)
                 for section, section_value in SETTING_LIST.items()
                 for key, (value, comment) in section_value.items()]

        if first:
            # save
            session.bulk_save_objects([cls(**item) for item in items])

        else:
            # update
            session.bulk_update_mappings(cls, items)

    @staticmethod
    def validate():
        available_limit = Setting.get_value('REBALANCE', 'AVAILABLE_LIMIT', dtype=float)
        domestic_limit = Setting.get_value('REBALANCE', 'DOMESTIC_LIMIT', dtype=float)
        overseas_limit = Setting.get_value('REBALANCE', 'OVERSEAS_LIMIT', dtype=float)

        assert 0 < available_limit <= 1.

        assert 0 <= domestic_limit <= 1.

        assert 0 <= overseas_limit <= 1.

        assert domestic_limit + overseas_limit < 1

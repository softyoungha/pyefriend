from typing import Optional
from sqlalchemy import Column, Integer, Text, String, JSON, Float, Index, ForeignKey, Boolean
from sqlalchemy.orm import Session

from rebalancing.utils.orm_helper import provide_session
from rebalancing.config import Config
from .base import Base, Length


# section - key - default value
SETTING_LIST = {
    'ACCOUNT': {
        'TEST_ACCOUNT': (Config.get('core', 'TEST_ACCOUNT'), '모의투자 계좌번호'),
        'REAL_ACCOUNT': (Config.get('core', 'REAL_ACCOUNT'), '실제투자 계좌번호'),
    },
    'AMOUNT_LIMIT': {
        'AVAILABLE': (0.9, r'계좌 전체 금액 중 사용할 금액 비율'),
        'DOMESTIC': (0.19, r'available 중 국내 주식 비율'),
        'OVERSEAS': (0.27, r'available 중 외국 주식 비율'),
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
    def initialize(cls, force: bool = False, session: Session = None):
        items = [cls(section=section, key=key, value=value, comment=comment)
                 for section, section_value in SETTING_LIST.items()
                 for key, (value, comment) in section_value.items()]
        session.bulk_save_objects(items, update_changed_only=not force)

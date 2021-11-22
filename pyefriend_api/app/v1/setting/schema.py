from typing import Optional
from pydantic import BaseModel, Field


class SettingUpdate(BaseModel):
    value: str = Field(None,
                       title='값',
                       example='5005775101')


class SettingOrm(BaseModel):
    section: str = Field(...,
                         title='섹션',
                         example='ACCOUNT')
    key: str = Field(True,
                     title='키',
                     example='ACCOUNT')
    value: Optional[str] = Field(None,
                                 title='값',
                                 example='5005775101')

    comment: Optional[str] = Field(None,
                                   title='설명',
                                   example='모의투자 계좌번호')

    class Config:
        orm_mode = True

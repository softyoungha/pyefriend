from typing import Optional
from pydantic import BaseModel, Field

from rebalancing.utils.const import Target


class LoginTest(BaseModel):
    target: Target = Field(...,
                           title='타겟장',
                           description="국내/해외 여부('domestic', 'overseas')",
                           example=Target.DOMESTIC)
    account: str = Field(None,
                                   title='계좌명',
                                   description='config.yml에 있는 계좌가 아닌 입력된 계좌를 사용',
                                   example='5005775101')
    password: str = Field(None,
                                    title='비밀번호',
                                    description='account를 직접 입력했을 경우 사용할 password',
                                    example='password')

class LoginTestOutput(LoginTest):
    account: str = Field(..., title='테스트 성공시 사용될 계좌명')
    is_vts: bool = Field(..., title='모의투자여부')


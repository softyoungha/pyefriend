import os
from typing import Optional, List
from fastapi import APIRouter, Request, Response, status, Depends

from rebalancing.models.setting import Setting as SettingModel
from rebalancing.app.auth import login_required
from .schema import SettingOrm, SettingUpdate

r = APIRouter(prefix='/setting',
              tags=['setting'])


@r.get('/', response_model=List[SettingOrm])
async def get_settings(user=Depends(login_required)):
    """### 세팅 가능한 값 전부 조회 """
    return [SettingOrm.from_orm(item) for item in SettingModel.list()]


@r.post('/', status_code=status.HTTP_200_OK)
async def initialize_settings(user=Depends(login_required)):
    """
    ### 세팅값 초기화
    - force: True일 경우 기존 값 초기화
    """
    SettingModel.initialize(first=False)

    return Response('Success', status_code=status.HTTP_200_OK)


@r.get('/{section}/{key}', response_model=SettingOrm)
async def get_a_setting(section: str, key: str, user=Depends(login_required)):
    """
    ### 세팅값 조회
    - section: setting 테이블 내 조회할 section
    - key: section 내 조회할 key
    """
    return SettingOrm.from_orm(SettingModel.get(section=section, key=key))


@r.put('/{section}/{key}', status_code=status.HTTP_200_OK)
async def change_setting(section: str,
                         key: str,
                         request: SettingUpdate,
                         user=Depends(login_required)):
    """
    ### 세팅값 수정
    - section: setting 테이블 내 조회할 section
    - key: section 내 조회할 key
    """
    SettingModel.update(section=section,
                        key=key,
                        value=request.value)

    return Response('Success', status_code=status.HTTP_200_OK)

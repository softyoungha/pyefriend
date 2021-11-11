from fastapi import APIRouter
from .setting.router import r as setting_router
from .database.router import r as database_router
from .report.router import r as report_router


r = APIRouter(prefix='/v1')

r.include_router(setting_router, tags=['v1'])
r.include_router(database_router, tags=['v1'])
r.include_router(report_router, tags=['v1'])

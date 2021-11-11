from fastapi import APIRouter
from .database.router import r as database_router
from .setting.router import r as setting_router
from .report.router import r as report_router


r = APIRouter(prefix='/v1')

r.include_router(database_router)
r.include_router(setting_router)
r.include_router(report_router)

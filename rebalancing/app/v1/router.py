from fastapi import APIRouter
from .database.router import r as database_router
from .setting.router import r as setting_router
from .stock.router import r as stock_router
from .report.router import r as report_router


r = APIRouter(prefix='/v1')

r.include_router(database_router)
r.include_router(setting_router)
r.include_router(stock_router)
r.include_router(report_router)

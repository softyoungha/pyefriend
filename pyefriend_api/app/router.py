from fastapi import APIRouter

from .v1.router import r as v1_router

r = APIRouter(prefix='/api')

r.include_router(v1_router)

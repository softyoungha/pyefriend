from fastapi import APIRouter
from .actions.router import r as execute_router


r = APIRouter(prefix='/v1',
              tags=['v1'])

r.include_router(execute_router)

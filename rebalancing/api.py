"""
RUN command in source:
    uvicorn rebalancing.api:app --reload
"""
import os

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

from rebalancing.models.setting import Setting
from rebalancing.settings import BASE_DIR
from rebalancing.app.router import r

# rebalance app info
title = 'Re-Balancing App'
description = f"""
### PID: {os.getpid()}
"""

# create app
app = FastAPI(title=title,
              description=description,
              debug=True,
              docs_url=None,
              redoc_url=None)

app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

# docs
@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )


@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


# redocs
@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{title} - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )


@app.exception_handler(RequestValidationError)
async def auth_exception_handler(request: Request, exc: RequestValidationError):
    msg = exc.errors()[0].get('msg')
    print('validation error:', msg)
    print('exc.body: ', exc.body)
    return JSONResponse(content={'detail': msg}, status_code=status.HTTP_400_BAD_REQUEST)


@app.get('/')
async def get_accounts_in_configs(request: Request):
    return {
        'test_account': Setting.get_value('ACCOUNT', 'TEST_ACCOUNT'),
        'real_account': Setting.get_value('ACCOUNT', 'REAL_ACCOUNT'),
    }

app.include_router(r)
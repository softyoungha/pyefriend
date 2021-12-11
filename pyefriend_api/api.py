"""
RUN command in source:
    uvicorn pyefriend_api.api:app --host 0.0.0.0 --port 8000 --reload
"""
import os

from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html, get_swagger_ui_oauth2_redirect_html

from pyefriend_api.settings import BASE_DIR
from pyefriend_api.app.auth import r as auth_router
from pyefriend_api.app.router import r as app_router
from pyefriend.exceptions import UnExpectedException

# rebalance app info
title = 'Py-Efriend API'
description = f"""
##### FastAPI PID: {os.getpid()}

<details><summary>Click to Expand</summary>

##### Author: Youngha Park

## Description

'리밸런싱 App'은 FastAPI unicorn으로 실행됩니다.



## **API Routers**

- [auth](#/auth): API 로그인을 위한 JWT Token Router

- [database](#/database): 데이터베이스 설정을 위한 API Router

- [setting](#/setting): 'Setting' 테이블

- [stock](#/stock): 주식 컨트롤용 api

## Getting Started


# Links

- [pyefriend Github](https://github.com/softyoungha/pyefriend)
- [pyefriend PyPi](https://pypi.org/project/pyefriend/1.0/)
- [Github Blog](https://softyoungha.github.io/)
- [한국투자증권 Expert 표준 API Refrence Guide](https://new.real.download.dws.co.kr/download/expert_manual.pdf)

</details>

"""  # + open(os.path.join(BASE_DIR, 'DESCRIPTION.md'), 'r', encoding='utf-8').read()


# create app
def create_app(debug: bool = True) -> FastAPI:
    app = FastAPI(title=title,
                  description=description,
                  version='v1',
                  debug=True,
                  docs_url=None,
                  redoc_url=None)

    app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")

    # docs
    @app.get("/", include_in_schema=False)
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

    @app.exception_handler(UnExpectedException)
    async def auth_exception_handler(request: Request, exc: UnExpectedException):
        print(exc.detail)
        return JSONResponse(content={'detail': exc.detail}, status_code=status.HTTP_400_BAD_REQUEST)

    app.include_router(auth_router)
    app.include_router(app_router)

    return app


app = create_app()

@echo off

set REBAL_HOME=.

:: Activate Python
call venv/Scripts/activate.bat

:: Run Fastapi
uvicorn rebalancing.api:app --reload
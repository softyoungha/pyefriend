@echo off

set REBAL_HOME=.

:: Activate Python
call venv/Scripts/activate.bat

:: Run Fastapi
uvicorn rebalancing.api:app --host 0.0.0.0 --port 8000 --reload
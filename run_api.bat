@echo off

:: Activate Python
activate.bat

:: Run Fastapi
uvicorn rebalancing.api:app --host 0.0.0.0 --port 8000 --reload
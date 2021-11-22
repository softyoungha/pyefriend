@echo off

:: [Warning] activate venv(python 32-bit) in cmd with administrator mode

:: Run Fastapi
uvicorn pyefriend_api.api:app --host 0.0.0.0 --port 8000 --reload
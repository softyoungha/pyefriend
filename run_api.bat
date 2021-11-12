@echo off

:: [주의] 관리자모드로 실행한 cmd.exe에서 venv를 활성화시킨 후 사용하세요
:: Run Fastapi
uvicorn rebalancing.api:app --host 0.0.0.0 --port 8000 --reload
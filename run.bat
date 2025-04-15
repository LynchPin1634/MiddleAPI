@echo off
start uvicorn MiddleAPI:app --host 0.0.0.0 --port 8000
timeout /t 1 >nul
start http://localhost:8000/?html=index.html
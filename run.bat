@echo off




call .venv\Scripts\activate.bat
uvicorn MiddleAPI:app --host 0.0.0.0 --port 8000

timeout /t 3 >nul
start http://localhost:8000/?html=index.html
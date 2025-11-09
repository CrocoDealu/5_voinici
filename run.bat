@echo off

start "FastAPI" /min cmd /c "cd quiz-feedback-engine && call venv\Scripts\activate.bat && python -m uvicorn main:app --host 127.0.0.1 --port 5000"
timeout /t 2 /nobreak >nul
start "Django" /min cmd /c "cd app-django && call venv\Scripts\activate.bat && python manage.py runserver 127.0.0.1:8001"

echo Services started.
echo Django:  http://127.0.0.1:8001
echo FastAPI: http://127.0.0.1:5000
echo Close the two console windows (FastAPI, Django) to stop.

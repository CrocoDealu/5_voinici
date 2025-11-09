@echo off

start /min cmd /c "cd quiz-feedback-engine && venv\Scripts\activate && python main.py"
timeout /t 2 /nobreak >nul
start /min cmd /c "cd app-django && venv\Scripts\activate && python manage.py runserver"

echo Services started.
echo Django: http://127.0.0.1:8000
echo FastAPI: http://127.0.0.1:5000
echo Close the terminal windows to stop services.

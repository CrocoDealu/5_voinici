@echo off
setlocal enabledelayedexpansion

REM Django
cd app-django
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python manage.py migrate --no-input
deactivate
cd ..

REM FastAPI
cd quiz-feedback-engine
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
deactivate
cd ..

echo Setup complete.

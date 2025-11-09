@echo off
setlocal enabledelayedexpansion

echo Setting up Django service...
cd app-django
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
python manage.py migrate --no-input
deactivate
cd ..

echo Setting up QuizFeedbackEngine service...
cd quiz-feedback-engine
python -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
deactivate
cd ..

echo Setup complete.

#!/usr/bin/env bash
set -euo pipefail

echo "Setting up Django service..."
cd app-django
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
python manage.py migrate --no-input
deactivate
cd ..

echo "Setting up QuizFeedbackEngine service..."
cd quiz-feedback-engine
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip --quiet
pip install -r requirements.txt --quiet
deactivate
cd ..

echo "Setup complete."

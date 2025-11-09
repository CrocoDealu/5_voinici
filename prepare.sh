#!/usr/bin/env bash
set -euo pipefail

# Django
cd app-django
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
python3 manage.py migrate --no-input
deactivate
cd ..

# FastAPI
cd quiz-feedback-engine
python3 -m venv venv
source venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install -r requirements.txt
deactivate
cd ..

echo "Setup complete."

#!/usr/bin/env bash
set -euo pipefail

cleanup() {
    if [[ -n "${django_pid:-}" ]] && kill -0 "${django_pid}" 2>/dev/null; then
        kill "${django_pid}"
    fi
    if [[ -n "${fastapi_pid:-}" ]] && kill -0 "${fastapi_pid}" 2>/dev/null; then
        kill "${fastapi_pid}"
    fi
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

cd quiz-feedback-engine
source venv/bin/activate
python main.py > /dev/null 2>&1 &
fastapi_pid=$!
deactivate
cd ..

cd app-django
source venv/bin/activate
python manage.py runserver > /dev/null 2>&1 &
django_pid=$!
deactivate
cd ..

echo "Services started."
echo "Django: http://127.0.0.1:8000"
echo "FastAPI: http://127.0.0.1:5000"
echo "Press Ctrl+C to stop."

wait

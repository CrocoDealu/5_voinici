#!/usr/bin/env bash
set -euo pipefail

cleanup() {
  [[ -n "${django_pid:-}"  ]] && kill -0 "$django_pid"  2>/dev/null && kill "$django_pid"  || true
  [[ -n "${fastapi_pid:-}" ]] && kill -0 "$fastapi_pid" 2>/dev/null && kill "$fastapi_pid" || true
  exit 0
}
trap cleanup SIGINT SIGTERM EXIT

# FastAPI (127.0.0.1:5000)
cd quiz-feedback-engine
source venv/bin/activate
python -m uvicorn main:app --host 127.0.0.1 --port 5000 &
fastapi_pid=$!
deactivate
cd ..

# Django (127.0.0.1:8001)
cd app-django
source venv/bin/activate
python manage.py runserver 127.0.0.1:8001 &
django_pid=$!
deactivate
cd ..

echo "Django:  http://127.0.0.1:8001"
echo "FastAPI: http://127.0.0.1:5000"
wait


FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

COPY backend/requirements.lock /app/backend/requirements.lock

RUN python -m pip install --no-cache-dir -r /app/backend/requirements.lock

COPY backend/ /app/backend/
COPY ml/models/ /app/ml/models/

RUN python backend/scripts/check_runtime.py

CMD ["sh", "-c", "exec python -m uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8000} --no-access-log"]

FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY backend /app/backend
ENV PYTHONPATH=/app

# single entrypoint, pick mode at runtime
ENV APP_MODE=api
CMD ["sh", "-c", "python -m backend.src.main ${APP_MODE}"]

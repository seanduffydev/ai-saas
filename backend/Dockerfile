# Backend for Commodity Forecasting Lab. Railway uses this instead of Nixpacks
# so we avoid NIXPACKS_PATH and secrets-in-build warnings.
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY app ./app

# PORT is injected by Railway at runtime; use shell so it is expanded
ENV PORT=8000
EXPOSE 8000
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]

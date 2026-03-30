# -------- STAGE 1 --------
FROM python:3.12-slim AS builder

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# -------- STAGE 2 --------
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libssl3 \
    ca-certificates \
    libglib2.0-0 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local

COPY . .

EXPOSE 8550

ENV PYTHONUNBUFFERED=1
ENV FLET_WEB_RENDERER=canvaskit
ENV PYTHONPATH=/app

RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

CMD ["python", "app.py"]
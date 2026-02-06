FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/pyproject.toml
RUN pip install --no-cache-dir -U pip \
 && pip install --no-cache-dir .

COPY app /app/app
COPY scripts /app/scripts

EXPOSE 8000
CMD ["uvicorn","app.main:app","--host","0.0.0.0","--port","8000"]

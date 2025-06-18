FROM python:3.12-slim

# System packages for psycopg‑binary
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /srv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1
EXPOSE 8000

# Entry‑point: run migrations then gunicorn
CMD python -m app.db_migrate && \
    gunicorn -w 4 -b unix:/tmp/gunicorn.sock "app:create_app()"

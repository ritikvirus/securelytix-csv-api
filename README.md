# Securelytix CSV Bulk-Ingest API

Upload a **100 k-row × 10-column CSV** and insert it into PostgreSQL in **≤ 50 ms**  
(measured inside the DB) through a minimalist Flask micro-service.

| Component | Version | Why |
|-----------|---------|-----|
| Python | 3.12-slim | Small base, long-term support |
| Flask  | 3.0 | Lightweight WSGI |
| psycopg | 3.1 | Modern driver, `copy()` helper |
| PostgreSQL | 15.6-alpine | Fast `COPY FROM STDIN` |
| Gunicorn | 22 | Production WSGI, UNIX socket |
| Nginx | 1.26-alpine | Reverse proxy + TLS |
| Docker Compose | v2 | One-command local stack |

---

## 1 . Architecture

Client ──► Nginx (TLS) ──► Gunicorn + Flask ──► PostgreSQL
▲ │ ▲
│ shared /tmp │ │
└───────── UNIX socket gunicorn.sock

---

## 2 . Repo layout
app/
├─ init.py # app factory + pooled PG
├─ main.py # /upload endpoint
└─ db_migrate.py # runs *.sql scripts
migrations/
└─ 001_init.sql
scripts/
├─ make_fake_csv.py # generate test CSV
└─ bench.py # quick latency bench
Dockerfile
docker-compose.yml
nginx.conf
---

## 3 . Prerequisites

* **Docker Desktop** (macOS / Windows) or docker-engine + Compose v2 on Linux.
* `git`, `python3` for local utilities.

---

## 4 . Quick start

```bash
git clone git@github.com:ritikvirus/securelytix-csv-api.git
cd securelytix-csv-api

# ① environment
cat > .env <<'EOF'
POSTGRES_USER=securelytix
POSTGRES_PASSWORD=securelytixpwd
POSTGRES_DB=securelytix
EOF

# ② build & run
docker compose build api
docker compose up -d

docker compose ps
open http://localhost/upload   # 405 = service up

python3 scripts/make_fake_csv.py 100000 > /tmp/test.csv
time curl -F file=@/tmp/test.csv http://localhost/upload

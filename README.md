# Securelytix CSV Bulk-Ingest API

[![CI](https://github.com/ritikvirus/securelytix-csv-api/actions/workflows/ci.yml/badge.svg)](https://github.com/ritikvirus/securelytix-csv-api/actions)
[![Docker Image](https://img.shields.io/docker/v/ritikvirus/securelytix-csv-api)](https://hub.docker.com/r/ritikvirus/securelytix-csv-api)
[![License: MIT](https://img.shields.io/github/license/ritikvirus/securelytix-csv-api)](https://github.com/ritikvirus/securelytix-csv-api/blob/main/LICENSE)

This repository contains a minimal **Flask** micro-service behind **Nginx** and **Gunicorn** to accept a **100,000‑row × 10‑column CSV** upload and perform a bulk insert into **PostgreSQL** in **≤ 50 ms** (measured *inside* the database).

---

## Table of Contents

1. [Overview](#overview)
2. [What & Why](#what--why)
3. [Architecture](#architecture)
4. [Repository Structure](#repository-structure)
5. [Prerequisites](#prerequisites)
6. [Setup & Configuration](#setup--configuration)
7. [Build & Run](#build--run)
8. [Testing & Benchmarking](#testing--benchmarking)
9. [Performance Optimizations](#performance-optimizations)
10. [Logging & Monitoring](#logging--monitoring)
11. [Commands Summary](#commands-summary)
12. [Contributing](#contributing)
13. [License](#license)
14. [Cleanup](#cleanup)

---

## Overview

The Securelytix CSV Bulk-Ingest API is designed to:

* **Stream** a large CSV upload without excessive memory usage.
* Use PostgreSQL’s `COPY FROM STDIN` to insert 100 k rows in under **50 ms**.
* Run in a **Docker Compose** stack, making local development and testing a one-command affair.

---

## What & Why

| Component          | Version       | Purpose & Rationale                                               |
| ------------------ | ------------- | ----------------------------------------------------------------- |
| **Python**         | `3.12-slim`   | Minimal base image, long-term support, security fixes.            |
| **Flask**          | `3.0`         | Lightweight WSGI framework for quick API development.             |
| **psycopg**        | `3.1`         | Modern driver with built-in `.copy()` helper for bulk load.       |
| **PostgreSQL**     | `15.6-alpine` | Fast bulk ingest via `COPY FROM STDIN`, small footprint.          |
| **Gunicorn**       | `22`          | Production WSGI server, manages worker processes via UNIX socket. |
| **Nginx**          | `1.26-alpine` | Reverse proxy, TLS termination, health checks.                    |
| **Docker Compose** | `v2`          | Orchestrate multi-container stack with one command.               |

Each component is chosen for **speed**, **small size**, and **production-readiness**.

---

## Architecture

```
Client ──► Nginx (TLS) ──► Gunicorn + Flask ──► PostgreSQL
              ▲                          ▲
              │  UNIX socket (gunicorn.sock)  
              └──── shared /tmp directory ──┘
```

* **Nginx** handles TLS and proxies to **gunicorn.sock**.
* **Gunicorn** runs multiple Flask workers for concurrency.
* **Flask** streams the CSV and invokes `psycopg.copy()` for bulk insert.
* **PostgreSQL** runs in its own container with tuned defaults.

---

## Repository Structure

```
├── app/
│   ├── __init__.py       # Application factory & DB pool setup
│   ├── main.py           # `/upload` endpoint
│   └── db_migrate.py     # Runs SQL migrations in `migrations/`
├── migrations/
│   └── 001_init.sql      # `records` table schema
├── scripts/
│   ├── make_fake_csv.py  # Generate dummy CSV
│   └── bench.py          # Benchmark script
├── Dockerfile            # Builds the Flask + psycopg app
├── docker-compose.yml    # Defines `api`, `db`, `nginx` services
├── nginx.conf            # Reverse-proxy & health-check config
└── README.md             # This file
```

---

## Prerequisites

* **Docker Desktop** (macOS/Windows) *or* Docker Engine + Compose v2 on Linux.
* **git** and **python3** for utility scripts.

---

## Setup & Configuration

1. **Clone the repo**:

   ```bash
   git clone git@github.com:ritikvirus/securelytix-csv-api.git
   cd securelytix-csv-api
   ```

2. **Create environment file** (`.env`):

   ```bash
   cat > .env << 'EOF'
   POSTGRES_USER=securelytix
   POSTGRES_PASSWORD=securelytixpwd
   POSTGRES_DB=securelytix
   EOF
   ```

3. **Run DB migrations** (creates `records` table):

   ```bash
   docker compose run --rm api python app/db_migrate.py
   ```

---

## Build & Run

1. **Build the API image**:

   ```bash
   docker compose down --remove-orphans
   docker compose up -d --build api     

   ```

   ```bash
   docker compose build api
   ```

3. **Start all services**:

   ```bash
   docker compose up -d
   ```

4. **Verify**:

   ```bash
   docker compose ps
   curl -I http://localhost/upload  # should return 405 (endpoint exists)
   ```

5. **Stop services**:

   ```bash
   docker compose down
   ```

---

## Testing & Benchmarking

* **Generate a fake CSV** (100 k rows × 10 cols):

  ```bash
  python3 scripts/make_fake_csv.py 100000 > /tmp/test.csv
  ```

* **Manual benchmark**:

  ```bash
  time curl -F file=@/tmp/test.csv http://localhost/upload
  ```

  * `time` shows client-side duration. Server logs include:

    ```
    Inserted 100000 rows in XX.XX ms
    ```

* **Automated bench**:

  ```bash
  python3 scripts/bench.py --rows 100000
  ```

  * Runs 5 uploads and reports mean ± stddev.

---

## Performance Optimizations

1. **Connection Pooling**: reuse DB connections via `psycopg.connect(pool_size=…)`.
2. **`COPY FROM STDIN`**: native bulk-load API, far faster than batched `INSERT`.
3. **Streaming CSV Parse**: use Python’s `csv.reader` on the request stream to minimize memory.

---

## Logging & Monitoring

* Logs to stdout:

  * Startup messages (Nginx, Gunicorn).
  * Flask logs at **INFO** level.
  * On each upload: row count, insert latency, errors.

* **Tail logs**:

  ```bash
  docker compose logs -f api
  ```

---

## Commands Summary

| Action            | Command                                                       |
| ----------------- | ------------------------------------------------------------- |
| Clone repo        | `git clone git@github.com:ritikvirus/securelytix-csv-api.git` |
| Generate `.env`   | see [Setup & Configuration](#setup--configuration)            |
| DB migrate        | `docker compose run --rm api python app/db_migrate.py`        |
| Build API         | `docker compose build api`                                    |
| Start stack       | `docker compose up -d`                                        |
| Stop stack        | `docker compose down`                                         |
| Generate test CSV | `python3 scripts/make_fake_csv.py 100000`                     |
| Manual benchmark  | `time curl -F file=@/tmp/test.csv http://localhost/upload`    |
| Automated bench   | `python3 scripts/bench.py --rows 100000`                      |
| Tail API logs     | `docker compose logs -f api`                                  |

---

## Contributing

Contributions are welcome! Please open issues or pull requests in this repository.

---

## License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## Cleanup

Remove all containers, volumes, and images:

```bash
bash -lc "docker compose down --volumes --rmi local"
```

"""
Very light migration runner: executes every *.sql file in /migrations
once, in lexical order, inside a transaction.
"""
from pathlib import Path
import psycopg
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(message)s")
MIGRATIONS_DIR = Path(__file__).resolve().parent.parent / "migrations"

def run():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL must be set")

    sql_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
    with psycopg.connect(dsn) as conn:
        with conn.transaction():
            for path in sql_files:
                logging.info("Applying %s ...", path.name)
                conn.execute(path.read_text())
    logging.info("✅  Migrations complete.")

if __name__ == "__main__":
    run()

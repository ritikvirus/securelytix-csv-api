import os
from flask import Flask
from psycopg_pool import ConnectionPool

def create_app() -> Flask:
    app = Flask(__name__)

    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise RuntimeError("DATABASE_URL must be set")

    # Global connection pool (lifetime = app life‑cycle)
    app.pg_pool = ConnectionPool(conninfo=dsn, open=True)

    # Blueprints / routes imported lazily to avoid circular deps
    from .main import bp as main_bp
    app.register_blueprint(main_bp)

    return app

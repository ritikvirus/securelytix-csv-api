import csv, io, time, logging
from flask import Blueprint, request, jsonify, current_app

bp = Blueprint("main", __name__)
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

@bp.post("/upload")
def upload_csv():
    if "file" not in request.files:
        return jsonify(error="missing file"), 400

    # Decode stream as UTF‑8 text; allow \r\n etc.
    raw = request.files["file"].stream
    stream = io.TextIOWrapper(raw, encoding="utf-8", newline="")

    # Basic validation while streaming header
    reader = csv.reader(stream)
    header = next(reader)
    if len(header) != 10:
        return jsonify(error="expected 10 columns in CSV header"), 400

    # Rewind so COPY sees whole file (including header)
    stream.seek(0)

    t0 = time.perf_counter_ns()
    with current_app.pg_pool.connection() as conn, conn.cursor() as cur:
        cur.copy_expert(
            "COPY records FROM STDIN WITH CSV HEADER",
            stream
        )
    latency_ms = (time.perf_counter_ns() - t0) / 1_000_000

    log.info("insert_ms=%0.2f rows=100k", latency_ms)
    return jsonify(insert_latency_ms=latency_ms), 201

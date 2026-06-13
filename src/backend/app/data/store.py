"""SQLite-backed WC 2026 fixture store."""

from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

DEFAULT_DB_PATH = os.environ.get(
    "FIXTURES_DB_PATH",
    str(Path(__file__).resolve().parents[4] / "workspace" / "artifacts" / "fixtures.db"),
)


def _connect(db_path: str | None = None) -> sqlite3.Connection:
    path = db_path or DEFAULT_DB_PATH
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str | None = None) -> None:
    with _connect(db_path) as conn:
        conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS fixtures (
                id INTEGER PRIMARY KEY,
                external_id TEXT,
                date TEXT NOT NULL,
                datetime TEXT,
                home_team TEXT NOT NULL,
                away_team TEXT NOT NULL,
                stage TEXT,
                group_code TEXT,
                venue TEXT,
                neutral INTEGER DEFAULT 1,
                home_score INTEGER,
                away_score INTEGER,
                status TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_fixtures_date ON fixtures(date);
            CREATE INDEX IF NOT EXISTS idx_fixtures_datetime ON fixtures(datetime);
            CREATE INDEX IF NOT EXISTS idx_fixtures_status ON fixtures(status);
            CREATE TABLE IF NOT EXISTS sync_runs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider TEXT NOT NULL,
                started_at TEXT NOT NULL,
                finished_at TEXT,
                rows_updated INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                error TEXT
            );
            """
        )
        conn.commit()


def upsert_fixtures(fixtures: list[dict[str, Any]], db_path: str | None = None) -> int:
    from app.data.loader import normalize_stage, normalize_team

    init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    count = 0
    with _connect(db_path) as conn:
        for fx in fixtures:
            conn.execute(
                """
                INSERT INTO fixtures (
                    id, external_id, date, datetime, home_team, away_team,
                    stage, group_code, venue, neutral, home_score, away_score,
                    status, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    external_id=excluded.external_id,
                    date=excluded.date,
                    datetime=excluded.datetime,
                    home_team=excluded.home_team,
                    away_team=excluded.away_team,
                    stage=excluded.stage,
                    group_code=excluded.group_code,
                    venue=excluded.venue,
                    neutral=excluded.neutral,
                    home_score=excluded.home_score,
                    away_score=excluded.away_score,
                    status=excluded.status,
                    updated_at=excluded.updated_at
                """,
                (
                    int(fx["id"]),
                    fx.get("external_id"),
                    fx["date"],
                    fx.get("datetime"),
                    normalize_team(fx["home_team"]),
                    normalize_team(fx["away_team"]),
                    normalize_stage(fx.get("stage", "Group")),
                    fx.get("group"),
                    fx.get("venue", ""),
                    1 if fx.get("neutral", True) else 0,
                    fx.get("home_score"),
                    fx.get("away_score"),
                    fx.get("status", "upcoming"),
                    now,
                ),
            )
            count += 1
        conn.commit()
    return count


def row_to_fixture(row: sqlite3.Row) -> dict[str, Any]:
    from app.data.loader import normalize_stage

    item = {
        "id": row["id"],
        "date": row["date"],
        "datetime": row["datetime"],
        "home_team": row["home_team"],
        "away_team": row["away_team"],
        "stage": normalize_stage(row["stage"]),
        "group": row["group_code"],
        "venue": row["venue"],
        "neutral": bool(row["neutral"]),
        "status": row["status"],
    }
    if row["external_id"]:
        item["external_id"] = row["external_id"]
    if row["home_score"] is not None:
        item["home_score"] = row["home_score"]
        item["away_score"] = row["away_score"]
    return item


def query_fixtures(
    *,
    status: str = "all",
    group: str | None = None,
    stage: str | None = None,
    sort: str = "datetime",
    order: str = "asc",
    db_path: str | None = None,
) -> list[dict[str, Any]]:
    init_db(db_path)
    clauses: list[str] = []
    params: list[Any] = []
    if status != "all":
        clauses.append("status = ?")
        params.append(status)
    if group:
        clauses.append("group_code = ?")
        params.append(group.upper())
    if stage:
        clauses.append("stage = ?")
        params.append(stage)

    where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
    sort_col = "datetime" if sort == "datetime" else "date"
    direction = "ASC" if order == "asc" else "DESC"
    # Null datetimes sort last when ascending
    nulls = "NULLS LAST" if order == "asc" else "NULLS FIRST"
    sql = f"SELECT * FROM fixtures {where} ORDER BY {sort_col} {direction} {nulls}, id {direction}"

    with _connect(db_path) as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_fixture(r) for r in rows]


def fixture_count(db_path: str | None = None) -> int:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT COUNT(*) AS c FROM fixtures").fetchone()
    return int(row["c"])


def record_sync_run(
    provider: str,
    status: str,
    rows_updated: int = 0,
    error: str | None = None,
    db_path: str | None = None,
) -> None:
    init_db(db_path)
    now = datetime.now(timezone.utc).isoformat()
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO sync_runs (provider, started_at, finished_at, rows_updated, status, error)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (provider, now, now, rows_updated, status, error),
        )
        conn.commit()


def last_sync_status(db_path: str | None = None) -> dict[str, Any] | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT * FROM sync_runs ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if not row:
        return None
    return {
        "provider": row["provider"],
        "started_at": row["started_at"],
        "finished_at": row["finished_at"],
        "rows_updated": row["rows_updated"],
        "status": row["status"],
        "error": row["error"],
    }


def seed_from_json(json_path: Path, db_path: str | None = None) -> int:
    from app.data.loader import load_wc2026_fixtures_from_json

    fixtures = load_wc2026_fixtures_from_json(json_path)
    return upsert_fixtures(fixtures, db_path=db_path)

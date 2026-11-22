import logging
import re
import sqlite3
from collections.abc import Iterator, Mapping
from pathlib import Path
from typing import Any

import psycopg

from ..config import DATABASE_URL, SUPABASE_KEY, SUPABASE_URL
from .schema import init_sqlite_db

logger = logging.getLogger(__name__)

supabase_client = None
if SUPABASE_URL and SUPABASE_KEY:
    try:
        from supabase import create_client

        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as exc:
        logger.warning("Supabase client initialization failed: %s", exc)


class _CompatibleRow(Mapping):
    """Provide SQLite Row-style named and positional access to PostgreSQL rows."""

    def __init__(self, names: tuple[str, ...], values: tuple[Any, ...]):
        self._names = names
        self._values = values
        self._indexes = {name: index for index, name in enumerate(names)}

    def __getitem__(self, key: str | int | slice) -> Any:
        if isinstance(key, (int, slice)):
            return self._values[key]
        return self._values[self._indexes[key]]

    def __iter__(self) -> Iterator[str]:
        return iter(self._names)

    def __len__(self) -> int:
        return len(self._names)


def _compatible_row_factory(cursor: Any):
    names: tuple[str, ...] | None = None

    def make_row(values: tuple[Any, ...]) -> _CompatibleRow:
        nonlocal names
        if names is None:
            names = tuple(column.name for column in cursor.description or ())
        return _CompatibleRow(names, values)

    return make_row


def _convert_qmark_placeholders(query: str) -> str:
    """Translate SQLite-style placeholders without changing quoted SQL text."""
    output: list[str] = []
    index = 0
    quote: str | None = None
    line_comment = False
    block_comment = False
    dollar_quote: str | None = None

    while index < len(query):
        if dollar_quote:
            if query.startswith(dollar_quote, index):
                output.append(dollar_quote)
                index += len(dollar_quote)
                dollar_quote = None
            else:
                output.append(query[index])
                index += 1
            continue

        char = query[index]
        next_char = query[index + 1] if index + 1 < len(query) else ""

        if line_comment:
            output.append(char)
            index += 1
            if char == "\n":
                line_comment = False
            continue

        if block_comment:
            output.append(char)
            index += 1
            if char == "*" and next_char == "/":
                output.append(next_char)
                index += 1
                block_comment = False
            continue

        if quote:
            output.append(char)
            index += 1
            if char == quote:
                if next_char == quote:
                    output.append(next_char)
                    index += 1
                else:
                    quote = None
            elif char == "\\" and next_char:
                output.append(next_char)
                index += 1
            continue

        if char in ("'", '"'):
            quote = char
            output.append(char)
            index += 1
        elif char == "-" and next_char == "-":
            line_comment = True
            output.extend((char, next_char))
            index += 2
        elif char == "/" and next_char == "*":
            block_comment = True
            output.extend((char, next_char))
            index += 2
        elif char == "$":
            match = re.match(r"\$(?:[A-Za-z_][A-Za-z_0-9]*)?\$", query[index:])
            if match:
                dollar_quote = match.group(0)
                output.append(dollar_quote)
                index += len(dollar_quote)
            else:
                output.append(char)
                index += 1
        elif char == "?":
            output.append("%s")
            index += 1
        else:
            output.append(char)
            index += 1

    return "".join(output)


class _PostgresConnection:
    def __init__(self, connection: psycopg.Connection):
        self._connection = connection

    def execute(self, query: str, params: Any = None, *, prepare: bool | None = None):
        return self._connection.execute(
            _convert_qmark_placeholders(query),
            params,
            prepare=prepare,
        )

    def commit(self) -> None:
        self._connection.commit()

    def close(self) -> None:
        self._connection.close()

    def __enter__(self):
        self._connection.__enter__()
        return self

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> Any:
        return self._connection.__exit__(exc_type, exc_value, traceback)


def get_db_path() -> str:
    if DATABASE_URL.startswith("sqlite:///"):
        return DATABASE_URL.replace("sqlite:///", "", 1)
    return str(Path(__file__).resolve().parents[2] / "cascade_intelligence.db")


def get_database_connection():
    if DATABASE_URL.startswith("sqlite:///"):
        path = get_db_path()
        init_sqlite_db(path)
        con = sqlite3.connect(path, timeout=15)
        con.row_factory = sqlite3.Row
        return con

    database_url = DATABASE_URL
    if database_url.startswith("postgres://"):
        database_url = "postgresql://" + database_url[len("postgres://"):]
    elif database_url.startswith("postgresql+psycopg://"):
        database_url = "postgresql://" + database_url[len("postgresql+psycopg://"):]
    if not database_url.startswith("postgresql://"):
        raise ValueError("DATABASE_URL must use sqlite:/// or postgresql://.")

    connection = psycopg.connect(database_url, row_factory=_compatible_row_factory)
    return _PostgresConnection(connection)


def get_sqlite_connection():
    """Backward-compatible connection name; uses DATABASE_URL's configured engine."""
    return get_database_connection()


def init_database() -> None:
    if DATABASE_URL.startswith("sqlite:///"):
        path = get_db_path()
        init_sqlite_db(path)
        backfill_country_metadata(path)
        logger.info("Initialized SQLite database at %s", path)
        return

    schema_path = Path(__file__).resolve().parents[2] / "postgres_schema.sql"
    if not schema_path.is_file():
        raise FileNotFoundError(f"PostgreSQL schema file not found: {schema_path}")

    schema_sql = schema_path.read_text(encoding="utf-8")
    with get_database_connection() as con:
        con.execute(schema_sql, prepare=False)
    logger.info("Initialized PostgreSQL database schema")


def backfill_country_metadata(path: str) -> None:
    """Best-effort metadata repair for local databases collected before geo fields existed."""
    with sqlite3.connect(path, timeout=15) as con:
        con.execute(
            """
            UPDATE articles
            SET source_country = CASE
                WHEN source IN ('BBC World', 'BBC') THEN 'United Kingdom'
                WHEN source IN ('The Guardian World', 'The Guardian') THEN 'United Kingdom'
                WHEN source IN ('UN News', 'WHO News') THEN 'Switzerland'
                ELSE COALESCE(source_country, 'Unknown')
            END
            WHERE source_country IS NULL OR source_country = '' OR source_country = 'Unknown'
            """
        )
        try:
            rows = con.execute(
                """
                SELECT id, title, description
                FROM articles
                WHERE event_country IS NULL OR event_country = '' OR event_country = 'Unknown'
                """
            ).fetchall()
            if rows:
                from ..services.geo_service import extract_event_country

                for row in rows:
                    result = extract_event_country(f"{row[1]}. {row[2] or ''}")
                    if result["country"] != "Unknown":
                        con.execute(
                            "UPDATE articles SET event_country = ? WHERE id = ?",
                            (result["country"], row[0]),
                        )
        except Exception as exc:
            logger.warning("Event-country backfill skipped: %s", exc)
        con.execute(
            """
            UPDATE articles SET event_country = CASE event_country
                WHEN 'USA' THEN 'United States'
                WHEN 'UK' THEN 'United Kingdom'
                WHEN 'Gaza' THEN 'Palestine'
                WHEN 'Russian' THEN 'Russia'
                ELSE event_country
            END
            """
        )
        con.commit()

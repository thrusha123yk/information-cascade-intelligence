
import sqlite3
from pathlib import Path

import psycopg
from psycopg import sql

from app.config import DATABASE_URL


# Original local database
BASE_DIR = Path(__file__).resolve().parent
SQLITE_PATH = BASE_DIR / "cascade_intelligence.db"

# All 12 existing tables
TABLES = [
    "articles",
    "cascade_metrics",
    "collection_logs",
    "evidence_records",
    "extracted_entities",
    "impact_assessments",
    "narrative_relationships",
    "predictions",
    "sources",
    "topic_articles",
    "topic_history",
    "topics",
]

BATCH_SIZE = 500


def migrate():
    if not DATABASE_URL.startswith("postgresql://"):
        raise ValueError("DATABASE_URL is not a PostgreSQL connection.")

    if not SQLITE_PATH.exists():
        raise FileNotFoundError(f"SQLite database not found: {SQLITE_PATH}")

    print("Connecting to local SQLite database...")

    sqlite_conn = sqlite3.connect(SQLITE_PATH)
    sqlite_conn.row_factory = sqlite3.Row

    try:
        with psycopg.connect(DATABASE_URL) as pg_conn:

            print("Connected to Supabase PostgreSQL.")

            # Check all destination tables before migration.
            for table in TABLES:
                count = pg_conn.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    )
                ).fetchone()[0]

                if count != 0:
                    raise RuntimeError(
                        f"Supabase table '{table}' is not empty. "
                        "Migration stopped to prevent duplicate data."
                    )

            print("All destination tables are empty.")
            print("\nStarting migration...\n")

            total_records = 0

            for table in TABLES:

                # Read local SQLite columns.
                sqlite_columns = [
                    row["name"]
                    for row in sqlite_conn.execute(
                        f'PRAGMA table_info("{table}")'
                    ).fetchall()
                ]

                if not sqlite_columns:
                    raise RuntimeError(
                        f"SQLite table '{table}' was not found."
                    )

                # Check PostgreSQL columns.
                pg_columns = [
                    row[0]
                    for row in pg_conn.execute(
                        """
                        SELECT column_name
                        FROM information_schema.columns
                        WHERE table_schema = 'public'
                          AND table_name = %s
                        ORDER BY ordinal_position
                        """,
                        (table,),
                    ).fetchall()
                ]

                if set(sqlite_columns) != set(pg_columns):
                    raise RuntimeError(
                        f"Column mismatch in '{table}'.\n"
                        f"SQLite: {sqlite_columns}\n"
                        f"PostgreSQL: {pg_columns}"
                    )

                columns = sqlite_columns

                select_query = (
                    f'SELECT * FROM "{table}"'
                )

                rows = sqlite_conn.execute(select_query)

                placeholders = sql.SQL(", ").join(
                    sql.Placeholder() for _ in columns
                )

                insert_query = sql.SQL(
                    "INSERT INTO {} ({}) VALUES ({})"
                ).format(
                    sql.Identifier(table),
                    sql.SQL(", ").join(
                        sql.Identifier(column)
                        for column in columns
                    ),
                    placeholders,
                )

                migrated_count = 0

                while True:
                    batch = rows.fetchmany(BATCH_SIZE)

                    if not batch:
                        break

                    values = [
                        tuple(row[column] for column in columns)
                        for row in batch
                    ]

                    pg_conn.cursor().executemany(
                        insert_query,
                        values
                    )

                    migrated_count += len(values)

                total_records += migrated_count

                print(
                    f"{table}: {migrated_count} records copied"
                )

            # Verify all destination counts before commit.
            print("\nVerifying migrated records...\n")

            for table in TABLES:
                sqlite_count = sqlite_conn.execute(
                    f'SELECT COUNT(*) FROM "{table}"'
                ).fetchone()[0]

                pg_count = pg_conn.execute(
                    sql.SQL("SELECT COUNT(*) FROM {}").format(
                        sql.Identifier(table)
                    )
                ).fetchone()[0]

                if sqlite_count != pg_count:
                    raise RuntimeError(
                        f"Count mismatch in {table}: "
                        f"SQLite={sqlite_count}, PostgreSQL={pg_count}"
                    )

                print(f"{table}: {pg_count} records verified")

            print("\nAll 12 tables verified successfully.")

        # PostgreSQL transaction commits automatically here.
        print("\nMIGRATION COMPLETED SUCCESSFULLY!")
        print(f"Total records migrated: {total_records}")

    finally:
        sqlite_conn.close()


if __name__ == "__main__":
    migrate()

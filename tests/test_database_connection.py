from backend.app.database.connection import (
    _CompatibleRow,
    _convert_qmark_placeholders,
)
from backend.app.database import connection
from backend.app.database.repository import get_entities_for_article, save_entities


def test_qmark_placeholder_conversion_preserves_quoted_text_and_comments():
    query = "SELECT '?', ?, 'can''t?', $$?$$ -- ?\n/* ? */ WHERE value = ?"

    assert _convert_qmark_placeholders(query) == (
        "SELECT '?', %s, 'can''t?', $$?$$ -- ?\n/* ? */ WHERE value = %s"
    )


def test_compatible_row_supports_mapping_and_positional_access():
    row = _CompatibleRow(("id", "name"), ("article-1", "Example"))

    assert row[0] == "article-1"
    assert row["name"] == "Example"
    assert dict(row) == {"id": "article-1", "name": "Example"}


def test_save_entities_updates_existing_id_on_sqlite(tmp_path, monkeypatch):
    database_path = tmp_path / "upsert-test.sqlite"
    monkeypatch.setattr(connection, "DATABASE_URL", f"sqlite:///{database_path}")

    save_entities([
        {
            "id": "entity-1",
            "article_id": "article-1",
            "entity_text": "Old name",
            "entity_type": "ORG",
        }
    ])
    save_entities([
        {
            "id": "entity-1",
            "article_id": "article-1",
            "entity_text": "Updated name",
            "entity_type": "ORG",
        }
    ])

    entities = get_entities_for_article("article-1")
    assert len(entities) == 1
    assert entities[0]["entity_text"] == "Updated name"


def test_postgres_startup_executes_schema_as_one_unprepared_script(monkeypatch):
    executed = []

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            return False

        def execute(self, query, params=None, *, prepare=None):
            executed.append((query, params, prepare))

    monkeypatch.setattr(connection, "DATABASE_URL", "postgresql://example")
    monkeypatch.setattr(connection, "get_database_connection", FakeConnection)

    connection.init_database()

    assert len(executed) == 1
    schema_sql, params, prepare = executed[0]
    assert params is None
    assert prepare is False
    assert (
        "limitations_note TEXT DEFAULT 'Historical public news observation "
        "coverage only; not social media reach.',"
    ) in schema_sql
    assert schema_sql.rstrip().endswith(");")

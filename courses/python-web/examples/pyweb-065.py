"""Finite cross-framework engineering investigation with explicit scope."""

import json
import sqlite3
import tempfile
from pathlib import Path


def run_cases():
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "db.sqlite3"
        first = sqlite3.connect(path, timeout=0)
        first.execute("CREATE TABLE notes(id INTEGER PRIMARY KEY, owner INTEGER, title TEXT)")
        first.executemany(
            "INSERT INTO notes(owner,title) VALUES(?,?)", [(i % 5, str(i)) for i in range(40)]
        )
        first.commit()
        query = "SELECT id,title FROM notes WHERE owner=? AND id>? ORDER BY id LIMIT 4"
        before = [row[3] for row in first.execute("EXPLAIN QUERY PLAN " + query, (2, 0))]
        expected = first.execute(query, (2, 0)).fetchall()
        first.execute("CREATE INDEX notes_owner_id ON notes(owner,id)")
        after = [row[3] for row in first.execute("EXPLAIN QUERY PLAN " + query, (2, 0))]
        assert first.execute(query, (2, 0)).fetchall() == expected
        assert any("notes_owner_id" in detail for detail in after)
        second = sqlite3.connect(path, timeout=0)
        first.execute("BEGIN IMMEDIATE")
        try:
            second.execute("UPDATE notes SET title=? WHERE id=1", ("conflict",))
        except sqlite3.OperationalError as error:
            assert "locked" in str(error).lower()
        else:
            raise AssertionError("Competing write unexpectedly succeeded")
        first.rollback()
        second.rollback()
        second.execute("UPDATE notes SET title=? WHERE id=1", ("recovered",))
        second.commit()
        assert first.execute("SELECT title FROM notes WHERE id=1").fetchone()[0] == "recovered"
        first.close()
        second.close()
    return {
        "plan_before": before,
        "plan_after": after,
        "rows_preserved": expected,
        "write_conflict_then_recovery": True,
        "database": "SQLite, not PostgreSQL lock qualification",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True))

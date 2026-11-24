# pyweb-050: Django relationships and query-count diagnosis

Tutorial mode. Stage: advanced. Direct prerequisites: `pyweb-049`.

## Starting point and result

An ORM can make related-object access look like ordinary attribute lookup while issuing extra SQL behind the scenes. This chapter measures the N-plus-one pattern and compares select_related with prefetch_related on the same small fixture. It checks query counts without claiming a universal latency improvement.

## Key terms

- **N+1 query pattern:** One query to load a list followed by one more query for each item's related object, which here gives four queries for three notes.
- **Foreign key:** A field that stores the identifier of a related row, such as a note's author, whose object may need another query to load.
- **select_related:** A QuerySet method that follows single-valued relationships with a SQL join and builds the related objects from the same rows.
- **prefetch_related:** A QuerySet method that loads related objects in a separate query and joins them to the main results in Python.
- **CaptureQueriesContext:** A Django test utility that records the SQL statements executed inside its block so query counts can be checked.

## Mechanism: choose where the relationship is resolved

A Note contains a foreign key to Author. Loading notes alone gives each note an author identifier, but accessing note.author may require another query. Repeating that access across several independently loaded notes can produce one initial query plus one query per note.

Select_related follows suitable single-valued relationships using a SQL join and constructs related objects from the same result. Prefetch_related issues separate queries and associates the results in Python. Prefetching is useful for relationships or access patterns that cannot be represented by one simple single-valued join.

Neither method is automatically best for every dataset. Wide joins duplicate columns across rows; large prefetches can consume memory. Filtering, pagination and relationship cardinality affect the choice. The first requirement is preserving the intended result, followed by observing the actual query and resource behavior.

## Worked case: detect four queries for three notes

The fixture creates one author and three notes. A straightforward iteration reads each note's title and author name. CaptureQueriesContext records four queries: one for notes and three relationship lookups. The program retains the resulting tuples as the semantic baseline.

The repeated author does not automatically imply one shared related-object cache across separately constructed note instances. Each instance can resolve its own relation. This makes a small fixture with one shared author particularly useful for exposing a mistaken caching assumption.

An application with hundreds of rows can turn this pattern into a significant database load. However, query count alone is not latency: network placement, index usage, row sizes and caching all matter. The lesson states the measured count and leaves performance claims to an actual workload test.

## Worked case: preserve results with join and prefetch

The select_related version produces the same tuples with one query. The prefetch_related version produces the same tuples with two queries. Assertions compare all three result sets before checking the expected counts 4, 1 and 2.

This ordering protects against a misleading optimization that changes which rows are returned. A faster query yielding incomplete data is not an equivalent implementation. The fixture's stable ordering also prevents nondeterministic row order from obscuring a genuine semantic comparison.

For many-to-many or reverse relationships, prefetching often fits naturally, but accessing a differently filtered relation afterward can issue a fresh query and bypass the prefetched cache. Inspect the exact access expression used by the template or serializer rather than assuming a prefetch anywhere in the code solves every lookup.

## Worked example: counting the queries behind a prefetch

```python
import sqlite3

db = sqlite3.connect(":memory:")
db.executescript(
    "CREATE TABLE author (id INTEGER PRIMARY KEY, name TEXT);"
    "CREATE TABLE note (id INTEGER PRIMARY KEY, author_id INTEGER, title TEXT);"
    "INSERT INTO author VALUES (1, 'Ada'), (2, 'Grace');"
    "INSERT INTO note (author_id, title) VALUES (1, 'a'), (2, 'b'), (1, 'c');"
)
seen = []
db.set_trace_callback(seen.append)
notes = db.execute("SELECT id, author_id, title FROM note ORDER BY id").fetchall()
ids = sorted({author_id for _, author_id, _ in notes})
marks = ", ".join("?" * len(ids))
names = dict(db.execute(f"SELECT id, name FROM author WHERE id IN ({marks})", ids))
print([(title, names[author_id]) for _, author_id, title in notes])
print(len(seen))
print(seen[1])
```

Expected output:

```text
[('a', 'Ada'), ('b', 'Grace'), ('c', 'Ada')]
2
SELECT id, name FROM author WHERE id IN (1, 2)
```

This is what `prefetch_related("author")` does by hand: one query for the notes, then one `IN` query for the distinct author ids, joined in Python. The trace callback plays the role of `CaptureQueriesContext` and records exactly two statements. Add a hundred more notes and it still records two, while the naive loop in the lesson grows to one query per note plus one. `select_related` would collapse this into a single JOIN, which suits a foreign key; prefetch is the tool for reverse and many-to-many relations, where a JOIN would repeat each parent row once per child.

## Failure diagnosis and discussion

**Why can a template cause database queries?** Attribute access can evaluate lazy relationships or QuerySets. Query behavior belongs to the complete rendering path, not only the view's visibly executed SQL.

**Why not prefetch every relationship?** It can fetch unused data, increase memory and complicate pagination. Load the relationships required by the actual representation and measure the result.

If query counts remain high after an optimization, inspect whether a serializer performs new filtered lookups or creates fresh QuerySets. If memory grows, inspect prefetched cardinality and response size. Continue with forms, which translate user input into model changes and need similarly explicit field ownership.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    from django.conf import settings

    settings.configure(
        SECRET_KEY="synthetic-local-fixture",
        INSTALLED_APPS=[],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
    )
    import django

    django.setup()
    from django.db import connection, models
    from django.test.utils import CaptureQueriesContext

    class Author(models.Model):
        name = models.CharField(max_length=20)

        class Meta:
            app_label = "webfixture"

    class Note(models.Model):
        author = models.ForeignKey(Author, on_delete=models.CASCADE)
        title = models.CharField(max_length=30)

        class Meta:
            app_label = "webfixture"

    with connection.schema_editor() as editor:
        editor.create_model(Author)
        editor.create_model(Note)
    a = Author.objects.create(name="Ada")
    Note.objects.bulk_create([Note(author=a, title=str(i)) for i in range(3)])
    with CaptureQueriesContext(connection) as naive:
        first = [(n.title, n.author.name) for n in Note.objects.order_by("id")]
    with CaptureQueriesContext(connection) as joined:
        second = [
            (n.title, n.author.name) for n in Note.objects.select_related("author").order_by("id")
        ]
    with CaptureQueriesContext(connection) as prefetched:
        third = [
            (n.title, n.author.name) for n in Note.objects.prefetch_related("author").order_by("id")
        ]
    assert first == second == third
    assert (len(naive), len(joined), len(prefetched)) == (4, 1, 2)
    connection.close()
    return {
        "same_rows": first,
        "query_counts": {"naive": 4, "join": 1, "prefetch": 2},
        "scope": "query count, not a latency benchmark",
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)

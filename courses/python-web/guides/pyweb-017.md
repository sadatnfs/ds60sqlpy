# pyweb-017: Flask relational queries and deterministic pagination

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-016`.

## Starting point and result

A result page needs a defined order and a defined continuation rule. This chapter joins items to owners, returns a bounded page and compares keyset continuation with an offset after earlier data is deleted. The database operations actually execute through SQLAlchemy and SQLite.

## Key terms

- **Deterministic ordering:** An ORDER BY on a unique key, such as item ID, so every request sees the rows in the same sequence.
- **Keyset pagination:** Fetching the next page with a condition such as `Item.id > after`, where the last observed ordering key serves as the cursor.
- **Offset pagination:** Skipping a counted number of rows in the ordered result, which can skip or repeat rows when earlier data changes between requests.
- **Explicit join:** A single query that combines items with their owners and selects only the needed columns, avoiding one extra owner query per item.
- **Tie-breaker:** A unique column appended to a nonunique sort key, such as a timestamp, so the ordering and any cursor built from it are unambiguous.

## Mechanism: pagination depends on ordering

The query selects the item ID and owner name in one explicit join, orders by item ID and limits the result to two rows. It does not load an object and then issue an extra owner query for every item. The projection makes the needed columns and relationship explicit.

A cursor value identifies where the next query should begin. Here the cursor is the last observed unique item ID, and the next page uses `Item.id > after`. An offset instead skips a number of rows in the current ordered result. If the result changes between requests, those two definitions can lead to different observations.

A unique ordering key makes this simple cursor unambiguous. If ordering by a nonunique value such as a timestamp, include a stable tie-breaker and encode the complete ordering tuple. A cursor is also application input: validate its type and meaning before constructing the query.

## Worked case: a joined first page

The first page contains item IDs one and two with their corresponding owner names. The query joins the owner table and returns only the selected columns. Assertions check both the IDs and names, so an accidental cross join or incorrect join condition would be visible.

The fixture defines a foreign-key relationship but tests the query behavior here. Database-specific enforcement settings and integrity failure cases are separate concerns. In particular, SQLite deployments must explicitly consider their foreign-key enforcement configuration rather than assuming every declared relation has been tested by a successful join.

## Worked case: deletion shifts an offset

After the first page, item one is deleted. Continuing with cursor two returns IDs three and four. Applying offset two to the changed result instead skips IDs two and three and returns only four. The program reproduces both results.

This does not make every offset API invalid. Offset pagination can be reasonable for small, stable results or explicit page-number navigation. The tradeoff becomes important when data changes, pages grow large or clients require a predictable traversal. A snapshot or other consistency contract may also be necessary for the product's meaning of a complete listing.

## Worked example: a tie-breaker makes keyset pages deterministic

```python
from sqlalchemy import create_engine, text

engine = create_engine("sqlite://")
with engine.begin() as db:
    db.execute(text("CREATE TABLE items (id INTEGER PRIMARY KEY, score INTEGER)"))
    db.execute(text("INSERT INTO items VALUES (1, 50), (2, 70), (3, 50), (4, 70), (5, 90)"))


def page(after_score, after_id, size=2):
    with engine.connect() as db:
        return db.execute(
            text(
                "SELECT score, id FROM items WHERE (score, id) > (:s, :i) "
                "ORDER BY score, id LIMIT :n"
            ),
            {"s": after_score, "i": after_id, "n": size},
        ).all()


first = page(-1, 0)
second = page(*first[-1])
third = page(*second[-1])
print(first, second, third, sep="\n")
```

Expected output:

```text
[(50, 1), (50, 3)]
[(70, 2), (70, 4)]
[(90, 5)]
```

Sorting only by `score` would leave the order of rows 1 and 3, and of 2 and 4, undefined, so a database could return them differently between requests and a cursor of `score > 50` would skip row 3 entirely. Adding `id` as a unique tie-breaker gives a total order, and the row-value comparison `(score, id) > (:s, :i)` resumes exactly after the last row the client saw. The three pages cover all five rows once with no duplicates. The lesson's simpler cursor uses `Item.id` alone because its order is already the primary key. If a new item with score 60 were inserted between page requests, it would appear on the second page without shifting any other row, which offset pagination cannot promise.

## Failure diagnosis

Duplicate or missing items across pages can come from unstable ordering, missing tie-breakers, changed filters or concurrent updates. A cursor must be bound to the relevant query contract, not blindly reused with a different sort order or tenant filter. Large offsets may also require the database to visit and discard substantial work before returning a small page.

If a relationship query becomes slow, inspect the actual SQL and query plan. An ORM method chain is not a performance guarantee. Select only required data, use appropriate indexes and compare observed query counts with the intended behavior.

## Interview discussion

**Why is a LIMIT without a meaningful ORDER BY insufficient?** It bounds the number of returned rows but does not define which stable sequence a client is traversing.

**Does keyset pagination provide a complete historical snapshot?** No. It defines continuation relative to ordering keys. Concurrent inserts, updates and deletion still need a documented consistency interpretation.

## Next step

Use real form validation and CSRF checks. A correctly scoped database query still needs an authenticated and authorized request to invoke it.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from flask import Flask, request
    from sqlalchemy import ForeignKey, String, create_engine, delete, select
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
    from sqlalchemy.pool import StaticPool

    class Base(DeclarativeBase):
        pass

    class Owner(Base):
        __tablename__ = "owners"
        id: Mapped[int] = mapped_column(primary_key=True)
        name: Mapped[str] = mapped_column(String(30))

    class Item(Base):
        __tablename__ = "items"
        id: Mapped[int] = mapped_column(primary_key=True)
        owner_id: Mapped[int] = mapped_column(ForeignKey("owners.id"))

    engine = create_engine("sqlite+pysqlite:///:memory:", poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    with Session.begin() as db:
        db.add_all([Owner(id=1, name="Ada"), Owner(id=2, name="Bo")])
        db.add_all([Item(id=i, owner_id=1 if i % 2 else 2) for i in range(1, 5)])
    app = Flask(__name__)

    @app.get("/items")
    def items():
        try:
            after = int(request.args.get("after", "0"))
        except ValueError:
            return {"error": "integer cursor required"}, 422
        query = (
            select(Item.id, Owner.name)
            .join(Owner)
            .where(Item.id > after)
            .order_by(Item.id)
            .limit(2)
        )
        with Session() as db:
            rows = db.execute(query).all()
            return {"items": [{"id": row.id, "owner": row.name} for row in rows]}

    try:
        client = app.test_client()
        first = client.get("/items").json["items"]
        assert [row["id"] for row in first] == [1, 2]
        assert [row["owner"] for row in first] == ["Ada", "Bo"]
        with Session.begin() as db:
            db.execute(delete(Item).where(Item.id == 1))
        next_page = client.get("/items?after=2").json["items"]
        with Session() as db:
            offset_page = list(db.scalars(select(Item.id).order_by(Item.id).offset(2).limit(2)))
        assert [row["id"] for row in next_page] == [3, 4] and offset_page == [4]
        return {
            "joined_first_page": first,
            "keyset_after_deletion": next_page,
            "offset_after_deletion": offset_page,
        }
    finally:
        engine.dispose()


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Flask documentation](https://flask.palletsprojects.com/en/stable/)
- [Flask testing](https://flask.palletsprojects.com/en/stable/testing/)

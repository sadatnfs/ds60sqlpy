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

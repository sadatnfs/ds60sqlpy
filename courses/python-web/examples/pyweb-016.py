"""Complete finite Flask investigation with original bounded fixtures."""

import json


def run_cases():
    from flask import Flask, request
    from sqlalchemy import String, create_engine, select
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
    from sqlalchemy.pool import StaticPool

    class Base(DeclarativeBase):
        pass

    class Item(Base):
        __tablename__ = "items"
        id: Mapped[int] = mapped_column(primary_key=True)
        title: Mapped[str] = mapped_column(String(40), unique=True)

    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    Session = sessionmaker(engine)
    app = Flask(__name__)

    @app.post("/batch")
    def batch():
        payload = request.get_json(silent=True)
        if (
            not isinstance(payload, dict)
            or not isinstance(payload.get("titles"), list)
            or not 1 <= len(payload["titles"]) <= 3
            or any(not isinstance(x, str) or not 1 <= len(x) <= 40 for x in payload["titles"])
        ):
            return {"error": "one to three bounded titles required"}, 422
        try:
            with Session.begin() as db:
                db.add_all([Item(title=title) for title in payload["titles"]])
                db.flush()
        except IntegrityError:
            return {"error": "duplicate title; batch rolled back"}, 409
        return {"created": len(payload["titles"])}, 201

    @app.get("/items")
    def items():
        with Session() as db:
            return {"titles": list(db.scalars(select(Item.title).order_by(Item.id)))}

    try:
        with app.test_client() as client:
            assert client.post("/batch", json={"titles": ["existing"]}).status_code == 201
            assert client.post("/batch", json={"titles": ["one", "two"]}).status_code == 201
            failed = client.post("/batch", json={"titles": ["temporary", "existing"]})
            assert failed.status_code == 409
            kept = client.get("/items").json["titles"]
            assert kept == ["existing", "one", "two"]
        return {
            "committed_titles": kept,
            "partial_batch_rolled_back": True,
            "database": "actual bounded SQLite transaction",
            "postgresql_executed": False,
        }
    finally:
        engine.dispose()


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))

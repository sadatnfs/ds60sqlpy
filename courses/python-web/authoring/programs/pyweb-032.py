"""Complete finite FastAPI investigation with original bounded fixtures."""

import json


def run_cases():
    from contextlib import asynccontextmanager
    from typing import Annotated

    from fastapi import Depends, FastAPI, HTTPException
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, Field
    from sqlalchemy import Column, Integer, MetaData, String, Table, insert, select
    from sqlalchemy.exc import IntegrityError
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

    metadata = MetaData()
    items = Table(
        "items",
        metadata,
        Column("id", Integer, primary_key=True),
        Column("name", String(40), nullable=False, unique=True),
    )

    @asynccontextmanager
    async def lifespan(app):
        engine = create_async_engine("sqlite+aiosqlite:///:memory:")
        async with engine.begin() as connection:
            await connection.run_sync(metadata.create_all)
        app.state.sessions = async_sessionmaker(engine, expire_on_commit=False)
        try:
            yield
        finally:
            await engine.dispose()

    app = FastAPI(lifespan=lifespan, docs_url=None, redoc_url=None)

    class Input(BaseModel):
        name: str = Field(min_length=1, max_length=40)

    async def session():
        async with app.state.sessions() as db:
            yield db

    @app.post("/items", status_code=201)
    async def create(payload: Input, db: Annotated[AsyncSession, Depends(session)]):
        try:
            async with db.begin():
                result = await db.execute(insert(items).values(name=payload.name))
                identifier = result.inserted_primary_key[0]
        except IntegrityError:
            raise HTTPException(status_code=409, detail="duplicate name") from None
        return {"id": identifier, "name": payload.name}

    @app.get("/items")
    async def listing(db: Annotated[AsyncSession, Depends(session)]):
        result = await db.execute(select(items).order_by(items.c.id))
        return {"items": [dict(row) for row in result.mappings()]}

    with TestClient(app) as client:
        assert client.post("/items", json={"name": "one"}).status_code == 201
        assert client.post("/items", json={"name": "one"}).status_code == 409
        assert client.post("/items", json={"name": "two"}).status_code == 201
        result = client.get("/items").json()
        assert result == {"items": [{"id": 1, "name": "one"}, {"id": 2, "name": "two"}]}
    return {
        "rows": result["items"],
        "async_transaction_recovery": True,
        "engine_owned_by_lifespan": True,
        "postgresql_executed": False,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))

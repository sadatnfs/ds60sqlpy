"""Finite real framework-client checks; this is not browser/TCP/deployment evidence."""

import importlib.metadata
import json
from contextlib import asynccontextmanager

EXPECTED = {
    "fastapi": "0.162.0",
    "starlette": "1.10.0",
    "pydantic": "2.14.1",
    "Flask": "3.1.3",
    "Django": "6.1.2",
    "httpx2": "2.16.0",
}


def flask_case():
    from flask import Flask, jsonify, request

    app = Flask(__name__)
    app.config.update(TESTING=True)

    @app.get("/hello/<name>")
    def hello(name):
        return jsonify(name=name)

    @app.post("/sum")
    def total():
        payload = request.get_json()
        if not isinstance(payload, dict) or set(payload) != {"left", "right"}:
            return {"error": "two named integers required"}, 400
        if any(type(payload[key]) is not int for key in ("left", "right")):
            return {"error": "integers required"}, 400
        return {"total": payload["left"] + payload["right"]}, 201

    with app.test_client() as client:
        assert client.get("/hello/Ada").json == {"name": "Ada"}
        valid = client.post("/sum", json={"left": 2, "right": 3})
        invalid = client.post("/sum", json={"left": True, "right": 3})
        assert valid.status_code == 201 and valid.json == {"total": 5}
        assert invalid.status_code == 400 and client.post("/hello/Ada").status_code == 405
    return {"valid": 201, "invalid": 400, "wrong_method": 405}


def fastapi_case():
    from fastapi import FastAPI, WebSocket
    from fastapi.testclient import TestClient
    from pydantic import BaseModel, ConfigDict, Field

    lifecycle = []

    @asynccontextmanager
    async def lifespan(app):
        lifecycle.append("started")
        app.state.ready = True
        yield
        lifecycle.append("stopped")

    class Item(BaseModel):
        model_config = ConfigDict(strict=True)
        name: str = Field(min_length=1, max_length=40)
        quantity: int = Field(ge=0)

    app = FastAPI(lifespan=lifespan)

    @app.post("/items", status_code=201, response_model=Item)
    async def item(payload: Item):
        assert app.state.ready
        return payload

    @app.websocket("/echo")
    async def echo(socket: WebSocket):
        await socket.accept()
        message = await socket.receive_text()
        await socket.send_text("echo:" + message)
        await socket.close()

    with TestClient(app) as client:
        valid = client.post("/items", json={"name": "book", "quantity": 2})
        invalid = client.post("/items", json={"name": "book", "quantity": "2"})
        assert valid.status_code == 201 and valid.json() == {"name": "book", "quantity": 2}
        assert invalid.status_code == 422
        with client.websocket_connect("/echo") as socket:
            socket.send_text("hello")
            assert socket.receive_text() == "echo:hello"
    assert lifecycle == ["started", "stopped"]
    return {
        "valid": 201,
        "invalid": 422,
        "lifespan": lifecycle,
        "websocket": "finite ASGI exchange",
    }


def django_case():
    import django
    from django.conf import settings

    settings.configure(
        SECRET_KEY="test-only-runtime-probe",
        DEBUG=False,
        ALLOWED_HOSTS=["testserver"],
        ROOT_URLCONF=__name__,
        INSTALLED_APPS=[],
        MIDDLEWARE=[],
        DATABASES={"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}},
        DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
    )
    django.setup()
    from django.db import connection, models
    from django.http import JsonResponse
    from django.test import Client
    from django.urls import path
    from django.views.decorators.http import require_GET

    class Note(models.Model):
        text = models.CharField(max_length=40)

        class Meta:
            app_label = "runtime_probe"
            db_table = "python_web_runtime_probe"

    @require_GET
    def listing(request):
        return JsonResponse(
            {"notes": list(Note.objects.order_by("id").values_list("text", flat=True))}
        )

    global urlpatterns
    urlpatterns = [path("notes/", listing)]
    with connection.schema_editor() as editor:
        editor.create_model(Note)
    try:
        Note.objects.create(text="first")
        Note.objects.create(text="second")
        client = Client()
        response = client.get("/notes/")
        assert response.status_code == 200 and response.json() == {"notes": ["first", "second"]}
        assert client.post("/notes/").status_code == 405
        assert client.get("/missing/").status_code == 404
    finally:
        with connection.schema_editor() as editor:
            editor.delete_model(Note)
        connection.close()
    return {"rows": 2, "wrong_method": 405, "missing": 404, "database": "temporary SQLite"}


def main():
    versions = {name: importlib.metadata.version(name) for name in EXPECTED}
    assert versions == EXPECTED, versions
    result = {
        "kind": "python-web-runtime-probe",
        "versions": versions,
        "flask": flask_case(),
        "fastapi": fastapi_case(),
        "django": django_case(),
        "browser_executed": False,
        "external_http_server_started": False,
        "scope": "real in-process framework clients and SQLite",
    }
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

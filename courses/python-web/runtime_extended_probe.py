"""Finite extra-library compatibility; browser/TCP/service acceptance is separate."""

import asyncio
import json
import platform
import time


def crypto():
    import jwt
    from argon2 import PasswordHasher
    from cryptography.hazmat.primitives.asymmetric import rsa

    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    now = int(time.time())
    claims = {"sub": "fixture-user", "aud": "web-course", "iss": "local-fixture", "exp": now + 300}
    token = jwt.encode(claims, key, algorithm="RS256")
    checked = jwt.decode(
        token, key.public_key(), algorithms=["RS256"], audience="web-course", issuer="local-fixture"
    )
    assert checked["sub"] == "fixture-user"
    expired = jwt.encode({**claims, "exp": now - 60}, key, algorithm="RS256")
    try:
        jwt.decode(
            expired,
            key.public_key(),
            algorithms=["RS256"],
            audience="web-course",
            issuer="local-fixture",
        )
    except jwt.ExpiredSignatureError:
        pass
    else:
        raise AssertionError("Expired token accepted")
    hasher = PasswordHasher()
    hashed = hasher.hash("fixture-password")
    assert hasher.verify(hashed, "fixture-password")
    return {"rsa_signature": True, "expiry_rejected": True, "argon2_verification": True}


async def database():
    from sqlalchemy import text
    from sqlalchemy.ext.asyncio import create_async_engine

    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    try:
        async with engine.begin() as connection:
            await connection.execute(text("CREATE TABLE entries (value INTEGER NOT NULL)"))
            await connection.execute(text("INSERT INTO entries(value) VALUES (1)"))
        try:
            async with engine.begin() as connection:
                await connection.execute(text("INSERT INTO entries(value) VALUES (2)"))
                raise RuntimeError("intentional rollback")
        except RuntimeError:
            pass
        async with engine.connect() as connection:
            values = (await connection.execute(text("SELECT value FROM entries"))).scalars().all()
        assert values == [1]
        return {"async_sqlite_commit_and_rollback": True}
    finally:
        await engine.dispose()


def observability():
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import SimpleSpanProcessor
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter
    from prometheus_client import CollectorRegistry, Counter, generate_latest

    exporter = InMemorySpanExporter()
    provider = TracerProvider()
    provider.add_span_processor(SimpleSpanProcessor(exporter))
    with provider.get_tracer("fixture").start_as_current_span("http-fixture") as span:
        span.set_attribute("http.request.method", "GET")
    assert len(exporter.get_finished_spans()) == 1
    provider.shutdown()
    registry = CollectorRegistry()
    counter = Counter("web_requests", "Bounded fixture requests", ["route"], registry=registry)
    counter.labels(route="/items").inc(2)
    assert b'web_requests_total{route="/items"} 2.0' in generate_latest(registry)
    return {"in_memory_span": True, "prometheus_counter": True, "external_exporter_started": False}


def tasks():
    from celery import Celery

    app = Celery("fixture", broker="memory://", backend="cache+memory://", fixups=[])
    app.conf.update(task_always_eager=True, task_eager_propagates=True)

    @app.task
    def add(a, b):
        return a + b

    assert add.delay(2, 3).get() == 5
    app.close()
    return {"celery_eager_result": 5, "broker_worker_executed": False}


def drf():
    import django
    from django.conf import settings

    settings.configure(
        SECRET_KEY="test-only-drf-probe",
        ROOT_URLCONF=__name__,
        ALLOWED_HOSTS=["testserver"],
        INSTALLED_APPS=[],
        MIDDLEWARE=[],
        REST_FRAMEWORK={"UNAUTHENTICATED_USER": None, "DEFAULT_AUTHENTICATION_CLASSES": []},
    )
    django.setup()
    from django.urls import path
    from rest_framework import serializers
    from rest_framework.response import Response
    from rest_framework.test import APIClient
    from rest_framework.views import APIView

    class Item(serializers.Serializer):
        quantity = serializers.IntegerField(min_value=1)

    class View(APIView):
        def post(self, request):
            value = Item(data=request.data)
            value.is_valid(raise_exception=True)
            return Response(value.validated_data, status=201)

    global urlpatterns
    urlpatterns = [path("items/", View.as_view())]
    client = APIClient()
    valid = client.post("/items/", {"quantity": 2}, format="json")
    invalid = client.post("/items/", {"quantity": 0}, format="json")
    assert valid.status_code == 201 and valid.json() == {"quantity": 2}
    assert invalid.status_code == 400
    return {"actual_drf_client": True, "invalid_status": 400, "authentication_exercised": False}


if __name__ == "__main__":
    print(
        json.dumps(
            {
                "crypto": crypto(),
                "database": asyncio.run(database()),
                "observability": observability(),
                "tasks": tasks(),
                "drf": drf(),
                "scope": "finite library compatibility; browser/TCP/service acceptance is separate",
                "platform": platform.system(),
                "architecture": platform.machine(),
            },
            sort_keys=True,
        )
    )

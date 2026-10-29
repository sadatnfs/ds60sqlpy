# pyweb-059: Django async views, ORM calls and sync bridges

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-058`, `python-lang-04`.

## Starting point and result

Django supports asynchronous views and asynchronous ORM operations, but synchronous database calls remain unsafe when invoked directly from an active async context. This chapter tests both the supported async path and an explicit sync bridge, using a file-backed temporary SQLite database shared by the involved threads.

## Mechanism: protect thread-sensitive database ownership

An async view can await operations that yield control. Django's async ORM methods provide an appropriate interface for supported query operations. A synchronous ORM call inside that async context raises SynchronousOnlyOperation rather than silently blocking the event loop under unsafe assumptions.

Sync_to_async can run a synchronous unit through a controlled thread-sensitive bridge. The unit should own its complete synchronous database work and cleanup, rather than passing live connections or cursors across threads. A transaction requiring synchronous behavior can be enclosed inside such a unit according to the framework's documented limits.

The fixture uses a temporary database file rather than an in-memory SQLite database. Separate thread-bound connections to an in-memory database may see separate databases, producing missing-table errors unrelated to the async logic. File-backed storage makes the intended shared fixture explicit.

## Worked case: call an actual async view and ORM

The program creates a table and row, then an async view awaits acount and afirst. AsyncClient invokes the real view path and receives the expected count and title. Assertions check the returned data rather than merely confirming that the function is declared async.

This is in-process async framework evidence. It does not establish ASGI server throughput, a network socket or PostgreSQL's behavior. The actual server workshop tests those additional layers with its own bounded acceptance contract.

Async database access also does not imply that a query is efficient. A slow query, missing index or oversized result remains a database problem. Async can improve how waiting is scheduled; it cannot remove the work required by the query.

## Worked case: refuse unsafe sync access and bridge a whole unit

Inside the async exercise, a direct synchronous count is expected to raise SynchronousOnlyOperation. The program then calls a small synchronous unit through sync_to_async with thread_sensitive enabled. That unit completes its count and closes the connections it owns in a finally block.

The refusal is a useful guard, not an error to suppress through a global unsafe setting. Disabling the guard would obscure the ownership problem and could permit concurrent access patterns that the database adapter does not support safely.

Bridging every tiny attribute access separately can create unnecessary overhead and fragmented transaction boundaries. Group related synchronous work into a coherent unit, return plain results and keep connection/session objects inside their owning context.

## Failure diagnosis and discussion

**Why does an in-memory SQLite async test report a missing table?** Another thread may have a different connection and therefore a different in-memory database. Use an explicitly shared supported fixture or a file-backed database when that is the intended test.

**Does async automatically make an ORM transaction safe across awaits?** No. Follow the pinned framework's transaction support and ownership guidance. A coherent synchronous transaction can be bridged as one unit when appropriate.

If a process remains alive after the test, inspect outstanding tasks and connection cleanup. If the event loop stalls, inspect synchronous calls inside the async path. Continue with caching, email and task interfaces, where backend selection also determines what a successful local call actually proves.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    import asyncio
    import tempfile
    from pathlib import Path

    from django.conf import settings

    with tempfile.TemporaryDirectory() as directory:
        settings.configure(
            SECRET_KEY="synthetic-local-fixture",
            ROOT_URLCONF=__name__,
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(Path(directory) / "db.sqlite3"),
                }
            },
            INSTALLED_APPS=[],
        )
        import django

        django.setup()
        from asgiref.sync import sync_to_async
        from django.core.exceptions import SynchronousOnlyOperation
        from django.db import connection, connections, models
        from django.http import JsonResponse
        from django.test import AsyncClient
        from django.urls import path

        class Note(models.Model):
            title = models.CharField(max_length=20)

            class Meta:
                app_label = "webfixture"

        with connection.schema_editor() as editor:
            editor.create_model(Note)
        Note.objects.create(title="Async ORM")

        async def view(request):
            count = await Note.objects.acount()
            title = await Note.objects.values_list("title", flat=True).afirst()
            return JsonResponse({"count": count, "title": title})

        global urlpatterns
        urlpatterns = [path("notes/", view)]

        async def exercise():
            response = await AsyncClient().get("/notes/")
            assert response.json() == {"count": 1, "title": "Async ORM"}
            try:
                Note.objects.count()
            except SynchronousOnlyOperation:
                pass
            else:
                raise AssertionError("Unsafe sync ORM admitted in async context")

            def owned_sync_unit():
                try:
                    return Note.objects.count()
                finally:
                    connections.close_all()

            assert await sync_to_async(owned_sync_unit, thread_sensitive=True)() == 1

        asyncio.run(exercise())
        connections.close_all()
    return {"actual_async_view_and_orm": True, "unsafe_sync_refused": True, "sync_bridge": True}


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)

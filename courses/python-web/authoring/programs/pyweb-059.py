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

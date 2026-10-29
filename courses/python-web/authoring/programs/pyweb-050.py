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

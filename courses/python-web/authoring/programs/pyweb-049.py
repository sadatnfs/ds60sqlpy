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
    from django.db.models import Count, Sum
    from django.test.utils import CaptureQueriesContext

    class Sale(models.Model):
        region = models.CharField(max_length=20)
        amount = models.IntegerField()

        class Meta:
            app_label = "webfixture"

    with connection.schema_editor() as editor:
        editor.create_model(Sale)
    Sale.objects.bulk_create(
        [
            Sale(region="north", amount=3),
            Sale(region="north", amount=5),
            Sale(region="south", amount=2),
        ]
    )
    with CaptureQueriesContext(connection) as observed:
        query = Sale.objects.filter(amount__gte=3).order_by("id")
        assert len(observed) == 0
        values = list(query)
        assert len(observed) == 1 and [item.amount for item in values] == [3, 5]
        list(query)
        assert len(observed) == 1
    summary = list(
        Sale.objects.values("region")
        .annotate(total=Sum("amount"), count=Count("id"))
        .order_by("region")
    )
    assert summary == [
        {"region": "north", "total": 8, "count": 2},
        {"region": "south", "total": 2, "count": 1},
    ]
    assert Sale.objects.filter(amount__gte=3).aggregate(total=Sum("amount"))["total"] == 8
    connection.close()
    return {"lazy_then_cached_queries": 1, "grouped_summary": summary}


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))

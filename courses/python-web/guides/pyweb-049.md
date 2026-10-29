# pyweb-049: Django QuerySets, aggregation and evaluation

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-048`.

## Starting point and result

A QuerySet describes a database query and usually delays execution until its results are needed. This laziness enables composition, but it can also surprise developers inspecting query counts or reusing evaluated objects. This chapter measures actual SQL execution and performs grouped aggregation on a small sales table.

## Mechanism: query description and materialized results differ

Calling filter and order_by constructs a QuerySet. Iteration, list conversion and several other operations evaluate it. Once evaluated, that specific QuerySet can cache its result objects. Creating a new QuerySet or using another operation can issue another query, so caching should not be generalized to every similar-looking expression.

Values selects named fields and changes the shape of returned rows. Annotate adds expressions such as a grouped sum or count. Aggregate computes an overall result. The placement of filters and annotations matters because it determines which rows contribute to each calculation.

The fixture uses integers and a deterministic ordering so its expected totals can be derived directly. North has values 3 and 5, while south has 2. The grouped totals are therefore 8 and 2. This numerical oracle is independent of the ORM expression being tested.

## Worked case: observe lazy evaluation and reuse

CaptureQueriesContext begins recording before the QuerySet is constructed. The program confirms that construction emits no SQL. Converting it to a list issues one query and yields the expected filtered values. Iterating the same evaluated QuerySet again does not increase the recorded count.

That observation concerns one QuerySet object. Calling a fresh filter expression would construct a new object whose evaluation can query again. Likewise, iterator-style streaming deliberately changes caching behavior and memory usage. Choose based on actual access patterns, not a vague belief that the ORM caches everything.

A lazy QuerySet returned from a function may execute after the surrounding transaction or request context has changed. Be explicit about whether a function returns a query description or completed data, especially at asynchronous or serialization boundaries.

## Worked case: compare grouped and overall aggregation

The grouped query selects region, annotates total and row count, and orders by region. The program compares the complete result with its hand-derived expected rows. A separate filtered aggregate returns the sum for amounts at least 3, which is 8.

These assertions catch grouping and filtering mistakes that a simple row-count check would miss. A total can be numerically plausible while using the wrong population. Name the cohort and aggregation grain before writing the ORM expression.

Nulls, joins and duplicate rows complicate real aggregates. A join can multiply a source row and inflate a sum. Count of a nullable field differs from count of rows. The lesson's small fixture avoids those complications so the basic execution model is clear; later SQL and engineering chapters examine them explicitly.

## Failure diagnosis and discussion

**Why does printing or inspecting a QuerySet sometimes issue SQL?** Some representation and evaluation operations need results. Debugging tools can therefore change when a lazy query executes.

**Why is an evaluated QuerySet not a durable cache?** Its results live in one Python object and can become stale as the database changes. It provides neither cross-process sharing nor an invalidation policy.

If an aggregate is wrong, inspect the generated SQL, grouping grain and input rows before blaming serialization. If query counts grow, identify which expressions create fresh QuerySets. Continue with relationships and the N-plus-one pattern, where these evaluation rules have a large practical effect.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
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
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)

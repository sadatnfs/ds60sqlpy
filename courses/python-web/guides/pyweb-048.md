# pyweb-048: Django models, migrations and constraints

Tutorial mode. Stage: intermediate. Direct prerequisites: `pyweb-047`, `python-12`, `sql-found-01`.

## Starting point and result

A Django model describes intended data structure in Python, while migrations record how the database schema evolves. This chapter creates a genuine temporary application package, generates its initial migration, applies it and repeats the migration command without losing an existing row.

## Mechanism: migration state is versioned schema history

Django's application registry loads model definitions. Makemigrations compares model state with migration state and writes operations describing the change. Migrate applies the outstanding operations and records which migrations have completed. These are separate steps: editing a model does not automatically alter a deployed database.

The fixture defines a Note with a unique title. The uniqueness rule becomes a database constraint through the generated migration. Application validation can improve user feedback, but only the database can resolve competing writes reliably at the final storage boundary.

The temporary package and database are owned by this finite program. It writes only inside its temporary directory and removes that directory after closing connections. A real project commits reviewed migration files to source control and applies them through a controlled deployment step, not through an arbitrary request handler.

## Worked case: generate, apply and replay an initial migration

The program creates the small package, configures Django to install it and runs makemigrations. It asserts that the initial migration file exists, applies migrations and inserts a row. A second migrate invocation leaves that row intact and produces no outstanding plan for the already applied migration.

This is actual migration execution, not a hand-created table pretending to exercise migrations. Other compact ORM chapters use schema_editor deliberately to focus on queries; this chapter tests the migration machinery itself.

The repeated command demonstrates idempotent migration planning for this unchanged schema. It does not prove that every future migration is reversible or safe under concurrent application traffic. Dropping a column or changing a large table needs a separate data-preservation and deployment plan.

## Worked case: let the database enforce uniqueness

A second row with the same title is attempted inside transaction.atomic. The database raises IntegrityError, and the transaction rolls back. The final count remains one. Catching the exception outside the atomic block ensures the failed transaction is unwound before later queries inspect the result.

This case explains why a form's uniqueness check is not enough under concurrency. Two requests can both observe that a title is available before either commits. The constraint provides the final decision, and the application must translate the expected conflict without leaving its transaction unusable.

Data migrations require equal care. A transformation should define how existing rows are mapped, how failures are resumed and whether the reverse direction is meaningful. A successful schema-only fixture does not certify an unrelated data migration.

## Failure diagnosis and discussion

**Why does the model include a field that SQL says is missing?** Model state and applied migration state may differ. Inspect the migration plan and target database before changing application code.

**Should developers regenerate a migration already deployed elsewhere?** Usually not. Changing its history can make environments disagree about what a recorded migration means. Add a new reviewed migration for the new state.

If a duplicate-write test poisons later queries, inspect where the IntegrityError is caught relative to atomic. If migration replay loses a row, inspect destructive operations rather than assuming migrate is harmless. Continue with QuerySets to learn when database reads actually execute.

## Complete reproducible program

Run this complete finite program in the prepared Python web profile. It exercises real framework clients and bounded local fixtures, then exits. It does not open a browser or start an externally reachable HTTP server. Long-running applications use the separately documented owned projects. Runtime: `python-web`.

```python
"""Finite Django investigation; fresh process owns settings and disposable fixtures."""

import json


def run_cases():
    import io
    import sys
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        package = root / "webfixture"
        package.mkdir()
        (package / "__init__.py").write_text("")
        (package / "models.py").write_text(
            "from django.db import models\nclass Note(models.Model):\n"
            "    title = models.CharField(max_length=60, unique=True)\n"
        )
        sys.path.insert(0, str(root))
        from django.conf import settings

        settings.configure(
            SECRET_KEY="synthetic-local-fixture",
            INSTALLED_APPS=["webfixture"],
            DATABASES={
                "default": {
                    "ENGINE": "django.db.backends.sqlite3",
                    "NAME": str(root / "db.sqlite3"),
                }
            },
            DEFAULT_AUTO_FIELD="django.db.models.BigAutoField",
        )
        import django

        django.setup()
        from django.core.management import call_command
        from django.db import IntegrityError, connection, transaction
        from django.db.migrations.executor import MigrationExecutor
        from webfixture.models import Note

        output = io.StringIO()
        call_command("makemigrations", "webfixture", verbosity=0, stdout=output)
        call_command("migrate", verbosity=0, stdout=output)
        assert (package / "migrations/0001_initial.py").is_file()
        first = Note.objects.create(title="Preserved")
        call_command("migrate", verbosity=0, stdout=output)
        assert Note.objects.get(pk=first.pk).title == "Preserved"
        try:
            with transaction.atomic():
                Note.objects.create(title="Preserved")
        except IntegrityError:
            pass
        else:
            raise AssertionError("Unique constraint not enforced")
        assert Note.objects.count() == 1
        assert MigrationExecutor(connection).migration_plan([("webfixture", "0001_initial")]) == []
        connection.close()
        sys.path.remove(str(root))
    return {
        "real_generated_migration": True,
        "repeat_migrate_preserves_row": True,
        "unique_constraint": True,
    }


if __name__ == "__main__":
    print(json.dumps(run_cases(), sort_keys=True, allow_nan=False))
```

## Primary references

- [Django 6.1 documentation](https://docs.djangoproject.com/en/6.1/)
- [Django 6.1 test tools](https://docs.djangoproject.com/en/6.1/topics/testing/tools/)

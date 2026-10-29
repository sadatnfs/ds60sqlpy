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

"""Explicit migration/fixture preparation, never run inside an HTTP request."""

import os


def main():
    import store

    store.prepare()
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_project.settings")
    import django

    django.setup()
    from django.contrib.auth import get_user_model
    from django.core.management import call_command

    call_command("migrate", interactive=False, verbosity=1)
    User = get_user_model()
    for username in ("alice", "bob"):
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(username=username, password="classroom-demo")
    if not User.objects.filter(username="operator").exists():
        User.objects.create_superuser(username="operator", email="", password="local-admin-demo")
    print("Owned web workshop schema and synthetic accounts prepared")


if __name__ == "__main__":
    main()

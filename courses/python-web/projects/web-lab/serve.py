"""Fixed server commands: preparation and app imports happen before serving."""

import os
import sys

role = sys.argv[1] if len(sys.argv) == 2 else ""
commands = {
    "flask": [
        "gunicorn",
        "--bind",
        "0.0.0.0:8080",
        "--workers",
        "1",
        "--threads",
        "4",
        "--timeout",
        "35",
        "flask_app:app",
    ],
    "django": [
        "gunicorn",
        "--bind",
        "0.0.0.0:8080",
        "--workers",
        "1",
        "--threads",
        "4",
        "--timeout",
        "35",
        "django_project.wsgi:application",
    ],
    "fastapi": [
        "uvicorn",
        "fastapi_app:app",
        "--host",
        "0.0.0.0",
        "--port",
        "8080",
        "--no-access-log",
        "--no-proxy-headers",
        "--ws-max-size",
        "1024",
        "--timeout-graceful-shutdown",
        "10",
    ],
    "worker": [sys.executable, "worker.py"],
}
if role not in commands:
    raise SystemExit("Choose the fixed flask, django, fastapi or worker role")
os.execvp(commands[role][0], commands[role])

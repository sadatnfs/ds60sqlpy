"""Django's own auth/session/CSRF and ORM flow, sharing only the teaching contract."""

import json
import os
from functools import wraps
from pathlib import Path

import store
from django.contrib.auth import authenticate
from django.contrib.auth import login as session_login
from django.contrib.auth import logout as session_logout
from django.db import connection
from django.http import FileResponse, JsonResponse
from django.middleware.csrf import get_token
from django.views.decorators.http import require_GET, require_http_methods, require_POST

from .models import Note


def api(function):
    @wraps(function)
    def call(request, *args, **kwargs):
        try:
            return function(request, *args, **kwargs)
        except store.Rejected as error:
            return JsonResponse({"error": str(error)}, status=error.status)

    return call


def body(request):
    if request.content_type != "application/json":
        raise store.Rejected(415, "Expected application/json")
    try:
        return json.loads(request.body)
    except (ValueError, UnicodeDecodeError) as error:
        raise store.Rejected(400, "Invalid JSON") from error


def principal(request):
    if not request.user.is_authenticated:
        raise store.Rejected(401, "Login required")
    return request.user


@require_GET
def home(request):
    return FileResponse((Path(__file__).resolve().parents[1] / "static/index.html").open("rb"))


@require_GET
def config(request):
    return JsonResponse({"framework": "Django", "jobs": False, "origin": os.environ["WEB_ORIGIN"]})


@require_GET
def health(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return JsonResponse({"status": "ready", "framework": "Django"})


@require_GET
def csrf(request):
    return JsonResponse({"csrf": get_token(request)})


@require_POST
@api
def login(request):
    store.require_origin(request.headers.get("Origin"))
    values = body(request)
    if (
        not isinstance(values, dict)
        or set(values) != {"username", "password"}
        or not all(isinstance(value, str) and len(value) <= 128 for value in values.values())
    ):
        raise store.Rejected(422, "Expected bounded username and password")
    user = authenticate(request, **values)
    if user is None:
        raise store.Rejected(401, "Invalid credentials")
    session_login(request, user)
    return JsonResponse({"username": user.username, "csrf": get_token(request)})


@require_GET
@api
def me(request):
    user = principal(request)
    return JsonResponse({"username": user.username, "csrf": get_token(request)})


@require_POST
@api
def logout(request):
    principal(request)
    session_logout(request)
    return JsonResponse({"logged_out": True})


@require_http_methods(["GET", "POST"])
@api
def notes(request):
    user = principal(request)
    if request.method == "POST":
        row = Note.objects.create(title=store.title_from(body(request)), owner=user)
        return JsonResponse({"id": row.pk, "title": row.title, "version": row.version}, status=201)
    return JsonResponse(
        {"notes": list(Note.objects.filter(owner=user).values("id", "title", "version")[:100])}
    )


@require_GET
@api
def detail(request, identifier):
    user = principal(request)
    row = Note.objects.filter(owner=user, pk=identifier).values("id", "title", "version").first()
    if row is None:
        raise store.Rejected(404, "Note not found")
    return JsonResponse(row)

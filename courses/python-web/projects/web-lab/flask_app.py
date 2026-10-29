"""Flask server with local UI and PostgreSQL-owned notes."""

import os
from pathlib import Path

import store
from flask import Flask, jsonify, request, send_from_directory

STATIC = Path(__file__).parent / "static"
app = Flask(__name__, static_folder=str(STATIC), static_url_path="/static")
app.config.update(MAX_CONTENT_LENGTH=16_384, TRUSTED_HOSTS=["127.0.0.1", "localhost"])
COOKIE = "pyweb_flask"


@app.errorhandler(store.Rejected)
def rejected(error):
    return jsonify(error=str(error)), error.status


@app.after_request
def headers(response):
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "connect-src 'self'; frame-ancestors 'none'; base-uri 'none'"
    )
    if request.path.startswith("/api/"):
        response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/")
def home():
    return send_from_directory(STATIC, "index.html")


@app.get("/config")
def config():
    return {"framework": "Flask", "jobs": False, "origin": os.environ["WEB_ORIGIN"]}


@app.get("/healthz")
def health():
    with store.connect() as conn:
        conn.execute("SELECT 1").fetchone()
    return {"status": "ready", "framework": "Flask"}


@app.post("/api/login")
def login():
    store.require_origin(request.headers.get("Origin"))
    token, body = store.login("flask", request.get_json())
    response = jsonify(body)
    response.set_cookie(COOKIE, token, httponly=True, samesite="Lax", max_age=7200)
    return response


def user(write=False):
    token = request.cookies.get(COOKIE)
    if write:
        return store.write_identity(
            "flask", token, request.headers.get("X-CSRF-Token"), request.headers.get("Origin")
        )
    return store.identity("flask", token)


@app.get("/api/me")
def me():
    principal = user()
    return {"username": principal["username"], "csrf": principal["csrf"]}


@app.post("/api/logout")
def logout():
    user(True)
    store.logout(request.cookies[COOKIE])
    response = jsonify(logged_out=True)
    response.delete_cookie(COOKIE)
    return response


@app.route("/api/notes", methods=["GET", "POST"])
def notes():
    principal = user(request.method == "POST")
    if request.method == "POST":
        return store.notes("flask", principal["id"], request.get_json()), 201
    return {"notes": store.notes("flask", principal["id"])}


@app.get("/api/notes/<int:identifier>")
def detail(identifier):
    return store.read_note("flask", user()["id"], identifier)

"""Shared original PostgreSQL fixture boundaries for three web frameworks."""

from __future__ import annotations

import hashlib
import hmac
import json
import os
import secrets
import uuid
from pathlib import Path

import psycopg
from psycopg.rows import dict_row
from werkzeug.security import check_password_hash, generate_password_hash


def database_settings():
    return {
        "host": os.environ.get("WEB_DB_HOST", "postgres"),
        "port": int(os.environ.get("WEB_DB_PORT", "5432")),
        "dbname": "web_lab",
        "user": "web_lab",
        "password": Path(os.environ["WEB_DB_PASSWORD_FILE"]).read_text().strip(),
        "connect_timeout": 5,
    }


def connect():
    return psycopg.connect(**database_settings(), row_factory=dict_row)


def prepare():
    with connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS web_users(
                id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS web_sessions(
                token_hash TEXT PRIMARY KEY, user_id INTEGER NOT NULL REFERENCES web_users,
                framework TEXT NOT NULL, csrf TEXT NOT NULL, expires TIMESTAMPTZ NOT NULL);
            CREATE TABLE IF NOT EXISTS web_notes(
                id BIGSERIAL PRIMARY KEY, framework TEXT NOT NULL,
                owner INTEGER NOT NULL REFERENCES web_users, title TEXT NOT NULL,
                version INTEGER NOT NULL DEFAULT 1,
                CHECK(length(title) BETWEEN 1 AND 120));
            CREATE INDEX IF NOT EXISTS web_notes_scope ON web_notes(framework,owner,id);
            CREATE TABLE IF NOT EXISTS web_jobs(
                id UUID PRIMARY KEY, owner INTEGER NOT NULL REFERENCES web_users,
                state TEXT NOT NULL CHECK(state IN ('queued','running','finished')),
                released BOOLEAN NOT NULL DEFAULT FALSE, values_json JSONB NOT NULL,
                result BIGINT, created TIMESTAMPTZ NOT NULL DEFAULT now());
            CREATE TABLE IF NOT EXISTS web_events(
                id BIGSERIAL PRIMARY KEY, job UUID NOT NULL REFERENCES web_jobs,
                state TEXT NOT NULL, result BIGINT);
        """)
        for identifier, name in [(1, "alice"), (2, "bob")]:
            conn.execute(
                "INSERT INTO web_users VALUES(%s,%s,%s) ON CONFLICT(id) DO NOTHING",
                (identifier, name, generate_password_hash("classroom-demo")),
            )


class Rejected(Exception):
    def __init__(self, status, message):
        super().__init__(message)
        self.status = status


def require_origin(origin):
    if origin != os.environ["WEB_ORIGIN"]:
        raise Rejected(403, "Untrusted request origin")


def login(framework, body):
    if not isinstance(body, dict) or set(body) != {"username", "password"}:
        raise Rejected(422, "Expected username and password")
    if not all(isinstance(body[key], str) and len(body[key]) <= 128 for key in body):
        raise Rejected(422, "Invalid credential shape")
    with connect() as conn:
        user = conn.execute(
            "SELECT * FROM web_users WHERE username=%s", (body["username"],)
        ).fetchone()
        if user is None or not check_password_hash(user["password_hash"], body["password"]):
            raise Rejected(401, "Invalid credentials")
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        conn.execute(
            "INSERT INTO web_sessions VALUES(%s,%s,%s,%s,now()+interval '2 hours')",
            (hashlib.sha256(token.encode()).hexdigest(), user["id"], framework, csrf),
        )
    return token, {"username": user["username"], "csrf": csrf}


def identity(framework, token):
    if not isinstance(token, str) or not 20 <= len(token) <= 128:
        raise Rejected(401, "Login required")
    with connect() as conn:
        user = conn.execute(
            "SELECT u.id,u.username,s.csrf FROM web_sessions s JOIN web_users u "
            "ON u.id=s.user_id WHERE s.token_hash=%s AND s.framework=%s AND s.expires>now()",
            (hashlib.sha256(token.encode()).hexdigest(), framework),
        ).fetchone()
    if user is None:
        raise Rejected(401, "Login required")
    return user


def write_identity(framework, token, csrf, origin):
    require_origin(origin)
    user = identity(framework, token)
    if not isinstance(csrf, str) or not hmac.compare_digest(user["csrf"], csrf):
        raise Rejected(403, "CSRF check failed")
    return user


def logout(token):
    with connect() as conn:
        conn.execute(
            "DELETE FROM web_sessions WHERE token_hash=%s",
            (hashlib.sha256(token.encode()).hexdigest(),),
        )


def title_from(body):
    if not isinstance(body, dict) or set(body) != {"title"}:
        raise Rejected(422, "Expected only title")
    title = body["title"]
    if not isinstance(title, str) or not 1 <= len(title.strip()) <= 120:
        raise Rejected(422, "Title must contain 1 to 120 characters")
    return title.strip()


def notes(framework, owner, body=None):
    with connect() as conn:
        if body is not None:
            return conn.execute(
                "INSERT INTO web_notes(framework,owner,title) VALUES(%s,%s,%s) "
                "RETURNING id,title,version",
                (framework, owner, title_from(body)),
            ).fetchone()
        return conn.execute(
            "SELECT id,title,version FROM web_notes WHERE framework=%s AND owner=%s "
            "ORDER BY id LIMIT 100",
            (framework, owner),
        ).fetchall()


def read_note(framework, owner, identifier):
    with connect() as conn:
        row = conn.execute(
            "SELECT id,title,version FROM web_notes WHERE framework=%s AND owner=%s AND id=%s",
            (framework, owner, identifier),
        ).fetchone()
    if row is None:
        raise Rejected(404, "Note not found")
    return row


def create_job(owner, body):
    if not isinstance(body, dict) or set(body) != {"values"}:
        raise Rejected(422, "Expected values")
    values = body["values"]
    if (
        not isinstance(values, list)
        or not 1 <= len(values) <= 32
        or not all(type(value) is int and abs(value) <= 1_000_000 for value in values)
    ):
        raise Rejected(422, "Expected 1 to 32 bounded integers")
    identifier = str(uuid.uuid4())
    with connect() as conn:
        conn.execute(
            "INSERT INTO web_jobs(id,owner,state,values_json) VALUES(%s,%s,'queued',%s)",
            (identifier, owner, json.dumps(values)),
        )
        conn.execute("INSERT INTO web_events(job,state) VALUES(%s,'queued')", (identifier,))
    return {"id": identifier, "state": "queued"}


def job(owner, identifier):
    try:
        identifier = str(uuid.UUID(identifier))
    except (ValueError, TypeError, AttributeError) as error:
        raise Rejected(404, "Job not found") from error
    with connect() as conn:
        row = conn.execute(
            "SELECT id,state,released,result FROM web_jobs WHERE id=%s AND owner=%s",
            (identifier, owner),
        ).fetchone()
    if row is None:
        raise Rejected(404, "Job not found")
    row["id"] = str(row["id"])
    return row


def release(owner, identifier):
    current = job(owner, identifier)
    with connect() as conn:
        conn.execute("UPDATE web_jobs SET released=TRUE WHERE id=%s", (current["id"],))
    return job(owner, identifier)


def events(owner, identifier, after):
    current = job(owner, identifier)
    with connect() as conn:
        if (
            after
            and conn.execute(
                "SELECT 1 FROM web_events WHERE job=%s AND id=%s", (current["id"], after)
            ).fetchone()
            is None
        ):
            raise Rejected(409, "Cursor does not belong to this job")
        return conn.execute(
            "SELECT id,state,result FROM web_events WHERE job=%s AND id>%s ORDER BY id",
            (current["id"], after),
        ).fetchall()


def worker_tick():
    with connect() as conn:
        queued = conn.execute(
            "SELECT id FROM web_jobs WHERE state='queued' ORDER BY created "
            "FOR UPDATE SKIP LOCKED LIMIT 1"
        ).fetchone()
        if queued:
            conn.execute("UPDATE web_jobs SET state='running' WHERE id=%s", (queued["id"],))
            conn.execute("INSERT INTO web_events(job,state) VALUES(%s,'running')", (queued["id"],))
        ready = conn.execute(
            "SELECT id,values_json FROM web_jobs WHERE state='running' AND released "
            "ORDER BY created FOR UPDATE SKIP LOCKED LIMIT 1"
        ).fetchone()
        if ready:
            result = sum(ready["values_json"])
            conn.execute(
                "UPDATE web_jobs SET state='finished',result=%s WHERE id=%s",
                (result, ready["id"]),
            )
            conn.execute(
                "INSERT INTO web_events(job,state,result) VALUES(%s,'finished',%s)",
                (ready["id"], result),
            )
    return bool(queued or ready)

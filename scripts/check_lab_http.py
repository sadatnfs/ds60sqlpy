#!/usr/bin/env python3
"""Smoke-test a disposable lab instance, including both authenticated coding backends."""

from __future__ import annotations

import argparse
import json
import re
import time
from typing import Any
from urllib.parse import urlsplit
from urllib.request import ProxyHandler, Request, build_opener


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8765")
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument(
        "--reset-sql",
        action="store_true",
        help="Explicitly reset and verify the disposable training schema before checking SQL.",
    )
    parser.add_argument(
        "--check-persistence",
        action="store_true",
        help="Require a previous smoke run's pad and evidence to survive application recreation.",
    )
    args = parser.parse_args()
    if not args.confirm_disposable:
        parser.error(
            "This writes test pads/evidence. Use --confirm-disposable only on a test workspace."
        )
    parsed = urlsplit(args.url)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.username is not None
        or parsed.password is not None
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") not in {"", "/classroom", "/learn"}
    ):
        parser.error("The smoke test accepts only an explicit loopback classroom URL.")
    url = f"http://{parsed.netloc}"
    opener = build_opener(ProxyHandler({}))
    deadline = time.monotonic() + 45
    while True:
        try:
            with opener.open(url + "/classroom", timeout=3) as response:
                html = response.read().decode()
            break
        except OSError:
            if time.monotonic() >= deadline:
                raise
            time.sleep(1)
    token = re.search(r'const SERVER_TOKEN = "([^"]+)";', html)
    if token is None:
        raise RuntimeError("The lab page did not include a private session token.")

    def call(action: str, **fields: Any) -> dict[str, Any]:
        request = Request(
            url + ("/api/classroom" if action.startswith("classroom-") else "/api/lab"),
            data=json.dumps({"action": action, **fields}).encode(),
            headers={
                "Content-Type": "application/json",
                "Origin": url,
                "X-DS60-Token": token.group(1),
            },
        )
        with opener.open(request, timeout=25) as response:
            result: dict[str, Any] = json.loads(response.read())
            return result

    directory = call("classroom-index")
    subjects = {track["id"] for track in directory["tracks"]}
    if not {"python", "sql", "cpp", "java", "javascript-typescript"} <= subjects:
        raise RuntimeError("The unified classroom omitted published subjects.")
    info = call("paths")
    if not info["paths"] or info["lesson_count"] < 128:
        raise RuntimeError("The bundled course catalog is incomplete.")
    plan = call("plan", targets=info["paths"]["python-foundations"]["targets"])
    if not any(lesson["id"] == "python-foundations-01" for lesson in plan["lessons"]):
        raise RuntimeError("The plan omitted beginner practice.")
    python_source = "print(6 * 7)"
    note = "HTTP smoke fixture; this is not learner mastery."
    if args.check_persistence:
        saved = call("read-pad", lesson_id="python-01", language="python")
        evidence = call("lesson", lesson_id="python-01")["session"]
        if not saved["saved"] or saved["code"] != python_source or evidence.get("read") != note:
            raise RuntimeError("The saved coding pad or evidence did not survive recreation.")
        history = call(
            "classroom-history", lesson_id="python-01", language="python", mode="snippet"
        )["history"]
        if not history:
            raise RuntimeError("The Python result history did not survive recreation.")
        receipt = call(
            "classroom-run-result",
            lesson_id="python-01",
            language="python",
            mode="snippet",
            receipt_id=history[0]["id"],
        )["receipt"]
        if receipt["source"] != python_source or receipt["result"]["output"].strip() != "42":
            raise RuntimeError("The original Python result or exact source was lost.")
    if args.reset_sql:
        setup = call("prepare-sql", confirmation="RESET TRAINING")
        if setup["returncode"]:
            raise RuntimeError(
                "The explicit training reset/verification failed: " + setup["output"]
            )
    python = call("run", lesson_id="python-01", language="python", code="print(6 * 7)")
    if (
        python["returncode"]
        or python["output"].strip() != "42"
        or python.get("receipt_saved") is not True
    ):
        raise RuntimeError("The Python coding backend did not produce 42.")
    sql = call("run", lesson_id="sql-start-01", language="sql", code="SELECT 42 AS answer;")
    if sql["returncode"] or json.loads(sql["output"])["results"][0]["rows"] != [[42]]:
        raise RuntimeError("The PostgreSQL coding backend did not produce one row containing 42.")
    role = call("run", lesson_id="sql-start-01", language="sql", code="SELECT current_user;")
    if role["returncode"] or json.loads(role["output"])["results"][0]["rows"][0][0] not in {
        "admin",
        "ds60",
    }:
        raise RuntimeError("The SQL pad did not show the limited course role without masking it.")
    denied = call(
        "run",
        lesson_id="sql-start-01",
        language="sql",
        code="SELECT pg_read_file('/etc/hostname');",
    )
    if denied["returncode"] == 0 or json.loads(denied["output"]).get("sqlstate") != "42501":
        raise RuntimeError("The SQL backend did not reject server-file access as the limited role.")
    if args.reset_sql or args.check_persistence:
        seed = call(
            "run",
            lesson_id="sql-01",
            language="sql",
            code="SELECT COUNT(*) FROM training.customers;",
        )
        if seed["returncode"] or json.loads(seed["output"])["results"][0]["rows"][0][0] < 1:
            raise RuntimeError("The initialized course fixture is missing or empty.")
    call("save-pad", lesson_id="python-01", language="python", code="")
    empty = call("read-pad", lesson_id="python-01", language="python")
    if not empty["saved"] or empty["code"] != "":
        raise RuntimeError("The app did not preserve an intentionally empty pad.")
    versions = call("pad-history", lesson_id="python-01", language="python")["history"]
    if not any(
        call("read-history", lesson_id="python-01", language="python", history_id=item["id"])[
            "code"
        ]
        == python_source
        for item in versions
    ):
        raise RuntimeError("The previous Python pad is missing from recovery history.")
    call("save-pad", lesson_id="python-01", language="python", code=python_source)
    call("save", lesson_id="python-01", phase="read", note=note)
    print(
        f"PASS: {info['lesson_count']} lessons, planning, Python/SQL pads, limited role, "
        "empty-pad/history recovery, durable run receipts"
        + (", persisted workspace" if args.check_persistence else "")
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

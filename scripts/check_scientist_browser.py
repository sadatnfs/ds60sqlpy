#!/usr/bin/env python3
"""Qualify scientific classroom UI/API behavior on an explicitly disposable URL.

Use the prepared Playwright contributor environment. Jobs run sequentially.
Unknown outcomes stop the gate with their original request IDs, never a retry.
Effective pads and notes are restored. Persistence uses fresh documents, original
receipt IDs and a request guard that blocks writes and execution.
"""

from __future__ import annotations

import argparse
import importlib
import json
import math
import re
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_classroom_browser import Audit, choose_lesson, save  # noqa: E402
from scripts.check_classroom_profiles import (  # noqa: E402
    TERMINAL,
    ClassroomClient,
    classroom_origin,
)
from scripts.check_scientific_artifacts import digest, source_digest  # noqa: E402

SUBJECTS = (
    "applied-science",
    "bayesian-computing",
    "polars",
    "dbt",
    "ml-engineering",
    "llm-evaluation",
    "julia",
)
PROFILES = ("python-core", "data-engineering", "dbt-duckdb", "stan-cpu", "julia")
CASE_IDS = (
    "polars-reference",
    "dbt-model",
    "julia-reference",
    "julia-diagnostic",
    "stan-reference",
    "stan-diagnostic",
    "structured-small",
    "structured-large",
)
PAD_IDS = (
    "dbt-002@sql-model",
    "dbt-002",
    "julia-020",
    "bayes-017",
    "eval-001",
    "eval-002",
    "science-001",
    "bayes-001",
    "polars-001",
)
READ_ACTIONS = {
    "module-index",
    "module-readiness",
    "module-lesson",
    "module-job",
    "classroom-index",
}
LITERAL = '<img src="https://example.invalid/scientist-probe" onerror="window.scientistProbe=true">'
TABLE = {
    "columns": ["Record", "Value"],
    "rows": [[LITERAL, 0], ["false", False], ["missing", None], ["large identifier", str(2**60)]],
}
SMALL_REPORT = {
    "literal": LITERAL,
    "count": 0,
    "enabled": False,
    "unknown": None,
    "large_identifier": str(2**60),
    "nested": {"mean": 1.5},
}
LARGE_REPORT = {"literal": LITERAL, "large_identifier": str(2**60), "padding": "x" * 65_000}
SMALL_SOURCE = (
    "# Disposable browser acceptance fixture, not the lesson reference.\n"
    "from ds60sqlpy.plot_artifacts import publish_table, publish_report\n"
    f"publish_table({TABLE['columns']!r}, {TABLE['rows']!r}, description='Exact browser table')\n"
    f"publish_report({SMALL_REPORT!r}, description='Exact browser JSON')\n"
    "print('SCIENTIST_BROWSER_SMALL_V1')\n"
)
LARGE_SOURCE = (
    "# Disposable browser acceptance fixture, not the lesson reference.\n"
    "from ds60sqlpy.plot_artifacts import publish_report\n"
    f"publish_report({ {'literal': LITERAL, 'large_identifier': str(2**60)}!r} | "
    "{'padding': 'x' * 65000}, description='Large plain JSON report')\n"
    "print('SCIENTIST_BROWSER_LARGE_V1')\n"
)
JULIA_ERROR = "# Deliberate diagnostic probe.\nvalues = [1, 2]\nprintln(values[3])\n"
STAN_ERROR = "parameters {\n  real mu;\n}\nmodel {\n  mu ~ normal(unknown_mean, 1);\n}\n"


class Client(Protocol):
    def call(self, action: str, **fields: Any) -> dict[str, Any]: ...


class ReadOnlyClient:
    def __init__(self, client: Client) -> None:
        self.client = client

    def call(self, action: str, **fields: Any) -> dict[str, Any]:
        if action not in READ_ACTIONS:
            raise ValueError("Persistence cannot write or execute: " + action)
        return self.client.call(action, **fields)


@dataclass(frozen=True)
class Case:
    id: str
    subject: str
    lesson_id: str
    profile: str
    source: str
    source_path: str
    status: str
    output_markers: tuple[str, ...]
    kinds: tuple[str, ...]
    diagnostic_line: int | None = None

    @property
    def source_sha256(self) -> str:
        return source_digest(self.source)


def subject_titles(root: Path = ROOT) -> dict[str, str]:
    titles: dict[str, str] = {}
    for subject in SUBJECTS:
        data = json.loads((root / "courses" / subject / "track.json").read_text("utf-8"))
        if data.get("id") != subject or not isinstance(data.get("title"), str):
            raise ValueError("Invalid scientific subject identity or title: " + subject)
        titles[subject] = data["title"]
    return titles


def admitted_source(
    subject: str, identity: str, profile: str, root: Path = ROOT
) -> tuple[str, str]:
    canonical, _, variant = identity.partition("@")
    data = json.loads((root / "courses" / subject / "lessons.json").read_text("utf-8"))
    lesson = next(row for row in data["lessons"] if row["id"] == canonical)
    if variant:
        lesson = next(row for row in lesson["variants"] if row["id"] == variant)
    if lesson.get("runtime_profile") != profile or lesson.get("verification_id") is not None:
        raise ValueError("The reviewed source changed its runtime or verifier contract.")
    path = next(
        (p for p in lesson.get("solution_paths", []) if not p.endswith(".md")),
        lesson["source_path"],
    )
    source = root / path
    boundary = (root / "courses" / subject).resolve()
    if source.is_symlink() or not source.resolve().is_relative_to(boundary):
        raise ValueError("Reference source must be a regular file inside its subject.")
    content = source.read_text("utf-8")
    if not content.strip() or len(content.encode()) > 48_000:
        raise ValueError("Reference source does not fit the admitted pad.")
    return path, content


def cases(root: Path = ROOT, profiles: list[str] | None = None) -> list[Case]:
    selection = set(PROFILES if profiles is None else profiles)
    if not selection or not selection <= set(PROFILES):
        raise ValueError("Choose one or more reviewed scientific runtime profiles")
    specifications = [
        (
            "polars-reference",
            "polars",
            "polars-001",
            "data-engineering",
            ("polars-001 reference checks passed", "'total_revenue': 30"),
            (),
        ),
        (
            "dbt-model",
            "dbt",
            "dbt-002@sql-model",
            "dbt-duckdb",
            ("dbt model built successfully",),
            ("table", "json"),
        ),
        (
            "julia-reference",
            "julia",
            "julia-020",
            "julia",
            ("julia-020: all reference checks passed",),
            ("plotly",),
        ),
        (
            "stan-reference",
            "bayesian-computing",
            "bayes-017",
            "stan-cpu",
            (
                "Chain 1: 100 retained draws",
                "Chain 2: 100 retained draws",
                "Stan sampling completed",
            ),
            ("table", "plotly"),
        ),
    ]
    result: dict[str, Case] = {}
    for identity, subject, lesson, profile, markers, kinds in specifications:
        path, source = admitted_source(subject, lesson, profile, root)
        result[identity] = Case(
            identity, subject, lesson, profile, source, path, "succeeded", markers, kinds
        )
    result["julia-diagnostic"] = Case(
        "julia-diagnostic",
        "julia",
        "julia-020",
        "julia",
        JULIA_ERROR,
        "synthetic:bounded-julia-diagnostic",
        "failed",
        ("BoundsError", "main.jl"),
        (),
        3,
    )
    result["stan-diagnostic"] = Case(
        "stan-diagnostic",
        "bayesian-computing",
        "bayes-017",
        "stan-cpu",
        STAN_ERROR,
        "synthetic:bounded-stan-diagnostic",
        "failed",
        ("unknown_mean", "main.stan"),
        (),
        5,
    )
    for identity, lesson, source, marker, kinds in (
        (
            "structured-small",
            "eval-001",
            SMALL_SOURCE,
            "SCIENTIST_BROWSER_SMALL_V1",
            ("table", "json"),
        ),
        ("structured-large", "eval-002", LARGE_SOURCE, "SCIENTIST_BROWSER_LARGE_V1", ("json",)),
    ):
        admitted_source("llm-evaluation", lesson, "python-core", root)
        result[identity] = Case(
            identity,
            "llm-evaluation",
            lesson,
            "python-core",
            source,
            "synthetic:" + identity,
            "succeeded",
            (marker,),
            kinds,
        )
    return [result[key] for key in CASE_IDS if result[key].profile in selection]


def fields_from_lesson(data: dict[str, Any]) -> dict[str, str]:
    session = data["session"]
    fields = {
        key: session.get(key, data.get("source", "") if key == "source" else "")
        for key in ("source", "prediction", "explanation", "review")
    }
    if any(not isinstance(value, str) for value in fields.values()):
        raise ValueError("A saved pad contains invalid text fields.")
    return fields


def receipt_digest(job: dict[str, Any]) -> str:
    fields = (
        "job_id",
        "lesson_id",
        "profile",
        "source_sha256",
        "source",
        "status",
        "returncode",
        "output",
        "checks",
        "artifacts",
        "truncated",
        "created_at",
        "worker_instance_id",
    )
    return digest({key: job.get(key) for key in fields})


def validate_job(case: Case, job: dict[str, Any]) -> dict[str, Any]:
    if (
        job.get("lesson_id") != case.lesson_id
        or job.get("profile") != case.profile
        or job.get("source") != case.source
        or job.get("source_sha256") != case.source_sha256
        or job.get("status") != case.status
        or job.get("truncated") is True
        or re.fullmatch(r"[a-f0-9]{32}", str(job.get("job_id", ""))) is None
        or not isinstance(job.get("created_at"), str)
    ):
        raise ValueError(case.id + ": result identity, source or status mismatch")
    if type(job.get("returncode")) is not int:
        raise ValueError(case.id + ": execution return code must be an integer")
    if (case.status == "succeeded" and job.get("returncode") != 0) or (
        case.status == "failed"
        and (type(job.get("returncode")) is not int or job["returncode"] == 0)
    ):
        raise ValueError(case.id + ": unexpected execution return code")
    if any(marker not in job.get("output", "") for marker in case.output_markers):
        raise ValueError(case.id + ": required real output or diagnostic is absent")
    artifacts = job.get("artifacts", [])
    if tuple(row.get("kind") for row in artifacts) != case.kinds:
        raise ValueError(case.id + ": required structured outputs were lost")
    if case.id == "dbt-model":
        table, report = artifacts[0]["table"], artifacts[1]["data"]
        if table["columns"] != ["order_id", "customer_id", "amount"] or sorted(table["rows"]) != [
            [1, 10, 100],
            [2, 20, 50],
            [5, 20, 120],
        ]:
            raise ValueError("The real dbt relation differs from its three-row fixture")
        sql = report.get("compiled_sql", "")
        if (
            "{{" in sql
            or "raw_orders" not in sql
            or "paid" not in sql
            or report.get("row_count") != 3
        ):
            raise ValueError("dbt compilation metadata is incomplete")
        if report.get("commands") != [
            {"command": "seed", "success": True},
            {"command": "build", "success": True},
        ]:
            raise ValueError("The actual seed/build commands did not both succeed")
    if case.id == "stan-reference":
        table, chart = artifacts[0]["table"], artifacts[1]["figure"]
        names = [str(value).lower() for value in table["columns"]]
        if "mean" not in names or not any("r_hat" in name or "rhat" in name for name in names):
            raise ValueError("Native Stan diagnostic columns are missing")
        mean_column = names.index("mean")
        posterior = next((row for row in table["rows"] if row[0] == "posterior_mean"), None)
        if posterior is None or not math.isclose(posterior[mean_column], 40 / 21, abs_tol=1e-4):
            raise ValueError("Stan's exact posterior mean differs from its numerical oracle")
        if len(chart["data"]) != 2 or any(len(trace["y"]) != 100 for trace in chart["data"]):
            raise ValueError("Stan must retain both real short-chain traces")
    if case.id == "structured-small" and (
        digest(artifacts[0]["table"]) != digest(TABLE)
        or digest(artifacts[1]["data"]) != digest(SMALL_REPORT)
    ):
        raise ValueError("Structured values, literal markup or large identifier changed")
    if case.id == "structured-large" and digest(artifacts[0]["data"]) != digest(LARGE_REPORT):
        raise ValueError("Large JSON report was truncated or changed")
    return {
        "case_id": case.id,
        "lesson_id": case.lesson_id,
        "profile": case.profile,
        "source_path": case.source_path,
        "source_sha256": case.source_sha256,
        "job_id": job["job_id"],
        "created_at": job["created_at"],
        "status": job["status"],
        "receipt_sha256": receipt_digest(job),
        "artifacts_sha256": digest(artifacts),
    }


def preflight(
    client: Client, root: Path = ROOT, profiles: list[str] | None = None
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    new_titles = subject_titles(root)
    index = client.call("classroom-index")
    local_ids = set(json.loads((root / "curriculum/catalog.json").read_text())["tracks"])
    local_ids |= {
        json.loads(path.read_text())["track_id"]
        for path in (root / "courses").glob("*/lessons.json")
    }
    local_ids.add("statistics-ml")
    if local_ids != {row["id"] for row in index["tracks"]}:
        raise ValueError("The runtime directory differs from all registered source subjects")
    titles = {row["id"]: row["title"] for row in index["tracks"]}
    if any(titles.get(key) != title for key, title in new_titles.items()):
        raise ValueError("A running scientific subject title differs from its source")
    if not set(SUBJECTS) <= {row["id"] for row in index["tracks"]}:
        raise ValueError("The running classroom omits a required scientific subject")
    if client.call("module-index").get("active_job") is not None:
        raise ValueError("A job is active or unresolved; do not interrupt or replay it")
    ready = {row["profile"] for row in client.call("module-readiness")["profiles"] if row["ready"]}
    if not {case.profile for case in cases(root, profiles)} <= ready:
        raise ValueError("Prepare every selected scientific worker profile first")
    pads = {}
    for identity in PAD_IDS:
        lesson = client.call("module-lesson", lesson_id=identity)
        if any(job.get("status") not in TERMINAL for job in lesson["history"]):
            raise ValueError("An original lesson job has an unresolved outcome: " + identity)
        pads[identity] = fields_from_lesson(lesson)
    return titles, pads


class NetworkLog:
    def __init__(self) -> None:
        self.submissions: list[dict[str, str]] = []
        self.highlights: list[int] = []
        self.blocked: list[str] = []

    def observe(self, request: Any) -> None:
        if request.method != "POST" or "/api/" not in request.url:
            return
        body = request.post_data_json or {}
        if body.get("action") == "module-run":
            self.submissions.append(
                {
                    "lesson_id": body.get("lesson_id", ""),
                    "request_id": body.get("request_id", ""),
                    "source_sha256": source_digest(body.get("source", "")),
                }
            )
        if body.get("action") == "classroom-highlight":
            self.highlights.append(len(str(body.get("source", "")).encode()))

    def readonly_route(self, route: Any) -> None:
        request = route.request
        if request.method == "POST":
            action = (request.post_data_json or {}).get("action", "")
            if action not in READ_ACTIONS | {"classroom-highlight"}:
                self.blocked.append(action)
                route.abort()
                return
        route.fallback()


def show_pad(page: Any, expect: Any) -> None:
    if page.locator("#reading-toggle").get_attribute("aria-pressed") == "true":
        page.locator("#reading-toggle").click()
    expect(page.locator("#source")).to_be_visible()
    expect(page.locator("#explanation")).to_be_visible()


def open_case(page: Any, case: Case, expect: Any) -> None:
    canonical, _, variant = case.lesson_id.partition("@")
    choose_lesson(page, case.subject, canonical, expect)
    if variant:
        page.locator("#variant").select_option(case.lesson_id)
        expect(page).to_have_url(
            re.compile(r"[#&]lesson=" + re.escape(quote(case.lesson_id, safe="")) + r"(?:&|$)")
        )
        expect(page.locator("#save-state")).to_contain_text("Loaded")
    show_pad(page, expect)


def check_tutorial(page: Any, subject: str, identity: str, expect: Any) -> None:
    choose_lesson(page, subject, identity, expect)
    expect(page.locator("#badges")).to_contain_text("Tutorial chapter")
    expect(page.locator("#solution-section")).to_be_hidden()
    show_pad(page, expect)
    expect(page.locator("#prediction")).to_be_hidden()
    expect(page.locator("#read-chapter")).to_be_visible()
    expect(page.locator("#explanation-label")).to_have_text("Notes and interpretations")
    expect(page.locator("#learning-guidance")).to_contain_text("no exams or withheld solutions")
    expect(page.locator("#guide pre code.language-python").first).to_be_visible()


def submit_once(
    page: Any,
    client: Client,
    case: Case,
    expect: Any,
    network: NetworkLog,
    report: dict[str, Any],
) -> dict[str, Any]:
    old = {
        row["job_id"] for row in client.call("module-lesson", lesson_id=case.lesson_id)["history"]
    }
    page.locator("#source").fill(case.source)
    page.locator("#explanation").fill("Disposable acceptance probe; no learner mastery claim.")
    save(page, expect)
    page.locator("#timeout").select_option("120")
    before = len(network.submissions)

    def is_submission(response: Any) -> bool:
        return bool(
            response.request.method == "POST"
            and response.url.endswith("/api/modules")
            and (response.request.post_data_json or {}).get("action") == "module-run"
        )

    try:
        with page.expect_response(is_submission, timeout=45_000) as observed:
            page.locator("#run").click()
        response = observed.value
        if response.status != 200:
            raise RuntimeError("Run request did not return a confirmed success response")
        submitted = response.json()
    except Exception as error:
        report["unconfirmed_submissions"] = network.submissions[before:]
        raise RuntimeError(
            "Submission outcome is unconfirmed. Inspect original request IDs; no retry was sent."
        ) from error
    sent = network.submissions[before:]
    if (
        len(sent) != 1
        or submitted.get("job_id") != sent[0]["request_id"]
        or submitted["job_id"] in old
        or sent[0]["source_sha256"] != case.source_sha256
    ):
        raise ValueError("Submission did not bind one fresh request ID to the intended source")
    report["submissions"].append(sent[0])
    deadline = time.monotonic() + 150
    while True:
        job = client.call("module-job", job_id=submitted["job_id"])
        if job.get("status") in TERMINAL:
            break
        if time.monotonic() >= deadline:
            report["unconfirmed_submissions"] = sent
            raise TimeoutError(
                "Original job remains unresolved; no replay or automatic recovery was attempted"
            )
        page.wait_for_timeout(250)
    validate_job(case, job)
    expect(page.locator("#job-status")).to_contain_text(case.status, timeout=20_000)
    expect(page.locator("#output")).to_have_text(job["output"] or "(No output yet.)")
    if case.diagnostic_line is not None:
        expect(page.locator("#error-line")).to_have_text(
            f"Inspect source line {case.diagnostic_line}"
        )
        page.locator("#error-line").click()
        selected = page.locator("#source").evaluate(
            "node => node.value.slice(node.selectionStart,node.selectionEnd)"
        )
        if selected != case.source.splitlines()[case.diagnostic_line - 1]:
            raise ValueError("Compiler diagnostic selected the wrong submitted source line")
    return job


def expected_json_bytes(page: Any, data: Any) -> bytes:
    value: str = page.evaluate("value => JSON.stringify(value, null, 2)", data)
    return value.encode("utf-8")


def check_outputs(
    page: Any, job: dict[str, Any], expect: Any, network: NetworkLog, case: Case
) -> None:
    artifacts = job.get("artifacts", [])
    expect(page.locator("#figures > figure")).to_have_count(len(artifacts))
    for index, artifact in enumerate(artifacts):
        figure = page.locator("#figures > figure").nth(index)
        figure.scroll_into_view_if_needed()
        expect(figure.locator("figcaption")).to_have_text(artifact["description"])
        kind = artifact["kind"]
        if kind == "table":
            table = artifact["table"]
            expect(figure.locator("thead th")).to_have_text(table["columns"])
            cells = page.evaluate(
                "rows => rows.flat().map(value => value === null ? 'Missing' : String(value))",
                table["rows"],
            )
            expect(figure.locator("tbody td")).to_have_text(cells)
        elif kind == "json":
            code = figure.locator("pre code")
            expect(code).to_have_text(expected_json_bytes(page, artifact["data"]).decode())
            if case.id == "structured-small":
                expect(code.locator("span").first).to_be_attached()
            if case.id == "structured-large":
                expect(code.locator("span")).to_have_count(0)
                if any(size > 60_000 for size in network.highlights):
                    raise ValueError("Large report was sent to the bounded syntax highlighter")
        elif kind == "plotly":
            frame = figure.locator("iframe.saved-plot")
            expect(frame).to_have_attribute("sandbox", "allow-scripts allow-downloads")
            expect(figure.locator("p")).to_contain_text("Saved chart.")
            expect(figure.frame_locator("iframe").locator(".main-svg").first).to_be_visible()
            details = figure.locator("details")
            details.locator("summary").click()
            expect(details.locator("tbody tr")).to_have_count(len(artifact["table"]["rows"]))
        if kind in {"table", "json", "plotly"}:
            data = (
                artifact["table"]
                if kind == "table"
                else (artifact["data"] if kind == "json" else artifact["figure"])
            )
            label = "Download figure JSON" if kind == "plotly" else "Download result JSON"
            with page.expect_download() as downloaded:
                figure.get_by_role("button", name=label, exact=True).click()
            download = downloaded.value
            expected_name = (
                ("figure-" if kind == "plotly" else "result-") + str(index + 1) + ".json"
            )
            if download.suggested_filename != expected_name or Path(
                download.path()
            ).read_bytes() != expected_json_bytes(page, data):
                raise ValueError("Downloaded JSON differs from the exact saved result")
    if case.id.startswith("structured"):
        expect(page.locator("#figures img, #figures script")).to_have_count(0)
        if page.evaluate("window.scientistProbe === true"):
            raise ValueError("Literal report markup executed")
    page.set_viewport_size({"width": 390, "height": 844})
    page.locator("#runtime-results").scroll_into_view_if_needed()
    if page.evaluate("document.documentElement.scrollWidth > innerWidth + 2"):
        raise ValueError("Scientific result layout overflows the narrow viewport")
    elements = page.locator("#figures .structured-table, #figures pre, #figures iframe")
    for element in elements.all():
        element.scroll_into_view_if_needed()
        if not element.evaluate(
            "node => { const r=node.getBoundingClientRect(); "
            "return r.left >= -2 && r.right <= innerWidth + 2; }"
        ):
            raise ValueError("Structured result extends outside the visible viewport")
    page.set_viewport_size({"width": 1440, "height": 1000})


def select_saved_job(page: Any, job: dict[str, Any], expect: Any) -> None:
    details = page.locator("#job-history")
    if details.get_attribute("open") is None:
        details.locator("summary").click()
    label = f"{job['created_at']} · {job['status']} · {job['source_sha256'][:10]}"
    button = page.locator("#history button").filter(
        has_text=re.compile("^" + re.escape(label) + "$")
    )
    expect(button).to_have_count(1)
    button.click()
    expect(page.locator("#output")).to_have_text(job["output"] or "(No output yet.)")


def history_isolation(
    page: Any,
    client: Client,
    case: Case,
    job: dict[str, Any],
    expect: Any,
    network: NetworkLog,
) -> None:
    prefix = "//" if case.profile == "stan-cpu" else ("--" if case.profile == "dbt-duckdb" else "#")
    draft = case.source + f"\n{prefix} Unexecuted draft after {case.id}.\n"
    page.locator("#source").fill(draft)
    save(page, expect)
    submissions = len(network.submissions)
    select_saved_job(page, job, expect)
    expect(page.locator("#source")).to_have_value(draft)
    if case.diagnostic_line is not None:
        expect(page.locator("#error-line")).to_be_hidden()
    if len(network.submissions) != submissions:
        raise ValueError("Reading saved output executed source")
    if client.call("module-lesson", lesson_id=case.lesson_id)["source"] != draft:
        raise ValueError("Reading history replaced the independent editable draft")


def restore_pads(
    client: Client,
    originals: dict[str, dict[str, str]],
    edited: set[str],
    report: dict[str, Any],
) -> None:
    failures = []
    for identity in sorted(edited):
        try:
            client.call("module-save", lesson_id=identity, fields=originals[identity])
        except Exception as error:
            failures.append(f"{identity}: {type(error).__name__}")
    for identity in PAD_IDS:
        try:
            saved = fields_from_lesson(client.call("module-lesson", lesson_id=identity))
            if saved != originals[identity]:
                raise ValueError("restored effective pad differs")
            report["pads"].append({"lesson_id": identity, "sha256": digest(saved)})
        except Exception as error:
            failures.append(f"{identity}: {type(error).__name__}")
    if failures:
        report["restoration_failures"] = failures
        raise RuntimeError("Original pad restoration could not be verified: " + ", ".join(failures))


def qualify(
    browser: Any,
    client: Client,
    origin: str,
    expect: Any,
    audit: Audit,
    report: dict[str, Any],
    root: Path = ROOT,
) -> None:
    titles, originals = preflight(client, root, report["profiles"])
    context = audit.context(browser, origin)
    network = NetworkLog()
    context.on("request", network.observe)
    edited: set[str] = set()
    try:
        page = context.new_page()
        page.goto(origin + "/classroom")
        expect(page.locator("#subject-cards .subject-card")).to_have_count(len(titles))
        for title in titles.values():
            card = page.locator("#subject-cards .subject-card").filter(
                has=page.locator("h3").filter(has_text=re.compile("^" + re.escape(title) + "$"))
            )
            expect(card).to_have_count(1)
        page.locator("#subject-cards .subject-card").filter(
            has=page.locator("h3").filter(has_text=re.compile("^" + re.escape(titles["dbt"]) + "$"))
        ).click()
        expect(page.locator("#workspace-view")).to_be_visible()
        choices = set(
            page.locator("#subject-select option").evaluate_all("nodes => nodes.map(n => n.value)")
        )
        if set(titles) != choices:
            raise ValueError("New subjects are missing from the workspace chooser")
        report["directory"] = sorted(titles)
        audit.passed(f"All {len(titles)} registered subjects appear in both choosers")
        check_tutorial(page, "applied-science", "science-001", expect)
        check_tutorial(page, "bayesian-computing", "bayes-001", expect)
        audit.passed("Scientific tutorials expose examples without exam or solution gates")
        for case in cases(root, report["profiles"]):
            open_case(page, case, expect)
            edited.add(case.lesson_id)
            job = submit_once(page, client, case, expect, network, report)
            report["receipts"].append(validate_job(case, job))
            check_outputs(page, job, expect, network, case)
            history_isolation(page, client, case, job, expect, network)
            for identity in set(PAD_IDS) - edited:
                current = fields_from_lesson(client.call("module-lesson", lesson_id=identity))
                if current != originals[identity]:
                    raise ValueError("An unrelated or canonical pad changed: " + identity)
            audit.passed(case.id + ": real source-bound output, UI, downloads and isolated history")
        audit.clean()
    finally:
        # End browser timers before restoring effective source and all note fields.
        context.close()
        restore_pads(client, originals, edited, report)
    report["passed"] = True


def verify_persistence(
    client: Client, report: dict[str, Any], root: Path = ROOT
) -> list[tuple[Case, dict[str, Any]]]:
    if (
        report.get("passed") is not True
        or not isinstance(report.get("profiles"), list)
        or tuple(row.get("case_id") for row in report.get("receipts", []))
        != tuple(case.id for case in cases(root, report["profiles"]))
        or tuple(row.get("lesson_id") for row in report.get("pads", [])) != PAD_IDS
    ):
        raise ValueError("Persistence requires the complete successful original report")
    readonly = ReadOnlyClient(client)
    result = []
    for case, expected in zip(cases(root, report["profiles"]), report["receipts"], strict=True):
        job = readonly.call("module-job", job_id=expected["job_id"])
        if validate_job(case, job) != expected:
            raise ValueError("Original receipt changed after replacement: " + case.id)
        lesson = readonly.call("module-lesson", lesson_id=case.lesson_id)
        if not any(row["job_id"] == expected["job_id"] for row in lesson["history"]):
            raise ValueError("Original receipt is absent from saved history")
        result.append((case, job))
    for row in report["pads"]:
        saved = fields_from_lesson(readonly.call("module-lesson", lesson_id=row["lesson_id"]))
        if digest(saved) != row["sha256"]:
            raise ValueError("Draft or notes changed after replacement: " + row["lesson_id"])
    return result


def persistence_browser(
    browser: Any,
    client: Client,
    origin: str,
    expect: Any,
    audit: Audit,
    report: dict[str, Any],
    root: Path = ROOT,
) -> None:
    records = verify_persistence(client, report, root)
    network = NetworkLog()
    for case, job in records:
        context = audit.context(browser, origin)
        context.route("**/api/*", network.readonly_route)
        context.on("request", network.observe)
        try:
            page = context.new_page()
            page.goto(origin + "/classroom#lesson=" + quote(case.lesson_id, safe=""))
            expect(page.locator("#authored")).to_be_visible()
            expect(page.locator("#save-state")).to_contain_text("Loaded")
            show_pad(page, expect)
            original = fields_from_lesson(client.call("module-lesson", lesson_id=case.lesson_id))
            expect(page.locator("#source")).to_have_value(original["source"])
            select_saved_job(page, job, expect)
            check_outputs(page, job, expect, network, case)
            expect(page.locator("#source")).to_have_value(original["source"])
        finally:
            context.close()
    if network.submissions or network.blocked:
        raise ValueError("Read-only browser verification attempted a mutation")
    verify_persistence(client, report, root)
    audit.clean()
    report["persistence"] = {
        "passed": True,
        "receipts": len(records),
        "pads": len(PAD_IDS),
        "method": "original IDs and hashes; fresh documents; writes and execution blocked",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--check-persistence", action="store_true")
    parser.add_argument("--profiles", nargs="+", choices=PROFILES)
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error("Use an owned disposable classroom and --confirm-disposable")
    report: dict[str, Any] = {
        "schema_version": 1,
        "passed": False,
        "receipts": [],
        "pads": [],
        "submissions": [],
    }
    report["profiles"] = sorted(set(args.profiles or PROFILES))
    audit = Audit(None)
    try:
        origin = classroom_origin(args.url)
        if args.check_persistence:
            report = json.loads(args.report.read_text("utf-8"))
            if args.profiles and sorted(set(args.profiles)) != report.get("profiles"):
                raise ValueError("Persistence must use the original profile selection")
        else:
            subject_titles()
            cases()
        client = ClassroomClient(args.url)
        api = importlib.import_module("playwright.sync_api")
        with api.sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True, channel="chromium")
            try:
                version_key = (
                    "persistence_browser_version" if args.check_persistence else "browser_version"
                )
                report[version_key] = browser.version
                if args.check_persistence:
                    persistence_browser(
                        browser, ReadOnlyClient(client), origin, api.expect, audit, report
                    )
                else:
                    qualify(browser, client, origin, api.expect, audit, report)
            finally:
                browser.close()
    except Exception as error:
        failure = f"{type(error).__name__}: {error}"
        if args.check_persistence:
            report["persistence"] = {"passed": False, "failure": failure}
        else:
            report.update(passed=False, failure=failure)
        print(failure, file=sys.stderr)
    report["checks"] = [*report.get("checks", []), *audit.checks]
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    if args.check_persistence:
        return int(report.get("persistence", {}).get("passed") is not True)
    return int(report.get("passed") is not True)


if __name__ == "__main__":
    raise SystemExit(main())

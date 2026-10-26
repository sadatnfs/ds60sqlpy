#!/usr/bin/env python3
"""Qualify every offline D3 reference through an explicitly disposable classroom UI.

This uses the real learner pad, preview iframe, saved-observation API and history.
Browser reports remain untrusted client observations, never worker verification.
Install the existing CI browser lock in a separate prepared browser environment.
No engine operations, dependency installs or external data requests occur here.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_classroom_browser import (  # noqa: E402
    Audit,
    choose_lesson,
    save,
    show_code_and_notes,
)
from scripts.check_classroom_profiles import ClassroomClient, classroom_origin  # noqa: E402

IDS = tuple(f"js-{n:03d}" for n in range(43, 67))
NOTE = "Disposable D3 qualification note for "


def references(root: Path = ROOT) -> list[dict[str, str]]:
    base = root / "courses/javascript-typescript"
    inventory = json.loads((base / "fixtures/d3-inventory.json").read_text(encoding="utf-8"))
    manifest = {
        row["id"]: row
        for row in json.loads((base / "lessons.json").read_text(encoding="utf-8"))["lessons"]
    }
    rows = inventory["references"]
    if tuple(row["id"] for row in rows) != IDS:
        raise ValueError("The D3 qualification inventory must cover exactly js-043 through js-066.")
    result = []
    for row in rows:
        lesson = manifest[row["id"]]
        path = root / row["reference"]
        if (
            lesson["runtime_profile"] != "javascript-browser"
            or lesson["language"] != "javascript"
            or row["reference"] not in lesson["solution_paths"]
            or path.is_symlink()
            or not path.resolve().is_relative_to(base.resolve())
            or path.suffix != ".js"
            or path.stat().st_size > 48_000
        ):
            raise ValueError("D3 reference admission or repository ownership changed.")
        source = path.read_text(encoding="utf-8")
        marker = row["id"] + " D3 complete"
        if row["marker"] != marker or marker not in source:
            raise ValueError("D3 completion marker does not match its actual reference.")
        result.append(
            {"id": row["id"], "path": row["reference"], "source": source, "marker": marker}
        )
    return result


def validate_observation(
    record: dict[str, Any], identity: str, source: str, marker: str, status: str = "succeeded"
) -> dict[str, Any]:
    if (
        record.get("kind") != "browser_observation"
        or record.get("lesson_id") != identity
        or record.get("profile") != "javascript-browser"
        or record.get("language") != "javascript"
        or record.get("library") != "d3@7.9.0+plotly@4.1.2"
        or record.get("verification_kind") != "browser_observation"
        or record.get("verified") is not False
        or record.get("checks") != []
        or record.get("returncode") is not None
        or record.get("status") != status
        or record.get("source") != source
        or record.get("source_sha256") != hashlib.sha256(source.encode("utf-8")).hexdigest()
        or marker not in record.get("output", "")
        or re.fullmatch(r"[0-9a-f]{32}", str(record.get("job_id", ""))) is None
    ):
        raise ValueError(
            "The saved observation does not match this source, lesson or honest evidence kind."
        )
    return {
        "lesson_id": identity,
        "source_sha256": record["source_sha256"],
        "observation_id": record["job_id"],
        "status": status,
        "verification_kind": "browser_observation",
        "verified": False,
        "record_sha256": digest_json(record),
        "output_sha256": hashlib.sha256(record["output"].encode("utf-8")).hexdigest(),
    }


def digest_json(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def pad_fingerprint(identity: str, session: dict[str, Any]) -> dict[str, str]:
    source = session.get("source", "")
    notes = {key: session.get(key, "") for key in ("prediction", "explanation", "review")}
    if not isinstance(source, str) or not all(isinstance(value, str) for value in notes.values()):
        raise ValueError("Saved pad contains invalid source or notes.")
    return {
        "lesson_id": identity,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "notes_sha256": digest_json(notes),
        "session_sha256": digest_json(session),
    }


def verify_persistence(
    client: ClassroomClient, report: dict[str, Any], root: Path = ROOT
) -> dict[str, Any]:
    if (
        report.get("passed") is not True
        or tuple(row.get("lesson_id") for row in report.get("references", [])) != IDS
    ):
        raise ValueError("Persistence requires a complete successful original D3 execution report.")
    if tuple(row.get("lesson_id") for row in report.get("pads", [])) != IDS:
        raise ValueError("Persistence requires all original saved-pad fingerprints.")
    by_id = {row["id"]: row for row in references(root)}
    for expected in report["references"]:
        identity = expected["lesson_id"]
        row = by_id[identity]
        record = client.call(
            "module-browser-result", lesson_id=identity, receipt_id=expected["observation_id"]
        )["receipt"]
        actual = validate_observation(record, identity, row["source"], row["marker"])
        if actual != expected:
            raise ValueError("An original D3 observation changed after container replacement.")
    for expected in report["pads"]:
        identity = expected["lesson_id"]
        session = client.call("module-lesson", lesson_id=identity)["session"]
        if pad_fingerprint(identity, session) != expected:
            raise ValueError("Saved D3 source or notes changed after container replacement.")
    return {
        "passed": True,
        "observations": len(IDS),
        "pads": len(IDS),
        "method": "read original IDs and saved pads without source execution or writes",
        "original_execution_evidence_preserved": True,
    }


def history(client: ClassroomClient, identity: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = client.call("module-browser-history", lesson_id=identity)[
        "history"
    ]
    return rows


def open_javascript(page: Any, origin: str, expect: Any, root: Path = ROOT) -> None:
    title = json.loads((root / "courses/javascript-typescript/track.json").read_text())["title"]
    page.goto(origin + "/classroom")
    card = page.locator("#subject-cards .subject-card").filter(
        has=page.locator("h3").filter(has_text=re.compile(r"^" + re.escape(title) + r"$"))
    )
    expect(card).to_have_count(1)
    card.click()
    expect(page.locator("#workspace-view")).to_be_visible()


def run_source(
    page: Any,
    client: ClassroomClient,
    identity: str,
    source: str,
    marker: str,
    expect: Any,
    status: str = "succeeded",
) -> dict[str, Any]:
    choose_lesson(page, "javascript-typescript", identity, expect)
    show_code_and_notes(page, expect)
    before = {record["job_id"] for record in history(client, identity)}
    page.locator("#source").fill(source)
    page.locator("#explanation").fill(NOTE + identity)
    save(page, expect)

    def submitted(response: Any) -> bool:
        if response.request.method != "POST" or not response.url.endswith("/api/modules"):
            return False
        body = response.request.post_data_json or {}
        return (
            body.get("action") == "module-browser-record"
            and body.get("lesson_id") == identity
            and body.get("fields", {}).get("source") == source
        )

    # Pump browser events until this actual submission is saved. A restored old
    # success message must not satisfy the completion boundary of a new run.
    with page.expect_response(submitted, timeout=30_000) as response:
        page.locator("#run").click()
    if response.value.status != 200:
        raise ValueError("The classroom refused to save the submitted browser observation.")
    record: dict[str, Any] = response.value.json()["receipt"]
    if record["job_id"] in before:
        raise ValueError("The new UI run reused an old browser observation ID.")
    validate_observation(record, identity, source, marker, status)
    expect(page.locator("#job-status")).to_contain_text(
        "Browser observation: " + status, timeout=30_000
    )
    expect(page.locator("#output")).to_contain_text(marker)
    expect(page.locator("#run-storage-status")).to_contain_text("client-reported")
    iframe = page.locator("#browser-preview iframe")
    expect(iframe).to_have_count(1)
    assert iframe.get_attribute("sandbox") == "allow-scripts"
    return record


def interaction_checks(page: Any, identity: str, expect: Any) -> None:
    frame = page.frame_locator("#browser-preview iframe")
    if identity == "js-056":
        button = frame.get_by_role("button", name="Inspect A", exact=True)
        button.focus()
        button.press("Enter")
        expect(frame.get_by_role("status")).to_have_text("A: 3")
    elif identity == "js-057":
        frame.get_by_role("button", name="Reset selection", exact=True).click()
        expect(frame.get_by_role("status")).to_have_text("Selected: 1, 2, 3, 4, 5")
        bounds = frame.locator(".overlay").bounding_box()
        assert bounds is not None
        y = bounds["y"] + bounds["height"] * 0.5
        page.mouse.move(bounds["x"] + bounds["width"] * 0.2, y)
        page.mouse.down()
        page.mouse.move(bounds["x"] + bounds["width"] * 0.6, y, steps=6)
        page.mouse.up()
        expect(frame.get_by_role("status")).to_have_text("Selected: 2, 3")
        frame.get_by_role("button", name="Select 2 through 4", exact=True).click()
        expect(frame.get_by_role("status")).to_have_text("Selected: 2, 3, 4")
    elif identity == "js-058":
        frame.locator("svg").hover()
        page.mouse.wheel(0, -200)
        expect(frame.locator("circle").first).not_to_have_attribute("cx", "60")
        frame.get_by_role("button", name="Reset zoom", exact=True).click()
        expect(frame.locator("circle").first).to_have_attribute("cx", "60")
    elif identity == "js-066":
        frame.get_by_label("Learner group", exact=True).select_option("A")
        expect(frame.get_by_role("status")).to_have_text("2 records; total 8 hours")
        expect(frame.locator("tbody tr")).to_have_count(2)
        frame.get_by_label("Learner group", exact=True).select_option("all")
        expect(frame.get_by_role("status")).to_have_text("4 records; total 20 hours")
        expect(frame.locator("tbody tr")).to_have_count(4)


def qualify(browser: Any, origin: str, audit: Audit, expect: Any, report: dict[str, Any]) -> None:
    client = ClassroomClient(origin)
    rows = references()
    by_id = {row["id"]: row for row in rows}
    context = audit.context(browser, origin)
    try:
        page = context.new_page()
        open_javascript(page, origin, expect)
        for row in rows:
            record = run_source(page, client, row["id"], row["source"], row["marker"], expect)
            frame = page.frame_locator("#browser-preview iframe")
            plot = frame.locator("#chart canvas" if row["id"] == "js-064" else "#chart svg")
            expect(plot).to_be_visible()
            assert plot.evaluate(
                "node => new Promise(resolve => { requestAnimationFrame(() => "
                "requestAnimationFrame(() => resolve(node.getBoundingClientRect().width > 0))); })"
            )
            expect(frame.locator("#output")).to_contain_text(row["marker"])
            interaction_checks(page, row["id"], expect)
            frame.locator("#chart").evaluate(
                "node => new Promise(resolve => requestAnimationFrame(() => "
                "requestAnimationFrame(() => requestAnimationFrame(() => resolve(true)))))"
            )
            expect(page.locator("#job-status")).to_contain_text("Browser observation: succeeded")
            expect(page.locator("#output")).to_have_text(row["marker"])
            report["references"].append(
                validate_observation(record, row["id"], row["source"], row["marker"])
            )
            audit.passed(
                row["id"] + ": actual classroom preview and source-bound saved observation"
            )
        page.locator("#browser-preview").scroll_into_view_if_needed()
        audit.screenshot(page, "d3-dashboard-desktop")
        page.set_viewport_size({"width": 390, "height": 844})
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
        expect(
            page.frame_locator("#browser-preview iframe").get_by_label("Learner group")
        ).to_be_visible()
        page.locator("#browser-preview").scroll_into_view_if_needed()
        painted_font_size = (
            page.frame_locator("#browser-preview iframe")
            .locator("svg text.label")
            .first.evaluate(
                "node => new Promise((resolve,reject) => { "
                "const deadline=performance.now()+5000; let stable=0; "
                "function observe(){ const size=parseFloat(getComputedStyle(node).fontSize) "
                "* node.getScreenCTM().a; stable=size>=12?stable+1:0; "
                "if(stable>=3){resolve(size);return;} "
                "if(performance.now()>deadline){"
                "reject(new Error('Chart labels did not settle at readable size'));return;} "
                "requestAnimationFrame(observe); } observe(); })"
            )
        )
        assert painted_font_size >= 12, "Responsive capstone labels became too small to read."
        expect(page.locator("#job-status")).to_contain_text("Browser observation: succeeded")
        expect(page.locator("#output")).to_have_text(by_id["js-066"]["marker"])
        audit.screenshot(page, "d3-dashboard-mobile")
        page.set_viewport_size({"width": 1440, "height": 1000})
        audit.passed(
            "Real keyboard control, pointer brushing, wheel zoom, "
            "dashboard filtering and narrow view"
        )

        # A fresh browser profile must recover server-saved output without executing it.
        final = by_id["js-066"]
        draft = "// Saved independent draft after the qualified reference.\n" + final["source"]
        page.locator("#source").fill(draft)
        save(page, expect)
        stored = history(client, "js-066")
        previous_ids = [row["job_id"] for row in stored]
        report["retained_observation_id"] = stored[0]["job_id"]
    finally:
        context.close()

    context = audit.context(browser, origin)
    try:
        page = context.new_page()
        open_javascript(page, origin, expect)
        choose_lesson(page, "javascript-typescript", "js-066", expect)
        show_code_and_notes(page, expect)
        expect(page.locator("#source")).to_have_value(draft)
        expect(page.locator("#browser-preview iframe")).to_have_count(0)
        if page.locator("#job-history").get_attribute("open") is None:
            page.locator("#job-history summary").click()
        page.locator("#history button").filter(has_text=stored[0]["created_at"]).click()
        expect(page.locator("#output")).to_contain_text(final["marker"])
        expect(page.locator("#source")).to_have_value(draft)
        expect(page.locator("#browser-preview iframe")).to_have_count(0)
        assert [row["job_id"] for row in history(client, "js-066")] == previous_ids
        audit.passed(
            "Fresh browser restores source and saved output; "
            "viewing history neither reruns nor overwrites draft"
        )

        failure = 'throw new Error("D3 controlled failure");\n'
        run_source(page, client, "js-043", failure, "D3 controlled failure", expect, "failed")
        first = by_id["js-043"]
        run_source(page, client, "js-043", first["source"], first["marker"], expect)
        audit.passed(
            "A real thrown error is saved as failed; the exact reference recovers successfully"
        )

        late_source = (
            "const button=document.createElement('button');"
            "button.type='button';button.textContent='Trigger controlled interaction error';"
            "button.addEventListener('click',()=>{"
            "throw new Error('D3 controlled interaction failure');});"
            "document.querySelector('#chart').append(button);"
            "console.log('D3 late-error baseline');"
        )
        initial_late = run_source(
            page, client, "js-043", late_source, "D3 late-error baseline", expect
        )
        page.frame_locator("#browser-preview iframe").get_by_role(
            "button", name="Trigger controlled interaction error", exact=True
        ).click()
        expect(page.locator("#job-status")).to_contain_text("An interaction raised")
        expect(page.locator("#output")).to_contain_text("D3 controlled interaction failure")
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and response.url.endswith("/api/modules")
                and (response.request.post_data_json or {}).get("action") == "module-browser-record"
            ),
            timeout=20_000,
        ) as saved_late:
            page.locator("#browser-observation-save").click()
        assert saved_late.value.status == 200
        failed_late = saved_late.value.json()["receipt"]
        validate_observation(
            failed_late, "js-043", late_source, "D3 controlled interaction failure", "failed"
        )
        assert failed_late["job_id"] != initial_late["job_id"]
        original_late = client.call(
            "module-browser-result", lesson_id="js-043", receipt_id=initial_late["job_id"]
        )["receipt"]
        assert original_late == initial_late
        expect(page.locator("#job-status")).to_contain_text("Browser observation: failed")
        run_source(page, client, "js-043", first["source"], first["marker"], expect)
        report["post_interaction_failure_saved"] = True
        audit.passed(
            "A later interaction error saves a new failed observation "
            "without changing its initial receipt"
        )

        isolation = """let blocked = 0;
try { void parent.document.body; } catch { blocked++; }
try { void localStorage.length; } catch { blocked++; }
try { await fetch('https://example.invalid/d3-network-probe'); } catch { blocked++; }
if (blocked !== 3 || self.origin !== 'null') throw new Error('Preview isolation failed');
console.log('D3 isolation checks complete');"""
        run_source(page, client, "js-043", isolation, "D3 isolation checks complete", expect)
        assert page.locator("#browser-preview iframe").evaluate(
            "node => node.contentDocument === null"
        )
        with client.opener.open(origin + "/browser-sandbox", timeout=10) as response:
            policies = "; ".join(response.headers.get_all("Content-Security-Policy", []))
        for directive in (
            "connect-src 'none'",
            "frame-src 'none'",
            "form-action 'none'",
            "frame-ancestors 'self'",
        ):
            assert directive in policies
        audit.passed(
            "Opaque sandbox denies parent/storage access; "
            "served CSP blocks external connections and embedding actions"
        )

        stale = (
            "console.log('D3 stale frame started'); "
            "await new Promise(resolve=>setTimeout(()=>{"
            "console.log('D3 stale frame late');resolve();},700));"
        )
        choose_lesson(page, "javascript-typescript", "js-043", expect)
        page.locator("#source").fill(stale)
        save(page, expect)
        page.locator("#run").click()
        expect(page.locator("#output")).to_contain_text("D3 stale frame started")
        second = by_id["js-044"]
        run_source(page, client, "js-044", second["source"], second["marker"], expect)
        # Observe beyond the old callback's scheduled boundary to catch stale delivery.
        page.wait_for_timeout(900)
        expect(page.locator("#output")).to_contain_text(second["marker"])
        expect(page.locator("#output")).not_to_contain_text("D3 stale frame late")
        assert (
            page.evaluate("new URLSearchParams(location.hash.slice(1)).get('lesson')") == "js-044"
        )
        audit.passed(
            "Navigation destroys obsolete preview and prevents "
            "its late output reaching the next lesson"
        )
        # Leave the disposable test pads with actual references, not deliberately broken probes.
        run_source(page, client, "js-043", first["source"], first["marker"], expect)
        report["fresh_context_persistence"] = True
        report["history_without_rerun"] = True
        report["failure_recovery"] = True
        report["origin_and_csp_isolation"] = True
        report["stale_frame_navigation"] = True
        report["pads"] = []
        for identity in IDS:
            session = client.call("module-lesson", lesson_id=identity)["session"]
            if session.get("explanation") != NOTE + identity:
                raise ValueError("A D3 note did not survive the UI qualification sequence.")
            report["pads"].append(pad_fingerprint(identity, session))
    finally:
        context.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument(
        "--check-persistence",
        action="store_true",
        help="Read original observations and saved pads after replacement; never rerun source.",
    )
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error(
            "This writes test pads and browser observations; "
            "use an explicitly disposable classroom."
        )
    origin = classroom_origin(args.url)
    if args.check_persistence:
        prior = json.loads(args.report.read_text(encoding="utf-8"))
        prior["container_replacement_persistence"] = verify_persistence(
            ClassroomClient(origin), prior
        )
        args.report.write_text(json.dumps(prior, indent=2) + "\n", encoding="utf-8")
        print(
            "PASS: original D3 observations, source and notes survived "
            "container replacement without rerun."
        )
        return 0
    playwright = importlib.import_module("playwright.sync_api")
    report: dict[str, Any] = {
        "schema_version": 1,
        "passed": False,
        "references": [],
        "evidence_kind": "actual UI execution with untrusted saved browser observations",
    }
    audit = Audit(args.report.parent / "browser-screenshots")
    try:
        with playwright.sync_playwright() as runtime:
            browser = runtime.chromium.launch(headless=True, channel="chromium")
            try:
                report["browser_version"] = browser.version
                qualify(browser, origin, audit, playwright.expect, report)
                audit.clean()
                report["passed"] = True
            finally:
                browser.close()
    finally:
        report["checks"] = audit.checks
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

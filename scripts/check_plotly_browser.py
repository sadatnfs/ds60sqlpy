#!/usr/bin/env python3
"""Exercise all Plotly browser references and offline DAX through the real classroom.

Use a disposable local HTTP classroom. Persistence mode only reads original
observations, reference hashes and saved pads after container replacement.
"""

from __future__ import annotations

import argparse
import importlib
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.check_classroom_browser import (  # noqa: E402
    Audit,
    choose_lesson,
    save,
    show_code_and_notes,
)
from scripts.check_classroom_profiles import ClassroomClient, classroom_origin  # noqa: E402
from scripts.check_d3_browser import digest_json, validate_observation  # noqa: E402
from scripts.check_scientific_artifacts import pad_digest  # noqa: E402

IDS = tuple(f"viz-{number:03}@javascript" for number in range(1, 9))
DAX_ID = "dax-001"
DAX_DRAFT = (
    'EVALUATE ROW("Draft audit", 23)\n// Editable source retained during worked comparison.\n'
)


def references(root: Path = ROOT) -> list[dict[str, Any]]:
    base = root / "courses/data-visualization"
    inventory = json.loads((base / "fixtures/plotly-inventory.json").read_text("utf-8"))
    lessons = {
        row["id"]: row for row in json.loads((base / "lessons.json").read_text("utf-8"))["lessons"]
    }
    if tuple(row["id"] + "@javascript" for row in inventory) != IDS:
        raise ValueError("Plotly browser inventory must include exactly eight admitted variants.")
    result = []
    for row in inventory:
        variant = next(
            item for item in lessons[row["id"]]["variants"] if item["id"] == "javascript"
        )
        path = root / row["javascript_reference"]
        if (
            variant["runtime_profile"] != "javascript-browser"
            or variant["language"] != "javascript"
            or row["javascript_reference"] not in variant["solution_paths"]
            or path.is_symlink()
            or not path.resolve().is_relative_to(base.resolve())
            or path.suffix != ".js"
            or path.stat().st_size > 100_000
        ):
            raise ValueError("Plotly reference admission or owned path changed.")
        source = path.read_text("utf-8")
        if row["marker"] != row["id"] + " Plotly complete" or row["marker"] not in source:
            raise ValueError("Plotly marker is not bound to its reference.")
        result.append(
            {**row, "id": row["id"] + "@javascript", "canonical": row["id"], "source": source}
        )
    return result


def validate_dax_reference(value: dict[str, Any]) -> str:
    if (
        value.get("lesson_id") != DAX_ID
        or value.get("evidence") != "hand-derived"
        or value.get("executed") is not False
        or not value.get("reference_source")
        or not value.get("cases")
    ):
        raise ValueError("DAX comparison must remain hand-derived reference evidence.")
    for key in ("source_sha256", "model_sha256"):
        if re.fullmatch(r"[a-f0-9]{64}", str(value.get(key, ""))) is None:
            raise ValueError("DAX comparison is missing a source/model digest.")
    return digest_json(value)


def verify_persistence(client: Any, report: dict[str, Any], root: Path = ROOT) -> dict[str, Any]:
    if (
        report.get("passed") is not True
        or tuple(row.get("lesson_id") for row in report.get("references", [])) != IDS
        or tuple(row.get("lesson_id") for row in report.get("pads", [])) != (*IDS, DAX_ID)
    ):
        raise ValueError("Persistence needs the complete successful Plotly and DAX report.")
    for row, expected in zip(references(root), report["references"], strict=True):
        record = client.call(
            "module-browser-result", lesson_id=row["id"], receipt_id=expected["observation_id"]
        )["receipt"]
        if validate_observation(record, row["id"], row["source"], row["marker"]) != expected:
            raise ValueError("An original Plotly observation changed after replacement.")
    for expected in report["pads"]:
        session = client.call("module-lesson", lesson_id=expected["lesson_id"])["session"]
        if pad_digest(session) != expected["sha256"]:
            raise ValueError("Restored Plotly or DAX source/notes changed after replacement.")
    dax = client.call("module-worked-examples", lesson_id=DAX_ID, reveal=True)
    if validate_dax_reference(dax) != report["dax"]["reference_sha256"]:
        raise ValueError("DAX hand-derived reference changed after replacement.")
    return {
        "passed": True,
        "observations": len(IDS),
        "pads": len(IDS) + 1,
        "method": "read original evidence and restored pads; no execution or writes",
    }


def select_plotly(page: Any, row: dict[str, Any], expect: Any) -> None:
    choose_lesson(page, "data-visualization", row["canonical"], expect)
    page.locator("#variant").select_option(row["id"])
    expect(page).to_have_url(
        re.compile(r"[#&]lesson=" + re.escape(quote(row["id"], safe="")) + r"(?:&|$)")
    )
    expect(page.locator("#save-state")).to_contain_text("Loaded")
    show_code_and_notes(page, expect)


def run_reference(page: Any, client: Any, row: dict[str, Any], expect: Any) -> dict[str, Any]:
    old_ids = {
        item["job_id"]
        for item in client.call("module-browser-history", lesson_id=row["id"])["history"]
    }
    page.locator("#source").fill(row["source"])
    save(page, expect)

    def submitted(response: Any) -> bool:
        if response.request.method != "POST" or not response.url.endswith("/api/modules"):
            return False
        body = response.request.post_data_json or {}
        return (
            body.get("action") == "module-browser-record"
            and body.get("lesson_id") == row["id"]
            and body.get("fields", {}).get("source") == row["source"]
        )

    with page.expect_response(submitted, timeout=45_000) as response:
        page.locator("#run").click()
    if response.value.status != 200:
        raise ValueError("The submitted Plotly observation was not saved.")
    record = response.value.json()["receipt"]
    if record.get("job_id") in old_ids:
        raise ValueError("A new Plotly run reused an earlier observation.")
    validated = validate_observation(record, row["id"], row["source"], row["marker"])
    expect(page.locator("#job-status")).to_contain_text("Browser observation: succeeded")
    frame = page.frame_locator("#browser-preview iframe")
    expect(page.locator("#browser-preview iframe")).to_have_attribute("sandbox", "allow-scripts")
    expect(frame.locator("#output")).to_contain_text(row["marker"])
    expect(frame.locator("table tbody tr")).to_have_count(row["expected_table_rows"])
    assert frame.locator(".main-svg").count() > 0, "Plotly did not render SVG."
    if row["canonical"] == "viz-004":
        button = frame.get_by_role("button", name="Group A", exact=True)
        button.focus()
        button.press("Enter")
        expect(frame.get_by_role("status")).to_contain_text("Chart group: A.")
        expect(button).to_have_attribute("aria-pressed", "true")
        frame.get_by_role("button", name="Group B", exact=True).click()
        expect(frame.get_by_role("status")).to_contain_text("Chart group: B.")
        frame.get_by_role("button", name="All groups", exact=True).click()
        expect(frame.get_by_role("status")).to_contain_text("Chart group: All.")
        expect(frame.locator("table tbody tr")).to_have_count(8)
    if row["canonical"] == "viz-008":
        frame.get_by_role("button", name="Show figure JSON").click()
        exported = json.loads(frame.locator("textarea").input_value())
        if exported["data"][0]["y"] != [8, 3, 1]:
            raise ValueError("Figure export changed the declared counts.")
    page.set_viewport_size({"width": 390, "height": 844})
    page.wait_for_timeout(300)
    overflow = frame.locator("html").evaluate("node => node.scrollWidth > innerWidth + 2")
    if overflow:
        raise ValueError("Plotly preview overflows the narrow viewport.")
    expect(page.locator("#job-status")).not_to_contain_text("An interaction raised")
    page.set_viewport_size({"width": 1440, "height": 1000})
    return validated


def restored_pad(
    page: Any, client: Any, identity: str, source: str, original: dict[str, Any], expect: Any
) -> dict[str, Any]:
    page.locator("#source").fill(source)
    save(page, expect)
    fields = {
        key: original.get(key, source if key == "source" else "")
        for key in ("source", "prediction", "explanation", "review")
    }
    client.call("module-save", lesson_id=identity, fields=fields)
    session = client.call("module-lesson", lesson_id=identity)["session"]
    if pad_digest(session) != pad_digest(fields):
        raise ValueError("Original draft and notes were not restored.")
    return {"lesson_id": identity, "sha256": pad_digest(session)}


def dax_flow(page: Any, client: Any, expect: Any, report: dict[str, Any]) -> None:
    choose_lesson(page, "dax", DAX_ID, expect)
    show_code_and_notes(page, expect)
    original = client.call("module-lesson", lesson_id=DAX_ID)["session"]
    source = page.locator("#source").input_value()
    submissions = []

    def watch(request: Any) -> None:
        if request.method == "POST" and request.url.endswith("/api/modules"):
            body = request.post_data_json or {}
            if body.get("lesson_id") == DAX_ID and body.get("action") == "module-run":
                submissions.append(body["action"])

    page.on("request", watch)
    try:
        page.locator("#source").fill(DAX_DRAFT)
        save(page, expect)
        expect(page.locator("#run")).to_be_hidden()
        expect(page.locator("#runtime-results")).to_be_hidden()
        expect(page.locator("#offline-workspace")).to_be_visible()
        page.locator("#source").press("Control+Enter")
        page.wait_for_timeout(100)
        expect(page.locator("#source")).to_have_value(DAX_DRAFT)
        with page.expect_download() as download:
            page.locator("#download-source").click()
        exported = download.value
        if (
            not exported.suggested_filename.endswith(".dax")
            or Path(exported.path()).read_text("utf-8") != DAX_DRAFT
        ):
            raise ValueError("DAX export did not preserve the editable source.")
        with page.expect_response(
            lambda response: (
                response.request.method == "POST"
                and response.url.endswith("/api/modules")
                and (response.request.post_data_json or {}).get("action")
                == "module-worked-examples"
            )
        ) as response:
            page.locator("#offline-compare").click()
        if response.value.status != 200:
            raise ValueError("DAX worked comparison could not be opened.")
        reference = response.value.json()
        signature = validate_dax_reference(reference)
        expect(page.locator("#offline-cases table")).to_have_count(len(reference["cases"]))
        expect(page.locator("#offline-cases")).to_contain_text("Hand-derived result")
        expect(page.locator("#source")).to_have_value(DAX_DRAFT)
        page.reload()
        show_code_and_notes(page, expect)
        expect(page.locator("#source")).to_have_value(DAX_DRAFT)
        expect(page.locator("#run")).to_be_hidden()
        page.set_viewport_size({"width": 390, "height": 844})
        if page.locator("html").evaluate("node => node.scrollWidth > innerWidth + 2"):
            raise ValueError("Offline DAX overflows the narrow viewport.")
        page.set_viewport_size({"width": 1440, "height": 1000})
        if submissions:
            raise ValueError("Offline DAX submitted an execution request.")
        report["dax"] = {
            "lesson_id": DAX_ID,
            "reference_sha256": signature,
            "draft_reload": True,
            "draft_export": True,
            "keyboard_guard": True,
            "mobile_layout": True,
            "no_execution_submission": True,
        }
    finally:
        page.remove_listener("request", watch)
        report["pads"].append(restored_pad(page, client, DAX_ID, source, original, expect))


def qualify(
    browser: Any,
    client: Any,
    origin: str,
    expect: Any,
    audit: Audit,
    report: dict[str, Any],
    root: Path = ROOT,
) -> None:
    context = audit.context(browser, origin)
    page = context.new_page()
    try:
        page.goto(origin + "/classroom")
        title = json.loads((root / "courses/data-visualization/track.json").read_text())["title"]
        page.locator("#subject-cards .subject-card").filter(
            has=page.locator("h3").filter(has_text=re.compile("^" + re.escape(title) + "$"))
        ).click()
        expect(page.locator("#workspace-view")).to_be_visible()
        for row in references(root):
            select_plotly(page, row, expect)
            original = client.call("module-lesson", lesson_id=row["id"])["session"]
            source = page.locator("#source").input_value()
            try:
                report["references"].append(run_reference(page, client, row, expect))
            finally:
                report["pads"].append(
                    restored_pad(page, client, row["id"], source, original, expect)
                )
            audit.passed(row["id"] + " SVG, accessible table, interaction and source restoration")
        dax_flow(page, client, expect, report)
        audit.clean()
        report["passed"] = True
    finally:
        context.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--check-persistence", action="store_true")
    args = parser.parse_args(argv)
    if not args.confirm_disposable:
        parser.error("Use only an owned disposable classroom and pass --confirm-disposable.")
    report: dict[str, Any] = {"schema_version": 1, "passed": False, "references": [], "pads": []}
    audit = Audit(None)
    try:
        origin = classroom_origin(args.url)
        client = ClassroomClient(args.url)
        if args.check_persistence:
            report = json.loads(args.report.read_text("utf-8"))
            report["persistence"] = verify_persistence(client, report)
        else:
            api = importlib.import_module("playwright.sync_api")
            with api.sync_playwright() as runtime:
                browser = runtime.chromium.launch(headless=True, channel="chromium")
                try:
                    report["browser_version"] = browser.version
                    qualify(browser, client, origin, api.expect, audit, report)
                finally:
                    browser.close()
    except Exception as error:
        report.update(passed=False, failure=f"{type(error).__name__}: {error}")
        print(report["failure"], file=sys.stderr)
    report["checks"] = audit.checks if not args.check_persistence else report.get("checks", [])
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + "\n", "utf-8")
    return int(report.get("passed") is not True)


if __name__ == "__main__":
    raise SystemExit(main())

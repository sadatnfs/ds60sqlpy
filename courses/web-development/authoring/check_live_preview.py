#!/usr/bin/env python3
"""Actual-browser checks for opt-in live HTML and D3 previews in disposable state."""

from __future__ import annotations

import argparse
import importlib
import json
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from scripts.check_classroom_browser import choose_lesson, show_code_and_notes  # noqa: E402


def document(label: str) -> str:
    return (
        '<!doctype html><html lang="en"><head><meta name="viewport" content="width=device-width">'
        "<title>Live preview check</title><style>body{margin:0;padding:1rem;font:1rem system-ui}"
        "h1{color:rgb(0,80,0)}@media(max-width:500px){h1{color:rgb(160,0,0)}}</style>"
        f"</head><body><main><h1>{label}</h1><p>Local preview data.</p></main>"
        f'<script>console.log("{label}")</script></body></html>'
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--screenshots", type=Path)
    args = parser.parse_args()
    address = urlsplit(args.url)
    if (
        not args.confirm_disposable
        or address.scheme != "http"
        or address.hostname != "127.0.0.1"
        or address.username
        or address.password
    ):
        raise SystemExit("Use an explicitly disposable local loopback classroom.")
    origin = f"{address.scheme}://{address.netloc}"
    api = importlib.import_module("playwright.sync_api")
    checks: list[str] = []
    receipts: list[dict[str, Any]] = []
    page_errors: list[str] = []
    frame_loads: list[str] = []
    passed = False
    with api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel="chromium")
        context = browser.new_context(
            viewport={"width": 1600, "height": 1100}, service_workers="block"
        )
        context.set_default_timeout(20000)
        page = context.new_page()
        page.on("pageerror", lambda error: page_errors.append(str(error)))

        def observe(request: Any) -> None:
            path = urlsplit(request.url).path
            if path == "/browser-sandbox":
                frame_loads.append(path)
            if request.method == "POST" and path == "/api/modules":
                payload = request.post_data_json
                if payload.get("action") == "module-browser-record":
                    receipts.append(
                        {"lesson_id": payload["lesson_id"], "source": payload["fields"]["source"]}
                    )

        page.on("request", observe)

        def record(label: str) -> None:
            checks.append(label)
            print("PASS " + label, flush=True)

        def heading(label: str) -> Any:
            frame = page.frame_locator("#browser-preview iframe")
            api.expect(frame.locator("h1")).to_have_text(label)
            api.expect(page.locator("#job-status")).to_contain_text("succeeded")
            return frame

        try:
            page.goto(origin + "/classroom#lesson=web-001")
            api.expect(page.locator("#save-state")).to_contain_text("Loaded", timeout=90000)
            show_code_and_notes(page, api.expect)
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            page.locator("#source").fill(document("LIVE_FIRST"))
            page.locator("#browser-live-toggle").check()
            frame = heading("LIVE_FIRST")
            api.expect(page.locator("#authored")).to_have_class("panes browser-focus")
            assert not receipts
            record("Live rendering requires explicit opt-in and does not create a saved run")

            previous = len(frame_loads)
            page.locator("#source").fill(document("LIVE_OLD_A"))
            page.wait_for_timeout(100)
            page.locator("#source").fill(document("LIVE_OLD_B"))
            page.wait_for_timeout(100)
            latest = document("LIVE_LATEST")
            page.locator("#source").fill(latest)
            frame = heading("LIVE_LATEST")
            assert len(frame_loads) == previous + 1, "Rapid typing created redundant frames"
            assert not receipts
            record("Rapid typing debounces into one latest-source preview")

            focus_source = document("FOCUS_RETAINED").replace(
                "</main>",
                '<input id="page-focus"><script>document.querySelector("#page-focus").focus();</script></main>',
            )
            page.locator("#source").fill(focus_source)
            heading("FOCUS_RETAINED")
            api.expect(page.locator("#source")).to_be_focused()
            page.locator("#source").fill(latest)
            frame = heading("LIVE_LATEST")
            record("Initial page focus requests do not interrupt typing in the live editor")

            previous = len(frame_loads)
            page.locator("#browser-viewport").select_option("390")
            api.expect(frame.locator("h1")).to_have_css("color", "rgb(160, 0, 0)")
            page.locator(
                "#browser-preview iframe"
            ).element_handle().content_frame().wait_for_function("innerWidth === 390")
            page.locator("#browser-viewport").select_option("768")
            api.expect(frame.locator("h1")).to_have_css("color", "rgb(0, 80, 0)")
            page.locator(
                "#browser-preview iframe"
            ).element_handle().content_frame().wait_for_function("innerWidth === 768")
            page.locator("#browser-viewport").select_option("1280")
            page.locator(
                "#browser-preview iframe"
            ).element_handle().content_frame().wait_for_function("innerWidth === 1280")
            assert len(frame_loads) == previous
            page.locator("#browser-viewport").select_option("fit")
            record("Viewport presets resize the same iframe and activate real media queries")

            page.locator("#browser-live-pause").click()
            api.expect(page.locator("#browser-live-pause")).to_have_text("Resume updates")
            previous = len(frame_loads)
            page.locator("#source").fill(document("LIVE_AFTER_PAUSE"))
            page.wait_for_timeout(900)
            api.expect(frame.locator("h1")).to_have_text("LIVE_LATEST")
            assert len(frame_loads) == previous
            page.locator("#browser-live-pause").click()
            frame = heading("LIVE_AFTER_PAUSE")
            record("Pause prevents automatic refresh and Resume renders the current draft")

            page.locator("#source").fill(document("MUST_NOT_START"))
            previous = len(frame_loads)
            page.locator("#browser-live-stop").click()
            page.wait_for_timeout(900)
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            assert len(frame_loads) == previous
            assert not receipts
            record("Stop cancels pending refresh without a background restart or receipt")

            manual = document("MANUAL_EXACT_SOURCE")
            page.locator("#source").fill(manual)
            page.locator("#browser-live-toggle").check()
            heading("MANUAL_EXACT_SOURCE")
            page.locator("#run").click()
            api.expect(page.locator("#run-storage-status")).to_contain_text(
                "Saved browser observation"
            )
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            assert len(receipts) == 1 and receipts[0]["source"] == manual
            record("Manual Run exits live mode and records its exact submitted source once")

            page.locator("#source").fill(document("UNSAVED_RUN_DRAFT"))
            page.locator("#browser-live-toggle").check()
            heading("UNSAVED_RUN_DRAFT")
            api.expect(page.locator("#job-history")).to_be_visible()
            page.locator("#job-history summary").click()
            page.locator("#history button").first.click()
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            api.expect(page.locator("#source")).to_have_value(document("UNSAVED_RUN_DRAFT"))
            page.wait_for_timeout(900)
            assert len(receipts) == 1
            record(
                "Viewing a historical result stops live updates and never overwrites or reruns the draft"
            )

            explicit = document("EXPLICIT_OBSERVATION")
            page.locator("#source").fill(explicit)
            page.locator("#browser-live-toggle").check()
            heading("EXPLICIT_OBSERVATION")
            page.locator("#browser-observation-save").click()
            api.expect(page.locator("#run-storage-status")).to_contain_text(
                "Saved browser observation"
            )
            api.expect(page.locator("#browser-live-pause")).to_have_text("Resume updates")
            assert len(receipts) == 2 and receipts[-1]["source"] == explicit
            record("Save observation deliberately stores one exact live source and pauses updates")

            page.locator("#browser-live-pause").click()
            heading("EXPLICIT_OBSERVATION")
            page.locator("#source").fill(document("NAVIGATION_MUST_CANCEL"))
            previous = len(frame_loads)
            choose_lesson(page, "web-development", "web-031", api.expect)
            page.wait_for_timeout(900)
            api.expect(page.locator("#browser-live-controls")).not_to_be_visible()
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            assert len(frame_loads) == previous
            choose_lesson(page, "web-development", "web-001", api.expect)
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            record("Navigation cancels pending refresh; PHP and reopened lessons do not auto-run")

            choose_lesson(page, "javascript-typescript", "js-043", api.expect)
            d3 = 'd3.select("#chart").append("svg").attr("viewBox","0 0 200 100").append("circle").attr("cx",80).attr("cy",50).attr("r",20); console.log("D3_LIVE_READY");'
            page.locator("#source").fill(d3)
            page.locator("#browser-live-toggle").check()
            api.expect(page.locator("#output")).to_contain_text("D3_LIVE_READY")
            api.expect(
                page.frame_locator("#browser-preview iframe").locator("svg circle")
            ).to_have_count(1)
            page.locator("#source").fill(
                'console.log("D3_STALE_STARTED");'
                "await new Promise(resolve => setTimeout(resolve, 1800));"
                'console.log("D3_STALE_FINISHED");'
            )
            api.expect(page.locator("#output")).to_contain_text("D3_STALE_STARTED")
            page.locator("#source").fill(d3)
            api.expect(page.locator("#output")).to_contain_text("D3_LIVE_READY")
            page.wait_for_timeout(1300)
            api.expect(page.locator("#output")).not_to_contain_text("D3_STALE_FINISHED")
            api.expect(
                page.frame_locator("#browser-preview iframe").locator("svg circle")
            ).to_have_count(1)
            record("Replacing an in-flight asynchronous preview ignores its stale completion")
            page.locator("#source").fill('throw new Error("D3_LIVE_ERROR");')
            api.expect(page.locator("#output")).to_contain_text("D3_LIVE_ERROR")
            api.expect(page.locator("#job-status")).to_contain_text("failed")
            page.locator("#source").fill(d3)
            api.expect(page.locator("#output")).to_contain_text("D3_LIVE_READY")
            api.expect(page.locator("#job-status")).to_contain_text("succeeded")
            assert len(receipts) == 2
            record(
                "Browser JavaScript/D3 renders live, reports errors and recovers without saved-run noise"
            )

            page.locator("#browser-live-toggle").focus()
            page.keyboard.press("Space")
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            page.keyboard.press("Space")
            api.expect(page.locator("#browser-live-toggle")).to_be_checked()
            api.expect(page.locator("#output")).to_contain_text("D3_LIVE_READY")
            page.locator("#browser-live-controls").scroll_into_view_if_needed()
            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                page.screenshot(path=str(args.screenshots / "studio-desktop.png"))
            page.set_viewport_size({"width": 390, "height": 844})
            page.locator("#browser-viewport").select_option("1280")
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1")
            api.expect(page.locator("#browser-live-toggle")).to_be_visible()
            if args.screenshots:
                page.screenshot(path=str(args.screenshots / "studio-phone.png"))
            record(
                "Live controls are keyboard operable and a wide preview does not overflow the mobile page"
            )

            page.reload()
            api.expect(page.locator("#save-state")).to_contain_text("Loaded")
            api.expect(page.locator("#browser-live-toggle")).not_to_be_checked()
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            assert len(receipts) == 2
            assert not page_errors, page_errors
            record("Reload restores the draft without persisting execution opt-in")
            passed = True
        finally:
            context.close()
            browser.close()
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(
                json.dumps(
                    {
                        "passed": passed,
                        "checks": checks,
                        "explicit_receipt_count": len(receipts),
                        "page_errors": page_errors,
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
                newline="\n",
            )
    print(f"Passed {len(checks)} live-preview acceptance groups.")


if __name__ == "__main__":
    main()

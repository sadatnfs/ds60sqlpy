#!/usr/bin/env python3
"""Exercise web references through a disposable classroom's actual browser preview."""

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
from scripts.check_classroom_browser import choose_lesson, save, show_code_and_notes  # noqa: E402

NATIVE_CASES = [
    (
        "Native parser and real lifecycle",
        '<!doctype html><html><head><script>'
        'console.log("head-late-absent", !document.querySelector("#late"), document.readyState);'
        'document.addEventListener("DOMContentLoaded", () => console.log("document-dom", document.readyState));'
        'window.addEventListener("DOMContentLoaded", () => console.log("window-dom", document.readyState));'
        'window.addEventListener("load", () => console.log("window-load", document.readyState));'
        '</script></head><body><main id="late">Late content</main></body></html>',
        ["head-late-absent true loading", "document-dom interactive", "window-dom interactive", "window-load complete"],
        "succeeded",
    ),
    (
        "Classic scripts share global lexical bindings",
        '<!doctype html><html><head><script>const sharedNumber = 41;</script></head>'
        '<body><main>Scopes</main><script>console.log("shared-binding", sharedNumber + 1);</script></body></html>',
        ["shared-binding 42"],
        "succeeded",
    ),
    (
        "Inline modules retain exports and strict this semantics",
        '<!doctype html><html><body><main>Module</main><script type="module">'
        'export const value = 42; console.log("module-this", this === undefined);'
        'console.log("module-value", value);</script></body></html>',
        ["module-this true", "module-value 42"],
        "succeeded",
    ),
    (
        "Load handler errors prevent initial success",
        '<!doctype html><html><body><main>Load failure</main><script>'
        'window.addEventListener("load", () => { throw new Error("deliberate load failure"); });'
        '</script></body></html>',
        ["deliberate load failure"],
        "failed",
    ),
    (
        "Opaque origin and response CSP survive native parsing",
        '<!doctype html><html><body><main>Isolation</main><script>'
        'try { parent.document.body; console.log("parent-accessible"); } catch (_) { console.log("parent-blocked"); }'
        'try { document.cookie; console.log("cookie-accessible"); } catch (_) { console.log("cookie-blocked"); }'
        'fetch("https://example.invalid/web-preview").then(() => console.log("network-accessible"))'
        '.catch(() => console.log("network-blocked"));</script></body></html>',
        ["parent-blocked", "cookie-blocked", "network-blocked"],
        "succeeded",
    ),
    (
        "External scripts fail explicitly",
        '<!doctype html><html><body><main>Blocked asset</main><script src="https://example.invalid/blocked.js"></script></body></html>',
        ["External scripts are blocked"],
        "failed",
    ),
    (
        "Navigation metadata fails explicitly",
        '<!doctype html><html><head><meta http-equiv="refresh" content="0;url=https://example.invalid/"></head><body><main>Blocked metadata</main></body></html>',
        ["Navigation metadata"],
        "failed",
    ),
]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    parsed = urlsplit(args.url)
    if not args.confirm_disposable or parsed.scheme != "http" or parsed.hostname != "127.0.0.1" or parsed.username or parsed.password:
        raise SystemExit("Use an explicitly disposable local loopback classroom.")
    origin = f"{parsed.scheme}://{parsed.netloc}"
    api = importlib.import_module("playwright.sync_api")
    checks: list[str] = []
    failures: list[str] = []
    unexpected_requests: list[str] = []
    passed = False
    with api.sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True, channel="chromium")
        context = browser.new_context(viewport={"width": 1440, "height": 1100}, service_workers="block")
        context.set_default_timeout(20000)
        page = context.new_page()
        page.on("pageerror", lambda error: failures.append(str(error)))

        def route(request: Any) -> None:
            target = urlsplit(request.request.url)
            if target.scheme in {"http", "https"} and f"{target.scheme}://{target.netloc}" != origin:
                unexpected_requests.append(f"{target.scheme}://{target.netloc}")
                request.abort()
            else:
                request.continue_()

        def run(source: str, markers: list[str], status: str = "succeeded") -> None:
            page.locator("#source").fill(source)
            page.locator("#run").click()
            page.locator("#browser-preview").scroll_into_view_if_needed()
            for marker in markers:
                api.expect(page.locator("#output")).to_contain_text(marker)
            api.expect(page.locator("#job-status")).to_contain_text(status)

        def record(label: str) -> None:
            checks.append(label)
            print("PASS " + label, flush=True)

        context.route("**/*", route)
        try:
            page.goto(origin + "/classroom#lesson=web-001")
            api.expect(page.locator("#save-state")).to_contain_text("Loaded", timeout=90000)
            for number in range(1, 31):
                key = f"web-{number:03d}"
                choose_lesson(page, "web-development", key, api.expect)
                show_code_and_notes(page, api.expect)
                source = (ROOT / f"courses/web-development/solutions/{key}_solution.html").read_text(encoding="utf-8")
                run(source, [key + " reference checks passed"])
                frame = page.frame_locator("#browser-preview iframe")
                api.expect(frame.locator("main")).to_be_visible()
                api.expect(frame.locator("#reference-status")).to_contain_text("reference checks passed")
                assert frame.locator("html").get_attribute("lang") == "en"
                if number == 25:
                    frame.locator("#add").focus()
                    page.keyboard.press("Enter")
                    api.expect(frame.locator("#count")).to_have_text("1")
                    frame.locator("#reset").click()
                    api.expect(frame.locator("#count")).to_have_text("0")
                if number == 26:
                    frame.locator("summary").click()
                    api.expect(frame.locator("details")).to_have_attribute("open", "")
                    frame.locator("#open").click()
                    api.expect(frame.locator("dialog")).to_be_visible()
                    frame.locator("#close").click()
                    api.expect(frame.locator("dialog")).not_to_be_visible()
                    api.expect(frame.locator("#open")).to_be_focused()
                if number == 27:
                    frame.locator("#minutes").fill("121")
                    frame.locator("#validate").click()
                    api.expect(frame.locator("#minutes")).to_have_attribute("aria-invalid", "true")
                    api.expect(frame.locator("#minutes")).to_have_value("121")
                    frame.locator("#minutes").fill("30")
                    frame.locator("#validate").click()
                    api.expect(frame.locator("#error")).to_contain_text("Valid local plan")
                if number == 28:
                    frame.locator("#threshold").select_option("100")
                    api.expect(frame.locator("tbody tr")).to_have_count(0)
                    api.expect(frame.locator("#summary")).to_contain_text("No records")
                    frame.locator("#threshold").select_option("40")
                    api.expect(frame.locator("tbody tr")).to_have_count(2)
                if number == 29:
                    api.expect(frame.locator("#untrusted img")).to_have_count(0)
                    api.expect(frame.locator("#untrusted")).to_contain_text("<img")
                if number >= 24:
                    page.set_viewport_size({"width": 390, "height": 844})
                    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), key
                    assert frame.locator("html").evaluate("node => node.scrollWidth <= innerWidth + 1"), key
                    api.expect(page.locator("#job-status")).to_contain_text("succeeded")
                    page.set_viewport_size({"width": 1440, "height": 1100})
                record(key + ": actual HTML/CSS/inline-script preview")

            choose_lesson(page, "web-development", "web-030", api.expect)
            for label, source, markers, status in NATIVE_CASES:
                run(source, markers, status)
                record(label)

            for identity in ("js-043", "js-055"):
                choose_lesson(page, "javascript-typescript", identity, api.expect)
                source = (ROOT / f"courses/javascript-typescript/solutions/{identity}_solution.js").read_text(encoding="utf-8")
                run(source, [identity + " D3 complete"])
                api.expect(page.frame_locator("#browser-preview iframe").locator("svg")).to_be_visible()
                record(identity + ": existing D3 preview remains operational")

            choose_lesson(page, "web-development", "web-025", api.expect)
            newest = '<!doctype html><html lang="en"><head><title>Saved draft</title></head><body><main><h1>Newer retained draft</h1></main></body></html>'
            page.locator("#source").fill(newest)
            save(page, api.expect)
            choose_lesson(page, "web-development", "web-031", api.expect)
            php = '<?php echo "Separate PHP source";\n'
            page.locator("#source").fill(php)
            save(page, api.expect)
            choose_lesson(page, "web-development", "web-025", api.expect)
            api.expect(page.locator("#source")).to_have_value(newest)
            api.expect(page.locator("#output")).to_contain_text("web-025 reference checks passed")
            page.reload()
            api.expect(page.locator("#save-state")).to_contain_text("Loaded")
            api.expect(page.locator("#source")).to_have_value(newest)
            api.expect(page.locator("#browser-preview iframe")).to_have_count(0)
            record("HTML/PHP pads stay separate; observation neither overwrites nor replays newer draft")
            run('<!doctype html><html><body><main><h1>Failure case</h1></main><script>throw new Error("deliberate web failure")</script></body></html>', ["deliberate web failure"], "failed")
            page.locator("#source").fill(newest)
            save(page, api.expect)
            record("Thrown inline-script failure is reported as failed")
            if failures or unexpected_requests:
                raise AssertionError(json.dumps({"page_errors": failures, "external_requests": unexpected_requests}))
            record("No uncaught classroom errors or external asset requests")
            passed = True
        finally:
            context.close()
            browser.close()
            args.report.parent.mkdir(parents=True, exist_ok=True)
            args.report.write_text(json.dumps({"passed": passed, "checks": checks, "page_errors": failures, "external_requests": unexpected_requests, "scope": "Actual Chromium on disposable local classroom; not all browsers or production qualification."}, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"Passed {len(checks)} browser acceptance groups.")


if __name__ == "__main__":
    main()

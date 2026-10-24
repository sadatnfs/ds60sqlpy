#!/usr/bin/env python3
"""Real Chromium acceptance for a disposable classroom and isolated JS references.

Install requirements/ci-browser.lock only in a CI/developer browser environment,
then run `python -m playwright install --with-deps chromium`. No production image
needs a browser. This script uses real DOM events and network responses, never
mocked classroom APIs. Run it after receipt-persistence checks because it saves
its own learning examples. Reports intentionally exclude tokens and browser traces.
"""

from __future__ import annotations

import argparse
import contextlib
import functools
import importlib
import json
import re
import shutil
import sys
import tempfile
import threading
import uuid
from collections.abc import Iterator
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))
from ds60sqlpy.http_server import LocalThreadingHTTPServer  # noqa: E402
from scripts.check_classroom_profiles import classroom_origin  # noqa: E402

SUBJECTS = {
    "python",
    "sql",
    "bridge",
    "cpp",
    "c",
    "go",
    "csharp",
    "rust",
    "swift",
    "docker",
    "java",
    "javascript-typescript",
    "scala-spark",
    "kubernetes",
    "deep-learning-tensorflow",
    "deep-learning-pytorch",
    "statistics-ml",
    "llm-theory",
    "llm-applied",
    "nlp",
}
NOTE = "Disposable browser acceptance note, not a learner mastery assessment."


def contrast_ratio(foreground: str, background: str) -> float:
    def luminance(value: str) -> float:
        match = re.fullmatch(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)", value)
        if match is None:
            raise ValueError("Expected opaque computed RGB colors for the output console.")
        rgb = [int(channel) / 255 for channel in match.groups()]
        channels = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
        return sum(c * weight for c, weight in zip(channels, (0.2126, 0.7152, 0.0722), strict=True))

    values = sorted((luminance(foreground), luminance(background)))
    return (values[1] + 0.05) / (values[0] + 0.05)


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, format: str, *args: Any) -> None:
        pass


@contextlib.contextmanager
def fixture_server(identity: str, root: Path = ROOT) -> Iterator[str]:
    if identity not in {"js-029", "js-030", "js-031"}:
        raise ValueError("Choose a reviewed browser lesson fixture.")
    source = root / "courses/javascript-typescript/solutions/browser" / identity
    with tempfile.TemporaryDirectory(prefix="ds60-browser-fixture-") as temporary:
        target = Path(temporary)
        # Serve only this fixed reference's regular files on a separate origin.
        for path in source.iterdir():
            if path.is_symlink() or not path.is_file():
                raise ValueError("A browser reference must contain only regular local files.")
            shutil.copyfile(path, target / path.name)
        server = LocalThreadingHTTPServer(
            ("127.0.0.1", 0), functools.partial(QuietHandler, directory=temporary)
        )
        server.daemon_threads = True
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f"http://127.0.0.1:{server.server_port}"
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)
            if thread.is_alive():
                raise RuntimeError("The temporary fixture server did not stop.")


class Audit:
    def __init__(self, screenshots: Path | None = None) -> None:
        self.screenshots = screenshots
        self.checks: list[str] = []
        self.page_errors: list[str] = []
        self.http_errors: list[str] = []
        self.outside_requests: list[str] = []

    def passed(self, name: str) -> None:
        self.checks.append(name)
        print("PASS: " + name, flush=True)

    def screenshot(self, page: Any, name: str) -> None:
        if self.screenshots is not None:
            self.screenshots.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(self.screenshots / (name + ".png")))

    def context(self, browser: Any, origin: str) -> Any:
        context = browser.new_context(
            viewport={"width": 1440, "height": 1000}, service_workers="block"
        )
        context.set_default_timeout(20_000)
        context.on(
            "page",
            lambda page: page.on(
                "pageerror", lambda error: self.page_errors.append(str(error)[:500])
            ),
        )
        context.on(
            "response",
            lambda response: (
                self.http_errors.append(f"HTTP {response.status}: {urlsplit(response.url).path}")
                if response.status >= 400
                else None
            ),
        )

        def route(request: Any) -> None:
            parsed = urlsplit(request.request.url)
            if (
                parsed.scheme in {"http", "https"}
                and f"{parsed.scheme}://{parsed.netloc}" != origin
            ):
                self.outside_requests.append(f"{parsed.scheme}://{parsed.netloc}")
                request.abort()
            else:
                request.continue_()

        context.route("**/*", route)
        return context

    def clean(self) -> None:
        if self.page_errors or self.http_errors or self.outside_requests:
            raise AssertionError(
                json.dumps(
                    {
                        "page_errors": self.page_errors,
                        "http_errors": self.http_errors,
                        "outside_requests": self.outside_requests,
                    }
                )
            )
        self.passed("No uncaught JavaScript exceptions, HTTP failures or external requests")


def lesson_label_pattern(identity: str) -> re.Pattern[str]:
    """Match the metadata child ID without accepting longer IDs or variants."""
    return re.compile(r"^" + re.escape(identity) + r"(?=\s|$)")


def choose_lesson(page: Any, subject: str, identity: str, expect: Any) -> None:
    title = page.locator(f'#subject-select option[value="{subject}"]').text_content()
    assert title, "The requested subject has no visible label."
    page.locator("#subject-select").select_option(subject)
    # The native selection changes before the asynchronous lesson request finishes.
    # Wait for the application's subject label before editing its saved filter.
    expect(page.locator("#subject-label")).to_have_text(title)
    expect(page.locator("#save-state")).to_contain_text("Loaded")
    page.locator("#lesson-query").fill(identity)
    # Title and <small> text concatenate without a DOM separator. The ID belongs
    # to the metadata child, so inspect that child rather than the whole button.
    metadata = page.locator("small").filter(has_text=lesson_label_pattern(identity))
    button = page.locator("#lessons button").filter(has=metadata)
    expect(button).to_have_count(1)
    current_id = page.evaluate("new URLSearchParams(location.hash.slice(1)).get('lesson')")
    if current_id != identity:
        button.click()
    expect(page).to_have_url(
        re.compile(r"[#&]lesson=" + re.escape(quote(identity, safe="")) + r"(?:&|$)")
    )
    expect(page.locator("#authored")).to_be_visible()
    expect(page.locator("#save-state")).to_contain_text("Loaded")


def choose_sql_snippet(page: Any, expect: Any) -> None:
    # Some SQL lessons open their whole-file workspace by default. Choose the
    # snippet workspace explicitly and wait for the async context switch.
    if page.locator("#pad-mode").input_value() != "snippet":
        page.locator("#pad-mode").select_option("snippet")
    expect(page).to_have_url(re.compile(r"[#&]mode=snippet(?:&|$)"))
    expect(page.locator("#pad-mode")).to_have_value("snippet")
    expect(page.locator("#save-state")).to_contain_text("Loaded")


def show_code_and_notes(page: Any, expect: Any) -> None:
    if page.locator("#reading-toggle").get_attribute("aria-pressed") == "true":
        page.locator("#reading-toggle").click()
    expect(page.locator("#authored .practice-pane")).to_be_visible()
    expect(page.locator("#source")).to_be_visible()
    expect(page.locator("#explanation")).to_be_visible()


def save(page: Any, expect: Any) -> None:
    page.locator("#save").click()
    expect(page.locator("#save-state")).to_have_text("Saved in your local learning workspace.")


def no_overflow(page: Any) -> None:
    assert page.evaluate("document.documentElement.scrollWidth <= innerWidth + 1"), (
        "The document overflows the viewport."
    )


def classroom_checks(browser: Any, origin: str, audit: Audit, expect: Any) -> None:
    # Each invocation must observe newly executed output, never a restored receipt.
    nonce = uuid.uuid4().hex
    python_marker = "BROWSER_PYTHON_42_" + nonce
    sql_marker = "BROWSER_SQL_42_" + nonce
    module_marker = "BROWSER_MODULE_42_" + nonce
    python_source = f"print({python_marker!r})\n"
    sql_source = f"SELECT 42 AS answer, '{sql_marker}' AS label;\n"
    module_source = f"print({module_marker!r})\n"
    context = audit.context(browser, origin)
    try:
        page = context.new_page()
        page.goto(origin + "/classroom")
        expect(page.locator("#subject-cards .subject-card")).to_have_count(len(SUBJECTS))
        no_overflow(page)
        audit.screenshot(page, "classroom-home-desktop")
        page.set_viewport_size({"width": 390, "height": 844})
        no_overflow(page)
        expect(page.locator(".pace-card h2")).to_have_text(
            "A little time. A meaningful next step.", use_inner_text=True
        )
        audit.screenshot(page, "classroom-home-mobile")
        page.set_viewport_size({"width": 1440, "height": 1000})
        page.locator("#subject-cards .subject-card").filter(
            has=page.locator("h3").filter(has_text=re.compile(r"^Python and data science$"))
        ).click()
        expect(page.locator("#workspace-view")).to_be_visible()
        subjects = set(
            page.locator("#subject-select option").evaluate_all(
                "nodes => nodes.map(node => node.value)"
            )
        )
        assert subjects == SUBJECTS, "The subject chooser omitted a published path."
        audit.passed(
            f"All {len(SUBJECTS)} subjects are selectable; home fits desktop and narrow viewports"
        )

        choose_lesson(page, "python", "python-02", expect)
        page.locator("#source").fill(python_source)
        page.locator("#phase-note").fill(NOTE)
        save(page, expect)
        page.locator("#run").click()
        expect(page.locator("#output")).to_have_text(python_marker, timeout=90_000)
        expect(page.locator("#job-status")).to_contain_text("Exit 0")
        expect(page.locator("#run-storage-status")).to_contain_text("Saved run")
        for mode in ("light", "dark"):
            if page.locator("body").get_attribute("data-mode") != mode:
                page.locator("#theme-toggle").click()
            colors = page.locator("#output").evaluate(
                "node => { const s=getComputedStyle(node); return [s.color,s.backgroundColor]; }"
            )
            ratio = contrast_ratio(*colors)
            assert ratio >= 4.5, f"Console contrast in {mode} mode is {ratio:.2f}:1."
            expect(page.locator("#output")).to_be_visible()
            body_colors = page.locator("body").evaluate(
                "node => { const s=getComputedStyle(node); return [s.color,s.backgroundColor]; }"
            )
            assert contrast_ratio(*body_colors) >= 4.5, f"Body contrast fails in {mode} mode."
            prose_colors = page.locator("#guide p").first.evaluate(
                "node => [getComputedStyle(node).color, "
                "getComputedStyle(node.closest('.reading-pane')).backgroundColor]"
            )
            assert contrast_ratio(*prose_colors) >= 4.5, (
                f"Lesson prose contrast fails in {mode} mode."
            )
        page.locator("#output").scroll_into_view_if_needed()
        audit.screenshot(page, "classroom-output-dark")
        audit.passed(
            "Fresh Python execution and receipts; readable output and prose in both appearances"
        )

        choose_lesson(page, "sql", "sql-start-02", expect)
        choose_sql_snippet(page, expect)
        page.locator("#source").fill(sql_source)
        save(page, expect)
        page.locator("#run").click()
        expect(page.locator("#sql-results")).to_contain_text(sql_marker, timeout=90_000)
        expect(page.locator("#job-status")).to_contain_text("Exit 0")
        expect(page.locator("#sql-results")).to_contain_text("42")
        choose_lesson(page, "llm-theory", "llm-002", expect)
        show_code_and_notes(page, expect)
        page.locator("#source").fill(module_source)
        page.locator("#explanation").fill(NOTE)
        save(page, expect)
        page.locator("#run").click()
        expect(page.locator("#output")).to_have_text(module_marker, timeout=150_000)
        expect(page.locator("#job-status")).to_contain_text("succeeded", timeout=150_000)
        choose_lesson(page, "python", "python-02", expect)
        expect(page.locator("#source")).to_have_value(python_source)
        expect(page.locator("#phase-note")).to_have_value(NOTE)
        expect(page.locator("#output")).to_have_text(python_marker)
        audit.passed(
            "Python, SQL and module source, notes and results remain isolated across switching"
        )

        choose_lesson(page, "statistics-ml", "statistics-009", expect)
        assert page.locator("#guide math").count() > 0, "The textbook has no rendered MathML."
        assert page.locator("#guide mfrac").count() > 0, "The textbook formula lost its fraction."
        assert page.locator("#guide .highlighted-code [class^='syntax-']").count() > 0, (
            "The code blocks have no syntax tokens."
        )
        box = page.locator("#guide math").first.bounding_box()
        assert box and box["width"] > 0 and box["height"] > 0
        page.locator("#read-chapter").check()
        # Tutorial reading focus deliberately hides the coding/notes pane.
        show_code_and_notes(page, expect)
        page.locator("#explanation").fill(NOTE)
        save(page, expect)
        page.set_viewport_size({"width": 390, "height": 844})
        no_overflow(page)
        page.locator("#guide math").first.scroll_into_view_if_needed()
        audit.screenshot(page, "classroom-math-mobile")
        audit.passed("Textbook renders MathML and syntax colors; chapter fits a narrow viewport")
    finally:
        context.close()

    # A fresh context cannot recover from the earlier browser's localStorage.
    context = audit.context(browser, origin)
    try:
        page = context.new_page()
        page.goto(origin + "/classroom#lesson=statistics-009")
        expect(page.locator("#read-chapter")).to_be_checked()
        show_code_and_notes(page, expect)
        expect(page.locator("#explanation")).to_have_value(NOTE)
        choose_lesson(page, "python", "python-02", expect)
        expect(page.locator("#source")).to_have_value(python_source)
        expect(page.locator("#phase-note")).to_have_value(NOTE)
        expect(page.locator("#output")).to_have_text(python_marker)
        choose_lesson(page, "sql", "sql-start-02", expect)
        choose_sql_snippet(page, expect)
        expect(page.locator("#source")).to_have_value(sql_source)
        expect(page.locator("#sql-results")).to_contain_text(sql_marker)
        choose_lesson(page, "llm-theory", "llm-002", expect)
        expect(page.locator("#source")).to_have_value(module_source)
        expect(page.locator("#explanation")).to_have_value(NOTE)
        expect(page.locator("#output")).to_have_text(module_marker)
        audit.passed("A fresh browser restores server-saved progress, notes, pads and run results")
    finally:
        context.close()


def fixture_checks(browser: Any, audit: Audit, expect: Any) -> None:
    for identity in ("js-029", "js-030", "js-031"):
        with fixture_server(identity) as origin:
            context = audit.context(browser, origin)
            try:
                page = context.new_page()
                page.goto(origin)
                if identity == "js-029":
                    page.keyboard.press("Tab")
                    expect(page.locator("#add")).to_be_focused()
                    page.keyboard.press("Enter")
                    page.keyboard.press("Space")
                    expect(page.locator("#count")).to_have_text("Count: 2")
                    page.locator("#list span").click()
                    expect(page.locator("#selection")).to_contain_text(
                        "target SPAN; currentTarget UL"
                    )
                    page.locator("#append").click()
                    page.get_by_role("button", name="Choose B", exact=True).click()
                    expect(page.locator("#selection")).to_contain_text("Selected B")
                    page.locator("#toggle").click()
                    expect(page.locator("#toggle")).to_have_attribute("aria-expanded", "true")
                    expect(page.locator("#toggle")).to_be_focused()
                    expect(page.locator("#details")).to_be_visible()
                    page.locator("#tracked").click()
                    page.locator("#stop").click()
                    page.locator("#tracked").click()
                    expect(page.locator("#tracked-count")).to_have_text("Tracked: 1")
                    page.locator("#diagnose").click()
                    expect(page.locator("#diagnosis")).to_have_text("Required element not found")
                elif identity == "js-030":
                    page.evaluate("localStorage.setItem('unrelated-fixture-key', 'preserve')")
                    page.locator("#name").fill("First draft")
                    page.locator("#quantity").fill("3")
                    page.get_by_role("button", name="Validate and save").click()
                    expect(page.locator("#status")).to_have_text("Accepted and saved")
                    other = context.new_page()
                    other.goto(origin)
                    expect(other.locator("#name")).to_have_value("First draft")
                    other.locator("#name").fill("Unsaved second tab")
                    page.locator("#name").fill("Updated first tab")
                    page.get_by_role("button", name="Validate and save").click()
                    expect(other.locator("#external")).to_contain_text("changed in another tab")
                    expect(other.locator("#name")).to_have_value("Unsaved second tab")
                    other.locator("#reload").click()
                    expect(other.locator("#name")).to_have_value("Updated first tab")
                    page.locator("#corrupt").click()
                    page.locator("#reload").click()
                    expect(page.locator("#status")).to_contain_text("Cannot load saved draft")
                    page.locator("#reset").click()
                    assert (
                        page.evaluate("localStorage.getItem('unrelated-fixture-key')") == "preserve"
                    )
                    assert page.evaluate("localStorage.getItem('ds60-js030-draft-v1')") is None
                else:
                    page.locator("#text").fill('<img src=x onerror="window.unexpected = true">')
                    page.locator("#render").click()
                    expect(page.locator("#count")).to_have_text(
                        "Child elements: 0; image elements: 0"
                    )
                    assert page.evaluate("window.unexpected") is None
                    for target in (
                        "https://example.invalid/",
                        "javascript:alert(1)",
                        origin.replace("//", "//user:password@") + "/",
                    ):
                        page.locator("#url").fill(target)
                        page.locator("#check").click()
                        expect(page.locator("#url-status")).to_contain_text("Rejected:")
                        expect(page.locator("#link a")).to_have_count(0)
                    page.locator("#url").fill("./help.html")
                    page.locator("#check").click()
                    expect(page.locator("#link a")).to_have_attribute("href", origin + "/help.html")
                    # Observe browser CSP enforcement, not merely the meta tag text.
                    page.evaluate(
                        """() => {
                            window.cspBlocked = false;
                            document.addEventListener('securitypolicyviolation', event => {
                                if (event.violatedDirective.startsWith('script-src')) {
                                    window.cspBlocked = true;
                                    document.body.dataset.cspBlocked = "true";
                                }
                            });
                            const script = document.createElement('script');
                            script.textContent = 'window.inlineExecuted = true';
                            document.body.append(script);
                        }"""
                    )
                    expect(page.locator("body")).to_have_attribute("data-csp-blocked", "true")
                    assert page.evaluate("window.inlineExecuted") is None
                audit.passed(
                    identity + " completed reference passes real browser interaction checks"
                )
            finally:
                context.close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--confirm-disposable", action="store_true")
    parser.add_argument("--fixtures-only", action="store_true")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args(argv)
    if not args.fixtures_only and (not args.url or not args.confirm_disposable):
        parser.error("Classroom acceptance saves test work. Supply --url and --confirm-disposable.")
    origin = classroom_origin(args.url) if args.url else None
    api = importlib.import_module("playwright.sync_api")
    audit = Audit(args.report.parent / "browser-screenshots")
    complete = False
    browser_version = "unavailable"
    try:
        with api.sync_playwright() as playwright:
            # Use the supported full Chromium headless mode for real rendering.
            # https://playwright.dev/python/docs/browsers#chromium-new-headless-mode
            browser = playwright.chromium.launch(headless=True, channel="chromium")
            browser_version = browser.version
            try:
                if origin is not None and not args.fixtures_only:
                    classroom_checks(browser, origin, audit, api.expect)
                fixture_checks(browser, audit, api.expect)
                audit.clean()
                complete = True
            finally:
                browser.close()
    finally:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "complete": complete,
                    "browser": "Chromium",
                    "browser_version": browser_version,
                    "scope": "fixtures" if args.fixtures_only else "classroom-and-fixtures",
                    "checks": audit.checks,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

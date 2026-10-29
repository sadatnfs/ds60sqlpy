"""Actual browser qualification for three explicit owned loopback service origins."""

from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import expect, sync_playwright


def origin(value):
    parsed = urlsplit(value)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port is None
        or parsed.path not in {"", "/"}
        or parsed.query
        or parsed.fragment
        or parsed.username
        or parsed.password
    ):
        raise ValueError("Use the exact owned loopback HTTP origin with an explicit port")
    return value.rstrip("/")


def qualify(urls, output):
    output.mkdir(parents=True, exist_ok=True)
    observations = []
    with sync_playwright() as toolkit:
        browser = toolkit.chromium.launch(headless=True)
        try:
            for framework, url in urls.items():
                context = browser.new_context(viewport={"width": 1280, "height": 1100})
                page = context.new_page()
                external, errors = [], []
                allowed = {url, url.replace("http://", "ws://", 1)}

                def observe(request, allowed=allowed, external=external):
                    parsed = urlsplit(request.url)
                    request_origin = f"{parsed.scheme}://{parsed.netloc}"
                    if request_origin not in allowed:
                        external.append(request.url)

                page.on("request", observe)
                page.on("pageerror", lambda error, errors=errors: errors.append(str(error)))
                page.goto(url, wait_until="networkidle")
                expect(page.locator("#framework")).to_contain_text(framework)
                page.get_by_label("Username", exact=True).fill("alice")
                page.get_by_label("Password", exact=True).fill("classroom-demo")
                page.get_by_role("button", name="Sign in", exact=True).click()
                expect(page.locator("#identity")).to_have_text("Signed in as alice.")
                title = f"Browser {framework} {time.time_ns()}"
                page.get_by_label("Note title", exact=True).fill(title)
                page.get_by_role("button", name="Create note", exact=True).click()
                expect(page.locator("#notes")).to_contain_text(title)
                page.reload(wait_until="networkidle")
                expect(page.locator("#notes")).to_contain_text(title)
                page.get_by_role("button", name="Sign out", exact=True).click()
                expect(page.locator("#identity")).to_have_text("Signed out.")
                page.get_by_label("Username", exact=True).fill("bob")
                page.get_by_role("button", name="Sign in", exact=True).click()
                expect(page.locator("#identity")).to_have_text("Signed in as bob.")
                expect(page.locator("#notes")).not_to_contain_text(title)
                checks = ["real-login-note-reload", "browser-owner-switch", "local-css-js"]
                if framework == "FastAPI":
                    page.get_by_role("link", name="Local API explorer").click()
                    expect(page.locator("#operations")).to_contain_text("/api/notes")
                    page.get_by_role("button", name="Run selected request").click()
                    expect(page.locator("#result")).to_contain_text("HTTP 200")
                    page.get_by_label("Operation", exact=True).select_option("create")
                    page.get_by_role("button", name="Run selected request").click()
                    expect(page.locator("#result")).to_contain_text("HTTP 201")
                    page.get_by_role("link", name="Workshop", exact=True).click()
                    expect(page.locator("#identity")).to_have_text("Signed in as bob.")
                    page.get_by_role("button", name="Create held job: 2 + 3 + 5").click()
                    expect(page.locator("#events")).to_contain_text("queued")
                    page.get_by_role("button", name="Disconnect stream", exact=True).click()
                    expect(page.locator("#job-state")).to_contain_text("deliberately disconnected")
                    page.get_by_role("button", name="Release job", exact=True).click()
                    page.get_by_role("button", name="Reconnect stream", exact=True).click()
                    expect(page.locator("#job-state")).to_contain_text("finished", timeout=20000)
                    expect(page.locator("#events")).to_contain_text("result 10")
                    page.reload(wait_until="domcontentloaded")
                    expect(page.locator("#job-state")).to_contain_text("finished", timeout=15000)
                    page.get_by_role("button", name="Check WebSocket echo", exact=True).click()
                    expect(page.locator("#output")).to_contain_text("Local WebSocket")
                    checks.extend(
                        [
                            "offline-interactive-openapi",
                            "browser-sse-disconnect-reconnect",
                            "saved-job-reload",
                            "browser-websocket",
                        ]
                    )
                if framework == "Django":
                    page.get_by_role("link", name="Django admin", exact=True).click()
                    expect(page.get_by_label("Username:", exact=True)).to_be_visible()
                    page.get_by_label("Username:", exact=True).fill("operator")
                    page.get_by_label("Password:", exact=True).fill("local-admin-demo")
                    page.get_by_role("button", name="Log in", exact=True).click()
                    expect(
                        page.locator("#notes-note").get_by_role("link", name="Notes", exact=True)
                    ).to_be_visible()
                    checks.append("actual-admin-and-collected-assets")
                    page.goto(url, wait_until="networkidle")
                page.screenshot(
                    path=str(output / (framework.lower() + "-light.png")), full_page=True
                )
                page.emulate_media(color_scheme="dark")
                page.screenshot(
                    path=str(output / (framework.lower() + "-dark.png")), full_page=True
                )
                assert not external, external
                assert not errors, errors
                observations.append(
                    {
                        "framework": framework,
                        "checks": checks,
                        "external_requests": [],
                        "page_errors": [],
                    }
                )
                context.close()
        finally:
            browser.close()
    files = {
        str(path.relative_to(Path(__file__).parent)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted((Path(__file__).parent / "static").glob("*"))
        if path.is_file()
    }
    return {
        "schema_version": 1,
        "status": "passed",
        "observations": observations,
        "asset_sha256": files,
        "scope": "actual local Chromium HTTP/WS/SSE; no public TLS claim",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for framework in ("flask", "fastapi", "django"):
        parser.add_argument("--" + framework, required=True, type=origin)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    urls = {"Flask": args.flask, "FastAPI": args.fastapi, "Django": args.django}
    assert len(set(urls.values())) == 3, "Use distinct owned origins"
    result = qualify(urls, args.output)
    (args.output / "browser-acceptance.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()

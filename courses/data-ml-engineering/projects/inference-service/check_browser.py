"""Actual Chromium gate for the explicit disposable inference workshop URL."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from playwright.sync_api import Route, expect, sync_playwright


def qualify(url: str, directory: Path, persisted: dict[str, Any] | None = None) -> dict[str, Any]:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "http"
        or parsed.hostname != "127.0.0.1"
        or parsed.port is None
        or parsed.path not in {"", "/"}
    ):
        raise ValueError("Use the explicit disposable workshop's loopback origin")
    url = url.rstrip("/")
    directory.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as toolkit:
        browser = toolkit.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1440, "height": 1100}, accept_downloads=True
        )
        page = context.new_page()
        external: list[str] = []
        errors: list[str] = []
        page.on(
            "request",
            lambda request: (
                external.append(request.url) if not request.url.startswith(url + "/") else None
            ),
        )
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url, wait_until="networkidle")
        token = page.locator("meta[name=workshop-token]").get_attribute("content")
        assert token is not None
        headers = {"X-Workshop-Token": token}
        initial = context.request.get(url + "/api/status", headers=headers).json()
        reconciled = False
        if persisted is None:
            accepted_identity: list[str] = []

            def uncertain_creation(route: Route) -> None:
                if route.request.method != "POST":
                    route.continue_()
                    return
                accepted = route.fetch()
                assert accepted.status == 202
                accepted_identity.append(accepted.json()["id"])
                accepted.dispose()
                # Deliberately simulate a proxy error after real server admission.
                route.fulfill(status=503, json={"error": "Synthetic lost admission response"})

            page.route("**/api/requests", uncertain_creation)
            page.get_by_role("button", name="Create and stream", exact=True).click()
            expect(page.locator("#request-status")).to_contain_text("outcome is unknown")
            page.unroute("**/api/requests", uncertain_creation)
            page.reload(wait_until="networkidle")
            expect(page.locator("#request-status")).to_contain_text("No request has been replayed")
            not_replayed = context.request.get(url + "/api/status", headers=headers).json()
            assert not_replayed["generation_calls"] == initial["generation_calls"]
            assert len(accepted_identity) == 1
            page.get_by_role("button", name="Create and stream", exact=True).click()
            expect(page.locator("#request-status")).to_have_text(
                re.compile(r"^completed:"), timeout=30000
            )
            identity = page.locator("#request-id").inner_text()
            assert identity == accepted_identity[0]
            reconciled = True
        else:
            identity = persisted["id"]
            row = page.locator(".history-row").filter(has_text=identity)
            row.get_by_role("button", name="Read events", exact=True).click()
            expect(page.locator("#readback")).to_be_enabled()
            assert page.locator("#request-id").inner_text() == identity
        before = context.request.get(url + "/api/status", headers=headers).json()
        response = context.request.get(url + "/api/requests/" + identity, headers=headers)
        assert response.ok
        raw = response.body()
        digest = hashlib.sha256(raw).hexdigest()
        if persisted is not None:
            assert digest == persisted["receipt_sha256"]
            assert before["generation_calls"] == initial["generation_calls"]
        with page.expect_download() as download:
            page.get_by_role("button", name="Download exact record", exact=True).click()
        output = directory / "browser-download.json"
        download.value.save_as(output)
        assert output.read_bytes() == raw
        page.get_by_role("button", name="Read saved events", exact=True).click()
        expect(page.locator("#readback")).to_be_enabled()
        after = context.request.get(url + "/api/status", headers=headers).json()
        assert after["generation_calls"] == before["generation_calls"]
        page.screenshot(path=str(directory / "desktop.png"), full_page=True)
        page.emulate_media(color_scheme="dark")
        page.screenshot(path=str(directory / "dark.png"), full_page=True)
        page.set_viewport_size({"width": 390, "height": 844})
        page.locator("#output").scroll_into_view_if_needed()
        assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
        page.screenshot(path=str(directory / "mobile.png"), full_page=True)
        assert not external, external
        assert not errors, errors
        result = {
            "id": identity,
            "receipt_sha256": digest,
            "model_sha256": before["model_sha256"],
            "generation_calls_unchanged": after["generation_calls"],
            "external_requests": external,
            "page_errors": errors,
            "download_exact": True,
            "mobile_no_horizontal_overflow": True,
            "read_only": persisted is not None,
            "unknown_creation_reconciled": reconciled,
        }
        browser.close()
        return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--verify-persisted", type=Path)
    args = parser.parse_args()
    prior = json.loads(args.verify_persisted.read_text()) if args.verify_persisted else None
    result = qualify(args.url, args.output, prior)
    (args.output / "browser.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

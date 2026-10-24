"""Unit checks for the browser probe's math and isolated fixture lifecycle.

These do not replace its real Chromium CI run.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import ProxyHandler, build_opener

import pytest

from scripts import check_classroom_browser as browser


def test_contrast_uses_srgb_linearization_and_detects_dark_on_dark() -> None:
    assert browser.contrast_ratio("rgb(255, 255, 255)", "rgb(0, 0, 0)") == 21
    assert browser.contrast_ratio("rgb(34, 36, 43)", "rgb(17, 29, 50)") < 1.2
    assert browser.contrast_ratio("rgb(232, 239, 255)", "rgb(17, 29, 50)") > 14
    assert browser.contrast_ratio("rgb(255, 255, 255)", "rgb(118, 118, 118)") > 4.5
    assert browser.contrast_ratio("rgb(255, 255, 255)", "rgb(119, 119, 119)") < 4.5


@pytest.mark.parametrize("color", ["transparent", "rgba(255, 255, 255, 0.2)", "#ffffff"])
def test_unproved_composite_colors_do_not_pass_the_contrast_gate(color: str) -> None:
    with pytest.raises(ValueError, match="opaque computed RGB"):
        browser.contrast_ratio(color, "rgb(0, 0, 0)")


def test_browser_chooser_baseline_matches_the_current_catalog_sources() -> None:
    root = Path(__file__).resolve().parents[1]
    legacy = json.loads((root / "curriculum/catalog.json").read_text())["tracks"]
    modules = {
        json.loads(path.read_text())["track_id"]
        for path in (root / "courses").glob("*/lessons.json")
    }
    assert set(legacy) | modules | {"statistics-ml"} == browser.SUBJECTS


@pytest.mark.parametrize("identity", ["js-029", "js-030", "js-031"])
def test_fixture_http_server_exposes_only_its_copy_and_closes(identity: str) -> None:
    opener = build_opener(ProxyHandler({}))
    with browser.fixture_server(identity) as origin:
        assert origin.startswith("http://127.0.0.1:")
        with opener.open(origin + "/", timeout=3) as response:
            assert identity.encode() in response.read()
        with opener.open(origin + "/app.js", timeout=3) as response:
            assert response.status == 200 and response.read()
        with pytest.raises(HTTPError) as error:
            opener.open(origin + "/AGENTS.md", timeout=3)
        assert error.value.code == 404
    with pytest.raises(URLError):
        opener.open(origin + "/", timeout=3)


def test_fixture_server_rejects_unreviewed_paths_before_starting() -> None:
    with (
        pytest.raises(ValueError, match="reviewed browser lesson"),
        browser.fixture_server("../private"),
    ):
        pytest.fail("No server should start for an unreviewed fixture.")


def test_live_browser_gate_refuses_missing_disposable_authorization_without_importing_browser() -> (
    None
):
    with pytest.raises(SystemExit) as error:
        browser.main(["--url", "http://127.0.0.1:8765/classroom", "--report", "unused.json"])
    assert error.value.code == 2


@pytest.mark.parametrize(
    "identity,label,expected",
    [
        ("python-02", "python-02 · beginner · ~2 sessions", True),
        ("python-02", "python-02 · Demonstrated · beginner", True),
        ("python-02", "python-02", True),
        ("python-02", "python-020 · beginner", False),
        ("python-02", "python-02-extra · beginner", False),
        ("python-02", "python-02@variant · beginner", False),
        ("python-02", "A title mentioning python-02", False),
        ("spark-013@pyspark", "spark-013@pyspark · intermediate", True),
    ],
)
def test_lesson_metadata_selector_matches_only_a_complete_leading_id(
    identity: str, label: str, expected: bool
) -> None:
    assert bool(browser.lesson_label_pattern(identity).search(label)) is expected

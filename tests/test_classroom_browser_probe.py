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
from scripts import check_classroom_workspace as workspace


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
    assert {"cuda", "web-development", "jax", "r", "dax", "data-visualization"} <= modules
    assert set(legacy) | modules | {"statistics-ml"} == browser.SUBJECTS


def test_browser_expectations_include_newly_admitted_subjects(tmp_path: Path) -> None:
    (tmp_path / "curriculum").mkdir()
    (tmp_path / "curriculum/catalog.json").write_text(json.dumps({"tracks": {"python": {}}}))
    subject = tmp_path / "courses/new-subject"
    subject.mkdir(parents=True)
    (subject / "lessons.json").write_text(json.dumps({"track_id": "new-subject"}))
    assert browser.published_subjects(tmp_path) == {"python", "new-subject"}


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


FIXTURE_INDEX = {
    "tracks": [
        {
            "id": "python",
            "lessons": [
                {
                    "id": "python-02",
                    "engine": "legacy",
                    "status": "authored",
                    "runtime_profile": "python",
                },
                {
                    "id": "python-01",
                    "engine": "legacy",
                    "status": "authored",
                    "runtime_profile": "python",
                },
            ],
        },
        {
            "id": "sql",
            "lessons": [
                {
                    "id": "sql-start-02",
                    "engine": "legacy",
                    "status": "authored",
                    "runtime_profile": "sql",
                },
            ],
        },
        {
            "id": "mixed",
            "lessons": [
                {
                    "id": "mod-b",
                    "engine": "module",
                    "status": "authored",
                    "runtime_profile": "python-core",
                },
                {
                    "id": "mod-a",
                    "engine": "module",
                    "status": "authored",
                    "runtime_profile": "python-core",
                },
                {
                    "id": "mod-r",
                    "engine": "module",
                    "status": "authored",
                    "runtime_profile": "r-statistics",
                },
                {
                    "id": "mod-read",
                    "engine": "module",
                    "status": "authored",
                    "runtime_profile": "reading",
                },
                {
                    "id": "mod-dax",
                    "engine": "module",
                    "status": "authored",
                    "runtime_profile": "dax-offline",
                },
                {
                    "id": "mod-web",
                    "engine": "module",
                    "status": "authored",
                    "runtime_profile": "html-browser",
                },
                {
                    "id": "mod-0-planned",
                    "engine": "module",
                    "status": "planned",
                    "runtime_profile": "reading",
                },
            ],
        },
    ]
}


def test_axe_findings_split_serious_and_critical_from_recorded() -> None:
    blocking, recorded = workspace.classify_axe(
        {
            "violations": [
                {"id": "x", "impact": "serious", "nodes": [{"target": ["#a"]}]},
                {"id": "y", "impact": "minor", "nodes": [{"target": ["#b"]}, {}]},
                {"id": "z", "impact": "critical", "nodes": []},
                {"id": "w", "impact": None, "nodes": [{"target": ["iframe", "#c"]}]},
            ]
        }
    )
    assert [item["id"] for item in blocking] == ["x", "z"]
    assert recorded == [
        {"id": "y", "impact": "minor", "nodes": 2, "targets": ["#b", ""]},
        {"id": "w", "impact": None, "nodes": 1, "targets": ["iframe #c"]},
    ]
    many = {"violations": [{"id": "m", "impact": "serious", "nodes": [{}] * 9}]}
    assert len(workspace.classify_axe(many)[0][0]["targets"]) == workspace.AXE_TARGET_LIMIT
    assert workspace.classify_axe({}) == ([], [])


def test_mode_samples_pick_the_first_authored_lesson_per_present_mode() -> None:
    assert workspace.choose_mode_samples(FIXTURE_INDEX) == {
        "legacy-python": "python-01",
        "sql-snippet": "sql-start-02",
        "sql-lesson": "sql-start-02",
        "module-ready": "mod-a",
        "module-not-ready": "mod-r",
        "module-reading": "mod-read",
        "dax-offline": "mod-dax",
        "browser-preview": "mod-web",
    }
    only_python = {"tracks": [FIXTURE_INDEX["tracks"][0]]}
    assert workspace.choose_mode_samples(only_python) == {"legacy-python": "python-01"}
    assert workspace.choose_mode_samples({"tracks": []}) == {}
    assert workspace.track_of(FIXTURE_INDEX, "mod-dax") == "mixed"


def test_ready_profiles_decide_module_ready_and_not_ready_samples() -> None:
    samples = workspace.choose_mode_samples(FIXTURE_INDEX, frozenset({"r-statistics"}))
    assert samples["module-ready"] == "mod-r"
    assert samples["module-not-ready"] == "mod-a"


@pytest.mark.parametrize(
    "style,expected",
    [
        ({"outlineStyle": "solid", "outlineWidth": "2px", "boxShadow": "none"}, True),
        ({"outlineStyle": "solid", "outlineWidth": "1px", "boxShadow": "none"}, False),
        ({"outlineStyle": "none", "outlineWidth": "0px", "boxShadow": "none"}, False),
        (
            {
                "outlineStyle": "none",
                "outlineWidth": "0px",
                "boxShadow": "rgb(47, 63, 179) 0px -2px 0px 0px inset",
            },
            True,
        ),
        ({"outlineStyle": "auto", "outlineWidth": "2.5px", "boxShadow": ""}, True),
        ({"outlineStyle": "hidden", "outlineWidth": "3px", "boxShadow": "none"}, False),
    ],
)
def test_focus_cue_requires_a_two_pixel_outline_or_a_shadow(
    style: dict[str, str], expected: bool
) -> None:
    assert workspace.focus_cue_ok(style) is expected


def test_expected_strip_copy_matches_each_mode() -> None:
    assert workspace.expected_strip("module-reading", "reading") == {
        "label": "Reading lesson",
        "run": "Reading and reasoning",
        "runs_in": "No code runs in this lesson.",
        "results_visible": False,
    }
    assert workspace.expected_strip("dax-offline", "dax-offline")["run"] is None
    assert workspace.expected_strip("module-not-ready", "go")["runs_in"] == (
        "The go worker container on this computer"
    )
    assert workspace.expected_strip("sql-lesson", "sql")["runs_in"] == (
        "PostgreSQL in your local classroom"
    )
    assert workspace.expected_strip("browser-preview", "html-browser")["run"] == (
        "Run browser preview"
    )


def test_module_actions_normalize_to_execution_names() -> None:
    assert workspace.normalized_action("/api/modules", "module-run") == "run"
    assert workspace.normalized_action("/api/modules", "module-walkthrough") == "walkthrough"
    assert workspace.normalized_action("/api/lab", "step-through") == "step-through"
    assert workspace.normalized_action("/api/classroom", "classroom-history") == (
        "classroom:classroom-history"
    )


@pytest.mark.parametrize(
    "extra",
    [["--restart-stage", "rewind"], ["--fixtures-only", "--restart-stage", "write"]],
)
def test_restart_stage_options_are_validated_before_importing_browser(extra: list[str]) -> None:
    with pytest.raises(SystemExit) as error:
        browser.main(
            [
                "--url",
                "http://127.0.0.1:8765/classroom",
                "--confirm-disposable",
                "--report",
                "unused.json",
                *extra,
            ]
        )
    assert error.value.code == 2


class _AxeAudit:
    def __init__(self, axe: object) -> None:
        self.workspace = {"axe": axe}
        self.checks: list[str] = []

    def passed(self, name: str) -> None:
        self.checks.append(name)


def test_axe_gate_fails_only_on_recorded_blocking_findings() -> None:
    skipped = _AxeAudit({"skipped": "no --axe-script"})
    workspace.assert_axe_clean(skipped)
    assert skipped.checks == []
    clean = _AxeAudit({"pages": ["home:light", "home:dark"], "blocking": []})
    workspace.assert_axe_clean(clean)
    assert clean.checks == ["axe-core 4.14.1: no serious or critical findings on 2 scans"]
    dirty = _AxeAudit({"pages": ["home:dark"], "blocking": [{"id": "color-contrast"}]})
    with pytest.raises(AssertionError, match="color-contrast"):
        workspace.assert_axe_clean(dirty)

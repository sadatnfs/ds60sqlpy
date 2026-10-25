"""Web curriculum admission, safe rendering and isolated saved-browser boundaries."""

from __future__ import annotations

import importlib.util
import json
from html.parser import HTMLParser
from pathlib import Path

import pytest

from ds60sqlpy.browser_runs import BrowserRunStore
from ds60sqlpy.lesson_reader import render_artifact
from ds60sqlpy.modules import ModuleCatalog, ModuleState
from ds60sqlpy.worker_operations import validate_operation

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "courses/web-development"


@pytest.fixture(scope="module")
def catalog() -> ModuleCatalog:
    return ModuleCatalog(ROOT)


class Structure(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.nodes: list[tuple[str, dict[str, str | None]]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.nodes.append((tag, dict(attrs)))


def test_complete_web_route_uses_real_runtime_boundaries(catalog: ModuleCatalog) -> None:
    lessons = [catalog.get(f"web-{number:03d}") for number in range(1, 61)]
    assert {item.runtime_profile for item in lessons[:30]} == {"html-browser"}
    assert {item.runtime_profile for item in lessons[30:56]} == {"php-cli"}
    assert {item.runtime_profile for item in lessons[56:]} == {"reading"}
    assert all(item.verification_id is None for item in lessons)
    # A newcomer can enter PHP after page/form basics, without completing advanced JS.
    assert catalog.planned["web-031"]["prerequisites"] == ["web-001", "web-009"]
    assert "js-029" in catalog.planned["web-025"]["prerequisites"]


def test_authoring_regeneration_is_exact_and_does_not_invoke_runtimes() -> None:
    path = COURSE / "authoring/build.py"
    specification = importlib.util.spec_from_file_location("web_authoring_test", path)
    assert specification and specification.loader
    module = importlib.util.module_from_spec(specification)
    specification.loader.exec_module(module)
    generated = module.artifacts()
    assert generated
    for path, expected in generated.items():
        assert path.read_text(encoding="utf-8") == expected, path.relative_to(ROOT)
    assert all(path.is_relative_to(COURSE) for path in generated)


@pytest.mark.parametrize("number", range(1, 31))
def test_html_references_have_connected_semantics_and_no_external_dependencies(number: int) -> None:
    source = (COURSE / f"solutions/web-{number:03d}_solution.html").read_text(encoding="utf-8")
    structure = Structure()
    structure.feed(source)
    ids = [attrs["id"] for _, attrs in structure.nodes if "id" in attrs]
    assert len(ids) == len(set(ids)), "Duplicate identifiers break labels and fragments"
    assert sum(tag == "main" for tag, _ in structure.nodes) == 1
    assert any(tag == "html" and attrs.get("lang") == "en" for tag, attrs in structure.nodes)
    for tag, attrs in structure.nodes:
        if tag == "script":
            assert "src" not in attrs, "Offline references cannot fetch scripts"
        if tag in {"img", "iframe", "link", "audio", "video", "source"}:
            assert not attrs.get("src") and not attrs.get("href"), "Unexpected external asset"
        if tag == "label" and attrs.get("for"):
            assert attrs["for"] in ids
        for attribute in ("aria-labelledby", "aria-describedby"):
            if attrs.get(attribute):
                assert set(str(attrs[attribute]).split()) <= set(ids)
        if tag == "a" and str(attrs.get("href", "")).startswith("#"):
            assert str(attrs["href"])[1:] in ids
    assert f"web-{number:03d} reference checks passed" in source


@pytest.mark.parametrize("number,suffix,language", [(29, "html", "html"), (45, "php", "php")])
def test_reference_reader_displays_source_without_executing_it(
    number: int, suffix: str, language: str
) -> None:
    rendered = render_artifact(
        COURSE / f"solutions/web-{number:03d}_solution.{suffix}",
        repo_root=ROOT,
        targets={},
    )
    assert f"language-{language}" in rendered
    assert "This page does not execute source code" in rendered
    structure = Structure()
    structure.feed(rendered)
    assert not any(tag in {"script", "img", "iframe"} for tag, _ in structure.nodes)


def test_html_draft_and_observation_survive_reload_without_cross_language_overwrite(
    tmp_path: Path, catalog: ModuleCatalog
) -> None:
    state = ModuleState(catalog, tmp_path / "modules")
    original = "<!doctype html><html><body><p>Original</p></body></html>"
    newest = "<!doctype html><html><body><p>Unsuperseded newer draft</p></body></html>"
    php_source = '<?php echo "Separate PHP pad";\n'
    state.save("web-025", {"source": original, "prediction": "One original paragraph"})
    store = BrowserRunStore(state)
    receipt = store.record(
        "web-025",
        {
            "source": original,
            "output": "Observed original",
            "status": "succeeded",
            "elapsed_seconds": 0.1,
        },
    )
    state.save("web-025", {"source": newest})
    state.save("web-031", {"source": php_source})
    reloaded = ModuleState(catalog, state.directory)
    historical = BrowserRunStore(reloaded).get("web-025", receipt["job_id"])
    assert historical["source"] == original
    assert historical["profile"] == "html-browser"
    assert historical["language"] == "html"
    assert historical["library"] == "html-css-dom"
    assert historical["verified"] is False
    assert historical["returncode"] is None
    assert reloaded.read("web-025")["source"] == newest
    assert reloaded.read("web-031")["source"] == php_source
    assert reloaded.read("web-026") == {}


def test_php_cannot_receive_browser_observations_or_forged_verifiers(
    tmp_path: Path, catalog: ModuleCatalog
) -> None:
    store = BrowserRunStore(ModuleState(catalog, tmp_path / "modules"))
    with pytest.raises(ValueError, match="browser lesson"):
        store.record(
            "web-031",
            {
                "source": "<?php echo 1;",
                "output": "1",
                "status": "succeeded",
                "elapsed_seconds": 0.1,
            },
        )
    validate_operation("php-cli", "php", None)
    with pytest.raises(ValueError):
        validate_operation("php-cli", "php", "cpp-ownership-v1")
    with pytest.raises(ValueError):
        validate_operation("php-cli", "html", None)


def test_server_models_and_optional_lab_do_not_claim_http_execution_from_cli() -> None:
    manifest = json.loads((COURSE / "lessons.json").read_text(encoding="utf-8"))
    for number in (46, 47, 48, 49, 54):
        row = manifest["lessons"][number - 1]
        guide = (ROOT / row["guide_path"]).read_text(encoding="utf-8")
        assert row["runtime_profile"] == "php-cli"
        assert "CLI" in guide and "synthetic" in guide
        assert "not persistent HTTP requests" in guide
    fixture = COURSE / "fixtures/php-http-lab"
    readme = (fixture / "README.md").read_text(encoding="utf-8")
    assert "anonymous session ownership" in readme
    assert "127.0.0.1:18088" in readme
    compose = (fixture / "compose.yaml").read_text(encoding="utf-8")
    assert "127.0.0.1:18088:8080" in compose
    assert "docker.sock" not in compose

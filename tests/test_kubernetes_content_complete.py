"""Complete Kubernetes teaching contracts, separate from any live cluster qualification."""

from __future__ import annotations

import ast
import hashlib
import json
import re
import runpy
import shutil
import socket
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

from ds60sqlpy.kubernetes_module import KubernetesRefusal, parse_manifests

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "courses/kubernetes"
PLAN = json.loads((ROOT / "docs/expansion/plans/kubernetes.json").read_text())["lessons"]
RECORDS = json.loads((BASE / "lessons.json").read_text())["lessons"]
ADDED = [x for x in RECORDS if x["id"] not in {"k8s-001", "k8s-002", "k8s-003", "k8s-008"}]


def test_full_planned_sequence_and_prerequisites() -> None:
    assert [x["id"] for x in RECORDS] == [x["id"] for x in PLAN]
    assert len(RECORDS) == 42
    for record, planned in zip(RECORDS, PLAN, strict=True):
        guide = (ROOT / record["guide_path"]).read_text()
        assert all(f"`{prerequisite}`" in guide for prerequisite in planned["prerequisites"])
        for relative in [record["guide_path"], record["source_path"], *record["solution_paths"]]:
            path = ROOT / relative
            assert path.is_file()
            assert "\u2014" not in path.read_text()
        assert record["status"] == "authored"


@pytest.mark.parametrize("record", ADDED, ids=lambda x: x["id"])
def test_added_lesson_has_substantive_separate_contracts(record: dict[str, Any]) -> None:
    key = record["id"]
    guide = (ROOT / record["guide_path"]).read_text()
    learner = (ROOT / record["source_path"]).read_text()
    explanation = (BASE / f"solutions/{key}_solutions.md").read_text()
    ledger = json.loads((BASE / f"fixtures/{key}-cases.json").read_text())
    assert re.findall(r"^### Exercise (\d):", guide, re.M) == list("123456")
    assert re.findall(r"^## Exercise (\d):", explanation, re.M) == list("123456")
    assert len(re.findall(r"^### Worked example \d:", guide, re.M)) >= 2
    assert len({x["task"] for x in ledger["cases"]}) == 6
    assert len({x["expected"] for x in ledger["cases"]}) == 6
    assert "synthetic" in ledger["provenance"]
    assert all(f"Exercise {n}:" in learner for n in range(1, 7))
    assert "no API calls" in guide
    assert "LAB_KUBECONFIG" in guide and "LAB_CONTEXT" in guide and "LAB_NAMESPACE" in guide
    assert "```powershell" in guide and "```sh" in guide
    assert guide.rfind("## Ask an AI tutor about this lesson") > guide.rfind("## Next step")
    assert record["guide_path"] in guide and record["source_path"] in guide
    assert len(explanation.split()) >= 450
    if record["runtime_profile"] == "k8s-kind":
        assert record["language"] == "yaml"
        parse_manifests(learner)
        parse_manifests((BASE / f"solutions/{key}_solution.yaml").read_text())
    else:
        assert record["runtime_profile"] == "reading" and record["language"] == "markdown"
        assert "does not provide the full" in guide
        manifest = json.loads((BASE / f"solutions/{key}_solution.json").read_text())
        assert manifest["apiVersion"] == "v1" and manifest["kind"] == "List"
        assert manifest["items"]
        for obj in manifest["items"]:
            assert obj["apiVersion"] and obj["kind"] and obj["metadata"]["name"]
            assert "namespace" not in obj["metadata"]
            assert "status" not in obj


@pytest.mark.parametrize("record", ADDED, ids=lambda x: x["id"])
def test_every_added_reference_runs_without_network(
    record: dict[str, Any], monkeypatch: pytest.MonkeyPatch
) -> None:
    def denied(*args: object, **kwargs: object) -> None:
        raise AssertionError("offline reference attempted network access")

    monkeypatch.setattr(socket, "socket", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    path = BASE / f"solutions/{record['id']}_checks.py"
    ast.parse(path.read_text())
    runpy.run_path(str(path), run_name="__main__")


def test_advanced_manifests_are_not_faked_as_browser_operations() -> None:
    for n in range(21, 43):
        record = next(x for x in RECORDS if x["id"] == f"k8s-{n:03d}")
        assert record["runtime_profile"] == "reading"
        source = (BASE / f"solutions/k8s-{n:03d}_solution.json").read_text()
        with pytest.raises(KubernetesRefusal):
            parse_manifests(source)
    for name in (
        "k8s-022-marker-writer.json",
        "k8s-022-marker-reader.json",
        "k8s-029-crd.json",
        "k8s-031-admission.json",
    ):
        with pytest.raises(KubernetesRefusal):
            parse_manifests((BASE / "fixtures" / name).read_text())


def test_marker_writer_is_exclusive_and_reader_is_independent(tmp_path: Path) -> None:
    marker = tmp_path / "marker"
    commands: dict[str, list[str]] = {}
    for mode in ("writer", "reader"):
        job = json.loads((BASE / f"fixtures/k8s-022-marker-{mode}.json").read_text())
        assert job["spec"]["backoffLimit"] == 0 and job["spec"]["activeDeadlineSeconds"] == 60
        pod = job["spec"]["template"]["spec"]
        container = pod["containers"][0]
        assert pod["restartPolicy"] == "Never"
        assert container["volumeMounts"][0]["readOnly"] is (mode == "reader")
        code = container["command"][2].replace("'/data/marker'", repr(str(marker)))
        commands[mode] = [sys.executable, "-c", code]
    first = subprocess.run(commands["writer"], capture_output=True, text=True, timeout=5)
    assert first.returncode == 0 and marker.read_bytes() == b"persistent-demo\n"
    assert first.stdout.strip() == hashlib.sha256(marker.read_bytes()).hexdigest()
    second = subprocess.run(commands["writer"], capture_output=True, text=True, timeout=5)
    assert second.returncode != 0 and "FileExistsError" in second.stderr
    read = subprocess.run(commands["reader"], capture_output=True, text=True, timeout=5)
    assert read.returncode == 0 and read.stdout == first.stdout
    marker.write_bytes(b"wrong")
    assert subprocess.run(commands["reader"], capture_output=True, timeout=5).returncode != 0


def test_real_signature_accepts_original_and_rejects_tamper() -> None:
    tool = shutil.which("openssl")
    if tool is None:
        pytest.skip("No already available OpenSSL-compatible verifier; no tool installed")
    directory = BASE / "fixtures/provenance"
    public = directory / "publisher-public.txt"
    receipt = json.loads((directory / "receipt.json").read_text())
    assert hashlib.sha256(public.read_bytes()).hexdigest() == receipt["public_key_sha256"]
    assert b"PRIVATE KEY" not in public.read_bytes()
    for filename, expected in (("attestation.json", True), ("attestation-tampered.json", False)):
        result = subprocess.run(
            [
                tool,
                "dgst",
                "-sha256",
                "-verify",
                str(public),
                "-signature",
                str(directory / "attestation.sig"),
                str(directory / filename),
            ],
            capture_output=True,
            timeout=10,
        )
        assert (result.returncode == 0) is expected


def test_vendored_render_inputs_have_no_remote_or_plugin_dependencies() -> None:
    yaml = pytest.importorskip("yaml")
    chart = BASE / "fixtures/helm/lesson-hello"
    metadata = yaml.safe_load((chart / "Chart.yaml").read_text())
    assert "dependencies" not in metadata
    assert not (chart / "charts").exists() and not (chart / "crds").exists()
    template = (chart / "templates/deployment.yaml").read_text()
    assert "helm.sh/hook" not in template and "lookup" not in template
    for path in (BASE / "fixtures/kustomize").rglob("kustomization.yaml"):
        data = yaml.safe_load(path.read_text())
        assert "generators" not in data and "transformers" not in data
        for resource in data.get("resources", []):
            assert "://" not in resource and (path.parent / resource).exists()


def test_prepared_kustomize_renders_both_fixtures_without_api_calls() -> None:
    tool = ROOT / "work/kubernetes-tools/kubectl-v1.37.0"
    if not tool.is_file():
        pytest.skip("Pinned local kubectl not prepared; no tool installed")
    yaml = pytest.importorskip("yaml")
    directory = BASE / "fixtures/kustomize"
    for name, count in (("dev", 1), ("test", 2)):
        result = subprocess.run(
            [
                str(tool),
                "--kubeconfig=" + str(directory / "unused-kubeconfig"),
                "kustomize",
                str(directory / "overlays" / name),
            ],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
        actual = yaml.safe_load(result.stdout)
        expected = json.loads((directory / f"expected-{name}.json").read_text())
        assert actual == expected and actual["spec"]["replicas"] == count

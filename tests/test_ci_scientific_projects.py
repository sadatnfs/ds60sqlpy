"""Full scientific publication gates, native bindings and bounded artifact recovery."""

from __future__ import annotations

import io
import json
import stat
import zipfile
from dataclasses import asdict, replace
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest

from scripts import ci_release_artifacts as artifacts
from scripts import ci_scientific_projects as execution
from scripts import docker_release as release
from scripts import scientific_receipts as scientific
from scripts.docker_registry import OCI_MANIFEST, Descriptor, ReleaseError

ROOT = Path(__file__).resolve().parents[1]


def hashed(value: str) -> str:
    return scientific.digest(value)


@pytest.fixture
def fixture(tmp_path: Path) -> dict[str, Any]:
    root = tmp_path / "checkout"
    root.mkdir()
    (root / "docker").mkdir()
    for name in ("classroom-images.tsv", "ci-profile-groups.json", "ci-scientific-projects.json"):
        (root / "docker" / name).write_bytes((ROOT / "docker" / name).read_bytes())
    declared = scientific.policy(root)
    for project in declared["projects"].values():
        for relative in project["maps"]:
            folder = root / relative
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "original.txt").write_text("Independent fixture source, not runtime evidence")
    package = root / "packages/spark-likelihood/src/ds60_spark_likelihood"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("# Synthetic fixture source, never runtime evidence\n")
    cpp = root / "courses/tmb-modeling/projects/tmb-cpp-api/models"
    cpp.mkdir()
    for number in range(5):
        (cpp / f"model{number}.cpp").write_text(f"// Source fixture {number}\n")
    context = release.Context(
        "exampleuser", "exampleuser/ds60sqlpy", "example/classroom", "1.1.0", "a" * 40, "12345", "1"
    )
    profiles = release.catalog(root)
    natives = {
        name: {
            arch: Descriptor(OCI_MANIFEST, hashed(name + arch), 1234)
            for arch in release.ARCHITECTURES
        }
        for name in profiles
    }

    class ImmutableRegistry:
        def head(self, reference: str) -> Any:
            manifest = self.get(reference).descriptor
            return SimpleNamespace(
                media_type=manifest.media_type, digest=manifest.digest, size=manifest.size
            )

        def get(self, reference: str) -> Any:
            for name, platforms in natives.items():
                for architecture, manifest in platforms.items():
                    if manifest.digest == reference:
                        return SimpleNamespace(
                            descriptor=manifest,
                            document={"config": {"digest": hashed(name + architecture + "config")}},
                        )
            raise ReleaseError("Unknown immutable fixture manifest")

    return {
        "registry": ImmutableRegistry(),
        "root": root,
        "policy": declared,
        "context": context,
        "profiles": profiles,
        "natives": natives,
    }


def ordinary(fixture: dict[str, Any], architecture: str, group: str) -> dict[str, Any]:
    context, profiles, natives = fixture["context"], fixture["profiles"], fixture["natives"]
    selected = release.release_groups(profiles, fixture["root"])[group]
    if group == "python-core":
        selected = release.SEEDS
    images = []
    for key in sorted(selected):
        native = natives[key][architecture]
        config = hashed(key + architecture + "config")
        images.append(
            {
                "profile": key,
                "local_repository": profiles[key].local_repository,
                "tested_image_id": config,
                "candidate_tag": release.candidate_tag(context, key, architecture),
                "candidate_root": native.record(),
                "native": {
                    **native.record(),
                    "platform": {"os": "linux", "architecture": architecture},
                },
                "config_digest": config,
                "identity_basis": "config",
            }
        )
    covered = (set(selected) - {"app"}) | ({"python-core"} if "app" in selected else set())
    common = {
        "sha256": hashed("qualification"),
        "profiles": sorted(covered),
        "passed": True,
        "complete": True,
    }
    return {
        "schema_version": 1,
        "kind": "ds60-staged-images",
        "context": asdict(context),
        "architecture": architecture,
        "group": group,
        "seed_native_digests": {}
        if group == "python-core"
        else {key: natives[key][architecture].digest for key in release.SEEDS},
        "qualification": [
            {**common, "kind": "module-references", "references": 2},
            {
                **common,
                "kind": "ci-summary",
                "group": group,
                "checks": sorted(release.mandatory_ci_checks(group)),
            },
        ],
        "images": images,
    }


def package_fixture(spec: dict[str, Any], architecture: str, root: Path) -> dict[str, Any]:
    """Synthetic receipt data for rejection tests; never presented as runtime evidence."""
    from scripts.scientific_package_receipts import package_sources

    path = "/usr/local/lib/python3.12/site-packages/ds60_spark_likelihood"
    identity = {
        "distribution": "ds60-spark-likelihood",
        "version": "0.2.0",
        "package_path": path,
        "isolated_python": True,
        "classroom_imported": False,
        "r_dependency_required": False,
        "wheel_name": "ds60_spark_likelihood-0.2.0-py3-none-any.whl",
        "wheel_sha256": "a" * 64,
        **{
            key: package_sources(root)
            for key in ("installed_source", "declared_source", "wheel_source")
        },
    }
    observations = {}
    by_kind = {}
    for mode, kinds in spec["package"]["observations"].items():
        observations[mode] = [{"kind": kind, "passed": True} for kind in kinds]
        observations[mode][0].update(
            version="0.2.0",
            module_path=path + "/__init__.py",
            classroom_imported=False,
            rscript_present=False,
        )
        by_kind.update({row["kind"]: row for row in observations[mode][1:]})
    by_kind["package-row-numerical"].update(
        partition_batch_cases=12,
        invalid_cases_rejected=5,
        max_analytic_error=0.0,
        max_nonlinear_gradient_error=0.0,
    )
    by_kind["package-unit-numerical"].update(
        rows=9,
        units=3,
        max_rank_one_value_gradient_error=0.0,
        max_finite_difference_error=0.0,
        max_hessian_oracle_error=0.0,
    )
    by_kind["package-prediction-optimizer"].update(
        max_prediction_error=0.0, custom_model_value_gradient_error=0.0, gradient_inf_norm=0.0
    )
    for kind in ("package-custom-gamma-poisson", "package-spark-custom-unit"):
        by_kind[kind].update(
            max_scipy_value_gradient_error=0.0,
            max_poisson_limit_value_gradient_error=0.0,
            serial_fit_parameter_error=0.0,
            gradient_inf_norm=0.0,
        )
    by_kind["package-spark-rows"].update(
        caller_cache_preserved=True,
        partition_cases=[{"partitions": n} for n in (1, 2, 5)],
        normal_mle={"gradient_inf_norm": 0.0},
        weighted_logistic_fit={"gradient_inf_norm": 0.0},
    )
    by_kind["package-spark-units"].update(
        caller_cache_preserved=True,
        closed_objective_rejected=True,
        duplicate_unit_rejected=True,
        raw_data_collected=False,
        layouts=[
            {"partitions": n, "error": 0.0, "row_count": 9, "unit_count": 3} for n in (1, 2, 5)
        ],
        shared_group_fit={"oracle_parameter_error": 0.0, "gradient_inf_norm": 0.0},
    )
    by_kind["package-dataframe-ml"].update(
        checks=spec["package"]["ml_checks"],
        classroom_imported=False,
        r_required=False,
        remote_cluster_executed=False,
        runtime={
            "spark": "4.0.1",
            "torch": "2.9.1+cpu",
            "scipy": "1.15.3",
            "package": "0.2.0",
            "architecture": architecture,
        },
        results={
            "rows": {"score": 0.0},
            "regression_custom": {"score": 0.0},
            "complete_units": {"score": 0.0},
            "custom_count_units": {
                "score": 0.0,
                "row_count": 13,
                "unit_count": 6,
                "prediction_target": "new_group_expected_count",
                "value_gradient_oracle_error": 0.0,
                "serial_fit_parameter_error": 0.0,
            },
        },
    )
    return {
        "identity": identity,
        "observations": observations,
        "executor_imports": {
            "kind": "package-executor-isolation",
            "passed": True,
            "spark": "4.0.1",
            "records": [{"partition": n, "fixture_rows": 1, **identity} for n in (0, 1)],
        },
    }


def observation_fixture(
    project: str, declared: dict[str, Any], architecture: str, root: Path
) -> list[dict[str, Any]]:
    spec = declared["projects"][project]
    rows = {item["id"]: {**item["selector"], **item["required"]} for item in spec["checks"]}
    if project == "spark-torch":
        rows["standalone-package"].update(package_fixture(spec, architecture, root))
        for key, shards in (("one-rank", [list(range(6))]), ("two-rank", [[0, 1, 2, 3], [4, 5]])):
            rows[key].update(rank_shards=shards, gradient=-1 / 6, parameter_after_step=1 / 60)
        rows["lightning"].update(rank_shards=[[0, 2, 4], [1, 3, 5]])
        rows["arrow"]["batch_cases"] = [
            {"configured_batch_limit": value, "max_observed_batch": value} for value in (1, 3)
        ]
    elif project == "spark-tmb":
        from scripts.scientific_package_receipts import package_sources

        source = {
            name.removeprefix("ds60_spark_likelihood/"): value
            for name, value in package_sources(root).items()
        }
        rows["reference-package"].update(
            installed_path="/usr/local/lib/python3.12/site-packages/ds60_spark_likelihood",
            wheel_sha256="a" * 64,
            installed_source_sha256=source,
            declared_source_sha256=source,
            wheel_source_sha256=source,
        )
        rows["process-cleanup"]["checks"] = [
            {"adapter": a, "mode": m, "descendant_stopped": True}
            for a in ("runner", "registry", "fixed-bridge")
            for m in ("parent-exit", "timeout")
        ]
        names = [
            "integer-upper",
            "integer-na-sentinel",
            "integer-beyond-float-exactness",
            "fractional",
            "boolean",
        ]
        rows["runtime-contracts"]["checks"] = (
            [{"check": "real-vector-integer-precision", "rejected_before_R_execution": True}]
            + [{"check": name, "rejected_by_actual_R": True} for name in names]
            + [{"check": "fixed-bridge-source-tamper", "rejected_before_R_execution": True}]
        )
        oracle = {"value_abs_error": 0.0, "gradient_max_abs_error": 0.0}
        rows["partition-normal"]["layouts"] = [
            {"partitions": n, "result": {"row_count": 12}, "oracle": oracle} for n in (2, 3)
        ]
        rows["group-laplace"]["oracle"] = oracle
        rows["global-normal-fit"].update(oracle=oracle, trace=[{"gradient": [0.0, 0.0]}] * 3)
        rows["rpy2-frame"].update(row_order=["r3", "r1", "r4", "r2", "r6", "r5"], gradient_max=0.0)
        rows["failure-contracts"]["rejected"] = [
            "unknown-model",
            "nonfinite",
            "duplicate-row",
            "singleton",
            "wrong-dimension",
        ]
        rows["registered-models"].update(
            normal_gradient_error=0.0,
            laplace_gradient_error=0.0,
            independent_fits=[{"fit": {"convergence": 0, "gradient": [0.0, 0.0]}}] * 4,
        )
        rows["prediction-models"].update(
            normal_value_gradient_error=0.0,
            regression_value_gradient_error=0.0,
            fit_parameter_error=0.0,
            prediction_error=0.0,
            fit_diagnostics=[{"convergence": 0, "gradient_max": 0.0}] * 2,
            rejected=[
                "undeclared-normal",
                "undeclared-random",
                "response-leak",
                "row-count",
                "wrong-target",
            ],
        )
        rows["dataframe-ml"].update(
            checks=spec["dataframe_checks"],
            results={
                "normal": {"rows": 6, "predicted_rows": 2, "score": 0.0},
                "regression": {"score": 0.0},
                "groups": {"gradient_max_abs_error": 0.0},
            },
        )
        rows["scala-dataframe"].update(
            fit={"converged": True, "gradient_inf_norm": 0.0},
            partition_batch_cases=[
                {"rows": 12, "oracle_error": 0.0, "partition_rows": [3, 3, 2, 2, 2]}
            ]
            * 3,
        )
    else:
        row = next(iter(rows.values()))
        row.update(
            checks=spec["completed_checks"],
            fixtures=spec["fixtures"],
            runtime={**spec["runtime"], "architecture": architecture},
            artifacts=[],
        )
        if project == "tmb-cpp-api":
            import hashlib

            row["artifacts"] = [
                {
                    "source_relative": path.relative_to(root).as_posix(),
                    "source_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                    "library_sha256": hashed(path.name).removeprefix("sha256:"),
                }
                for path in sorted(
                    (root / "courses/tmb-modeling/projects/tmb-cpp-api/models").glob("*.cpp")
                )
            ]
    return list(rows.values())


def successful_receipt(fixture: dict[str, Any], architecture: str = "arm64") -> dict[str, Any]:
    context, root, declared, natives = (
        fixture["context"],
        fixture["root"],
        fixture["policy"],
        fixture["natives"],
    )
    bases = {}
    for key, group in declared["base_profiles"].items():
        original = ordinary(fixture, architecture, group)
        config = hashed(key + architecture + "config")
        bases[key] = {
            "receipt": original,
            "receipt_sha256": scientific.digest(original),
            "reference": context.repository + "@" + natives[key][architecture].digest,
            "local_image_id": config,
            "config_digest": config,
        }
    prep = {
        "target": "dependencies",
        "image_id": hashed("dependencies" + architecture),
        "r_base": bases["r-statistics"]["reference"],
        "log_sha256": hashed("dependencies-log"),
    }
    projects = []
    for key, spec in declared["projects"].items():
        observed = observation_fixture(key, declared, architecture, root)
        needed = (
            ("spark-local-python", "llm-torch-cpu")
            if key == "spark-torch"
            else ("spark-local-python", "r-statistics", "java21")
        )
        projects.append(
            {
                "id": key,
                "image_id": hashed(("torch" if key == "spark-torch" else "tmb") + architecture),
                "build_inputs": {base: bases[base]["reference"] for base in needed},
                "preparation": None if key == "spark-torch" else prep,
                "source_manifest_sha256": scientific.digest(
                    scientific.source_manifest(root, spec["maps"])
                ),
                "sealed_source_manifest_sha256": scientific.digest(
                    scientific.source_manifest(root, spec["maps"])
                ),
                "runtime": {**spec["runtime"], "architecture": architecture},
                "fixtures": spec["fixtures"],
                "checks": [
                    {"id": item["id"], "result": row}
                    for item, row in zip(spec["checks"], observed, strict=True)
                ],
                "log_sha256": hashed(key + "log"),
                "observations_sha256": scientific.digest(observed),
                "execution_scope": "native-single-host-cpu-offline",
            }
        )
    return {
        "schema_version": 1,
        "kind": "ds60-scientific-projects",
        "context": asdict(context),
        "architecture": architecture,
        "runner": declared["architectures"][architecture],
        "policy_sha256": scientific.digest(declared),
        "passed": True,
        "complete": True,
        "seed_native_digests": {key: natives[key][architecture].digest for key in release.SEEDS},
        "base_images": bases,
        "projects": projects,
        "source_manifest_sha256": scientific.source_binding(root, declared),
        "evidence_manifest_sha256": scientific.digest(projects),
        "machine": {
            "host_system": "Linux",
            "host_architecture": architecture,
            "docker_os": "linux",
            "docker_architecture": architecture,
        },
    }


def validate(raw: dict[str, Any], fixture: dict[str, Any]) -> dict[str, Any]:
    return scientific.validate_receipt(
        raw, fixture["context"], fixture["profiles"], fixture["natives"], fixture["root"]
    )


def test_complete_receipts_require_both_native_architectures_and_allow_same_run_retry(
    fixture: dict[str, Any], tmp_path: Path
) -> None:
    directory = tmp_path / "science"
    directory.mkdir()
    for architecture in release.ARCHITECTURES:
        raw = successful_receipt(fixture, architecture)
        assert validate(raw, fixture) == raw
        (directory / (architecture + ".json")).write_text(json.dumps(raw))
    current = replace(fixture["context"], run_attempt="2")
    result = scientific.validate_scientific_receipts(
        directory,
        current,
        fixture["profiles"],
        fixture["natives"],
        fixture["root"],
        registry=fixture["registry"],
    )
    assert set(result) == {"amd64", "arm64"}
    assert all(row["context"]["run_attempt"] == "1" for row in result.values())
    (directory / "amd64.json").unlink()
    with pytest.raises(ReleaseError, match="amd64 and arm64"):
        scientific.validate_scientific_receipts(
            directory,
            current,
            fixture["profiles"],
            fixture["natives"],
            fixture["root"],
            registry=fixture["registry"],
        )
    with pytest.raises(ReleaseError, match="project-receipts-dir"):
        scientific.validate_scientific_receipts(
            None,
            current,
            fixture["profiles"],
            fixture["natives"],
            fixture["root"],
            registry=fixture["registry"],
        )


@pytest.mark.parametrize(
    "field,value",
    [
        ("revision", "b" * 40),
        ("run_id", "999"),
        ("run_attempt", "2"),
        ("source_repository", "other/repo"),
        ("version", "1.1.1"),
    ],
)
def test_other_source_run_version_or_future_attempt_is_rejected(
    fixture: dict[str, Any], field: str, value: str
) -> None:
    raw = successful_receipt(fixture)
    raw["context"][field] = value
    with pytest.raises(ReleaseError, match="source/run"):
        validate(raw, fixture)


@pytest.mark.parametrize(
    "mutation",
    [
        "failed",
        "incomplete",
        "missing-base",
        "wrong-seed",
        "wrong-native",
        "wrong-config",
        "mutable-tag",
        "wrong-runner",
        "host-emulation",
        "engine-emulation",
        "missing-project",
        "missing-check",
        "wrong-source",
        "wrong-sealed-source",
        "wrong-policy",
        "missing-build-input",
        "wrong-dependency",
        "wrong-runtime",
        "missing-r-guard",
        "duplicate-rank-row",
        "missing-cpp-library",
        "changed-fixture",
    ],
)
def test_failed_or_mismatched_scientific_evidence_cannot_promote(
    fixture: dict[str, Any], mutation: str
) -> None:
    raw = successful_receipt(fixture)
    projects = {p["id"]: p for p in raw["projects"]}
    checks = {p: {c["id"]: c["result"] for c in row["checks"]} for p, row in projects.items()}
    if mutation == "failed":
        raw["passed"] = False
    elif mutation == "incomplete":
        raw["complete"] = False
    elif mutation == "missing-base":
        raw["base_images"].pop("java21")
    elif mutation == "wrong-seed":
        raw["seed_native_digests"]["app"] = hashed("other-seed")
    elif mutation == "wrong-native":
        fixture["natives"]["java21"]["arm64"] = Descriptor(OCI_MANIFEST, hashed("new-native"), 1234)
    elif mutation == "wrong-config":
        raw["base_images"]["java21"]["config_digest"] = hashed("other-config")
    elif mutation == "mutable-tag":
        raw["base_images"]["java21"]["reference"] = "exampleuser/ds60sqlpy:latest"
    elif mutation == "wrong-runner":
        raw["runner"] = "ubuntu-24.04"
    elif mutation == "host-emulation":
        raw["machine"]["host_architecture"] = "amd64"
    elif mutation == "engine-emulation":
        raw["machine"]["docker_architecture"] = "amd64"
    elif mutation == "missing-project":
        raw["projects"].pop()
    elif mutation == "missing-check":
        projects["spark-torch"]["checks"].pop()
    elif mutation == "wrong-source":
        raw["source_manifest_sha256"] = hashed("old-source")
    elif mutation == "wrong-sealed-source":
        projects["spark-tmb"]["sealed_source_manifest_sha256"] = hashed("not-shipped")
    elif mutation == "wrong-policy":
        raw["policy_sha256"] = hashed("old-policy")
    elif mutation == "missing-build-input":
        projects["spark-tmb"]["build_inputs"].clear()
    elif mutation == "wrong-dependency":
        projects["spark-tmb"]["preparation"] = {
            **projects["spark-tmb"]["preparation"],
            "r_base": "exampleuser/ds60sqlpy:latest",
        }
    elif mutation == "wrong-runtime":
        projects["spark-torch"]["runtime"]["torch"] = "0.0"
    elif mutation == "missing-r-guard":
        checks["spark-tmb"]["runtime-contracts"]["checks"].pop()
    elif mutation == "duplicate-rank-row":
        checks["spark-torch"]["two-rank"]["rank_shards"] = [[0, 1, 2, 3], [4, 4]]
    elif mutation == "missing-cpp-library":
        checks["tmb-cpp-api"]["cpp-api"]["artifacts"].pop()
    elif mutation == "changed-fixture":
        checks["tmb-public-api"]["public-api"]["fixtures"] = {
            **checks["tmb-public-api"]["public-api"]["fixtures"],
            "seed": 1,
        }
    # Recompute aggregate digests so these tests exercise semantic validation,
    # not merely a stale final checksum.
    for p in raw["projects"]:
        p["observations_sha256"] = scientific.digest([c["result"] for c in p["checks"]])
    raw["evidence_manifest_sha256"] = scientific.digest(raw["projects"])
    with pytest.raises(ReleaseError):
        validate(raw, fixture)


def test_current_source_change_invalidates_prior_receipt(fixture: dict[str, Any]) -> None:
    raw = successful_receipt(fixture)
    path = fixture["root"] / "packages/spark-likelihood/src/ds60_spark_likelihood/__init__.py"
    path.write_text("Changed executable source")
    with pytest.raises(ReleaseError, match="source or policy"):
        validate(raw, fixture)


def scientific_archive(document: dict[str, Any], *, linked: bool = False) -> bytes:
    target = io.BytesIO()
    with zipfile.ZipFile(target, "w") as bundle:
        item = zipfile.ZipInfo("scientific-receipt.json")
        if linked:
            item.external_attr = (stat.S_IFLNK | 0o777) << 16
        bundle.writestr(item, json.dumps(document))
    return target.getvalue()


def test_scientific_artifacts_are_distinct_bounded_and_same_run(fixture: dict[str, Any]) -> None:
    raw = successful_receipt(fixture)
    artifact = artifacts.Artifact("scientific-arm64", 1, 17, "scientific-projects-arm64-attempt-1")
    result = artifacts.receipt_bytes(
        scientific_archive(raw),
        artifact,
        repository=fixture["context"].source_repository,
        revision=fixture["context"].revision,
        run_id=fixture["context"].run_id,
    )
    assert json.loads(result) == raw
    for altered in (
        scientific_archive(raw, linked=True),
        scientific_archive({**raw, "passed": False}),
        scientific_archive({**raw, "architecture": "amd64"}),
    ):
        with pytest.raises(ValueError):
            artifacts.receipt_bytes(
                altered,
                artifact,
                repository=fixture["context"].source_repository,
                revision=fixture["context"].revision,
                run_id=fixture["context"].run_id,
            )
    assert artifacts.logical_keys("scientific") == ["scientific-amd64", "scientific-arm64"]
    page = {
        "artifacts": [
            {"id": 17, "name": artifact.name, "expired": False, "size_in_bytes": 1000},
            {
                "id": 18,
                "name": "scientific-diagnostics-arm64-attempt-2",
                "expired": False,
                "size_in_bytes": 1000000,
            },
        ]
    }
    assert artifacts.select_artifacts([page], ["scientific-arm64"], 2) == [artifact]


@pytest.mark.parametrize("mode", ["build", "promote-existing"])
def test_full_cli_cannot_write_without_scientific_receipts_including_recovery(
    fixture: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    gate = tmp_path / "gate.json"
    gate.write_text("{}")
    calls = []
    monkeypatch.setattr(
        release, "load_gate", lambda _path: (fixture["context"], fixture["profiles"], mode)
    )
    monkeypatch.setattr(release, "registry_for", lambda *args, **kwargs: object())
    monkeypatch.setattr(release, "promotion_inputs", lambda *args, **kwargs: fixture["natives"])
    monkeypatch.setattr(release, "promote_release", lambda *args, **kwargs: calls.append("write"))
    assert (
        release.main(
            [
                "promote",
                "--gate",
                str(gate),
                "--receipts-dir",
                str(tmp_path),
                "--output",
                str(tmp_path / "out.json"),
            ]
        )
        == 2
    )
    assert calls == [] and not (tmp_path / "out.json").exists()


def test_partial_recovery_keeps_its_original_ordinary_scope(
    fixture: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    gate = tmp_path / "gate.json"
    gate.write_text(json.dumps({"selection": {"group": "java"}}))
    calls = []
    monkeypatch.setattr(
        release,
        "load_gate",
        lambda _path: (fixture["context"], fixture["profiles"], "promote-existing"),
    )
    monkeypatch.setattr(release, "registry_for", lambda *args, **kwargs: object())
    monkeypatch.setattr(release, "promote_release", lambda *args, **kwargs: calls.append(kwargs))
    assert (
        release.main(
            [
                "promote",
                "--gate",
                str(gate),
                "--receipts-dir",
                str(tmp_path),
                "--output",
                str(tmp_path / "out.json"),
            ]
        )
        == 0
    )
    assert len(calls) == 1 and calls[0]["target_group"] == "java" and calls[0]["natives"] is None


def test_workflow_native_order_concurrency_and_secret_separation() -> None:
    yaml = pytest.importorskip("yaml")
    path = ROOT / ".github/workflows/publish-images.yml"
    jobs = yaml.load(path.read_text(), Loader=yaml.BaseLoader)["jobs"]
    job = jobs["scientific-projects"]
    assert job["needs"] == ["gate", "seed", "workers"]
    assert job["strategy"]["max-parallel"] == "2" and job["strategy"]["fail-fast"] == "false"
    assert job["strategy"]["matrix"]["include"] == [
        {"architecture": "amd64", "runner": "ubuntu-24.04"},
        {"architecture": "arm64", "runner": "ubuntu-24.04-arm"},
    ]
    commands = [step.get("run", "") for step in job["steps"]]
    assert not any("ci_classroom.py prepare" in command for command in commands)
    assert "needs.scientific-projects.result == 'success'" in jobs["promote"]["if"]
    assert "--project-receipts-dir work/scientific-receipts" in json.dumps(jobs["promote"])
    assert "ci_release_artifacts.py receipts" in json.dumps(jobs["promote"])
    for step in job["steps"]:
        if "ci_scientific_projects.py qualify" in step.get(
            "run", ""
        ) or "ci_scientific_projects.py complete" in step.get("run", ""):
            assert "DOCKERHUB" not in json.dumps(step.get("env", {}))
    assert [
        command.split("--project ")[1].split()[0]
        for command in commands
        if "ci_scientific_projects.py qualify" in command
    ] == ["spark-torch", "spark-tmb"]
    assert len(release.catalog(ROOT)) == 26
    assert "python-web" in release.catalog(ROOT)
    assert (
        "ci_scientific_projects" not in (ROOT / ".github/workflows/targeted-images.yml").read_text()
    )


def test_offline_native_container_contract_has_no_socket_credentials_or_source_mount() -> None:
    command = execution.docker_run(
        hashed("image"),
        "owned-science",
        scientific.policy(ROOT),
        entrypoint="python",
        arguments=["/opt/spark-torch/runner.py", "check"],
    )
    assert command[command.index("--network") + 1] == "none"
    assert command[command.index("--user") + 1] == "65534:65534"
    assert "--read-only" in command and "--pull" in command
    assert "--mount" not in command and "docker.sock" not in " ".join(command)
    assert "DOCKERHUB" not in " ".join(command)
    assert ":rw,exec,nosuid," in command[command.index("--tmpfs") + 1]


def test_sealed_readback_request_can_reach_container_stdin() -> None:
    command = execution.docker_run(
        hashed("image"),
        "owned-readback",
        scientific.policy(ROOT),
        entrypoint="python",
        arguments=["-c", "import json,sys;json.load(sys.stdin)"],
        interactive=True,
    )
    assert "--interactive" in command
    assert "--tty" not in command and "-t" not in command


def test_base_import_pulls_only_four_qualified_native_digests(
    fixture: dict[str, Any], tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    receipts = tmp_path / "ordinary"
    receipts.mkdir()
    groups = release.release_groups(fixture["profiles"], fixture["root"])
    for architecture in release.ARCHITECTURES:
        for group in groups:
            path = receipts / f"{group}-{architecture}.json"
            path.write_text(json.dumps(ordinary(fixture, architecture, group)))
    checked: list[str] = []

    def qualified(*args: Any, **kwargs: Any) -> Any:
        checked.append("complete ordinary validation")
        return fixture["natives"]

    monkeypatch.setattr(release, "promotion_inputs", qualified)

    class ImportedDocker(release.Docker):
        def __init__(self) -> None:
            self.pulls: list[tuple[str, str, str]] = []

        def native(self, architecture: str) -> None:
            assert architecture == "arm64"

        def pull(self, repository: str, digest: str, architecture: str) -> dict[str, Any]:
            self.pulls.append((repository, digest, architecture))
            manifest = fixture["registry"].get(digest)
            return {
                "Id": manifest.document["config"]["digest"],
                "Os": "linux",
                "Architecture": architecture,
                "Descriptor": manifest.descriptor.record(),
                "Config": {"Labels": {}},
            }

    docker = ImportedDocker()
    imported = execution.import_bases(
        fixture["context"],
        fixture["profiles"],
        receipts,
        "arm64",
        fixture["registry"],
        docker,
        fixture["root"],
    )
    assert checked == ["complete ordinary validation"]
    assert len(docker.pulls) == 4
    assert {item[1] for item in docker.pulls} == {
        fixture["natives"][key]["arm64"].digest for key in scientific.BASES
    }
    assert all(
        item[0] == fixture["context"].repository and item[2] == "arm64" for item in docker.pulls
    )
    assert set(imported["seed_native_descriptors"]) == release.SEEDS
    assert set(imported["base_images"]) == scientific.BASES


def test_immutable_config_readback_catches_a_tampered_import_when_old_worker_config_was_absent(
    fixture: dict[str, Any], tmp_path: Path
) -> None:
    directory = tmp_path / "science"
    directory.mkdir()
    for architecture in release.ARCHITECTURES:
        raw = successful_receipt(fixture, architecture)
        if architecture == "arm64":
            base = raw["base_images"]["java21"]
            image = next(row for row in base["receipt"]["images"] if row["profile"] == "java21")
            image["config_digest"] = None
            image["identity_basis"] = "root"
            image["tested_image_id"] = image["candidate_root"]["digest"]
            base["receipt_sha256"] = scientific.digest(base["receipt"])
            base["config_digest"] = hashed("tampered-config")
            base["local_image_id"] = hashed("tampered-config")
            validate(raw, fixture)
        (directory / (architecture + ".json")).write_text(json.dumps(raw))
    with pytest.raises(ReleaseError, match="immutable native manifest"):
        scientific.validate_scientific_receipts(
            directory,
            fixture["context"],
            fixture["profiles"],
            fixture["natives"],
            fixture["root"],
            registry=fixture["registry"],
        )


def test_cleanup_refuses_unowned_images_and_never_prunes_bases_or_volumes(
    fixture: dict[str, Any],
) -> None:
    class OwnedDocker(release.Docker):
        def __init__(self, valid: bool) -> None:
            self.valid = valid
            self.commands: list[list[str]] = []

        def output(self, args: list[str], *, timeout: int = 120) -> str:
            self.commands.append(args)
            return "fixture-image" if args[:2] == ["image", "ls"] else ""

        def inspect(self, reference: str) -> dict[str, Any]:
            labels = (
                execution.owner_labels(fixture["context"], "arm64")
                if self.valid
                else {"io.ds60.scientific.owner": "someone-else"}
            )
            return {"Config": {"Labels": labels}}

    wrong = OwnedDocker(False)
    with pytest.raises(ReleaseError, match="owner labels"):
        execution.cleanup_owned_images(fixture["context"], "arm64", wrong)
    assert not any(command[:2] == ["image", "rm"] for command in wrong.commands)
    owned = OwnedDocker(True)
    execution.cleanup_owned_images(fixture["context"], "arm64", owned)
    removed = [command for command in owned.commands if command[:2] == ["image", "rm"]]
    assert len(removed) == 3
    assert all(
        command[2] == "--no-prune" and command[3].startswith("ds60-scientific-12345-1-arm64-")
        for command in removed
    )
    assert not any("volume" in command or "prune" in command for command in owned.commands)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing-ml",
        "missing-ml-check",
        "wrong-wheel-source",
        "source-import",
        "missing-executor",
        "wrong-executor-source",
        "gamma-cancellation",
        "wrong-runtime",
        "raw-collect",
        "failed-fit",
        "bad-wheel-digest",
    ],
)
def test_standalone_package_gate_rejects_partial_or_mismatched_proof(
    fixture: dict[str, Any], mutation: str
) -> None:
    from copy import deepcopy

    from scripts.scientific_package_receipts import validate_package

    spec = fixture["policy"]["projects"]["spark-torch"]
    row = deepcopy(package_fixture(spec, "arm64", fixture["root"]))
    observed = {item["kind"]: item for mode in row["observations"].values() for item in mode}
    if mutation == "missing-ml":
        row["observations"].pop("ml")
    elif mutation == "missing-ml-check":
        observed["package-dataframe-ml"]["checks"].pop()
    elif mutation == "wrong-wheel-source":
        row["identity"]["wheel_source"] = {"other.py": "b" * 64}
    elif mutation == "source-import":
        row["identity"]["package_path"] = "/opt/ds60-package-source/src/ds60_spark_likelihood"
    elif mutation == "missing-executor":
        row["executor_imports"]["records"].pop()
    elif mutation == "wrong-executor-source":
        row["executor_imports"]["records"][0]["installed_source"] = {}
    elif mutation == "gamma-cancellation":
        observed["package-custom-gamma-poisson"]["max_poisson_limit_value_gradient_error"] = 3.0
    elif mutation == "wrong-runtime":
        observed["package-dataframe-ml"]["runtime"]["torch"] = "0.0"
    elif mutation == "raw-collect":
        observed["package-spark-units"]["raw_data_collected"] = True
    elif mutation == "failed-fit":
        observed["package-dataframe-ml"]["results"]["custom_count_units"]["score"] = 0.1
    elif mutation == "bad-wheel-digest":
        row["identity"]["wheel_sha256"] = "invalid"
    with pytest.raises(ReleaseError):
        validate_package(row, spec, "arm64", fixture["root"])


@pytest.mark.parametrize(
    "field",
    [
        "installed_path",
        "wheel_sha256",
        "installed_source_sha256",
        "declared_source_sha256",
        "wheel_source_sha256",
    ],
)
def test_optional_reference_pure_wheel_identity_is_required(
    fixture: dict[str, Any], field: str
) -> None:
    rows = observation_fixture("spark-tmb", fixture["policy"], "arm64", fixture["root"])
    rows[0][field] = {} if field.endswith("source_sha256") else "invalid"
    with pytest.raises(ReleaseError, match="pure wheel"):
        scientific.observation_checks(
            "spark-tmb", rows, fixture["policy"], "arm64", fixture["root"]
        )

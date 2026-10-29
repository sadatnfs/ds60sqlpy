"""Fail-closed policy and source-bound native scientific qualification receipts."""

from __future__ import annotations

import ast
import hashlib
import json
import math
import re
from pathlib import Path
from typing import Any

from scripts import docker_release as release
from scripts.docker_registry import Descriptor, Registry, ReleaseError, descriptor, require_digest

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = "docker/ci-scientific-projects.json"
PROJECTS = frozenset({"spark-torch", "spark-tmb", "tmb-public-api", "tmb-cpp-api"})
BASES = frozenset({"spark-local-python", "llm-torch-cpu", "r-statistics", "java21"})
IGNORED = frozenset(
    {
        "__pycache__",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
        ".workshop",
        ".learning",
        "build",
        "dist",
    }
)


def digest(value: Any) -> str:
    return (
        "sha256:"
        + hashlib.sha256(
            json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()
        ).hexdigest()
    )


def same(actual: Any, expected: Any) -> bool:
    if type(actual) is not type(expected):
        return False
    if isinstance(expected, dict):
        return actual.keys() == expected.keys() and all(
            same(actual[k], v) for k, v in expected.items()
        )
    if isinstance(expected, list):
        return len(actual) == len(expected) and all(
            same(a, b) for a, b in zip(actual, expected, strict=True)
        )
    return bool(actual == expected)


def safe_json(value: Any, depth: int = 0) -> None:
    if depth > 20:
        raise ReleaseError("Scientific evidence nesting exceeds its bound")
    if value is None or type(value) is bool:
        return
    if type(value) in {int, float}:
        if not math.isfinite(value):
            raise ReleaseError("Scientific evidence contains nonfinite numbers")
    elif isinstance(value, str):
        if len(value) > 4096:
            raise ReleaseError("Scientific evidence string exceeds its bound")
    elif isinstance(value, list):
        if len(value) > 4096:
            raise ReleaseError("Scientific evidence array exceeds its bound")
        for item in value:
            safe_json(item, depth + 1)
    elif isinstance(value, dict):
        if len(value) > 256 or any(not isinstance(key, str) for key in value):
            raise ReleaseError("Scientific evidence object exceeds its bound")
        for item in value.values():
            safe_json(item, depth + 1)
    else:
        raise ReleaseError("Scientific evidence must be JSON values")


def policy(root: Path = ROOT) -> dict[str, Any]:
    result = release.read_json(root / POLICY_PATH)
    if (
        type(result.get("schema_version")) is not int
        or result["schema_version"] != 1
        or result.get("kind") != "ds60-scientific-project-policy"
        or result.get("ordinary_profile_count") != 26
        or set(result.get("base_profiles", {})) != BASES
        or set(result.get("projects", {})) != PROJECTS
        or result.get("architectures") != {"amd64": "ubuntu-24.04", "arm64": "ubuntu-24.04-arm"}
    ):
        raise ReleaseError("Invalid dedicated scientific qualification policy")
    for name, project in result["projects"].items():
        checks = project.get("checks")
        if not isinstance(checks, list) or not checks:
            raise ReleaseError("Scientific projects need explicit nonempty checks")
        identifiers = [item.get("id") for item in checks if isinstance(item, dict)]
        if (
            len(identifiers) != len(checks)
            or any(
                not isinstance(value, str) or re.fullmatch(r"[a-z][a-z0-9-]{0,63}", value) is None
                for value in identifiers
            )
            or len(set(identifiers)) != len(checks)
        ):
            raise ReleaseError("Scientific check IDs must be unique")
        if any(
            set(item) != {"id", "selector", "required"}
            or not isinstance(item["selector"], dict)
            or not item["selector"]
            or not isinstance(item["required"], dict)
            for item in checks
        ):
            raise ReleaseError("Scientific checks need fixed selectors and expectations")
        if not project.get("maps") or not project.get("runtime") or not project.get("fixtures"):
            raise ReleaseError("Scientific policy lacks source/runtime/fixture contracts")
        if name in {"spark-torch", "spark-tmb"} and not project.get("runner_cases"):
            raise ReleaseError("Scientific workshop needs declared cases")
    package = result["projects"]["spark-torch"].get("package")
    if (
        not isinstance(package, dict)
        or set(package) != {"distribution", "version", "ml_checks", "observations"}
        or package.get("distribution") != "ds60-spark-likelihood"
        or re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", str(package.get("version"))) is None
        or not isinstance(package.get("ml_checks"), list)
        or len(package["ml_checks"]) != 33
        or not all(isinstance(item, str) for item in package["ml_checks"])
        or len(set(package["ml_checks"])) != 33
        or set(package.get("observations", {})) != {"numerical", "spark", "ml"}
    ):
        raise ReleaseError("Invalid standalone package completeness policy")
    return result


def source_manifest(root: Path, maps: dict[str, str]) -> dict[str, str]:
    files: dict[str, str] = {}
    for relative, installed in sorted(maps.items()):
        if not isinstance(relative, str) or not isinstance(installed, str):
            raise ReleaseError("Scientific source mappings must use fixed string paths")
        folder = root / relative
        if (
            not installed.startswith("/opt/")
            or Path(relative).is_absolute()
            or ".." in Path(relative).parts
            or not folder.is_dir()
            or folder.is_symlink()
            or not folder.resolve().is_relative_to(root.resolve())
        ):
            raise ReleaseError("Invalid scientific source mapping")
        for path in sorted(folder.rglob("*")):
            parts = path.relative_to(folder).parts
            if any(
                part in IGNORED or part.endswith(".egg-info") for part in parts
            ) or path.suffix in {".pyc", ".pyo"}:
                continue
            if path.is_symlink():
                raise ReleaseError("Scientific source must not contain links")
            if path.is_file():
                if path.stat().st_size > 8 * 1024 * 1024:
                    raise ReleaseError("Scientific source file exceeds its bound")
                files[path.relative_to(root).as_posix()] = (
                    "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()
                )
            elif not path.is_dir():
                raise ReleaseError("Scientific source must contain ordinary files")
    if not files or len(files) > 1000:
        raise ReleaseError("Scientific source manifest is empty or too large")
    return files


def source_binding(root: Path, declared: dict[str, Any]) -> str:
    return digest(
        {
            name: source_manifest(root, project["maps"])
            for name, project in declared["projects"].items()
        }
    )


def require_runner_cases(root: Path, project: str, specification: dict[str, Any]) -> None:
    if project not in {"spark-torch", "spark-tmb"}:
        return
    source = root / f"courses/advanced-spark-modeling/projects/{project}/runner.py"
    trees = ast.parse(source.read_text("utf-8"))
    assignments = [
        node
        for node in trees.body
        if isinstance(node, ast.Assign)
        and any(isinstance(t, ast.Name) and t.id == "CASES" for t in node.targets)
    ]
    if (
        len(assignments) != 1
        or list(ast.literal_eval(assignments[0].value)) != specification["runner_cases"]
    ):
        raise ReleaseError("Workshop case list changed without reviewed scientific policy")


def observation_checks(
    project: str,
    observations: list[dict[str, Any]],
    declared: dict[str, Any],
    architecture: str,
    root: Path = ROOT,
) -> list[dict[str, Any]]:
    safe_json(observations)
    specification = declared["projects"][project]
    selected = []
    used: set[int] = set()
    for check in specification["checks"]:
        matching = [
            (i, row)
            for i, row in enumerate(observations)
            if all(same(row.get(key), value) for key, value in check["selector"].items())
        ]
        if len(matching) != 1:
            raise ReleaseError(f"Scientific check {project}/{check['id']} is missing or duplicated")
        index, row = matching[0]
        if index in used or any(
            not same(row.get(key), value) for key, value in check["required"].items()
        ):
            raise ReleaseError(
                f"Scientific check {project}/{check['id']} failed its expected result"
            )
        used.add(index)
        selected.append({"id": check["id"], "result": row})
    if len(used) != len(observations):
        raise ReleaseError("Unexpected scientific observation; review the exact check policy")
    if project in {"tmb-public-api", "tmb-cpp-api"}:
        row = observations[0]
        if not same(row.get("checks"), specification["completed_checks"]) or not same(
            row.get("fixtures"), specification["fixtures"]
        ):
            raise ReleaseError("TMB scientific checks or fixture/seed contract differ")
        runtime = row.get("runtime", {})
        aliases = {"aarch64": "arm64", "arm64": "arm64", "x86_64": "amd64", "amd64": "amd64"}
        if aliases.get(str(runtime.get("architecture", "")).split("-")[0]) != architecture:
            raise ReleaseError("Native TMB probe ran on another architecture")
        if any(runtime.get(key) != value for key, value in specification["runtime"].items()):
            raise ReleaseError("TMB scientific runtime differs from pinned policy")
        artifacts = row.get("artifacts")
        if not isinstance(artifacts, list):
            raise ReleaseError("TMB probes must report artifact identities")
        if project == "tmb-public-api" and artifacts:
            raise ReleaseError("Public API probe unexpectedly compiled new artifacts")
        if project == "tmb-cpp-api":
            expected = {
                path.relative_to(root).as_posix()
                for path in (root / "courses/tmb-modeling/projects/tmb-cpp-api/models").glob(
                    "*.cpp"
                )
            }
            if (
                len(expected) != 5
                or len(artifacts) != 5
                or {item.get("source_relative") for item in artifacts} != expected
            ):
                raise ReleaseError("C++ qualification needs all five original compiled templates")
            for item in artifacts:
                source = item["source_relative"]
                if (
                    item.get("source_sha256")
                    != hashlib.sha256((root / source).read_bytes()).hexdigest()
                    or release.HASH.fullmatch(str(item.get("library_sha256"))) is None
                ):
                    raise ReleaseError("C++ source/library identity is invalid")
    if project == "spark-torch":
        from scripts.scientific_package_receipts import validate_package

        by_id = {row["id"]: row["result"] for row in selected}
        validate_package(by_id["standalone-package"], specification, architecture, root)
        for key, size in (("one-rank", 1), ("two-rank", 2)):
            row = by_id[key]
            shards = row.get("rank_shards", [])
            if len(shards) != size or sorted(x for shard in shards for x in shard) != list(
                range(6)
            ):
                raise ReleaseError("DDP coverage duplicates or omits observations")
            if size == 2 and shards != specification["fixtures"]["ddp_rank_shards"]:
                raise ReleaseError("DDP did not execute the unequal-rank fixture")
            if (
                abs(row.get("gradient", math.inf) + 1 / 6) > 1e-12
                or abs(row.get("parameter_after_step", math.inf) - 1 / 60) > 1e-12
            ):
                raise ReleaseError("DDP gradient/update differs from independent oracle")
        lightning = by_id["lightning"]
        if sorted(x for shard in lightning.get("rank_shards", []) for x in shard) != list(range(6)):
            raise ReleaseError("Lightning coverage differs from its declared fixture")
        batches = by_id["arrow"].get("batch_cases", [])
        if [row.get("configured_batch_limit") for row in batches] != [1, 3] or any(
            row.get("max_observed_batch", 0) != row.get("configured_batch_limit") for row in batches
        ):
            raise ReleaseError("Arrow batch-bound invariance was not exercised")
    if project == "spark-tmb":
        by_id = {row["id"]: row["result"] for row in selected}
        from scripts.scientific_package_receipts import package_sources

        package = by_id["reference-package"]
        expected_source = {
            name.removeprefix("ds60_spark_likelihood/"): value
            for name, value in package_sources(root).items()
        }
        if (
            not expected_source
            or package.get("installed_path")
            != "/usr/local/lib/python3.12/site-packages/ds60_spark_likelihood"
            or release.HASH.fullmatch(str(package.get("wheel_sha256"))) is None
            or any(
                package.get(key) != expected_source
                for key in (
                    "installed_source_sha256",
                    "declared_source_sha256",
                    "wheel_source_sha256",
                )
            )
        ):
            raise ReleaseError("Optional R reference did not use its source-bound pure wheel")
        lifecycle = by_id["process-cleanup"].get("checks", [])
        wanted = {
            (adapter, mode)
            for adapter in ("runner", "registry", "fixed-bridge")
            for mode in ("parent-exit", "timeout")
        }
        if (
            len(lifecycle) != 6
            or {(row.get("adapter"), row.get("mode")) for row in lifecycle} != wanted
            or any(row.get("descendant_stopped") is not True for row in lifecycle)
        ):
            raise ReleaseError("Scientific process cleanup did not exercise all real child cases")
        contracts = by_id["runtime-contracts"].get("checks", [])
        names = [
            "real-vector-integer-precision",
            "integer-upper",
            "integer-na-sentinel",
            "integer-beyond-float-exactness",
            "fractional",
            "boolean",
            "fixed-bridge-source-tamper",
        ]
        if (
            [row.get("check") for row in contracts] != names
            or any(row.get("rejected_by_actual_R") is not True for row in contracts[1:6])
            or contracts[0].get("rejected_before_R_execution") is not True
            or contracts[-1].get("rejected_before_R_execution") is not True
        ):
            raise ReleaseError("Actual R support/source rejection evidence is incomplete")
        layouts = by_id["partition-normal"].get("layouts", [])
        if [row.get("partitions") for row in layouts] != [2, 3]:
            raise ReleaseError("TMB partition invariance did not execute both layouts")
        numerical = [*layouts, by_id["group-laplace"], by_id["global-normal-fit"]]
        for row in numerical:
            oracle = row.get("oracle", {})
            for name in ("value_abs_error", "gradient_max_abs_error"):
                value = oracle.get(name)
                if type(value) not in {int, float} or not 0 <= value <= 2e-7:
                    raise ReleaseError("TMB objective/gradient did not match the numerical oracle")
        if any(row.get("result", {}).get("row_count") != 12 for row in layouts):
            raise ReleaseError("TMB normal layouts changed observation count")
        fitted = by_id["global-normal-fit"].get("trace", [])
        if (
            len(fitted) != 3
            or not fitted[-1].get("gradient")
            or max(map(abs, fitted[-1]["gradient"])) > 1e-7
        ):
            raise ReleaseError("Global TMB fit lacks its three evaluations and stationary score")
        conversion = by_id["rpy2-frame"]
        if (
            conversion.get("row_order") != ["r3", "r1", "r4", "r2", "r6", "r5"]
            or not 0 <= conversion.get("gradient_max", math.inf) < 1e-4
        ):
            raise ReleaseError("rpy2 conversion/fitting receipt lost row identity or stationarity")
        if by_id["failure-contracts"].get("rejected") != [
            "unknown-model",
            "nonfinite",
            "duplicate-row",
            "singleton",
            "wrong-dimension",
        ]:
            raise ReleaseError("Python failure-contract evidence is incomplete")
        registered = by_id["registered-models"]
        if any(
            not 0 <= registered.get(name, math.inf) <= 2e-6
            for name in ("normal_gradient_error", "laplace_gradient_error")
        ):
            raise ReleaseError("Registered TMB gradients differ from independent oracles")
        fits = registered.get("independent_fits", [])
        if len(fits) != 4 or any(
            row.get("fit", {}).get("convergence") != 0
            or not row["fit"].get("gradient")
            or max(map(abs, row["fit"]["gradient"])) > 1e-4
            for row in fits
        ):
            raise ReleaseError("Registered independent fits did not all converge")
        prediction = by_id["prediction-models"]
        limits = {
            "normal_value_gradient_error": 2e-7,
            "regression_value_gradient_error": 2e-7,
            "fit_parameter_error": 1e-5,
            "prediction_error": 1e-5,
        }
        if any(not 0 <= prediction.get(name, math.inf) <= limit for name, limit in limits.items()):
            raise ReleaseError("Optional TMB prediction/reference fitting differs from its oracles")
        fit_diagnostics = prediction.get("fit_diagnostics", [])
        if len(fit_diagnostics) != 2 or any(
            row.get("convergence") != 0 or not 0 <= row.get("gradient_max", math.inf) <= 1e-5
            for row in fit_diagnostics
        ):
            raise ReleaseError("Optional TMB prediction fits lack convergence/score evidence")
        if prediction.get("rejected") != [
            "undeclared-normal",
            "undeclared-random",
            "response-leak",
            "row-count",
            "wrong-target",
        ]:
            raise ReleaseError("Optional TMB prediction refusal coverage is incomplete")
        dataframe = by_id["dataframe-ml"]
        if dataframe.get("checks") != specification["dataframe_checks"]:
            raise ReleaseError("Optional TMB DataFrame/Pipeline checks are incomplete")
        data_results = dataframe.get("results", {})
        if (
            data_results.get("normal", {}).get("rows") != 6
            or data_results.get("normal", {}).get("predicted_rows") != 2
        ):
            raise ReleaseError("Optional TMB DataFrame normal fixture lost row coverage")
        if any(
            not 0 <= data_results.get(name, {}).get("score", math.inf) <= 1e-5
            for name in ("normal", "regression")
        ):
            raise ReleaseError("Optional TMB DataFrame fits did not meet their score threshold")
        if not 0 <= data_results.get("groups", {}).get("gradient_max_abs_error", math.inf) <= 2e-7:
            raise ReleaseError("Optional TMB DataFrame complete-group score differs from oracle")
        scala = by_id["scala-dataframe"]
        if (
            scala.get("fit", {}).get("converged") is not True
            or not 0 <= scala["fit"].get("gradient_inf_norm", math.inf) < 1e-6
        ):
            raise ReleaseError("Scala DataFrame shared fit did not reach its required stationarity")
        cases = scala.get("partition_batch_cases", [])
        if (
            len(cases) != 3
            or any(
                row.get("rows") != 12 or not 0 <= row.get("oracle_error", math.inf) <= 1e-10
                for row in cases
            )
            or not any(
                len({n for n in row.get("partition_rows", []) if n > 0}) > 1 for row in cases
            )
        ):
            raise ReleaseError("Scala DataFrame fixture lacks unequal partition/oracle evidence")
    return selected


def selected_ordinary(
    directory: Path,
    context: release.Context,
    profiles: dict[str, release.Profile],
    root: Path = ROOT,
) -> dict[tuple[str, str], dict[str, Any]]:
    selected: dict[tuple[str, str], dict[str, Any]] = {}
    for path in release.receipt_files(directory):
        raw = release.staged_receipt(release.read_json(path), context, profiles, root=root)
        key = raw["group"], raw["architecture"]
        prior = selected.get(key)
        if prior is not None and prior["context"]["run_attempt"] == raw["context"]["run_attempt"]:
            raise ReleaseError("Ambiguous ordinary receipt selection")
        if prior is None or int(prior["context"]["run_attempt"]) < int(
            raw["context"]["run_attempt"]
        ):
            selected[key] = raw
    return selected


def validate_base_records(
    records: Any,
    context: release.Context,
    architecture: str,
    profiles: dict[str, release.Profile],
    natives: dict[str, dict[str, Descriptor]],
    declared: dict[str, Any],
    root: Path = ROOT,
) -> None:
    if not isinstance(records, dict) or set(records) != BASES:
        raise ReleaseError("Scientific receipt needs exactly four qualified base images")
    expected_seeds = {key: natives[key][architecture].digest for key in release.SEEDS}
    for key, row in records.items():
        if not isinstance(row, dict) or set(row) != {
            "receipt",
            "receipt_sha256",
            "reference",
            "local_image_id",
            "config_digest",
        }:
            raise ReleaseError("Invalid scientific base receipt fields")
        original = release.staged_receipt(row["receipt"], context, profiles, root=root)
        if (
            original["architecture"] != architecture
            or original["group"] != declared["base_profiles"][key]
            or original["seed_native_digests"] != expected_seeds
        ):
            raise ReleaseError("Scientific base uses another architecture, group or App/Core seed")
        if row["receipt_sha256"] != digest(original):
            raise ReleaseError("Scientific base provenance was modified")
        images = [image for image in original["images"] if image["profile"] == key]
        if len(images) != 1 or descriptor(images[0]["native"]) != natives[key][architecture]:
            raise ReleaseError(
                "Scientific base differs from the ordinary image selected for promotion"
            )
        native = natives[key][architecture].digest
        if row["reference"] != context.repository + "@" + native:
            raise ReleaseError("Scientific builds must use immutable qualified native references")
        config = require_digest(row["config_digest"])
        if images[0]["config_digest"] is not None and config != images[0]["config_digest"]:
            raise ReleaseError("Scientific base config differs from its qualified image")
        if require_digest(row["local_image_id"]) not in {native, config}:
            raise ReleaseError(
                "Imported scientific base identity differs from its native/config digest"
            )


def _validate_receipt(
    raw: dict[str, Any],
    context: release.Context,
    profiles: dict[str, release.Profile],
    natives: dict[str, dict[str, Descriptor]],
    root: Path = ROOT,
) -> dict[str, Any]:
    required = {
        "schema_version",
        "kind",
        "context",
        "architecture",
        "runner",
        "policy_sha256",
        "passed",
        "complete",
        "seed_native_digests",
        "base_images",
        "projects",
        "source_manifest_sha256",
        "evidence_manifest_sha256",
        "machine",
    }
    if (
        set(raw) != required
        or type(raw.get("schema_version")) is not int
        or raw["schema_version"] != 1
        or raw.get("kind") != "ds60-scientific-projects"
        or raw.get("passed") is not True
        or raw.get("complete") is not True
    ):
        raise ReleaseError("Scientific receipt must be complete and passed with the exact schema")
    recorded = release.bound_context(raw, context, earlier=True)
    declared = policy(root)
    architecture = raw["architecture"]
    if (
        architecture not in release.ARCHITECTURES
        or raw["runner"] != declared["architectures"][architecture]
    ):
        raise ReleaseError("Scientific receipt is not from the required native runner")
    if raw["policy_sha256"] != digest(declared) or raw["source_manifest_sha256"] != source_binding(
        root, declared
    ):
        raise ReleaseError("Scientific source or policy changed after qualification")
    seeds = {key: natives[key][architecture].digest for key in release.SEEDS}
    if raw["seed_native_digests"] != seeds:
        raise ReleaseError("Scientific receipt used different qualified App/Core seeds")
    machine = raw["machine"]
    if (
        not isinstance(machine, dict)
        or set(machine) != {"host_system", "host_architecture", "docker_os", "docker_architecture"}
        or machine
        != {
            "host_system": "Linux",
            "host_architecture": architecture,
            "docker_os": "linux",
            "docker_architecture": architecture,
        }
    ):
        raise ReleaseError("Scientific qualification must execute natively on host and engine")
    validate_base_records(
        raw["base_images"], recorded, architecture, profiles, natives, declared, root
    )
    projects = raw["projects"]
    if (
        not isinstance(projects, list)
        or len(projects) != len(PROJECTS)
        or {p.get("id") for p in projects} != PROJECTS
    ):
        raise ReleaseError("Scientific receipt lacks the complete project set")
    for project in projects:
        if set(project) != {
            "id",
            "image_id",
            "build_inputs",
            "preparation",
            "source_manifest_sha256",
            "sealed_source_manifest_sha256",
            "runtime",
            "fixtures",
            "checks",
            "log_sha256",
            "observations_sha256",
            "execution_scope",
        }:
            raise ReleaseError("Scientific project receipt fields differ")
        key = project["id"]
        specification = declared["projects"][key]
        require_digest(project["image_id"])
        require_digest(project["log_sha256"])
        expected_source = digest(source_manifest(root, specification["maps"]))
        if (
            project["source_manifest_sha256"] != expected_source
            or project["sealed_source_manifest_sha256"] != expected_source
        ):
            raise ReleaseError("Sealed scientific image did not match its source manifest")
        if (
            project["fixtures"] != specification["fixtures"]
            or project["execution_scope"] != "native-single-host-cpu-offline"
        ):
            raise ReleaseError("Scientific fixture or execution scope differs")
        runtime = project["runtime"]
        if (
            not isinstance(runtime, dict)
            or runtime.get("architecture") != architecture
            or any(runtime.get(k) != v for k, v in specification["runtime"].items())
        ):
            raise ReleaseError("Scientific project runtime differs from native version policy")
        observations = [check["result"] for check in project["checks"]]
        if observation_checks(key, observations, declared, architecture, root) != project[
            "checks"
        ] or project["observations_sha256"] != digest(observations):
            raise ReleaseError("Scientific observations were changed or incompletely recorded")
        needed = (
            {"spark-local-python", "llm-torch-cpu"}
            if key == "spark-torch"
            else {"spark-local-python", "r-statistics", "java21"}
        )
        if not isinstance(project["build_inputs"], dict) or set(project["build_inputs"]) != needed:
            raise ReleaseError("Scientific build inputs are incomplete or include unrelated bases")
        preparation = project["preparation"]
        if key == "spark-torch":
            if preparation is not None:
                raise ReleaseError("Unexpected TMB preparation on Spark/Torch")
        else:
            if (
                not isinstance(preparation, dict)
                or set(preparation) != {"target", "image_id", "r_base", "log_sha256"}
                or preparation["target"] != "dependencies"
                or preparation["r_base"] != raw["base_images"]["r-statistics"]["reference"]
            ):
                raise ReleaseError(
                    "TMB dependencies were not prepared from the qualified native R image"
                )
            require_digest(preparation["image_id"])
            require_digest(preparation["log_sha256"])
        for base, reference in project["build_inputs"].items():
            if base not in BASES or reference != raw["base_images"][base]["reference"]:
                raise ReleaseError("Scientific build did not use qualified immutable bases")
    tmb_reports = [p for p in projects if p["id"] != "spark-torch"]
    if (
        len({p["image_id"] for p in tmb_reports}) != 1
        or len({digest(p["preparation"]) for p in tmb_reports}) != 1
    ):
        raise ReleaseError("TMB scientific checks must use the same prepared immutable image")
    if raw["evidence_manifest_sha256"] != digest(projects):
        raise ReleaseError("Scientific evidence manifest differs")
    return raw


def validate_receipt(
    raw: dict[str, Any],
    context: release.Context,
    profiles: dict[str, release.Profile],
    natives: dict[str, dict[str, Descriptor]],
    root: Path = ROOT,
) -> dict[str, Any]:
    try:
        return _validate_receipt(raw, context, profiles, natives, root)
    except (KeyError, TypeError, AttributeError, OverflowError) as error:
        raise ReleaseError("Scientific receipt has malformed structured evidence") from error


def validate_scientific_receipts(
    directory: Path | None,
    context: release.Context,
    profiles: dict[str, release.Profile],
    natives: dict[str, dict[str, Descriptor]],
    root: Path = ROOT,
    *,
    registry: Registry,
) -> dict[str, Any]:
    if directory is None:
        raise ReleaseError(
            "Full promotion requires --project-receipts-dir for both native scientific checks"
        )
    chosen: dict[str, dict[str, Any]] = {}
    for path in release.receipt_files(directory):
        raw = validate_receipt(release.read_json(path), context, profiles, natives, root)
        arch = raw["architecture"]
        previous = chosen.get(arch)
        attempt = int(raw["context"]["run_attempt"])
        if previous is not None and attempt == int(previous["context"]["run_attempt"]):
            raise ReleaseError("Ambiguous scientific receipt for one successful native attempt")
        if previous is None or attempt > int(previous["context"]["run_attempt"]):
            chosen[arch] = raw
    if set(chosen) != set(release.ARCHITECTURES):
        raise ReleaseError("Full promotion requires scientific qualification on amd64 and arm64")
    for architecture, receipt in chosen.items():
        for key, base in receipt["base_images"].items():
            expected = natives[key][architecture]
            manifest = registry.get(expected.digest)
            if (
                manifest.descriptor != expected
                or release.config_digest(manifest) != base["config_digest"]
            ):
                raise ReleaseError(
                    "Scientific imported config differs from the immutable native manifest"
                )
    return chosen

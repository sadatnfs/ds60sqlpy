"""Build, check and search a source-derived DS60 accomplishment lookup.

Only JSON, TOML, AST and C++ source text are read. No lessons or runtimes run.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import re
import sys
import tomllib
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote

HERE = Path(__file__).resolve().parent
KIND_ORDER = (
    "track",
    "lesson",
    "package",
    "api",
    "likelihood-model",
    "model-factory",
    "native-model",
    "scala-api",
    "torch-api",
    "r-model",
    "r-case",
    "study",
    "capability",
)
SOURCE_STATUS = {"implementation": "authored", "acceptance": "source_registered"}


def read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError("Expected a JSON object: " + str(path))
    return value


def relative(root: Path, path: Path) -> str:
    value = path.relative_to(root).as_posix()
    if value.startswith("/") or ".." in Path(value).parts:
        raise ValueError("Index paths must be repository-relative")
    return value


def words(*values: str) -> list[str]:
    found = []
    for value in values:
        found.extend(re.findall(r"[a-z0-9]+", value.lower()))
    return sorted(set(found))


def item(
    identifier: str,
    kind: str,
    title: str,
    *,
    source: list[str],
    docs: list[str] | None = None,
    aliases: list[str] | None = None,
    related: list[str] | None = None,
    status: dict[str, str] | None = None,
    evidence: list[dict[str, str]] | None = None,
    keywords: list[str] | None = None,
) -> dict[str, Any]:
    aliases = sorted(set(aliases or []))
    return {
        "id": identifier,
        "kind": kind,
        "title": title,
        "source_paths": sorted(set(source)),
        "docs_paths": sorted(set(docs or [])),
        "aliases": aliases,
        "keywords": words(*(keywords or []), identifier, title, *aliases),
        "related_ids": sorted(set(related or [])),
        "status": status or dict(SOURCE_STATUS),
        "evidence": evidence
        or [{"tier": "source", "path": source[0], "note": "Registered source identity"}],
    }


def tracks_and_lessons(repo: Path) -> list[dict[str, Any]]:
    catalog_path = repo / "curriculum/catalog.json"
    catalog = read_json(catalog_path)
    if catalog.get("schema_version") != 1 or not isinstance(catalog.get("lessons"), list):
        raise ValueError("Unsupported legacy catalog")
    entries = []
    for track_id, row in sorted(catalog["tracks"].items()):
        entries.append(
            item(
                "track:" + track_id,
                "track",
                row["title"],
                source=["curriculum/catalog.json", "src/ds60sqlpy/catalog_builder.py"],
                docs=[row["plan"]],
                aliases=[track_id],
                keywords=["legacy", "course", "track"],
            )
        )
    for lesson in catalog["lessons"]:
        content_present = (repo / lesson["lesson_path"]).is_file() and (
            repo / lesson["guide_path"]
        ).is_file()
        sources = [lesson["lesson_path"]] if content_present else ["curriculum/catalog.json"]
        guides = (
            [lesson["guide_path"], *lesson.get("solution_paths", [])] if content_present else []
        )
        entries.append(
            item(
                "lesson:" + lesson["id"],
                "lesson",
                lesson["title"],
                source=sources,
                docs=guides,
                aliases=[lesson["id"], f"{lesson['track']} day {lesson['day']}"],
                related=[
                    "track:" + lesson["track"],
                    *["lesson:" + x for x in lesson["prerequisites"]],
                ],
                status={
                    "implementation": "authored" if content_present else "catalog_only",
                    "acceptance": "catalog_registered",
                },
                evidence=[
                    {
                        "tier": "source",
                        "path": "curriculum/catalog.json",
                        "note": "Generated legacy catalog record",
                    }
                ],
                keywords=[lesson["track"], lesson["phase"], lesson["level"], "legacy"],
            )
        )

    plans: dict[str, tuple[dict[str, Any], str]] = {}
    for path in sorted((repo / "courses").glob("*/track.json")):
        payload = read_json(path)
        plans[payload["id"]] = (payload, relative(repo, path))
    for path in sorted((repo / "docs/expansion/plans").glob("*.json")):
        payload = read_json(path)
        if payload["id"] in plans:
            raise ValueError("Duplicate course track plan")
        plans[payload["id"]] = (payload, relative(repo, path))
    manifests = {path.parent.name: path for path in (repo / "courses").glob("*/lessons.json")}
    if not set(manifests) <= set(plans):
        raise ValueError("Authored manifest has no registered track plan")
    for track, (plan, plan_path) in sorted(plans.items()):
        manifest = manifests.get(track)
        payload = read_json(manifest) if manifest else {"track_id": track, "lessons": []}
        if payload.get("track_id") != track or plan.get("id") != track:
            raise ValueError("Course track identity differs")
        planned = {row["id"]: row for row in plan["lessons"]}
        authored = {row["id"] for row in payload["lessons"]}
        if not authored <= set(planned):
            raise ValueError("Authored lesson has no plan identity: " + track)
        manifest_path = relative(repo, manifest) if manifest else None
        guide = repo / "courses" / track / "README.md"
        entries.append(
            item(
                "track:" + track,
                "track",
                plan["title"],
                source=[plan_path, *([manifest_path] if manifest_path else [])],
                docs=[relative(repo, guide)] if guide.exists() else [],
                aliases=[track],
                keywords=[plan.get("learning_mode", "practice"), "course", "track"],
                evidence=[
                    {
                        "tier": "source",
                        "path": manifest_path or plan_path,
                        "note": "Track plan and optional authored lesson manifest",
                    }
                ],
            )
        )
        for identifier, planned_row in planned.items():
            if identifier in authored:
                continue
            entries.append(
                item(
                    "lesson:" + identifier,
                    "lesson",
                    planned_row["title"],
                    source=[plan_path],
                    docs=[relative(repo, guide)] if guide.exists() else [],
                    aliases=[identifier],
                    related=[
                        "track:" + track,
                        *["lesson:" + x for x in planned_row["prerequisites"]],
                    ],
                    status={"implementation": "planned", "acceptance": "not_authored"},
                    evidence=[
                        {
                            "tier": "plan",
                            "path": plan_path,
                            "note": "Planned lesson identity only",
                        }
                    ],
                    keywords=[track, "planned", plan.get("learning_mode", "practice")],
                )
            )
        for row in payload["lessons"]:
            base = row["id"]
            planned_row = planned[base]
            if row.get("status") != "authored":
                raise ValueError("Non-authored manifest row")
            variants = [(base, planned_row["title"], row)]
            for variant in row.get("variants", []):
                variants.append(
                    (
                        base + "@" + variant["id"],
                        planned_row["title"] + " | " + variant["title"],
                        row | variant,
                    )
                )
            for identifier, title, authored_row in variants:
                sources = [authored_row["source_path"]]
                guides = [authored_row["guide_path"], *authored_row["solution_paths"]]
                if identifier == base:
                    related = ["track:" + track]
                    related += ["lesson:" + x for x in planned_row["prerequisites"]]
                else:
                    related = ["track:" + track, "lesson:" + base]
                entries.append(
                    item(
                        "lesson:" + identifier,
                        "lesson",
                        title,
                        source=sources,
                        docs=guides,
                        aliases=[identifier, base, f"{track} {identifier}"],
                        related=related,
                        status={
                            "implementation": "authored"
                            if identifier == base
                            else "authored_variant",
                            "acceptance": "manifest_registered"
                            if identifier == base
                            else "variant_registered",
                        },
                        evidence=[
                            {
                                "tier": "source",
                                "path": manifest_path or plan_path,
                                "note": "Authored course manifest",
                            }
                        ],
                        keywords=[
                            track,
                            authored_row["language"],
                            authored_row["runtime_profile"],
                            plan.get("learning_mode", "practice"),
                        ],
                    )
                )
    entries.extend(statistics_book(repo))
    return entries


def statistics_book(repo: Path) -> list[dict[str, Any]]:
    """Mirror the declarative chapter and additive tutorial registrations."""
    manifest_path = "courses/statistics-ml/manifest.json"
    extension_path = "courses/statistics-ml/tutorials/index.json"
    manifest, extension = (
        read_json(repo / manifest_path),
        read_json(repo / extension_path),
    )
    if manifest.get("id") != "statistics-ml" or extension.get("mode") != "tutorial":
        raise ValueError("Statistics book manifest identity changed")
    rows = [
        item(
            "track:statistics-ml",
            "track",
            manifest["title"],
            source=[manifest_path, extension_path],
            docs=["courses/statistics-ml/README.md"],
            aliases=["statistics-ml", "statistics book"],
            keywords=["tutorial", "statistics", "machine learning"],
        )
    ]
    for origin, records in (
        (manifest_path, manifest["chapters"]),
        (extension_path, extension["units"]),
    ):
        for record in records:
            identifier = record["id"]
            examples = record["example_paths"]
            guide = record["chapter_path"]
            if not examples:
                raise ValueError("Statistics chapter has no example plan: " + identifier)
            if not all((repo / path).is_file() for path in [guide, *examples]):
                rows.append(
                    item(
                        "lesson:" + identifier,
                        "lesson",
                        record["title"],
                        source=[origin],
                        docs=[guide] if (repo / guide).is_file() else [],
                        aliases=[identifier],
                        related=[
                            "track:statistics-ml",
                            *["lesson:" + x for x in record["prerequisites"]],
                        ],
                        status={
                            "implementation": "planned",
                            "acceptance": "not_authored",
                        },
                        evidence=[
                            {
                                "tier": "plan",
                                "path": origin,
                                "note": "Tutorial unit planned but complete file pair absent",
                            }
                        ],
                        keywords=["statistics", "tutorial", "planned"],
                    )
                )
                continue
            for number, source in enumerate(examples, start=1):
                suffix = "" if number == 1 else "@example-" + str(number)
                title = (
                    record["title"]
                    if number == 1
                    else record["title"] + " | Example " + str(number)
                )
                related = ["track:statistics-ml"]
                related += (
                    ["lesson:" + x for x in record["prerequisites"]]
                    if number == 1
                    else ["lesson:" + identifier]
                )
                rows.append(
                    item(
                        "lesson:" + identifier + suffix,
                        "lesson",
                        title,
                        source=[source],
                        docs=[guide],
                        aliases=[identifier + suffix, identifier],
                        related=related,
                        status={
                            "implementation": "authored" if number == 1 else "authored_variant",
                            "acceptance": "tutorial_manifest_registered"
                            if number == 1
                            else "variant_registered",
                        },
                        evidence=[
                            {
                                "tier": "source",
                                "path": origin,
                                "note": (
                                    "Worked tutorial registration, not mastery or "
                                    "runtime acceptance"
                                ),
                            }
                        ],
                        keywords=[
                            "statistics",
                            "tutorial",
                            record.get("profile", "python-core"),
                        ],
                    )
                )
    return rows


def exported_api(repo: Path, package_key: str, base: Path, module: str) -> list[dict[str, Any]]:
    init = base / "__init__.py"
    tree = ast.parse(init.read_text(encoding="utf-8"))
    exports: list[str] | None = None
    origins: dict[str, str] = {}
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module:
            for alias in node.names:
                origins[alias.asname or alias.name] = node.module
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "__all__" for target in node.targets
        ):
            exports = ast.literal_eval(node.value)
    if not isinstance(exports, list) or not all(isinstance(name, str) for name in exports):
        raise ValueError("Package __all__ is not a static list")
    if len(exports) != len(set(exports)):
        raise ValueError("Duplicate public API export")
    entries = []
    for name in exports:
        source = [relative(repo, init)]
        if name in origins:
            path = base / (origins[name].replace(".", "/") + ".py")
            if path.is_file():
                source.append(relative(repo, path))
        entries.append(
            item(
                f"api:{package_key}:{name}",
                "api",
                name,
                source=source,
                docs=[relative(repo, base.parents[1] / "README.md")],
                aliases=[name, f"{module}.{name}"],
                related=["package:" + package_key],
                keywords=["public", "python", "api", package_key],
            )
        )
    return entries


def packages(repo: Path) -> list[dict[str, Any]]:
    rows = []
    definitions = (
        (
            "spark-likelihood",
            "packages/spark-likelihood/pyproject.toml",
            "packages/spark-likelihood/src/ds60_spark_likelihood",
            "ds60_spark_likelihood",
        ),
        (
            "spark-tmbad",
            "packages/spark-tmbad/python/pyproject.toml",
            "packages/spark-tmbad/python/src/ds60_spark_tmbad",
            "ds60_spark_tmbad",
        ),
    )
    for key, metadata_path, source_path, module in definitions:
        metadata = tomllib.loads((repo / metadata_path).read_text())
        project = metadata["project"]
        package_root = repo / source_path
        readme = "packages/" + key + "/README.md"
        rows.append(
            item(
                "package:" + key,
                "package",
                project["name"] + " " + project["version"],
                source=[metadata_path, relative(repo, package_root / "__init__.py")],
                docs=[readme],
                aliases=[project["name"], module, key],
                status={
                    "implementation": "source_package",
                    "acceptance": "consult_release_receipts",
                },
                evidence=[
                    {
                        "tier": "source",
                        "path": metadata_path,
                        "note": "Distribution metadata, not publication proof",
                    }
                ],
                keywords=["independent", "wheel", "api"],
            )
        )
        rows.extend(exported_api(repo, key, package_root, module))
    rows.extend(likelihood_models_and_factories(repo))
    rows.extend(scala_operations(repo))
    rows.extend(integrated_torch_api(repo))
    return rows


def likelihood_models_and_factories(repo: Path) -> list[dict[str, Any]]:
    base = repo / "packages/spark-likelihood/src/ds60_spark_likelihood"
    registry_path = base / "registry.py"
    registry = ast.parse(registry_path.read_text())
    registered: dict[str, str] = {}
    for node in registry.body:
        if not isinstance(node, ast.For) or not isinstance(node.iter, ast.Call):
            continue
        if not isinstance(node.iter.func, ast.Attribute) or node.iter.func.attr != "items":
            continue
        mapping = node.iter.func.value
        if not isinstance(mapping, ast.Dict):
            continue
        if not any(
            isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id == "register_model_factory"
            for child in ast.walk(node)
        ):
            continue
        for key, value in zip(mapping.keys, mapping.values, strict=True):
            if (
                not isinstance(key, ast.Constant)
                or not isinstance(key.value, str)
                or not isinstance(value, ast.Name)
            ):
                raise TypeError("Registered model mapping is not static")
            registered[key.value] = value.id
    if not registered:
        raise ValueError("No static Spark likelihood factory registry found")
    registry_functions = {
        node.name: node for node in registry.body if isinstance(node, ast.FunctionDef)
    }
    factory_paths: dict[str, str] = {}
    for filename in ("models.py", "registered_models.py"):
        path = base / filename
        tree = ast.parse(path.read_text())
        for node in tree.body:
            if not isinstance(node, ast.FunctionDef) or not isinstance(node.returns, ast.Name):
                continue
            if node.returns.id in {"TorchLoss", "TorchUnitLoss"}:
                if node.name in factory_paths:
                    raise ValueError("Duplicate named Torch likelihood factory")
                factory_paths[node.name] = relative(repo, path)
    if not factory_paths:
        raise ValueError("No named Torch likelihood factories found")
    registry_source = relative(repo, registry_path)
    guide = "packages/spark-likelihood/docs/custom-models.md"
    rows = []
    used: set[str] = set()
    for model_id, registry_function in sorted(registered.items()):
        function = registry_functions.get(registry_function)
        if function is None:
            raise ValueError("Registered model constructor is missing")
        matches = {
            child.func.id
            for child in ast.walk(function)
            if isinstance(child, ast.Call)
            and isinstance(child.func, ast.Name)
            and child.func.id in factory_paths
        }
        if len(matches) != 1:
            raise ValueError("Registered model has no unique named loss factory: " + model_id)
        factory = matches.pop()
        used.add(factory)
        rows.append(
            item(
                "likelihood-model:" + model_id,
                "likelihood-model",
                model_id.replace("_", " ").title(),
                source=[registry_source, factory_paths[factory]],
                docs=[guide],
                aliases=[model_id, factory, "resolve_model(" + model_id + ")"],
                related=["package:spark-likelihood", "model-factory:" + factory],
                status={
                    "implementation": "registered_factory",
                    "acceptance": "source_only_runtime_separate",
                },
                evidence=[
                    {
                        "tier": "source",
                        "path": registry_source,
                        "note": "Static registration via register_model_factory",
                    }
                ],
                keywords=["Spark", "PyTorch", "custom", "likelihood", "model"],
            )
        )
    for factory, factory_path in sorted(factory_paths.items()):
        rows.append(
            item(
                "model-factory:" + factory,
                "model-factory",
                factory,
                source=[factory_path],
                docs=[guide],
                aliases=[factory, "ds60_spark_likelihood." + factory],
                related=[
                    "package:spark-likelihood",
                    *[
                        "likelihood-model:" + name
                        for name, constructor in registered.items()
                        if constructor in registry_functions
                        and any(
                            isinstance(child, ast.Call)
                            and isinstance(child.func, ast.Name)
                            and child.func.id == factory
                            for child in ast.walk(registry_functions[constructor])
                        )
                    ],
                ],
                status={
                    "implementation": "named_source_factory",
                    "acceptance": "runtime_evidence_separate",
                },
                keywords=["TorchLoss", "TorchUnitLoss", "PyTorch", "model factory"],
            )
        )
    if set(factory_paths) != used:
        raise ValueError("Named Torch likelihood factory is not accounted for by the registry")
    example_path = base / "example_models.py"
    example = ast.parse(example_path.read_text())
    if not any(
        isinstance(node, ast.FunctionDef) and node.name == "quadratic_model"
        for node in example.body
    ):
        raise ValueError("Documented custom quadratic factory is missing")
    rows.append(
        item(
            "model-factory:quadratic_model",
            "model-factory",
            "quadratic_model",
            source=[relative(repo, example_path)],
            docs=[guide],
            aliases=["quadratic_model", "quadratic_mean example"],
            related=["package:spark-likelihood"],
            status={
                "implementation": "example_factory",
                "acceptance": "not_builtin_registered",
            },
            evidence=[
                {
                    "tier": "source",
                    "path": relative(repo, example_path),
                    "note": "Custom example, not a built-in registry entry",
                }
            ],
            keywords=["custom", "PyTorch", "model factory"],
        )
    )
    return rows


def scala_operations(repo: Path) -> list[dict[str, Any]]:
    path = repo / "packages/spark-tmbad/jvm/src/main/scala/io/ds60/spark/tmbad/PythonBridge.scala"
    source = path.read_text()
    if "object PythonBridge {" not in source:
        raise ValueError("Primary Scala facade object is absent")
    names = re.findall(r"(?m)^  def ([A-Za-z][A-Za-z0-9]*)\s*\(", source)
    if not names or len(names) != len(set(names)):
        raise ValueError("Primary Scala facade operations are absent or duplicated")
    source_path = relative(repo, path)
    docs = [
        "packages/spark-tmbad/docs/PROTOCOL.md",
        "packages/spark-tmbad/python/docs/EXTENDED-TARGETS.md",
    ]
    return [
        item(
            "scala-api:PythonBridge." + name,
            "scala-api",
            "PythonBridge." + name,
            source=[source_path],
            docs=docs,
            aliases=[name, "io.ds60.spark.tmbad.PythonBridge." + name],
            related=["package:spark-tmbad"],
            status={
                "implementation": "source_facade",
                "acceptance": "operation_specific_runtime_evidence_required",
            },
            evidence=[
                {
                    "tier": "source",
                    "path": source_path,
                    "note": "Public Scala facade method; execution must be checked by operation",
                }
            ],
            keywords=["Scala", "Spark", "JVM", "modeling", "API"],
        )
        for name in names
    ]


def integrated_torch_api(repo: Path) -> list[dict[str, Any]]:
    """Appear only after the sibling namespace is actually in the repository."""
    base = repo / "packages/spark-likelihood/src/ds60_torch_training"
    if not base.exists():
        return []
    metadata = tomllib.loads((repo / "packages/spark-likelihood/pyproject.toml").read_text())
    includes = metadata["tool"]["setuptools"]["packages"]["find"]["include"]
    if "ds60_torch_training*" not in includes:
        raise ValueError("Torch namespace exists but is excluded from the package wheel")
    guide = "packages/spark-likelihood/docs/CPU-TORCH-TRAINING.md"
    surface = {
        "program.py": ("TrainingProgram",),
        "data.py": (
            "prepare_rows",
            "prepare_dataframe",
            "assign_shards",
            "load_manifest",
        ),
        "launch.py": ("run_training",),
        "checkpoint.py": ("CheckpointRef", "load_rank"),
    }
    rows = []
    for filename, names in surface.items():
        path = base / filename
        tree = ast.parse(path.read_text())
        declared = {
            node.name for node in tree.body if isinstance(node, (ast.FunctionDef, ast.ClassDef))
        }
        for name in names:
            if name not in declared:
                raise ValueError("Integrated Torch public API declaration is missing: " + name)
            rows.append(
                item(
                    "torch-api:" + name,
                    "torch-api",
                    name,
                    source=[relative(repo, path)],
                    docs=[guide],
                    aliases=[
                        name,
                        "ds60_torch_training." + filename.removesuffix(".py") + "." + name,
                    ],
                    related=["package:spark-likelihood"],
                    status={
                        "implementation": "integrated_source",
                        "acceptance": "installed_wheel_and_runtime_evidence_required",
                    },
                    evidence=[
                        {
                            "tier": "source",
                            "path": relative(repo, path),
                            "note": "Repository namespace declaration only",
                        }
                    ],
                    keywords=["Torch", "Spark", "executor", "checkpoint", "CPU"],
                )
            )
    return rows


def native_registration_map(repo: Path) -> dict[str, str]:
    """Resolve each prepared_models call to its descriptor ID declaration."""
    base = repo / "packages/spark-tmbad/native"
    registry = base / "include/ds60_tmbad/registry.hpp"
    registry_text = registry.read_text()
    headers = sorted((base / "include/ds60_tmbad").glob("models*.hpp")) + [
        base / "models/custom_models.hpp"
    ]
    definitions: dict[str, tuple[str, str]] = {}
    declaration = re.compile(r"inline\s+(?:Model|std::vector<Model>)\s+(\w+)\s*\(")
    for path in headers:
        source = path.read_text()
        starts = list(declaration.finditer(source))
        for number, match in enumerate(starts):
            name = match[1]
            body = source[
                match.end() : starts[number + 1].start()
                if number + 1 < len(starts)
                else len(source)
            ]
            expressions = re.findall(r"d\.id\s*=\s*([^;]+);", body)
            if len(expressions) != 1 or name in definitions:
                raise ValueError("Native descriptor definition is not uniquely parsed: " + name)
            definitions[name] = (expressions[0].strip(), relative(repo, path))
    initializer = re.search(r"std::vector<Model>\s+result\s*\{(.*?)\};", registry_text, re.DOTALL)
    if initializer is None:
        raise ValueError("Native prepared model initializer is unparsed")
    call_pattern = re.compile(r"([a-z][a-z0-9_]*)\(([^()]*)\)")
    calls = call_pattern.findall(initializer[1])
    if re.sub(call_pattern, "", initializer[1]).strip(" \n\t,\r") or not calls:
        raise ValueError("Native prepared model call is unparsed")
    custom = definitions.get("custom_models")
    if custom is None or "for (auto model : custom_models())" not in registry_text:
        raise ValueError("Native custom model extension is unparsed")
    custom_source = (repo / custom[1]).read_text()
    extension = re.search(r"return\s*\{model,\s*([a-z_]+)\(\)\s*\};", custom_source)
    if extension is None:
        raise ValueError("Native custom model return is unparsed")
    calls.extend([("custom_models", ""), (extension[1], "")])
    found: dict[str, str] = {}
    for function, argument in calls:
        if function not in definitions:
            raise ValueError("Unparsed native registration: " + function)
        expression, descriptor_path = definitions[function]
        literal = re.fullmatch(r'"([a-z][a-z0-9_]*)"', expression)
        conditional = re.fullmatch(
            r'\w+\s*\?\s*"([a-z][a-z0-9_]*)"\s*:\s*"([a-z][a-z0-9_]*)"',
            expression,
            re.DOTALL,
        )
        if literal and not argument.strip():
            identifier = literal[1]
        elif conditional and argument.strip() in {"", "true", "false"}:
            identifier = conditional[1] if argument.strip() == "true" else conditional[2]
        elif expression == "kind" and re.fullmatch(r'"[a-z][a-z0-9_]*"', argument.strip()):
            identifier = argument.strip().strip('"')
        else:
            raise ValueError("Unparsed native descriptor choice: " + function)
        if identifier in found:
            raise ValueError("Duplicate prepared native model: " + identifier)
        found[identifier] = descriptor_path
    if set(definitions) != {name for name, _ in calls}:
        raise ValueError("Native descriptor function is not represented in registration")
    return found


def native_models(repo: Path) -> list[dict[str, Any]]:
    base = repo / "packages/spark-tmbad/native"
    registry = base / "include/ds60_tmbad/registry.hpp"
    found = native_registration_map(repo)
    rows = []
    for identifier, path in sorted(found.items()):
        guide = repo / "packages/spark-tmbad/docs/models" / (identifier + ".md")
        rows.append(
            item(
                "native-model:" + identifier,
                "native-model",
                identifier.replace("_", " ").title(),
                source=[path, relative(repo, registry)],
                docs=[relative(repo, guide)]
                if guide.exists()
                else ["packages/spark-tmbad/native/README.md"],
                aliases=[identifier, "model " + identifier],
                related=["package:spark-tmbad"],
                status={
                    "implementation": "native_registered",
                    "acceptance": "see_architecture_receipts",
                },
                evidence=[
                    {
                        "tier": "source",
                        "path": relative(repo, registry),
                        "note": "Prepared native model registry",
                    }
                ],
                keywords=["custom", "likelihood", "native", "model"],
            )
        )
    return rows


def reference_cases(repo: Path) -> list[dict[str, Any]]:
    registry_path = "packages/spark-tmbad/reference/registry.json"
    registry = read_json(repo / registry_path)
    qualification_path = "packages/spark-tmbad/reference/qualification/index-v2.json"
    qualification = read_json(repo / qualification_path)
    accepted = {row["case"]: row for row in qualification["cases"]}
    if qualification.get("passed") is not True or qualification.get("case_count") != len(accepted):
        raise ValueError("Reference qualification index is incomplete")
    rows = []
    for model in registry["models"]:
        rows.append(
            item(
                "r-model:" + model,
                "r-model",
                model.replace("_", " ").title(),
                source=[registry_path, "packages/spark-tmbad/reference/R/run.R"],
                docs=["packages/spark-tmbad/reference/docs/MODELS.md"],
                aliases=[model, "R " + model],
                related=["package:spark-tmbad"],
                status={
                    "implementation": "optional_reference",
                    "acceptance": "historical_arm64_v2",
                },
                evidence=[
                    {
                        "tier": "historical_local",
                        "path": qualification_path,
                        "note": "ARM64 v2 reference index, not hosted recurrence",
                    }
                ],
                keywords=["R", "TMB", "glmmTMB", "reference"],
            )
        )
    expanded: set[str] = set()
    for case, definition in registry["cases"].items():
        options = definition.get("options", {})
        if not options:
            names = [case]
        elif len(options) == 1:
            values = next(iter(options.values()))
            names = [case + "-" + value for value in values]
        else:
            raise ValueError("Reference option expansion changed")
        for identifier in names:
            if identifier not in accepted or identifier in expanded:
                raise ValueError("Reference case and qualified option set differ")
            expanded.add(identifier)
            record = accepted[identifier]
            evidence_file = "packages/spark-tmbad/reference/qualification/" + record["file"]
            if hashlib.sha256((repo / evidence_file).read_bytes()).hexdigest() != record["sha256"]:
                raise ValueError("Reference case receipt hash differs")
            rows.append(
                item(
                    "r-case:" + identifier,
                    "r-case",
                    identifier.replace("_", " ").replace("-", " ").title(),
                    source=[registry_path, "packages/spark-tmbad/reference/R/run.R"],
                    docs=["packages/spark-tmbad/reference/docs/MODELS.md"],
                    aliases=[identifier, case],
                    related=["package:spark-tmbad"],
                    status={
                        "implementation": "optional_reference",
                        "acceptance": "historical_arm64_v2",
                    },
                    evidence=[
                        {
                            "tier": "historical_local",
                            "path": evidence_file,
                            "note": "Hash-bound optional R reference case, not hosted recurrence",
                        }
                    ],
                    keywords=["R", "TMB", "glmmTMB", "reference", *options.keys()],
                )
            )
    if expanded != set(accepted) or len(expanded) != qualification["case_count"]:
        raise ValueError("Reference registry does not cover the v2 case index")
    return rows


def studies(repo: Path) -> list[dict[str, Any]]:
    design_path = "packages/spark-tmbad/studies/design/studies.json"
    design = read_json(repo / design_path)
    rows = []
    for record in design["studies"]:
        identifier = record["id"]
        raw_status = record["status"]
        source_name = record.get("source")
        implementation = "runner_source_prepared" if source_name else "design"
        acceptance = "not_attested"
        if "accepted all" in raw_status or "32/32" in raw_status:
            acceptance = "historical_local_partial_scope"
        elif re.search(r"[0-9]+/[0-9]+ method records accepted", raw_status):
            acceptance = "historical_local_incomplete"
        elif (
            "host-tested" in raw_status
            or "host-smoke tested" in raw_status
            or "reference tested" in raw_status
        ):
            acceptance = "host_reference_only"
        paths = [design_path]
        if source_name:
            paths.append("packages/spark-tmbad/studies/" + source_name)
        rows.append(
            item(
                "study:" + identifier,
                "study",
                record["title"],
                source=paths,
                docs=["packages/spark-tmbad/studies/README.md"],
                aliases=[identifier, record.get("case", "")],
                related=[
                    "package:spark-tmbad",
                    *["lesson:" + x for x in record.get("existing_lesson_links", [])],
                ],
                status={
                    "implementation": implementation,
                    "acceptance": acceptance,
                    "source_statement": raw_status,
                },
                evidence=[
                    {
                        "tier": "design_or_historical",
                        "path": design_path,
                        "note": raw_status,
                    }
                ],
                keywords=["simulation", "study", record.get("case", "")],
            )
        )
    if not rows or len({row["id"] for row in rows}) != len(rows):
        raise ValueError("Study design IDs are empty or duplicate")
    return rows


def manual_capabilities(repo: Path) -> list[dict[str, Any]]:
    payload = read_json(HERE / "manual-capabilities.json")
    rows = []
    for record in payload["entries"]:
        rows.append(
            item(
                record["id"],
                "capability",
                record["title"],
                source=record["source_paths"],
                docs=record["docs_paths"],
                aliases=record.get("aliases", []),
                related=record.get("related_ids", []),
                status=record["status"],
                evidence=record["evidence"],
                keywords=record.get("keywords", []),
            )
        )
    return rows


def inventory(repo: Path) -> dict[str, Any]:
    if not (repo / "AGENTS.md").is_file():
        raise ValueError("Choose the DS60 repository root")
    rows = [
        *tracks_and_lessons(repo),
        *packages(repo),
        *native_models(repo),
        *reference_cases(repo),
        *studies(repo),
        *manual_capabilities(repo),
    ]
    rows.sort(key=lambda row: (KIND_ORDER.index(row["kind"]), row["id"]))
    identifiers = [row["id"] for row in rows]
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("Duplicate stable index ID")
    known = set(identifiers)
    for row in rows:
        if not row["source_paths"] or not row["keywords"]:
            raise ValueError("Index row lacks source or search terms: " + row["id"])
        for path in [
            *row["source_paths"],
            *row["docs_paths"],
            *[e["path"] for e in row["evidence"]],
        ]:
            if Path(path).is_absolute() or ".." in Path(path).parts or not (repo / path).is_file():
                raise ValueError("Index path is absent or unsafe: " + row["id"] + " " + path)
        for identifier in row["related_ids"]:
            if identifier not in known:
                raise ValueError(
                    "Index relationship has no target: " + row["id"] + " -> " + identifier
                )
    counts = dict(sorted(Counter(row["kind"] for row in rows).items()))
    return {
        "schema_version": 1,
        "kind": "ds60-accomplishment-lookup",
        "counts": counts,
        "entries": rows,
    }


def render(document: dict[str, Any]) -> str:
    def cell(value: str) -> str:
        return value.replace("|", "\\|").replace("\n", " ")

    def link(path: str, label: str = "source") -> str:
        return f"[{label}](../{quote(path)})"

    rows = document["entries"]
    by_kind: dict[str, list[dict[str, Any]]] = {
        kind: [row for row in rows if row["kind"] == kind] for kind in KIND_ORDER
    }
    lines = [
        "# DS60 accomplishment and learning index",
        "",
        "Generated from the repository's maintained catalog, course manifests, "
        "package exports, native registry and study/reference registries. The "
        "running accomplishment log is maintained separately in `RUNNING.md`.",
        "",
        "Use `python index.py search QUERY` to find a lesson, model, package or API. "
        "Every path below is relative to the repository root. Status describes "
        "the cited evidence tier, not learner mastery or current publication.",
        "",
        "## Coverage",
        "",
        "| Kind | Entries |",
        "| --- | ---: |",
    ]
    lines += [f"| {kind} | {len(by_kind[kind])} |" for kind in KIND_ORDER]
    lines += [
        "",
        "## Learning tracks",
        "",
        "| Track | Lessons | Source |",
        "| --- | ---: | --- |",
    ]
    lessons = by_kind["lesson"]
    for row in by_kind["track"]:
        track_id = row["id"]
        count = sum(track_id in lesson["related_ids"] for lesson in lessons)
        lines.append(
            f"| {cell(row['title'])} (`{track_id}`) | {count} | {link(row['source_paths'][0])} |"
        )
    lines += ["", "## Independent packages and public APIs", ""]
    for row in by_kind["package"]:
        count = sum(row["id"] in api["related_ids"] for api in by_kind["api"])
        lines.append(
            f"- **{row['title']}**: {count} exported names, "
            f"{link(row['source_paths'][0])}. {row['status']['acceptance']}."
        )
    for kind, heading in (
        ("likelihood-model", "Registered Spark/PyTorch likelihood models"),
        ("model-factory", "Named PyTorch model factories"),
        ("scala-api", "Primary Scala facade operations"),
    ):
        lines += [
            "",
            "## " + heading,
            "",
            "| ID | Title | Scope |",
            "| --- | --- | --- |",
        ]
        for row in by_kind[kind]:
            lines.append(
                f"| `{row['id']}` | {cell(row['title'])} | "
                f"{row['status']['acceptance']} "
                f"({link(row['docs_paths'][0], 'guide')}) |"
            )
    if by_kind["torch-api"]:
        lines += [
            "",
            "## Integrated CPU Torch executor API",
            "",
            "| ID | Source | Scope |",
            "| --- | --- | --- |",
        ]
        for row in by_kind["torch-api"]:
            lines.append(
                f"| `{row['id']}` | {link(row['source_paths'][0])} | "
                f"{row['status']['acceptance']} |"
            )
    else:
        lines += [
            "",
            "## CPU Torch executor integration",
            "",
            "The sibling `ds60_torch_training` namespace is a work-only "
            "candidate and is not indexed as a repository API. The lookup "
            "adds its reviewed entrypoints only after its source and wheel "
            "discovery are integrated into the independent package; "
            "installed-wheel and runtime acceptance remain separate.",
        ]
    for kind, heading in (
        ("native-model", "Native custom models"),
        ("r-case", "Optional R/TMB reference cases"),
        ("study", "Simulation study IDs"),
    ):
        lines += [
            "",
            "## " + heading,
            "",
            "| ID | Title | Evidence status |",
            "| --- | --- | --- |",
        ]
        for row in by_kind[kind]:
            lines.append(
                f"| `{row['id']}` | {cell(row['title'])} | "
                f"{row['status']['acceptance']} "
                f"({link(row['docs_paths'][0], 'guide')}) |"
            )
    lines += ["", "## Cross-cutting capabilities", ""]
    for row in by_kind["capability"]:
        lines.append(
            f"- **{row['title']}** (`{row['id']}`): "
            f"{row['status']['implementation']}; {row['status']['acceptance']}. "
            f"See {link(row['docs_paths'][0], 'guide')}."
        )
    lines += [
        "",
        "## Maintenance",
        "",
        "Run `python index.py build --repo /path/to/ds60sqlpy` after a catalog, "
        "model, package, reference or study source change. Run "
        "`python index.py check --repo /path/to/ds60sqlpy` in CI. Edit "
        "`manual-capabilities.json` for cross-cutting capabilities and "
        "`RUNNING.md` for dated accomplishments; the build never overwrites "
        "the running log. Add the check to the repository's source/reader "
        "validation route after review.",
        "",
    ]
    return "\n".join(lines)


def canonical(document: dict[str, Any]) -> str:
    return json.dumps(document, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"


def search(
    document: dict[str, Any], query: str, kind: str | None, limit: int
) -> list[dict[str, Any]]:
    tokens = words(query)
    if not tokens:
        raise ValueError("Search needs at least one term")
    matches = []
    for row in document["entries"]:
        if kind and row["kind"] != kind:
            continue
        haystack = set(row["keywords"])
        if all(any(term in value for value in haystack) for term in tokens):
            identifier = row["id"].lower()
            aliases = {value.lower() for value in row["aliases"]}
            score = sum(
                10 if term == identifier or term in aliases else 2 if term in identifier else 1
                for term in tokens
            )
            matches.append((score, row))
    matches.sort(key=lambda pair: (-pair[0], pair[1]["id"]))
    return [row for _, row in matches[:limit]]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check", "search"))
    parser.add_argument("query", nargs="?")
    parser.add_argument("--repo", type=Path)
    parser.add_argument("--kind", choices=KIND_ORDER)
    parser.add_argument("--limit", type=int, default=20)
    args = parser.parse_args()
    if args.command in {"build", "check"}:
        if args.repo is None:
            parser.error("Build/check require --repo")
        document = inventory(args.repo.resolve())
        raw, markdown = canonical(document), render(document)
        if args.command == "build":
            (HERE / "inventory.json").write_text(raw, encoding="utf-8")
            (HERE / "INDEX.md").write_text(markdown, encoding="utf-8")
            print(json.dumps(document["counts"], sort_keys=True))
        else:
            if (HERE / "inventory.json").read_text() != raw or (
                HERE / "INDEX.md"
            ).read_text() != markdown:
                raise ValueError("Accomplishment index is stale; run build")
            print("Accomplishment index matches maintained sources")
    else:
        if args.query is None or not 1 <= args.limit <= 100:
            parser.error("Search needs a query and limit from 1 to 100")
        document = read_json(HERE / "inventory.json")
        print(
            json.dumps(
                search(document, args.query, args.kind, args.limit),
                ensure_ascii=False,
                indent=2,
            )
        )
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, TypeError, ValueError, KeyError, SyntaxError) as error:
        print("Accomplishment index error: " + str(error), file=sys.stderr)
        raise SystemExit(2) from None

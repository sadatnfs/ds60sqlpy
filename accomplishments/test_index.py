"""Meaningful parity and evidence-tier checks for the pure lookup builder."""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("accomplishment_index_under_test", HERE / "index.py")
assert SPEC is not None and SPEC.loader is not None
index = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = index
SPEC.loader.exec_module(index)


class IndexTests(unittest.TestCase):
    repo: Path
    document: dict[str, Any]
    by_id: dict[str, dict[str, Any]]

    @classmethod
    def setUpClass(cls) -> None:
        raw = os.environ.get("DS60_INDEX_REPO")
        if not raw:
            raise RuntimeError("Set DS60_INDEX_REPO to the DS60 repository root")
        cls.repo = Path(raw).resolve()
        cls.document = index.inventory(cls.repo)
        cls.by_id = {row["id"]: row for row in cls.document["entries"]}

    def test_exact_loader_lesson_parity_without_heavy_imports(self) -> None:
        sys.path.insert(0, str(self.repo / "src"))
        from ds60sqlpy.catalog import Catalog
        from ds60sqlpy.modules import ModuleCatalog

        legacy = {row.id for row in Catalog.load(self.repo).lessons()}
        modern = set(ModuleCatalog(self.repo).lessons)
        indexed = {
            row["id"].removeprefix("lesson:")
            for row in self.document["entries"]
            if row["kind"] == "lesson"
        }
        self.assertEqual(indexed, legacy | modern)
        self.assertEqual(self.document["counts"]["lesson"], len(legacy) + len(modern))
        self.assertGreater(len(legacy), 0)
        self.assertGreater(len(modern), 0)
        self.assertFalse(
            any(
                name in {"torch", "pyspark", "rpy2"}
                or name.startswith(("torch.", "pyspark.", "rpy2."))
                for name in sys.modules
            )
        )

    def test_required_registries_and_stable_relationships(self) -> None:
        self.assertEqual(
            self.document["counts"]["native-model"],
            len(index.native_registration_map(self.repo)),
        )
        self.assertEqual(
            self.document["counts"]["r-case"],
            index.read_json(
                self.repo / "packages/spark-tmbad/reference/qualification/index-v2.json"
            )["case_count"],
        )
        self.assertEqual(
            self.document["counts"]["study"],
            len(
                index.read_json(self.repo / "packages/spark-tmbad/studies/design/studies.json")[
                    "studies"
                ]
            ),
        )
        self.assertEqual(self.document["counts"]["package"], 2)
        self.assertEqual(self.document["counts"]["api"], 27)
        self.assertEqual(self.document["counts"]["likelihood-model"], 6)
        self.assertEqual(self.document["counts"]["model-factory"], 7)
        self.assertEqual(self.document["counts"]["scala-api"], 14)
        integrated = (self.repo / "packages/spark-likelihood/src/ds60_torch_training").is_dir()
        self.assertEqual(self.document["counts"].get("torch-api", 0), 8 if integrated else 0)
        self.assertIn("track:statistics-ml", self.by_id)
        self.assertIn("lesson:statistics-003", self.by_id)
        self.assertIn("lesson:bayes-001", self.by_id)
        self.assertIn("lesson:statistics-003", self.by_id["lesson:bayes-001"]["related_ids"])
        self.assertIn("package:spark-tmbad", self.by_id["native-model:normal"]["related_ids"])
        self.assertEqual(
            self.by_id["model-factory:quadratic_model"]["status"]["acceptance"],
            "not_builtin_registered",
        )
        self.assertIn(
            "model-factory:gaussian_random_intercept",
            self.by_id["likelihood-model:gaussian_random_intercept"]["related_ids"],
        )

    def test_search_finds_model_lesson_package_api_and_study(self) -> None:
        probes = {
            "gaussian_correlated_random_slope": "native-model:gaussian_correlated_random_slope",
            "spark-deploy-001": "lesson:spark-deploy-001",
            "ds60-spark-tmbad": "package:spark-tmbad",
            "SparkTMBad": "api:spark-tmbad:SparkTMBad",
            "gaussian_random_intercept": "likelihood-model:gaussian_random_intercept",
            "normal_mean": "model-factory:normal_mean",
            "fitShared": "scala-api:PythonBridge.fitShared",
            "JVM fitShared": "scala-api:PythonBridge.fitShared",
            "sim-028": "study:sim-028",
        }
        for query, expected in probes.items():
            with self.subTest(query=query):
                self.assertIn(
                    expected,
                    {row["id"] for row in index.search(self.document, query, None, 100)},
                )

    def test_partial_study_and_reference_evidence_are_not_global_claims(self) -> None:
        self.assertEqual(
            self.by_id["study:sim-020"]["status"]["acceptance"],
            "historical_local_incomplete",
        )
        self.assertEqual(
            self.by_id["r-case:glmm_family-poisson"]["status"]["acceptance"],
            "historical_arm64_v2",
        )
        self.assertEqual(
            self.by_id["capability:classroom-publisher"]["status"]["acceptance"],
            "version_and_run_specific",
        )

    def test_deterministic_generated_files_and_public_paths(self) -> None:
        self.assertEqual((HERE / "inventory.json").read_text(), index.canonical(self.document))
        self.assertEqual((HERE / "INDEX.md").read_text(), index.render(self.document))
        for row in self.document["entries"]:
            for path in [
                *row["source_paths"],
                *row["docs_paths"],
                *[e["path"] for e in row["evidence"]],
            ]:
                self.assertFalse(Path(path).is_absolute())
                self.assertNotIn("..", Path(path).parts)
        raw = (HERE / "inventory.json").read_text()
        self.assertNotIn(str(Path.home()), raw)
        self.assertEqual(json.loads(raw)["schema_version"], 1)

    def test_planned_authored_and_variant_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "curriculum").mkdir()
            (root / "curriculum/catalog.json").write_text(
                json.dumps(
                    {
                        "schema_version": 1,
                        "tracks": {"python": {"title": "Python", "plan": "python/plan.md"}},
                        "lessons": [
                            {
                                "id": "python-01",
                                "track": "python",
                                "day": 1,
                                "title": "Missing source",
                                "lesson_path": "python/missing.py",
                                "guide_path": "python/missing.md",
                                "solution_paths": [],
                                "prerequisites": [],
                                "phase": "base",
                                "level": "beginner",
                            }
                        ],
                    }
                )
            )
            track = root / "courses/demo"
            track.mkdir(parents=True)
            (track / "track.json").write_text(
                json.dumps(
                    {
                        "id": "demo",
                        "title": "Demo",
                        "lessons": [
                            {"id": "demo-001", "title": "Planned", "prerequisites": []},
                            {
                                "id": "demo-002",
                                "title": "Authored",
                                "prerequisites": [],
                            },
                        ],
                    }
                )
            )
            (track / "lessons.json").write_text(
                json.dumps(
                    {
                        "track_id": "demo",
                        "lessons": [
                            {
                                "id": "demo-002",
                                "status": "authored",
                                "source_path": "courses/demo/source.py",
                                "guide_path": "courses/demo/guide.md",
                                "solution_paths": [],
                                "language": "python",
                                "runtime_profile": "python-core",
                                "variants": [
                                    {
                                        "id": "alt",
                                        "title": "Alternate",
                                        "source_path": "courses/demo/alternate.py",
                                        "language": "python",
                                        "runtime_profile": "python-core",
                                        "solution_paths": [],
                                        "verification_id": None,
                                    }
                                ],
                            }
                        ],
                    }
                )
            )
            stats = root / "courses/statistics-ml/tutorials"
            stats.mkdir(parents=True)
            (stats.parent / "manifest.json").write_text(
                json.dumps({"id": "statistics-ml", "title": "Stats", "chapters": []})
            )
            (stats / "index.json").write_text(json.dumps({"mode": "tutorial", "units": []}))
            rows = {row["id"]: row for row in index.tracks_and_lessons(root)}
            self.assertEqual(rows["lesson:python-01"]["status"]["implementation"], "catalog_only")
            self.assertEqual(rows["lesson:demo-001"]["status"]["implementation"], "planned")
            self.assertEqual(rows["lesson:demo-002"]["status"]["implementation"], "authored")
            self.assertEqual(
                rows["lesson:demo-002@alt"]["status"]["implementation"],
                "authored_variant",
            )

    def test_unparsed_native_registration_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = self.repo / "packages/spark-tmbad/native"
            target = root / "packages/spark-tmbad/native"
            shutil.copytree(source / "include/ds60_tmbad", target / "include/ds60_tmbad")
            shutil.copytree(source / "models", target / "models")
            registry = target / "include/ds60_tmbad/registry.hpp"
            registry.write_text(
                registry.read_text().replace("normal_model(),", "unknown_model(),", 1)
            )
            with self.assertRaisesRegex(ValueError, "Unparsed native registration"):
                index.native_registration_map(root)

    def test_future_torch_namespace_is_conditional_source_only(self) -> None:
        current = index.integrated_torch_api(self.repo)
        self.assertIn(len(current), {0, 8})
        self.assertEqual(len(current), self.document["counts"].get("torch-api", 0))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            base = root / "packages/spark-likelihood/src/ds60_torch_training"
            base.mkdir(parents=True)
            metadata = root / "packages/spark-likelihood/pyproject.toml"
            metadata.write_text(
                "[tool.setuptools.packages.find]\n"
                'include = ["ds60_spark_likelihood*", "ds60_torch_training*"]\n'
            )
            declarations = {
                "program.py": "class TrainingProgram: pass\n",
                "data.py": (
                    "def prepare_rows(): pass\n"
                    "def prepare_dataframe(): pass\n"
                    "def assign_shards(): pass\n"
                    "def load_manifest(): pass\n"
                ),
                "launch.py": "def run_training(): pass\n",
                "checkpoint.py": "class CheckpointRef: pass\ndef load_rank(): pass\n",
            }
            for name, source in declarations.items():
                (base / name).write_text(source)
            rows = index.integrated_torch_api(root)
            self.assertEqual(len(rows), 8)
            self.assertTrue(
                all(
                    row["status"]["acceptance"] == "installed_wheel_and_runtime_evidence_required"
                    for row in rows
                )
            )


if __name__ == "__main__":
    unittest.main()

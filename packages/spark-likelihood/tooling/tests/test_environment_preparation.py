"""Lightweight lock and explicit-preparation controls; no scientific runtime is started."""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

TOOLING = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(TOOLING))
import locks  # noqa: E402
import prepare_environment  # noqa: E402


class PreparationChecks(unittest.TestCase):
    def test_all_owned_locks_are_exact_hashed_and_match_provenance(self):
        provenance = json.loads((TOOLING / "lock-provenance.json").read_text())
        for relative, record in provenance["locks"].items():
            path = TOOLING / relative
            self.assertEqual(
                hashlib.sha256(path.read_bytes()).hexdigest(), record["copied_lock_sha256"]
            )
            self.assertTrue(locks.read_lock(path))
        for arch in ("arm64", "amd64"):
            cpu = locks.read_lock(locks.selected_lock("cpu", arch))
            science = locks.read_lock(locks.selected_lock("scientific", arch))
            self.assertEqual(cpu["torch"], "2.9.1+cpu")
            self.assertEqual(cpu["numpy"], "2.2.6")
            self.assertEqual(science["scipy"], "1.15.3")
            self.assertEqual(science["lightning"], "2.6.1")
            self.assertFalse(cpu.keys() & science.keys())

    def test_unhashed_unpinned_duplicate_and_directive_inputs_fail(self):
        digest = "a" * 64
        bad = [
            "torch>=2.9",
            "torch==2.9.1",
            "--index-url https://example.invalid",
            f"x==1 --hash=sha256:{digest}\nx==1 --hash=sha256:{digest}",
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.lock"
            for value in bad:
                with self.subTest(value=value):
                    path.write_text(value + "\n")
                    with self.assertRaises(ValueError):
                        locks.read_lock(path)

    def test_prepared_override_checks_every_locked_version(self):
        expected = locks.read_lock(locks.selected_lock("cpu", "arm64"))
        with patch.object(locks.importlib.metadata, "version", side_effect=expected.__getitem__):
            self.assertEqual(locks.check_versions(locks.selected_lock("cpu", "arm64")), expected)
        changed = dict(expected, torch="2.9.1")
        with (
            patch.object(locks.importlib.metadata, "version", side_effect=changed.__getitem__),
            self.assertRaisesRegex(ValueError, "Prepared dependency differs"),
        ):
            locks.check_versions(locks.selected_lock("cpu", "arm64"))

    def fixture(self, root, version="4.0.1"):
        folder = root / "python/lib"
        folder.mkdir(parents=True)
        with zipfile.ZipFile(folder / "pyspark.zip", "w") as archive:
            archive.writestr("pyspark/version.py", f'__version__: str = "{version}"\n')
        with zipfile.ZipFile(folder / "py4j-0.10.9.9-src.zip", "w") as archive:
            archive.writestr("py4j/version.py", '__version__ = "0.10.9.9"\n')

    def test_unknown_spark_release_is_rejected_before_preparation(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root, "4.0.2")
            with self.assertRaisesRegex(ValueError, "specific to Spark 4.0.1"):
                prepare_environment.spark_archives(root)

    def test_wrong_py4j_archive_version_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root)
            with zipfile.ZipFile(root / "python/lib/py4j-0.10.9.9-src.zip", "w") as archive:
                archive.writestr("py4j/version.py", '__version__ = "0.10.9.8"\n')
            with self.assertRaisesRegex(ValueError, "matching Py4J"):
                prepare_environment.spark_archives(root)

    def test_read_only_check_never_applies_the_launcher_patch(self):
        class Prepared:
            def wrapper_status(self, path):
                return {"status": "prepared"}

            def patch_archive(self, path):
                raise AssertionError("Read-only check tried to mutate Spark")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root / "spark")
            site = root / "site"
            site.mkdir()
            with (
                patch.object(prepare_environment, "helper", return_value=Prepared()),
                self.assertRaisesRegex(ValueError, "explicit environment preparation"),
            ):
                prepare_environment.prepare(root / "spark", site, apply=False)
            self.assertEqual(list(site.iterdir()), [])

    def test_conflicting_managed_path_fails_before_patch(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.fixture(root / "spark")
            site = root / "site"
            site.mkdir()
            path = site / "ds60_spark_likelihood_spark.pth"
            path.write_text("/another/prepared/spark.zip\n")
            with (
                patch.object(
                    prepare_environment, "helper", side_effect=AssertionError("Must not patch")
                ),
                self.assertRaisesRegex(ValueError, "different Spark distribution"),
            ):
                prepare_environment.prepare(root / "spark", site, apply=True)
            self.assertEqual(path.read_text(), "/another/prepared/spark.zip\n")


if __name__ == "__main__":
    unittest.main()

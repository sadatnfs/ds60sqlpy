"""Pure source, lock, data-only admission and simulation-accounting contracts."""

from __future__ import annotations

import copy
import importlib.util
import io
import json
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "python"))
from client import request  # noqa: E402
from simulate import aggregate  # noqa: E402

SPEC = importlib.util.spec_from_file_location("reference_prepare", ROOT / "prepare.py")
assert SPEC is not None and SPEC.loader is not None
prepare = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(prepare)


class ReferenceContracts(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((ROOT / "dependencies.lock.json").read_text())

    def test_complete_lock_is_compatible_with_selected_r(self):
        prepare.validate_lock(self.lock)
        self.assertEqual(len(self.lock["packages"]), 65)
        self.assertEqual(self.lock["upstream"]["license"], "AGPL-3")
        self.assertEqual(self.lock["upstream"]["version"], "1.1.15.9000")

    def test_newer_r_requirement_cannot_be_silently_bypassed(self):
        altered = copy.deepcopy(self.lock)
        altered["packages"][0]["dependencies"]["Depends"] = "R (>= 4.7)"
        with self.assertRaisesRegex(ValueError, "incompatible"):
            prepare.validate_lock(altered)

    def test_missing_or_out_of_order_dependency_is_rejected(self):
        altered = copy.deepcopy(self.lock)
        altered["packages"] = list(reversed(altered["packages"]))
        with self.assertRaisesRegex(ValueError, "topological"):
            prepare.validate_lock(altered)

    def test_registry_rejects_executable_text_unknown_options_and_noninteger_seeds(self):
        self.assertEqual(
            request("glmm_family", 1729, {"family_name": "nbinom2"})["case"], "glmm_family"
        )
        for case, seed, options in [
            ("system('unsafe')", 1, {}),
            ("gaussian_ridge", True, {}),
            ("glmm_family", 1, {"family_name": "eval(code)"}),
            ("gaussian_ridge", 1, {"source": "function() 1"}),
        ]:
            with self.assertRaises(ValueError):
                request(case, seed, options)

    def test_registry_templates_exist_with_explicit_license_boundary(self):
        registry = json.loads((ROOT / "registry.json").read_text())
        self.assertEqual(len(registry["models"]), 4)
        for model in registry["models"]:
            source = (ROOT / "models" / (model + ".cpp")).read_text()
            self.assertIn("SPDX-License-Identifier: MIT", source)
            self.assertIn("objective_function<Type>::operator()", source)
        self.assertIn("AGPL-3", (ROOT / "NOTICE.md").read_text())

    def test_upstream_archive_traversal_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            archive = directory / "source.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                entry = tarfile.TarInfo("reviewed/../../escape")
                entry.size = 4
                stream.addfile(entry, io.BytesIO(b"test"))
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                prepare.unpack_package(archive, "reviewed/", directory / "unpacked")
            self.assertFalse((directory / "escape").exists())

    def test_cached_source_hash_failure_never_installs(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            source = directory / "source.tar.gz"
            source.write_bytes(b"altered")
            entry = {"sha256": "0" * 64}
            with self.assertRaisesRegex(ValueError, "hash/size"):
                prepare.acquire(entry, source.name, directory, directory / "copy", False)
            self.assertFalse((directory / "copy").exists())

    def test_failures_and_unattempted_replications_remain_visible(self):
        passed = {"status": "passed", "result": {"metrics": {"primary_estimate": 1.2, "truth": 1}}}
        summary = aggregate([passed, {"status": "failed"}], 3)
        self.assertEqual(summary["successful_replications"], 1)
        self.assertEqual(summary["failed_replications"], 1)
        self.assertEqual(summary["completion"], "incomplete")
        self.assertIsNone(summary["bias_mcse"])
        self.assertEqual(summary["failure_rate"], 0.5)

    def test_mcse_is_across_replications_and_zero_failures_have_uncertainty(self):
        records = [
            {
                "status": "passed",
                "result": {
                    "metrics": {"primary_estimate": value, "truth": 0, "pointwise_coverage": 0.5}
                },
            }
            for value in [-1, 1]
        ]
        summary = aggregate(records, 2)
        self.assertEqual(summary["bias"], 0)
        self.assertAlmostEqual(summary["bias_mcse"], 1)
        self.assertEqual(summary["mse"], 1)
        self.assertGreater(summary["failure_rate_wilson95"][1], 0)
        self.assertEqual(summary["procedural_pointwise_coverage"], 0.5)


if __name__ == "__main__":
    unittest.main()

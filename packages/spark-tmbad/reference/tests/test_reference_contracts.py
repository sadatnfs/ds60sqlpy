"""Pure source, lock, data-only admission and simulation-accounting contracts."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import io
import json
import ssl
import sys
import tarfile
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest.mock import patch

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

    def test_dependency_lock_must_match_actual_archive_description(self):
        raw = b"Package: example\nVersion: 1.0\nDepends: R (>= 4.4),\n methods\n"
        entry = {
            "name": "example",
            "version": "1.0",
            "dependencies": {"Depends": "R (>= 4.4), methods", "Imports": "", "LinkingTo": ""},
            "description_sha256": hashlib.sha256(raw).hexdigest(),
        }
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "example.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                item = tarfile.TarInfo("example/DESCRIPTION")
                item.size = len(raw)
                stream.addfile(item, io.BytesIO(raw))
            prepare.verify_archive_metadata(archive, entry)
            altered = copy.deepcopy(entry)
            altered["dependencies"]["Depends"] = "R (>= 4.7), methods"
            with self.assertRaisesRegex(ValueError, "metadata differs"):
                prepare.verify_archive_metadata(archive, altered)
            altered = copy.deepcopy(entry)
            altered["description_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "hash differs"):
                prepare.verify_archive_metadata(archive, altered)

    def test_repeated_description_fields_are_rejected(self):
        raw = b"Package: example\nVersion: 1.0\nVersion: 2.0\n"
        with tempfile.TemporaryDirectory() as temporary:
            archive = Path(temporary) / "example.tar.gz"
            with tarfile.open(archive, "w:gz") as stream:
                item = tarfile.TarInfo("example/DESCRIPTION")
                item.size = len(raw)
                stream.addfile(item, io.BytesIO(raw))
            with self.assertRaisesRegex(ValueError, "repeated"):
                prepare.verify_archive_metadata(archive, {"name": "example"})

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

    def test_transient_reset_and_timeout_retry_once_then_verify(self):
        payload = b"exact pinned archive bytes"
        entry = {
            "url": "https://cran.r-project.org/src/contrib/example_1.0.tar.gz",
            "sha256": hashlib.sha256(payload).hexdigest(),
        }
        failures = (
            urllib.error.URLError(ConnectionResetError(104, "connection reset")),
            urllib.error.URLError(TimeoutError("read timed out")),
            TimeoutError("connect timed out"),
        )
        for failure in failures:
            with (
                self.subTest(error=type(failure).__name__),
                tempfile.TemporaryDirectory() as temporary,
            ):
                destination = Path(temporary) / "source.tar.gz"
                with (
                    patch.object(
                        prepare.urllib.request,
                        "urlopen",
                        side_effect=[failure, io.BytesIO(payload)],
                    ) as opener,
                    patch.object(prepare.time, "sleep") as sleeper,
                ):
                    self.assertEqual(
                        prepare.acquire(entry, destination.name, None, destination, True),
                        destination,
                    )
                self.assertEqual(destination.read_bytes(), payload)
                self.assertEqual(opener.call_count, 2)
                self.assertEqual(sleeper.call_count, 1)
                self.assertEqual(opener.call_args.kwargs["timeout"], 90)

    def test_transient_transport_exhaustion_is_bounded(self):
        entry = {
            "url": "https://cran.r-project.org/src/contrib/example_1.0.tar.gz",
            "sha256": hashlib.sha256(b"expected").hexdigest(),
        }
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "source.tar.gz"
            with (
                patch.object(
                    prepare.urllib.request,
                    "urlopen",
                    side_effect=urllib.error.URLError(ConnectionResetError(104, "reset")),
                ) as opener,
                patch.object(prepare.time, "sleep") as sleeper,
                self.assertRaisesRegex(RuntimeError, "five transport attempts"),
            ):
                prepare.acquire(entry, destination.name, None, destination, True)
            self.assertEqual(opener.call_count, 5)
            self.assertEqual(sleeper.call_count, 4)
            self.assertFalse(destination.exists())

    def test_certificate_failure_is_not_retried(self):
        entry = {
            "url": "https://cran.r-project.org/src/contrib/example_1.0.tar.gz",
            "sha256": hashlib.sha256(b"expected").hexdigest(),
        }
        certificate = ssl.SSLCertVerificationError(1, "certificate verify failed")
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "source.tar.gz"
            with (
                patch.object(
                    prepare.urllib.request,
                    "urlopen",
                    side_effect=urllib.error.URLError(certificate),
                ) as opener,
                patch.object(prepare.time, "sleep") as sleeper,
                self.assertRaisesRegex(RuntimeError, "nontransient transport"),
            ):
                prepare.acquire(entry, destination.name, None, destination, True)
            self.assertEqual(opener.call_count, 1)
            sleeper.assert_not_called()
            self.assertFalse(destination.exists())

    def test_downloaded_bad_hash_is_not_retried(self):
        entry = {
            "url": "https://cran.r-project.org/src/contrib/example_1.0.tar.gz",
            "sha256": hashlib.sha256(b"expected").hexdigest(),
        }
        with tempfile.TemporaryDirectory() as temporary:
            destination = Path(temporary) / "source.tar.gz"
            with (
                patch.object(
                    prepare.urllib.request, "urlopen", return_value=io.BytesIO(b"bad")
                ) as opener,
                patch.object(prepare.time, "sleep") as sleeper,
                self.assertRaisesRegex(ValueError, "hash/size mismatch"),
            ):
                prepare.acquire(entry, destination.name, None, destination, True)
            self.assertEqual(opener.call_count, 1)
            sleeper.assert_not_called()
            self.assertFalse(destination.exists())

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

    def test_fixed_data_posterior_draw_replays_do_not_invent_dataset_mcse(self):
        records = [
            {
                "status": "passed",
                "result": {
                    "fixture_sha256": "a" * 64,
                    "metrics": {"primary_estimate": 0.7, "truth": 0.8},
                },
            }
            for _ in range(4)
        ]
        for fixed in [False, True]:
            summary = aggregate(records, 4, fixed_dataset=fixed)
            self.assertEqual(summary["distinct_observed_dataset_hashes"], 1)
            self.assertTrue(summary["repeated_observed_dataset"])
            self.assertFalse(summary["dataset_monte_carlo_uncertainty"])
            self.assertIsNone(summary["bias_mcse"])
            self.assertIsNone(summary["mse_mcse"])
            self.assertIsNone(summary["failure_rate_wilson95"])
            self.assertAlmostEqual(summary["bias"], -0.1)

    def test_predictive_mse_is_separate_from_parameter_mse(self):
        records = [
            {
                "status": "passed",
                "result": {"metrics": {"primary_estimate": 1, "truth": 1, "mse": value}},
            }
            for value in [1, 9]
        ]
        summary = aggregate(records, 2)
        self.assertEqual(summary["mse"], 0)
        self.assertEqual(summary["prediction_mse_conditional_on_success"], 5)
        self.assertEqual(summary["prediction_mse_mcse_across_datasets"], 4)


if __name__ == "__main__":
    unittest.main()

"""Tests for the python-pro-01 reference implementation."""

from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

from python.professional.solutions.py_pro_01_package_engineering_solution import (
    FIXTURE,
    build_distributions,
    classify_artifact,
    install_wheel_and_prove,
    summarize_project,
)


class PackageEngineeringTests(unittest.TestCase):
    def test_fixture_has_the_expected_packaging_contract(self) -> None:
        summary = summarize_project()

        self.assertEqual(summary.name, "ds60-tiny-greeter")
        self.assertEqual(summary.build_backend, "setuptools.build_meta")
        self.assertEqual(
            summary.console_scripts,
            {"ds60-greet": "ds60_tiny_greeter.cli:main"},
        )
        self.assertEqual(summary.dependency_groups, ("quality", "test"))
        self.assertEqual(summary.optional_dependencies, ("pretty",))

    def test_artifact_classification_uses_complete_suffixes(self) -> None:
        self.assertEqual(classify_artifact(Path("demo-1.0.whl")), "wheel")
        self.assertEqual(
            classify_artifact(Path("demo-1.0.tar.gz")),
            "source distribution",
        )
        with self.assertRaises(ValueError):
            classify_artifact(Path("demo.whl.txt"))

    @unittest.skipUnless(
        all(
            importlib.util.find_spec(name) is not None for name in ("build", "setuptools", "wheel")
        ),
        "offline build tools are not installed in this interpreter",
    )
    def test_wheel_install_imports_from_fresh_target(self) -> None:
        generated_before = {
            path.relative_to(FIXTURE)
            for pattern in ("*.egg-info", "build", "dist")
            for path in FIXTURE.rglob(pattern)
        }
        with tempfile.TemporaryDirectory(prefix="ds60-package-test-") as directory:
            workspace = Path(directory)
            wheel, sdist = build_distributions(FIXTURE, workspace / "dist")
            proof = install_wheel_and_prove(wheel, workspace)

            self.assertEqual(classify_artifact(sdist), "source distribution")
            self.assertTrue(proof.import_origin.is_relative_to(proof.install_target))
            self.assertEqual(proof.distribution_version, "0.1.0")
            self.assertIn("ds60-greet", proof.console_scripts)
            self.assertEqual(proof.command_output, "Hello, wheel!")
        generated_after = {
            path.relative_to(FIXTURE)
            for pattern in ("*.egg-info", "build", "dist")
            for path in FIXTURE.rglob(pattern)
        }
        self.assertEqual(generated_after, generated_before)


if __name__ == "__main__":
    unittest.main()

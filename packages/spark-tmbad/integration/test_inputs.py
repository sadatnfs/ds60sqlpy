"""Pure negative checks for wheel, artifact, native image and ownership admission."""

from __future__ import annotations

import copy
import importlib.util
import json
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

SPEC = importlib.util.spec_from_file_location(
    "integration_inputs", Path(__file__).with_name("inputs.py")
)
assert SPEC is not None and SPEC.loader is not None
inputs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(inputs)


class InputContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "source"
        self.source.mkdir()
        (self.source / "__init__.py").write_text('VALUE = "source-bound"\n')
        self.wheel = self.root / "example_package-0.1.0-py3-none-any.whl"

    def write_wheel(self, extra=(), version="0.1.0", source=b'VALUE = "source-bound"\n'):
        with warnings.catch_warnings(), zipfile.ZipFile(self.wheel, "w") as archive:
            warnings.simplefilter("ignore", UserWarning)
            archive.writestr("example_package/__init__.py", source)
            archive.writestr(
                "example_package-0.1.0.dist-info/METADATA",
                f"Name: example-package\nVersion: {version}\n",
            )
            for name, content in extra:
                archive.writestr(name, content)

    def admit(self):
        return inputs.wheel_identity(self.wheel, self.source, "example_package", "0.1.0")

    def test_valid_exact_wheel_source_is_identified(self):
        self.write_wheel()
        self.assertEqual(
            self.admit()["python_source_sha256"],
            {"__init__.py": inputs.digest(self.source / "__init__.py")},
        )

    def test_stale_code_or_metadata_is_rejected(self):
        self.write_wheel(source=b"VALUE = 'different'\n")
        with self.assertRaisesRegex(ValueError, "exactly match"):
            self.admit()
        self.write_wheel(version="0.0.9")
        with self.assertRaisesRegex(ValueError, "distribution/version"):
            self.admit()

    def test_duplicate_traversal_and_unexpected_startup_code_are_rejected(self):
        for name in [
            "example_package/__init__.py",
            "example_package/../escape.py",
            "sitecustomize.py",
        ]:
            self.write_wheel(extra=[(name, b"# unexpected\n")])
            with self.assertRaisesRegex(ValueError, "Unexpected or duplicate"):
                self.admit()

    def test_non_zip_wheel_is_rejected_before_runtime(self):
        self.wheel.write_bytes(b"not a wheel")
        with self.assertRaisesRegex(ValueError, "Malformed"):
            self.admit()

    def test_source_symlink_is_not_accepted_as_copied_source(self):
        self.write_wheel()
        (self.source / "alias.py").symlink_to(self.source / "__init__.py")
        with self.assertRaisesRegex(ValueError, "symlinks"):
            self.admit()

    def test_only_native_linux_images_without_implicit_volumes_are_accepted(self):
        image = {"Id": "sha256:" + "a" * 64, "Os": "linux", "Architecture": "arm64", "Config": {}}
        engine = {"Architecture": "aarch64"}
        self.assertEqual(inputs.image_identity(image, engine), "arm64")
        for replacement in [
            {"Architecture": "amd64"},
            {"Os": "windows"},
            {"Config": {"Volumes": {"/state": {}}}},
            {"Id": "moving:tag"},
        ]:
            with self.assertRaises(ValueError):
                inputs.image_identity({**image, **replacement}, engine)

    def test_container_alias_or_other_project_cannot_be_operated_on(self):
        value = {
            "Id": "owned-id",
            "Config": {
                "Labels": {"com.docker.compose.project": "owned-project", "ds60.owner": "owner"}
            },
        }
        self.assertEqual(
            inputs.container_identity([value], "owned-id", "owned-project", "owner"), value
        )
        for identifier, project, owner in [
            ("other-id", "owned-project", "owner"),
            ("owned-id", "other-project", "owner"),
            ("owned-id", "owned-project", "other-owner"),
        ]:
            with self.assertRaises(ValueError):
                inputs.container_identity([value], identifier, project, owner)

    def native_fixture(self):
        package = self.root / "package"
        for name in ["native", "tooling", "jvm/src/main/scala"]:
            (package / name).mkdir(parents=True)
        for name in [
            "native/model.cpp",
            "tooling/build.py",
            "jvm/build.py",
            "jvm/src/main/scala/Model.scala",
        ]:
            (package / name).write_text("synthetic static-admission fixture\n")
        installation = self.root / "installation"
        installation.mkdir()
        for name in ["tmbad-worker", "spark-tmbad.jar"]:
            (installation / name).write_bytes(b"synthetic artifact, never executed")
        manifest = {
            "kind": "spark-tmbad-artifact",
            "schema_version": 1,
            "protocol": 1,
            "package_version": "0.1.0",
            "platform": {"os": "linux", "arch": "arm64"},
            "build_id": "fixture",
        }
        for key, filename in [("binary", "tmbad-worker"), ("jvm", "spark-tmbad.jar")]:
            manifest[key] = {
                "path": "/opt/spark-tmbad/" + filename,
                "sha256": inputs.digest(installation / filename),
            }
        native = {
            "native_source": inputs.file_inventory(package / "native"),
            "build_scripts": inputs.file_inventory(package / "tooling"),
            "build_id": "fixture",
            "binary_sha256": manifest["binary"]["sha256"],
        }
        jvm = {
            "jar_sha256": manifest["jvm"]["sha256"],
            "include_tests": False,
            "build_script_sha256": inputs.digest(package / "jvm/build.py"),
            "source_sha256": {
                "src/main/scala/Model.scala": inputs.digest(
                    package / "jvm/src/main/scala/Model.scala"
                )
            },
        }
        for name, data in [
            ("artifact.json", manifest),
            ("native-build.json", native),
            ("jvm-build.json", jvm),
        ]:
            (installation / name).write_text(json.dumps(data))
        return installation, package, manifest

    def test_native_wrong_platform_or_mutated_artifact_is_rejected(self):
        installation, package, _ = self.native_fixture()
        self.assertEqual(
            inputs.native_identity(installation, package, "arm64", "0.1.0")["build_id"], "fixture"
        )
        with self.assertRaisesRegex(ValueError, "platform identity"):
            inputs.native_identity(installation, package, "amd64", "0.1.0")
        (installation / "spark-tmbad.jar").write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "path/hash"):
            inputs.native_identity(installation, package, "arm64", "0.1.0")

    def test_native_stale_source_receipt_or_manifest_path_is_rejected(self):
        installation, package, manifest = self.native_fixture()
        altered = copy.deepcopy(manifest)
        altered["binary"]["path"] = "/unexpected/worker"
        (installation / "artifact.json").write_text(json.dumps(altered))
        with self.assertRaisesRegex(ValueError, "path/hash"):
            inputs.native_identity(installation, package, "arm64", "0.1.0")
        (installation / "artifact.json").write_text(json.dumps(manifest))
        (package / "tooling/build.py").write_text("changed preparation source\n")
        with self.assertRaisesRegex(ValueError, "copied source"):
            inputs.native_identity(installation, package, "arm64", "0.1.0")


if __name__ == "__main__":
    unittest.main()

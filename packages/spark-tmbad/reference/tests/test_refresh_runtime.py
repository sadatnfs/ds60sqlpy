"""Changed-condition guards for offline runtime-source refresh, without R or builds."""

from __future__ import annotations

import ast
import copy
import hashlib
import importlib.util
import io
import json
import os
import shutil
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "refresh_reference_runtime", ROOT / "refresh_runtime.py"
)
assert SPEC is not None and SPEC.loader is not None
refresh = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(refresh)


def sha(data):
    return hashlib.sha256(data).hexdigest()


def write_json(path, data):
    path.write_text(json.dumps(data) + "\n")


def archive(path, member, data):
    with tarfile.open(path, "w:gz") as stream:
        item = tarfile.TarInfo(member)
        item.size = len(data)
        stream.addfile(item, io.BytesIO(data))


class RefreshTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name).resolve()
        self.old = self.directory / "old-source"
        self.current = self.directory / "source"
        self.prepared = self.directory / "prepared"
        self.output = self.directory / "fresh"
        for name in ("models", "R", "python", "tests", "licenses"):
            (self.old / name).mkdir(parents=True)
        for name in ("models", "sources", "library/TMB", "library/glmmTMB"):
            (self.prepared / name).mkdir(parents=True)
        tree = ast.parse((ROOT / "prepare.py").read_text())
        replaced = 0
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.List)
                and all(isinstance(item, ast.Constant) for item in node.elts)
                and [item.value for item in node.elts]
                == refresh.BASE_INVENTORY + refresh.EXTRA_INVENTORY
            ):
                node.elts = node.elts[:3]
                replaced += 1
        self.assertEqual(replaced, 1)
        (self.old / "prepare.py").write_text(ast.unparse(tree) + "\n")
        for name in ("common.R", "glmm_cases.R", "run.R", "compile.R"):
            (self.old / "R" / name).write_text("value <- 1\n")
        (self.old / "tests/pure.R").write_text("stopifnot(TRUE)\n")
        (self.old / "python/client.py").write_text("VALUE = 1\n")
        (self.old / "models/example.cpp").write_text("// Original MIT template\n")
        (self.old / "LICENSE").write_text("MIT\n")
        (self.old / "NOTICE.md").write_text("Retain upstream AGPL-3\n")
        (self.old / "licenses/AGPL-3.0.txt").write_text("Retained license fixture\n")
        write_json(self.old / "registry.json", {"models": ["example"], "cases": {}})
        raw = b"Package: TMB\nVersion: 1.0\n"
        archive(self.prepared / "sources/TMB_1.0.tar.gz", "TMB/DESCRIPTION", raw)
        revision = "1db3b4692aa4c61ae5c9974b32b9f91555cf5f2c"
        prefix = "glmmTMB-" + revision + "/glmmTMB/"
        archive(
            self.prepared / "sources/glmmTMB-pinned.tar.gz",
            prefix + "DESCRIPTION",
            b"Package: glmmTMB\nVersion: 1.0\n",
        )
        self.lock = {
            "schema_version": 1,
            "r_version": "4.6.1",
            "packages": [
                {
                    "name": "TMB",
                    "version": "1.0",
                    "sha256": refresh.digest(self.prepared / "sources/TMB_1.0.tar.gz"),
                    "description_sha256": sha(raw),
                    "dependencies": {"Depends": "", "Imports": "", "LinkingTo": ""},
                }
            ],
            "upstream": {
                "name": "glmmTMB",
                "version": "1.0",
                "revision": revision,
                "sha256": refresh.digest(self.prepared / "sources/glmmTMB-pinned.tar.gz"),
                "package_prefix": prefix,
                "license": "AGPL-3",
            },
        }
        write_json(self.old / "dependencies.lock.json", self.lock)
        for name in ("TMB", "glmmTMB"):
            root = self.prepared / "library" / name
            (root / "DESCRIPTION").write_text(
                "Package: "
                + name
                + "\nVersion: 1.0\nBuilt: R 4.6.1; aarch64-unknown-linux-gnu; 2026-10-30; unix\n"
            )
            (root / "NAMESPACE").write_text("# fixture\n")
            (root / "libs").mkdir()
            (root / "libs" / (name + ".so")).write_bytes(b"immutable-native-fixture")
            (root / "extra-file").write_text("Newly observed, not historically hashed\n")
        shutil.copy2(self.old / "models/example.cpp", self.prepared / "models/example.cpp")
        (self.prepared / "models/example.so").write_bytes(b"compiled-template")
        self.compiled = {
            "models": {
                "example": {
                    "library": "models/example.so",
                    "sha256": refresh.digest(self.prepared / "models/example.so"),
                    "source_sha256": refresh.digest(self.old / "models/example.cpp"),
                    "flags": "-O1 -g0",
                    "framework": "CppAD",
                }
            },
            "r_version": "4.6.1",
            "architecture": "aarch64",
            "packages": {"TMB": "1.0", "glmmTMB": "1.0"},
        }
        write_json(self.prepared / "models/compile.json", self.compiled)
        self.manifest = {
            "schema_version": 1,
            "kind": refresh.KIND,
            **self.compiled,
            "source_sha256": refresh.executable_sources(self.old, extended=False),
            "package_files": {
                name: {
                    path: sha
                    for path, sha in refresh.inventory(self.prepared / "library" / name).items()
                    if path != "extra-file"
                }
                for name in ("TMB", "glmmTMB")
            },
            "upstream_revision": revision,
            "upstream_archive_sha256": self.lock["upstream"]["sha256"],
            "upstream_license": "AGPL-3",
            "scope": "preparation only",
        }
        write_json(self.prepared / "manifest.json", self.manifest)
        self.expected = refresh.digest(self.prepared / "manifest.json")
        shutil.copytree(self.old, self.current)
        shutil.copy2(ROOT / "prepare.py", self.current / "prepare.py")
        shutil.copy2(ROOT / "refresh_runtime.py", self.current / "refresh_runtime.py")
        self.allowed = ["R/common.R", "R/glmm_cases.R", "R/run.R", "tests/pure.R"]
        for name in self.allowed:
            with (self.current / name).open("a") as stream:
                stream.write("# Controller revision\n")
        self.identity = {
            "r_version": "4.6.1",
            "architecture": "aarch64",
            "platform": "aarch64-unknown-linux-gnu",
            "dynlib_ext": ".so",
            "packages": {"TMB": "1.0", "glmmTMB": "1.0"},
        }

    def run_refresh(self):
        return refresh.refresh(
            self.prepared,
            self.old,
            self.current,
            self.output,
            self.expected,
            self.allowed,
        )

    def guarded_failure(self, pattern):
        with mock.patch.object(refresh, "checks", return_value=self.identity) as checks:
            with self.assertRaisesRegex(ValueError, pattern):
                self.run_refresh()
            checks.assert_not_called()
        self.assertFalse((self.output / "manifest.json").exists())

    def test_success_copies_bytes_and_provenance_without_changing_old_preparation(self):
        before = refresh.inventory(self.prepared)
        old_source = refresh.inventory(self.old)
        with mock.patch.object(refresh, "checks", return_value=self.identity):
            report = self.run_refresh()
        self.assertEqual(report["numerical_acceptance"], "not_run")
        self.assertEqual(refresh.inventory(self.prepared), before)
        self.assertEqual(refresh.inventory(self.old), old_source)
        self.assertEqual(
            (self.output / "provenance/old-manifest.json").read_bytes(),
            (self.prepared / "manifest.json").read_bytes(),
        )
        manifest = refresh.read_json(self.output / "manifest.json")
        self.assertFalse(manifest["refresh"]["installed_or_compiled"])
        self.assertEqual(
            set(manifest["refresh"]["runtime_changes"]),
            set(self.allowed) | {"prepare.py"},
        )
        self.assertEqual(
            manifest["source_sha256"],
            refresh.executable_sources(self.current, extended=True),
        )
        self.assertEqual(manifest["refresh"]["old_manifest_sha256"], self.expected)
        observed = refresh.read_json(self.output / "provenance/reused-files.json")
        self.assertIn("library/TMB/extra-file", observed)
        self.assertTrue(manifest["refresh"]["additional_reused_hashes_observed_now"])
        self.assertNotEqual(
            (self.output / "models/example.so").stat().st_ino,
            (self.prepared / "models/example.so").stat().st_ino,
        )

    def test_manifest_digest_mismatch(self):
        self.expected = "0" * 64
        self.guarded_failure("manifest SHA256")

    def test_old_source_mutation(self):
        (self.old / "R/common.R").write_text("modified\n")
        self.guarded_failure("Hash mismatch")

    def test_template_dll_mutation(self):
        (self.prepared / "models/example.so").write_text("modified")
        self.guarded_failure("Hash mismatch")

    def test_dependency_dll_mutation(self):
        (self.prepared / "library/TMB/libs/TMB.so").write_text("modified")
        self.guarded_failure("Hash mismatch")

    def test_archive_mutation(self):
        (self.prepared / "sources/TMB_1.0.tar.gz").write_text("modified")
        self.guarded_failure("Hash mismatch")

    def test_upstream_archive_mutation(self):
        (self.prepared / "sources/glmmTMB-pinned.tar.gz").write_text("modified")
        self.guarded_failure("Hash mismatch")

    def test_compile_metadata_mutation(self):
        altered = copy.deepcopy(self.compiled)
        altered["models"]["example"]["flags"] = "-O3"
        write_json(self.prepared / "models/compile.json", altered)
        self.guarded_failure("Compile metadata")

    def test_changed_build_inputs_are_not_runtime_changes(self):
        for path in (
            "models/example.cpp",
            "R/compile.R",
            "registry.json",
            "dependencies.lock.json",
        ):
            original = (self.current / path).read_bytes()
            (self.current / path).write_bytes(original + b"\n")
            with self.subTest(path=path):
                self.guarded_failure("immutable build change")
            (self.current / path).write_bytes(original)

    def test_undeclared_controller_change(self):
        self.allowed.remove("R/run.R")
        self.guarded_failure("Undeclared runtime")

    def test_build_script_cannot_be_explicitly_allowed(self):
        self.allowed.append("R/compile.R")
        self.guarded_failure("Not an allowed runtime")

    def test_unnecessary_declaration_is_rejected(self):
        self.allowed.append("python/client.py")
        self.guarded_failure("did not change")

    def test_new_controller_inventory_is_rejected(self):
        (self.current / "R/additional.R").write_text("1\n")
        self.guarded_failure("Source inventory changed")

    def test_altered_preparation_logic_is_rejected(self):
        path = self.current / "prepare.py"
        path.write_text(path.read_text().replace("80_000_000", "90_000_000"))
        self.guarded_failure("Preparation logic")

    def test_inventory_normalization_does_not_allow_an_unrelated_matching_list(self):
        old = "x = ['prepare.py', 'dependencies.lock.json', 'registry.json']\n"
        new = old + "y = " + repr(refresh.BASE_INVENTORY + refresh.EXTRA_INVENTORY) + "\n"
        self.assertFalse(refresh.preparer_compatible(old, new))
        self.assertFalse(refresh.preparer_compatible(old, old))

    def test_insufficient_space_refuses_before_any_copy_or_output_directory(self):
        with (
            mock.patch.object(refresh.shutil, "disk_usage", return_value=SimpleNamespace(free=0)),
            mock.patch.object(refresh, "copy_checked") as copier,
            mock.patch.object(refresh, "checks") as checker,
            self.assertRaisesRegex(ValueError, "Insufficient free space"),
        ):
            self.run_refresh()
        copier.assert_not_called()
        checker.assert_not_called()
        self.assertFalse(self.output.exists())

    def test_existing_output_is_preserved(self):
        self.output.mkdir()
        (self.output / "sentinel").write_text("preserve")
        self.guarded_failure("fresh output")
        self.assertEqual((self.output / "sentinel").read_text(), "preserve")

    def test_overlapping_output_is_rejected(self):
        self.output = self.prepared / "nested"
        self.guarded_failure("overlaps input")

    def test_symlink_source_and_parent_component_are_rejected(self):
        path = self.current / "R/common.R"
        path.unlink()
        path.symlink_to(self.old / "R/common.R")
        self.guarded_failure("Symlink")
        path.unlink()
        path.write_text("value <- 2\n")
        alias = self.directory / "alias"
        alias.symlink_to(self.current, target_is_directory=True)
        self.current = alias
        self.guarded_failure("Symlink")

    def test_description_symlink_is_rejected_before_reading(self):
        alias = self.directory / "description-alias"
        alias.symlink_to(self.prepared / "library/TMB/DESCRIPTION")
        with self.assertRaisesRegex(ValueError, "Symlink"):
            refresh.description(alias)

    def test_unrecorded_library_symlink_is_rejected(self):
        (self.prepared / "library/TMB/escape").symlink_to(self.old / "LICENSE")
        self.guarded_failure("Symlink")

    def test_path_traversal_and_duplicate_json_are_rejected(self):
        for path in ("../escape", "/absolute", "a/../b", "a\\b", "a//b", "./file"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                refresh.relative(path)
        path = self.directory / "repeated.json"
        path.write_text('{"one": 1, "one": 2}')
        with self.assertRaisesRegex(ValueError, "Repeated JSON"):
            refresh.read_json(path)

    def test_parse_or_pure_failure_has_no_success_manifest(self):
        with (
            mock.patch.object(refresh, "checks", side_effect=ValueError("pure failed")),
            self.assertRaisesRegex(ValueError, "pure failed"),
        ):
            self.run_refresh()
        self.assertFalse((self.output / "manifest.json").exists())
        self.assertEqual(refresh.read_json(self.output / "failure.json")["status"], "failed")

    def test_input_mutation_during_checks_is_rejected(self):
        def mutate(*args):
            (self.prepared / "library/TMB/extra-file").write_text("changed after copy")
            return self.identity

        with (
            mock.patch.object(refresh, "checks", side_effect=mutate),
            self.assertRaisesRegex(ValueError, "Artifact changed"),
        ):
            self.run_refresh()
        self.assertFalse((self.output / "manifest.json").exists())

    def test_snapshot_mutation_during_checks_is_rejected(self):
        def mutate(*args):
            (self.output / "source/R/common.R").write_text("changed after parse")
            return self.identity

        with (
            mock.patch.object(refresh, "checks", side_effect=mutate),
            self.assertRaisesRegex(ValueError, "Source snapshot changed"),
        ):
            self.run_refresh()
        self.assertFalse((self.output / "manifest.json").exists())

    def test_copy_rejects_changed_readback(self):
        actual = refresh.inventory(self.prepared / "models")
        actual["example.so"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "changed during copy"):
            refresh.copy_checked(self.prepared / "models", self.output, actual)

    def test_r_checks_verify_identity_parse_and_pure_only(self):
        self.output.mkdir()
        shutil.copytree(self.current, self.output / "source")
        shutil.copytree(self.prepared / "library", self.output / "library")
        (self.output / "logs").mkdir()
        commands = []

        def run(command, log, environment, timeout):
            commands.append(command)
            self.assertEqual(environment["R_LIBS_USER"], str(self.output / "library"))
            self.assertEqual(environment["HOME"], str(self.output / "check-home"))
            self.assertLessEqual(timeout, 180)
            if log.name == "identity.json":
                write_json(log, self.identity)
            else:
                log.write_text("passed")

        with mock.patch.object(refresh, "run_bounded", side_effect=run):
            observed = refresh.checks(
                self.output,
                {"TMB": "1.0", "glmmTMB": "1.0"},
                self.manifest,
                self.identity["platform"],
            )
        self.assertEqual(observed, self.identity)
        self.assertEqual(len(commands), 3)
        self.assertTrue(all(command[:2] == ["Rscript", "--vanilla"] for command in commands))
        self.assertEqual(commands[-1][2], str(self.output / "source/tests/pure.R"))
        self.assertFalse(
            any(
                "compile.R" in argument or "INSTALL" in argument
                for command in commands
                for argument in command
            )
        )
        parsed_paths = (self.output / "logs/r-sources.txt").read_text()
        self.assertIn("R/compile.R", parsed_paths)

    def test_wrong_runtime_identity_fails_before_pure_checks(self):
        for field, value in (
            ("architecture", "x86_64"),
            ("r_version", "4.6.0"),
            ("platform", "other-linux"),
            ("dynlib_ext", ".dll"),
        ):
            output = self.directory / field
            output.mkdir()
            (output / "logs").mkdir()
            wrong = dict(self.identity, **{field: value})

            def run(command, log, environment, timeout, observed=wrong):
                write_json(log, observed)

            with (
                self.subTest(field=field),
                mock.patch.object(refresh, "run_bounded", side_effect=run) as runner,
            ):
                with self.assertRaisesRegex(ValueError, "native platform"):
                    refresh.checks(
                        output,
                        {"TMB": "1.0", "glmmTMB": "1.0"},
                        self.manifest,
                        self.identity["platform"],
                    )
                self.assertEqual(runner.call_count, 1)

    def test_owned_process_timeout_retains_bounded_log(self):
        with self.assertRaisesRegex(ValueError, "deadline"):
            refresh.run_bounded(
                [sys.executable, "-c", "import time; time.sleep(5)"],
                self.directory / "timeout.log",
                dict(os.environ),
                0,
            )
        self.assertLessEqual((self.directory / "timeout.log").stat().st_size, refresh.MAX_LOG)

    def test_owned_process_output_is_bounded(self):
        with self.assertRaises(ValueError):
            refresh.run_bounded(
                [sys.executable, "-c", "import os; os.write(1,b'x' * 3000000)"],
                self.directory / "large.log",
                dict(os.environ),
                5,
            )
        self.assertLessEqual((self.directory / "large.log").stat().st_size, refresh.MAX_LOG)


if __name__ == "__main__":
    unittest.main()

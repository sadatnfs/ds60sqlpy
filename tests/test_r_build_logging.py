"""R source-build diagnostics stay complete while repeated libsass traces shrink."""

from __future__ import annotations

import gzip
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "r_build_installer", ROOT / "docker/workers/r/install_packages.py"
)
assert SPEC is not None and SPEC.loader is not None
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)

WARNING = (
    b"src/ast.hpp:90:18: warning: virtual Sass::operator== was hidden [-Woverloaded-virtual=]\n"
    b"   90 |     virtual bool operator== (const AST_Node& rhs) const {\n"
    b"      |                  ^~~~~~~~\n"
    b"src/ast.hpp:165:18: note: by Sass::Expression::operator==\n"
    b"  165 |     virtual bool operator== (const Expression& rhs) const { return false; }\n"
    b"      |                  ^~~~~~~~\n"
)


class BuildLoggingTests(unittest.TestCase):
    def summarize(self, payload: bytes, name: str = "sass") -> tuple[str, bytes, dict[str, Any]]:
        output = io.StringIO()
        raw = io.BytesIO()
        summary = installer.DiagnosticSummary(name, output)
        stats = installer.copy_build_output(io.BytesIO(payload), raw, summary)
        return output.getvalue(), raw.getvalue(), {**stats, "repeated": summary.repeated_blocks}

    def test_exact_repetitions_shrink_but_raw_output_is_complete(self) -> None:
        payload = b"compiler command\n" + WARNING * 3 + b"* DONE (sass)\n"
        console, raw, stats = self.summarize(payload)
        self.assertEqual(console, (b"compiler command\n" + WARNING + b"* DONE (sass)\n").decode())
        self.assertEqual(raw, payload)
        self.assertEqual(stats["repeated"], 2)
        self.assertEqual(stats["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertEqual(stats["bytes"], len(payload))

    def test_changed_overload_note_is_a_new_diagnostic(self) -> None:
        different = WARNING.replace(b"by Sass::Expression", b"by Sass::CssMediaRule")
        payload = WARNING + different + WARNING
        console, raw, stats = self.summarize(payload)
        self.assertEqual(console, (WARNING + different).decode())
        self.assertEqual(raw, payload)
        self.assertEqual(stats["repeated"], 1)

    def test_other_package_and_other_warnings_remain_verbatim(self) -> None:
        payload = WARNING * 2 + b"Warning in setGenericS3.default: method overwritten\n"
        console, raw, stats = self.summarize(payload, "R.utils")
        self.assertEqual(console, payload.decode())
        self.assertEqual(raw, payload)
        self.assertEqual(stats["repeated"], 0)
        unknown = b"src/ast.hpp:90:18: warning: new problem [-Wconversion]\n 90 | code\n"
        console, _, _ = self.summarize(WARNING * 2 + unknown * 2)
        self.assertEqual(console, (WARNING + unknown * 2).decode())

    def test_error_and_unrecognized_context_are_not_swallowed(self) -> None:
        error = b"src/ast.hpp:90:18: error: actual compiler failure\n"
        payload = WARNING * 2 + error + b"unexpected tool output\n"
        console, raw, _ = self.summarize(payload)
        self.assertEqual(console, (WARNING + error + b"unexpected tool output\n").decode())
        self.assertEqual(raw, payload)

    def test_raw_non_utf8_and_unterminated_tail_are_retained(self) -> None:
        payload = WARNING * 2 + b"legacy byte \xff without final newline"
        console, raw, _ = self.summarize(payload)
        self.assertEqual(raw, payload)
        self.assertIn("legacy byte", console)
        self.assertTrue(console.endswith("without final newline"))

    def test_identity_limit_keeps_new_diagnostics_visible(self) -> None:
        different = WARNING.replace(b"by Sass::Expression", b"by Sass::CssMediaRule")
        with patch.object(installer, "_MAX_BLOCK_IDENTITIES", 1):
            console, _, _ = self.summarize(WARNING + different * 2)
        self.assertEqual(console, (WARNING + different * 2).decode())

    def test_successful_process_keeps_compressed_log_and_source_bound_receipt(self) -> None:
        payload = WARNING * 2 + b"* DONE (sass)\n"
        with tempfile.TemporaryDirectory() as temporary:
            output = io.StringIO()
            log_dir = Path(temporary)
            package = {"name": "sass", "version": "0.4.10", "sha256": "f" * 64}
            receipt = installer.run_logged_install(
                [sys.executable, "-c", "import os; os.write(1, " + repr(payload) + ")"],
                package,
                log_dir,
                output,
            )
            self.assertEqual(receipt["returncode"], 0)
            self.assertEqual(gzip.decompress((log_dir / receipt["log"]).read_bytes()), payload)
            self.assertEqual(receipt["archive_sha256"], package["sha256"])
            self.assertEqual(receipt["uncompressed"]["sha256"], hashlib.sha256(payload).hexdigest())
            self.assertEqual(json.loads((log_dir / "sass_0.4.10.json").read_text()), receipt)
            self.assertIn("Summarized 1 exact repeated", output.getvalue())
            self.assertNotIn("BEGIN COMPLETE FAILED", output.getvalue())

    def test_failed_process_replays_every_original_line_and_keeps_nonzero_status(self) -> None:
        payload = WARNING * 2 + b"fatal compiler failure\n"
        with tempfile.TemporaryDirectory() as temporary:
            output = io.StringIO()
            receipt = installer.run_logged_install(
                [
                    sys.executable,
                    "-c",
                    "import os; os.write(2, " + repr(payload) + "); raise SystemExit(17)",
                ],
                {"name": "sass", "version": "0.4.10", "sha256": "a" * 64},
                Path(temporary),
                output,
            )
            self.assertEqual(receipt["returncode"], 17)
            replay = output.getvalue().split("BEGIN COMPLETE FAILED R BUILD LOG: sass 0.4.10\n")[1]
            self.assertEqual(
                replay, payload.decode() + "END COMPLETE FAILED R BUILD LOG: exit 17\n"
            )

    def test_failed_install_stops_the_locked_closure_and_writes_manifest(self) -> None:
        package = {
            "name": "sass",
            "version": "0.4.10",
            "sha256": hashlib.sha256(b"fixture archive").hexdigest(),
            "url": "https://cloud.r-project.org/src/contrib/sass_0.4.10.tar.gz",
        }
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            lock = directory / "lock.json"
            lock.write_text(json.dumps({"schema_version": 1, "packages": [package, package]}))
            with (
                patch.object(
                    installer.urllib.request, "urlopen", return_value=io.BytesIO(b"fixture archive")
                ),
                patch.object(
                    installer, "run_logged_install", return_value={"returncode": 17}
                ) as run,
                patch.object(installer.subprocess, "run") as version_check,
                self.assertRaises(subprocess.CalledProcessError) as error,
            ):
                installer.main(lock, directory)
            self.assertEqual(error.exception.returncode, 17)
            self.assertEqual(run.call_count, 1)
            version_check.assert_not_called()
            manifest = json.loads((directory / "manifest.json").read_text())
            self.assertEqual(manifest["packages"], [{"returncode": 17}])


if __name__ == "__main__":
    unittest.main()

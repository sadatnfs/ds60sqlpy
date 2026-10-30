"""Evidence transport preserves bytes and refuses unsafe or mismatched exports."""

import copy
import json
import tempfile
import unittest
from pathlib import Path

from evidence import export_payload, retain_payload


class EvidenceTests(unittest.TestCase):
    def test_nested_binary_and_empty_files_round_trip(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch).resolve()
            source = root / "source"
            (source / "model").mkdir(parents=True)
            (source / "driver.json").write_text('{"status":"passed"}')
            (source / "model/.crc").write_bytes(b"\x00\xff")
            (source / "model/_SUCCESS").touch()
            payload = json.loads(json.dumps(export_payload(source)))
            self.assertEqual(retain_payload(payload, root / "saved"), 3)
            self.assertEqual((root / "saved/model/.crc").read_bytes(), b"\x00\xff")
            self.assertEqual(retain_payload(payload, root / "saved"), 3)

    def test_path_and_hash_failures_do_not_write(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch).resolve()
            (root / "source").mkdir()
            (root / "source/driver.json").write_text("{}")
            good = export_payload(root / "source")
            for name in ["../outside", "/outside", ".", "nested/../outside", "x\\outside"]:
                bad = copy.deepcopy(good)
                bad["files"][0]["path"] = name
                with self.assertRaises(ValueError):
                    retain_payload(bad, root / "saved")
            bad = copy.deepcopy(good)
            bad["files"][0]["sha256"] = "0" * 64
            with self.assertRaises(ValueError):
                retain_payload(bad, root / "saved")
            self.assertFalse((root / "saved").exists())

    def test_symlinks_collisions_and_existing_evidence_are_preserved(self):
        with tempfile.TemporaryDirectory() as scratch:
            root = Path(scratch).resolve()
            source = root / "source"
            source.mkdir()
            (source / "driver.json").write_text("{}")
            good = export_payload(source)
            bad = copy.deepcopy(good)
            duplicate = copy.deepcopy(bad["files"][0])
            duplicate["path"] = "DRIVER.JSON"
            bad["files"].append(duplicate)
            with self.assertRaises(ValueError):
                retain_payload(bad, root / "saved")
            (source / "linked").symlink_to(source / "driver.json")
            with self.assertRaises(ValueError):
                export_payload(source)
            saved = root / "saved"
            saved.mkdir()
            (saved / "driver.json").write_text("preserve")
            with self.assertRaises(ValueError):
                retain_payload(good, saved)
            self.assertEqual((saved / "driver.json").read_text(), "preserve")


if __name__ == "__main__":
    unittest.main()

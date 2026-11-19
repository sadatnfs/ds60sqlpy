"""Keep offline browser libraries and their licenses together and byte-identical."""

import hashlib
import json
from importlib import resources


def test_packaged_d3_matches_its_pinned_distribution_and_license() -> None:
    vendor = resources.files("ds60sqlpy").joinpath("assets/vendor")
    manifest = json.loads(vendor.joinpath("d3-manifest.json").read_text(encoding="utf-8"))
    assert manifest["package"] == "d3" and manifest["version"] == "7.9.0"
    assert manifest["license"] == "ISC"
    assert set(manifest["files"]) == {"d3.v7.9.0.min.js", "LICENSE.d3.txt"}
    for name, digest in manifest["files"].items():
        assert hashlib.sha256(vendor.joinpath(name).read_bytes()).hexdigest() == digest
    license_text = vendor.joinpath("LICENSE.d3.txt").read_text(encoding="utf-8")
    assert "Mike Bostock" in license_text
    assert "Permission to use, copy, modify, and/or distribute" in license_text


def test_packaged_code_editor_matches_its_recipe_manifest_and_license() -> None:
    vendor = resources.files("ds60sqlpy").joinpath("assets/vendor")
    manifest = json.loads(vendor.joinpath("codemirror-manifest.json").read_text(encoding="utf-8"))
    assert manifest["license"] == "MIT" and manifest["recipe"] == "scripts/codemirror-bundle"
    assert set(manifest["files"]) == {"codemirror.v6.min.js", "LICENSE.codemirror.txt"}
    for name, digest in manifest["files"].items():
        assert hashlib.sha256(vendor.joinpath(name).read_bytes()).hexdigest() == digest
    bundle = vendor.joinpath("codemirror.v6.min.js").read_text(encoding="utf-8")
    assert "DS60Editor" in bundle and "</script" not in bundle.lower()
    assert "Marijn Haverbeke" in vendor.joinpath("LICENSE.codemirror.txt").read_text("utf-8")

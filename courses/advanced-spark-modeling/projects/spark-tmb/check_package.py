"""Check the optional R reference consumes the installed pure core wheel."""

from __future__ import annotations

import hashlib
import importlib.metadata
import json
import sys
from pathlib import Path
from zipfile import ZipFile

import ds60_spark_likelihood as package

root = Path(package.__file__).resolve().parent
distribution = importlib.metadata.distribution("ds60-spark-likelihood")
assert "site-packages" in root.parts
assert root == distribution.locate_file("ds60_spark_likelihood").resolve()
assert distribution.read_text("WHEEL") is not None
direct_url = distribution.read_text("direct_url.json")
assert not direct_url or not json.loads(direct_url).get("dir_info", {}).get("editable")
assert not any(name == "ds60sqlpy" or name.startswith("ds60sqlpy.") for name in sys.modules)
assert "torch" not in sys.modules
wheels = list(Path("/opt/ds60-wheels").glob("ds60_spark_likelihood-*.whl"))
assert len(wheels) == 1
files = {
    str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(root.rglob("*.py"))
}
source = Path("/opt/ds60-package-source/src/ds60_spark_likelihood")
declared = {
    str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
    for path in sorted(source.rglob("*.py"))
}
with ZipFile(wheels[0]) as archive:
    assert len(archive.namelist()) == len(set(archive.namelist()))
    packaged = {
        name.removeprefix("ds60_spark_likelihood/"): hashlib.sha256(archive.read(name)).hexdigest()
        for name in archive.namelist()
        if name.startswith("ds60_spark_likelihood/") and name.endswith(".py")
    }
assert files and files == declared == packaged
print(
    json.dumps(
        {
            "case": "reference-package",
            "passed": True,
            "role": "optional-r-tmb-reference",
            "distribution": "ds60-spark-likelihood",
            "version": distribution.version,
            "installed_path": str(root),
            "wheel_sha256": hashlib.sha256(wheels[0].read_bytes()).hexdigest(),
            "installed_source_sha256": files,
            "declared_source_sha256": declared,
            "wheel_source_sha256": packaged,
            "isolated_python": bool(sys.flags.isolated),
            "classroom_imported": False,
            "torch_imported": False,
        },
        sort_keys=True,
        allow_nan=False,
    )
)

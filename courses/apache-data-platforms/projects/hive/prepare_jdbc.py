"""Prepare one pinned public JDBC artifact; no lesson-time dependency fetch."""

import hashlib
import urllib.request
from pathlib import Path

URL = "https://repo.maven.apache.org/maven2/org/postgresql/postgresql/42.7.5/postgresql-42.7.5.jar"
SHA256 = "69020b3bd20984543e817393f2e6c01a890ef2e37a77dd11d6d8508181d079ab"
path = Path("/project/.workshop/postgresql.jar")
if path.is_symlink() or path.parent.is_symlink():
    raise ValueError("Refusing symbolic preparation paths")
if path.exists():
    if not path.is_file() or path.stat().st_size > 2000000:
        raise ValueError("Existing JDBC cache exceeds the regular-file size contract")
    data = path.read_bytes()
else:
    with urllib.request.urlopen(URL, timeout=30) as response:
        if response.geturl() != URL:
            raise ValueError("Unexpected JDBC artifact redirect")
        data = response.read(2000001)
if len(data) > 2000000 or hashlib.sha256(data).hexdigest() != SHA256:
    raise ValueError("JDBC size or SHA256 mismatch")
if not path.exists():
    path.parent.mkdir(exist_ok=True)
    with path.open("xb") as output:
        output.write(data)
print("Pinned PostgreSQL42.7.5 JDBC artifact is verified")

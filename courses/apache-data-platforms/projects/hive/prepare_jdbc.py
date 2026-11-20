"""Prepare one pinned public JDBC artifact; no lesson-time dependency fetch."""

import hashlib
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


def open_download(source: Any, timeout: float, attempts: int = 5) -> Any:
    """Open a pinned download, retrying brief throttling and gateway errors."""
    for attempt in range(attempts):
        try:
            return urllib.request.urlopen(source, timeout=timeout)
        except urllib.error.HTTPError as error:
            if error.code not in {429, 502, 503, 504} or attempt + 1 == attempts:
                raise
            delay = float(min(30, 2 ** (attempt + 1)))
            retry_after = error.headers.get("Retry-After", "") if error.headers else ""
            if retry_after.isdecimal() and len(retry_after) <= 6:
                delay = float(min(60, int(retry_after)))
            print(
                f"Download returned HTTP {error.code}; retrying the same pinned file "
                f"in {delay:g}s (attempt {attempt + 2}/{attempts}).",
                file=sys.stderr,
                flush=True,
            )
            error.close()
            time.sleep(delay)
    raise AssertionError("Unreachable download attempt boundary")


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
    with open_download(URL, 30) as response:
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

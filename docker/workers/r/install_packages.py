"""Install the SHA-256 locked CRAN closure and retain complete build diagnostics."""

from __future__ import annotations

import gzip
import hashlib
import json
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import BinaryIO, TextIO

LOG_DIRECTORY = Path("/usr/local/share/ds60-build-logs/r")
# Only exact repeated libsass diagnostics are summarized. Distinct notes and
# source excerpts form part of the identity, and unknown output stays visible.
_SASS_WARNING = re.compile(
    rb"^src/[\w./-]+:\d+:\d+: warning: .*\[-Woverloaded-virtual(?:=\d*)?\]\r?\n?$"
)
_DIAGNOSTIC_CONTEXT = re.compile(
    rb"^(?:\s*(?:\d+)?\s*\||src/[\w./-]+:\d+(?::\d+)?: note:"
    rb"|In file included from src/|\s+from src/)"
)
_MAX_BLOCK_BYTES = 128 * 1024
_MAX_BLOCK_IDENTITIES = 4096
_DOWNLOAD_ATTEMPTS = 5


def download_archive(url: str) -> bytes:
    """Retry bounded CRAN throttling/transient failures without changing source."""
    for attempt in range(_DOWNLOAD_ATTEMPTS):
        try:
            with urllib.request.urlopen(url, timeout=120) as response:
                return response.read(80_000_001)
        except urllib.error.HTTPError as error:
            if error.code not in {429, 502, 503, 504} or attempt + 1 == _DOWNLOAD_ATTEMPTS:
                raise
            delay = float(min(30, 2 ** (attempt + 1)))
            retry_after = error.headers.get("Retry-After", "")
            if retry_after.isdecimal() and len(retry_after) <= 6:
                delay = float(min(60, int(retry_after)))
            print(
                f"CRAN returned HTTP {error.code}; retrying the same locked source "
                f"in {delay:g}s (attempt {attempt + 2}/{_DOWNLOAD_ATTEMPTS}).",
                flush=True,
            )
            error.close()
            time.sleep(delay)
    raise AssertionError("Unreachable download attempt boundary")


class DiagnosticSummary:
    """Print every distinct complete diagnostic; retain duplicate counts."""

    def __init__(self, package_name: str, output: TextIO) -> None:
        self.enabled = package_name == "sass"
        self.output = output
        self.block: list[bytes] = []
        self.block_bytes = 0
        self.seen: set[bytes] = set()
        self.repeated_blocks = 0
        self.repeated_lines = 0

    def _write(self, data: bytes) -> None:
        self.output.write(data.decode("utf-8", errors="replace"))
        self.output.flush()

    def flush(self) -> None:
        if not self.block:
            return
        data = b"".join(self.block)
        identity = hashlib.sha256(data).digest()
        if identity in self.seen:
            self.repeated_blocks += 1
            self.repeated_lines += len(self.block)
        else:
            self._write(data)
            if len(self.seen) < _MAX_BLOCK_IDENTITIES:
                self.seen.add(identity)
        self.block = []
        self.block_bytes = 0

    def feed(self, line: bytes) -> None:
        if self.block and (
            not _DIAGNOSTIC_CONTEXT.match(line) or self.block_bytes + len(line) > _MAX_BLOCK_BYTES
        ):
            self.flush()
        if self.enabled and _SASS_WARNING.match(line):
            self.block = [line]
            self.block_bytes = len(line)
        elif self.block:
            self.block.append(line)
            self.block_bytes += len(line)
        else:
            self._write(line)


def copy_build_output(source: BinaryIO, archive: BinaryIO, summary: DiagnosticSummary) -> dict:
    digest = hashlib.sha256()
    byte_count = 0
    line_count = 0
    for line in source:
        archive.write(line)
        digest.update(line)
        byte_count += len(line)
        line_count += 1
        summary.feed(line)
    summary.flush()
    return {"sha256": digest.hexdigest(), "bytes": byte_count, "lines": line_count}


def run_logged_install(
    command: list[str], package: dict, log_directory: Path, output: TextIO | None = None
) -> dict:
    """Preserve raw stdout/stderr, summarize duplicates, and expose failure output."""
    if output is None:
        output = sys.stdout
    name, version = package["name"], package["version"]
    if not re.fullmatch(r"[A-Za-z][A-Za-z0-9.]*", name) or not re.fullmatch(
        r"[A-Za-z0-9.+-]+", version
    ):
        raise ValueError("Invalid locked R package identity")
    log_directory.mkdir(parents=True, exist_ok=True)
    stem = name + "_" + version
    log_path = log_directory / (stem + ".log.gz")
    summary = DiagnosticSummary(name, output)
    with (
        log_path.open("wb") as raw,
        gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as compressed,
        subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process,
    ):
        assert process.stdout is not None
        stats = copy_build_output(process.stdout, compressed, summary)
        returncode = process.wait()
    receipt = {
        "schema_version": 1,
        "package": name,
        "version": version,
        "archive_sha256": package["sha256"],
        "returncode": returncode,
        "log": log_path.name,
        "uncompressed": stats,
        "gzip_sha256": hashlib.sha256(log_path.read_bytes()).hexdigest(),
        "distinct_sass_diagnostics": len(summary.seen),
        "repeated_diagnostic_blocks": summary.repeated_blocks,
        "repeated_diagnostic_lines": summary.repeated_lines,
    }
    (log_directory / (stem + ".json")).write_text(json.dumps(receipt, indent=2) + "\n")
    print(
        f"R build log: {log_path} (uncompressed SHA256 {stats['sha256']}, exit {returncode})",
        file=output,
        flush=True,
    )
    if summary.repeated_blocks:
        print(
            f"Summarized {summary.repeated_blocks} exact repeated libsass warning blocks "
            f"({summary.repeated_lines} lines); every distinct diagnostic remains above. "
            "The complete original output is retained in the build log.",
            file=output,
            flush=True,
        )
    if returncode:
        # A failed Docker layer cannot be exported as an image. Replay the entire
        # failed package log so the hosted job log retains every diagnostic.
        print(f"BEGIN COMPLETE FAILED R BUILD LOG: {name} {version}", file=output, flush=True)
        with gzip.open(log_path, "rb") as source:
            for line in source:
                output.write(line.decode("utf-8", errors="replace"))
        print(f"END COMPLETE FAILED R BUILD LOG: exit {returncode}", file=output, flush=True)
    return receipt


def main(
    lock_path: Path = Path("/tmp/r-packages.lock.json"), log_directory: Path = LOG_DIRECTORY
) -> None:
    lock = json.loads(lock_path.read_text())
    if lock["schema_version"] != 1:
        raise ValueError("Unknown R dependency lock")
    receipts = []
    with tempfile.TemporaryDirectory(prefix="cran-") as scratch:
        for package in lock["packages"]:
            data = None
            for key in ("url", "archive_url"):
                url = package[key]
                if not url.startswith("https://cloud.r-project.org/src/contrib/"):
                    raise ValueError("Unreviewed R package host")
                try:
                    data = download_archive(url)
                    break
                except urllib.error.HTTPError as exc:
                    if exc.code != 404:
                        raise
            if (
                data is None
                or len(data) > 80_000_000
                or hashlib.sha256(data).hexdigest() != package["sha256"]
            ):
                raise ValueError(
                    "R package archive failed integrity verification: " + package["name"]
                )
            target = Path(scratch) / (package["name"] + "_" + package["version"] + ".tar.gz")
            target.write_bytes(data)
            print("Installing locked package", package["name"], package["version"], flush=True)
            command = ["R", "CMD", "INSTALL", "--no-docs", "--no-html", str(target)]
            receipt = run_logged_install(command, package, log_directory)
            receipts.append(receipt)
            (log_directory / "manifest.json").write_text(
                json.dumps({"schema_version": 1, "packages": receipts}, indent=2) + "\n"
            )
            if receipt["returncode"]:
                raise subprocess.CalledProcessError(receipt["returncode"], command)
            target.unlink()
    subprocess.run(
        ["Rscript", "--vanilla", "-e", 'stopifnot(getRversion() == "' + lock["r_version"] + '")'],
        check=True,
    )


if __name__ == "__main__":
    main()

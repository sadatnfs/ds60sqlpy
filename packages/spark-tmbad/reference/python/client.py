"""Bounded Python driver for the optional trusted R reference registry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAX_RESULT = 4 * 1024 * 1024


def request(case, seed, options):
    registry = json.loads((ROOT / "registry.json").read_text())
    if case not in registry["cases"] or type(seed) is not int or not 1 <= seed <= 100_000_000:
        raise ValueError("Choose a registered case and a bounded integer seed")
    expected = registry["cases"][case]["options"]
    if not isinstance(options, dict) or set(options) != set(expected):
        raise ValueError("Request option keys differ from the trusted registry")
    if any(
        type(value) is not str or value not in expected[name] for name, value in options.items()
    ):
        raise ValueError("Unsupported registered option value")
    return {"case": case, "seed": seed, "options": options}


def run_case(case, *, seed, options, prepared, output, timeout=300, rscript="Rscript"):
    payload = request(case, seed, options)
    prepared, output = Path(prepared).resolve(), Path(output).absolute()
    if output.exists() or output.is_symlink():
        raise ValueError("Use a fresh output directory; prior evidence is never replaced")
    if not (prepared / "manifest.json").is_file():
        raise ValueError("Prepare the optional reference explicitly before running")
    if type(timeout) is not int or not 10 <= timeout <= 1800:
        raise ValueError("Choose a bounded10..1800 second runtime")
    output.mkdir(parents=True)
    request_path = output / "request.json"
    request_path.write_text(json.dumps(payload, sort_keys=True) + "\n")
    environment = dict(
        os.environ,
        R_LIBS_USER=str(prepared / "library"),
        R_LIBS_SITE=str(prepared / "library"),
        OMP_NUM_THREADS="1",
        OPENBLAS_NUM_THREADS="1",
        MAKEFLAGS="-j1",
    )
    command = [
        rscript,
        "--vanilla",
        str(ROOT / "R/run.R"),
        str(ROOT),
        str(prepared),
        str(request_path),
        str(output / "case"),
    ]
    with (output / "runtime.log").open("wb") as log:
        process = subprocess.Popen(
            command, stdout=log, stderr=subprocess.STDOUT, env=environment, start_new_session=True
        )
        try:
            returncode = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            process.wait(timeout=10)
            failure = {"status": "failed", "stage": "runtime_timeout", "timeout_seconds": timeout}
            (output / "driver-failure.json").write_text(json.dumps(failure, indent=2) + "\n")
            raise TimeoutError("Owned reference process exceeded its runtime bound") from None
    result_path = output / "case/result.json"
    if not result_path.is_file() or result_path.stat().st_size > MAX_RESULT:
        raise RuntimeError("Reference returned no bounded result; inspect its retained runtime log")
    result = json.loads(result_path.read_text())
    if returncode != 0 or result.get("status") != "passed":
        raise RuntimeError("Reference case failed; retained result/log are not acceptance")
    result["driver"] = {
        "returncode": returncode,
        "request_sha256": hashlib.sha256(request_path.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    (output / "driver-result.json").write_text(json.dumps(result, indent=2, allow_nan=False) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--case")
    parser.add_argument("--seed", type=int, default=1729)
    parser.add_argument("--option", action="append", default=[], help="Registered NAME=VALUE")
    parser.add_argument("--prepared", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=300)
    args = parser.parse_args()
    if args.list:
        print(json.dumps(json.loads((ROOT / "registry.json").read_text()), indent=2))
        return
    if not args.case or not args.prepared or not args.output:
        parser.error("Run requires --case, --prepared and --output")
    options = {}
    for item in args.option:
        name, separator, value = item.partition("=")
        if not separator or name in options:
            parser.error("Options must be unique NAME=VALUE pairs")
        options[name] = value
    result = run_case(
        args.case,
        seed=args.seed,
        options=options,
        prepared=args.prepared,
        output=args.output,
        timeout=args.timeout,
    )
    print(json.dumps({"status": result["status"], "case": args.case, "output": str(args.output)}))


if __name__ == "__main__":
    main()

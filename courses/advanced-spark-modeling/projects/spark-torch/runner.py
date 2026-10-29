"""Fixed offline project cases with bounded subprocesses and process cleanup."""

from __future__ import annotations

import argparse
import contextlib
import os
import signal
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CASES = (
    "additive-logistic",
    "nonlinear-gaussian",
    "independent-groups",
    "arrow-batches",
    "torch-distributor",
    "lightning-ddp",
    "sharding-audit",
    "standalone-package",
)


def execute(arguments: list[str], *, seconds: int = 600) -> None:
    process = subprocess.Popen(arguments, start_new_session=True)
    try:
        code = process.wait(timeout=seconds)
        if code:
            raise SystemExit(code)
    finally:
        # The direct parent may already have failed while a child still runs.
        # Always clean the owned process group, including this orphan case.
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            return_code = process.poll()
            if return_code is None:
                process.wait()
        else:
            with contextlib.suppress(subprocess.TimeoutExpired):
                process.wait(timeout=5)
            with contextlib.suppress(ProcessLookupError):
                os.killpg(process.pid, signal.SIGKILL)
            process.wait()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("case", nargs="?", choices=CASES)
    args = parser.parse_args()
    if args.command == "run" and args.case is None:
        parser.error("run needs a named case")
    if args.command == "check" and args.case is not None:
        parser.error("check does not take a case")
    spark = [
        "/opt/spark/bin/spark-submit",
        "--driver-memory",
        "768m",
        "--conf",
        "spark.jars.ivy=/tmp/ivy",
    ]

    def run(case: str) -> None:
        if case == "standalone-package":
            execute([sys.executable, "-I", str(ROOT / "checks/check_package.py")], seconds=2400)
        elif case in {"torch-distributor", "lightning-ddp"}:
            execute([*spark, str(ROOT / "checks/check_distributor.py"), case])
        else:
            execute([*spark, str(ROOT / "examples.py"), case])

    if args.command == "check":
        execute([sys.executable, str(ROOT / "checks/check_cleanup.py")])
        execute([sys.executable, str(ROOT / "checks/check_torch_math.py")])
        execute([*spark, str(ROOT / "checks/check_spark_math.py")])
        execute([*spark, str(ROOT / "checks/check_distributor_failure.py")])
        for case in CASES:
            run(case)
    else:
        run(args.case)


if __name__ == "__main__":
    main()

"""Only the declared bounded documented project cases are executable."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from spark_tmb.processes import cleanup_process_group

ROOT = Path(__file__).resolve().parent
CASES = (
    "partition-normal",
    "group-laplace",
    "global-normal-fit",
    "rpy2-frame",
    "failure-contracts",
    "registered-models",
    "prediction-models",
    "dataframe-ml",
    "scala-dataframe",
)


def execute(arguments, seconds=600):
    process = subprocess.Popen(arguments, start_new_session=True)
    try:
        code = process.wait(timeout=seconds)
        if code:
            raise SystemExit(code)
    finally:
        cleanup_process_group(process)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("run", "check"))
    parser.add_argument("case", nargs="?", choices=CASES)
    args = parser.parse_args()
    if (args.command == "run") != (args.case is not None):
        parser.error("run takes one case; check takes no case")
    if args.command == "check":
        execute([sys.executable, "-I", str(ROOT / "check_package.py")], seconds=30)
        execute([sys.executable, str(ROOT / "check_processes.py")], seconds=30)
        execute([sys.executable, str(ROOT / "check_contracts.py")], seconds=60)
    for case in CASES if args.command == "check" else (args.case,):
        if case == "scala-dataframe":
            execute([sys.executable, str(ROOT / "scala/run.py")], seconds=900)
            continue
        engine = (
            [sys.executable]
            if case in {"rpy2-frame", "failure-contracts", "prediction-models"}
            else ["/opt/spark/bin/spark-submit", "--driver-memory", "768m"]
        )
        programs = {
            "registered-models": "check_registered.py",
            "prediction-models": "check_prediction.py",
            "dataframe-ml": "check_dataframe_ml.py",
        }
        if case in programs:
            execute([*engine, str(ROOT / programs[case])])
        else:
            execute([*engine, str(ROOT / "examples.py"), case])


if __name__ == "__main__":
    main()

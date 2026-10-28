"""A reproducible local program bundle with actual subprocess evidence and bounded claims."""

import hashlib
import json
import platform
import subprocess
import sys
import tempfile
from pathlib import Path

SOURCE = """import json
from pathlib import Path
values = json.loads(Path('input.json').read_text())
print(json.dumps({'rows': len(values), 'total': sum(values)}, sort_keys=True))
"""


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bundle(root):
    (root / "input.json").write_text("[2,3,1]\n")
    (root / "program.py").write_text(SOURCE)
    (root / "README.md").write_text(
        "# Reproducible local fixture\n\nRun `python program.py` in this directory.\n"
        "The declared input has three positive counts with expected total six.\n"
        "A local process result does not qualify a distributed deployment or accelerator.\n"
    )


def expected(root):
    values = json.loads((root / "input.json").read_text())
    if (
        not isinstance(values, list)
        or len(values) > 100
        or any(type(value) is not int or value < 1 for value in values)
    ):
        raise ValueError("The independent oracle requires bounded positive counts")
    total = 0
    for value in values:
        total += value
    return {"rows": len(values), "total": total}


def execute(root):
    oracle = expected(root)
    process = subprocess.run(
        [sys.executable, "program.py"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=10,
        stdin=subprocess.DEVNULL,
    )
    observed = json.loads(process.stdout) if process.returncode == 0 else None
    receipt = {
        "schema_version": 1,
        "evidence_kind": "bounded-local-process",
        "source_sha256": sha(root / "program.py"),
        "input_sha256": sha(root / "input.json"),
        "runtime": {
            "python": platform.python_version(),
            "os": sys.platform,
            "machine": platform.machine(),
        },
        "command_in_bundle": ["python", "program.py"],
        "returncode": process.returncode,
        "stdout_sha256": hashlib.sha256(process.stdout.encode()).hexdigest(),
        "observed": observed,
        "independent_oracle": oracle,
        "passed": process.returncode == 0 and observed == oracle,
    }
    (root / "receipt.json").write_text(json.dumps(receipt, sort_keys=True))
    return receipt


def validate_claim(root, receipt, claim):
    if claim != "bounded-local-correctness":
        raise ValueError("That claim requires separate runtime and operational evidence")
    if receipt["source_sha256"] != sha(root / "program.py") or receipt["input_sha256"] != sha(
        root / "input.json"
    ):
        raise ValueError("The recorded evidence belongs to different source or input")
    if not receipt["passed"] or receipt["returncode"] != 0 or receipt["observed"] != expected(root):
        raise ValueError("The observed result does not satisfy the independent oracle")
    return True


def example_one():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        bundle(root)
        receipt = execute(root)
        assert validate_claim(root, receipt, "bounded-local-correctness")
        assert receipt["observed"] == {"rows": 3, "total": 6}
        return {
            "receipt": receipt,
            "supported_claim": "bounded-local-correctness",
            "bundle_files": ["README.md", "program.py", "input.json", "receipt.json"],
        }


def example_two():
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        bundle(root)
        original = execute(root)
        (root / "program.py").write_text(SOURCE.replace("sum(values)", "sum(values)+1"))
        rejected = []
        try:
            validate_claim(root, original, "bounded-local-correctness")
        except ValueError:
            rejected.append("stale-source-evidence")
        changed = execute(root)
        assert (
            changed["returncode"] == 0
            and changed["observed"]["total"] == 7
            and not changed["passed"]
        )
        try:
            validate_claim(root, changed, "bounded-local-correctness")
        except ValueError:
            rejected.append("zero-exit-with-wrong-answer")
        try:
            validate_claim(root, changed, "multi-host-production-readiness")
        except ValueError:
            rejected.append("unsupported-evidence-tier")
        assert rejected == [
            "stale-source-evidence",
            "zero-exit-with-wrong-answer",
            "unsupported-evidence-tier",
        ]
        return {
            "rejected_claims": rejected,
            "changed_observed": changed["observed"],
            "independent_expected": changed["independent_oracle"],
            "exit_zero_is_not_correctness": True,
        }


def main():
    from ds60sqlpy.plot_artifacts import publish_report

    first, second = example_one(), example_two()
    print("A source-bound reproducible local result:", first)
    print("Unsupported and stale claims are rejected:", second)
    publish_report(
        first,
        description=(
            "Actual local subprocess evidence binds source, input, runtime "
            "and a three-row six-count independent oracle."
        ),
    )
    publish_report(
        second,
        description=(
            "A changed program exits zero with total seven; stale evidence, "
            "the wrong answer and unsupported production claims are rejected."
        ),
    )


if __name__ == "__main__":
    main()

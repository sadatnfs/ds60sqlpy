"""Compare actual native AD log-Gamma probe output with optional installed SciPy.

SciPy is a validation dependency here, never a production frontend dependency.
"""

import argparse
import hashlib
import json
import math
from pathlib import Path


def main():
    import scipy
    from scipy.special import digamma, gammaln, polygamma

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--probe-binary", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.input.read_text().splitlines() if line.strip()]
    if not 1 <= len(rows) <= 4096:
        raise AssertionError("Expected a bounded nonempty native AD probe grid")
    maxima = {
        name: {"absolute": 0.0, "scaled_by_max_1_reference": 0.0}
        for name in ("value", "gradient", "hessian")
    }
    for row in rows:
        x = row["x"]
        if not math.isfinite(x) or x <= 0:
            raise AssertionError("Invalid special-function grid input")
        expected = {
            "value": float(gammaln(x)),
            "gradient": float(digamma(x)),
            "hessian": float(polygamma(1, x)),
        }
        for name, reference in expected.items():
            actual = row[name]
            error = abs(actual - reference)
            scaled = error / max(abs(reference), 1.0)
            maxima[name]["absolute"] = max(maxima[name]["absolute"], error)
            maxima[name]["scaled_by_max_1_reference"] = max(
                maxima[name]["scaled_by_max_1_reference"], scaled
            )
            if not math.isfinite(actual) or not math.isclose(
                actual, reference, rel_tol=3e-12, abs_tol=3e-12
            ):
                raise AssertionError(
                    f"Native log-Gamma {name} mismatch at {x}: {actual} versus {reference}"
                )
    report = {
        "status": "passed",
        "scope": "native AD scalar probe versus optional SciPy; no Spark",
        "grid_points": len(rows),
        "minimum_x": min(row["x"] for row in rows),
        "maximum_x": max(row["x"] for row in rows),
        "scipy_version": scipy.__version__,
        "maximum_errors": maxima,
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "validator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    if args.probe_binary:
        report["probe_binary_sha256"] = hashlib.sha256(args.probe_binary.read_bytes()).hexdigest()
    text = json.dumps(report, indent=2, sort_keys=True)
    if args.output:
        with args.output.open("x", encoding="utf-8") as stream:
            stream.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()

"""Emit small Scala test data from independently certified rational oracle records."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def number(value):
    return repr(float(value))


def vec(values, formatter=number):
    return "Vector(" + ", ".join(formatter(value) for value in values) + ")"


def main():
    path = ROOT / "oracles/convex-targets.json"
    cases = json.loads(path.read_text())["cases"]
    lines = [
        "// SPDX-License-Identifier: MIT",
        "// Independent rational oracle data; execution is qualified separately.",
        "// Source JSON SHA256: " + hashlib.sha256(path.read_bytes()).hexdigest(),
        "package io.ds60.spark.tmbad",
        "",
        "import NamedRegularization.{Domain, Fixed, Gaussian, L1, RawEvaluation}",
        "",
        "object RegularizationOracleFixtures {",
        "  final case class Quadratic(",
        "      id: String, names: Vector[String], matrix: Vector[Vector[Double]], "
        "linear: Vector[Double],",
        "      lower: Vector[Double], upper: Vector[Double], initial: Vector[Double],",
        "      gaussian: Vector[Gaussian], l1: Vector[L1], fixed: Vector[Fixed], weight: Double,",
        "      expected: Vector[Double], expectedDigest: String, expectedComposite: Double) {",
        "    def domain: Domain = Domain(names, lower, upper)",
        "    def evaluate(theta: Vector[Double]): RawEvaluation = {",
        "      val product = matrix.map(row => row.indices.map(i => row(i) * theta(i)).sum)",
        "      val value = theta.indices.map(i => "
        "0.5 * theta(i) * product(i) - linear(i) * theta(i)).sum",
        "      RawEvaluation(value, theta.indices.map(i => product(i) - linear(i)).toVector, "
        "weight)",
        "    }",
        "  }",
        "  val values: Vector[Quadratic] = Vector(",
    ]
    for index, case in enumerate(cases):
        gaussian = vec(
            list(case["gaussian"].items()),
            lambda item: "Gaussian("
            + json.dumps(item[0])
            + ", "
            + number(item[1]["mean"])
            + ", "
            + number(item[1]["precision"])
            + ")",
        )
        l1 = vec(
            list(case["l1"].items()),
            lambda item: "L1(" + json.dumps(item[0]) + ", " + number(item[1]) + ")",
        )
        fixed = vec(
            list(case["fixed"].items()),
            lambda item: "Fixed(" + json.dumps(item[0]) + ", " + number(item[1]) + ")",
        )
        fields = [
            json.dumps(case["id"]),
            vec(case["names"], json.dumps),
            vec(case["matrix"], vec),
            vec(case["linear"]),
            vec(case["lower"], lambda x: "Double.NegativeInfinity" if x is None else number(x)),
            vec(case["upper"], lambda x: "Double.PositiveInfinity" if x is None else number(x)),
            vec(case["initial"]),
            gaussian,
            l1,
            fixed,
            number(case["weight"]),
            vec(case["expected"]["parameters"]),
            json.dumps(case["expected_target_digest"]),
            number(case["expected"]["composite_sum"]),
        ]
        lines.append(
            "    Quadratic(\n      "
            + ",\n      ".join(fields)
            + ")"
            + ("," if index + 1 < len(cases) else "")
        )
    lines += ["  )", "}", ""]
    output = ROOT / "src/test/scala/io/ds60/spark/tmbad/RegularizationOracleFixtures.scala"
    output.write_text("\n".join(lines))
    print("Emitted nine independent oracle data cases; JVM execution is a separate check")


if __name__ == "__main__":
    main()

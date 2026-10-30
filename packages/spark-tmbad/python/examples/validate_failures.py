"""Actual Spark failure acceptance with paired valid native controls.

Run only after the prepared JVM/native runtime and installed wheel are available:
  spark-submit --jars PREPARED.jar validate_failures.py --manifest FILE --output FILE

All observations are tiny Spark SQL fixtures. No Python UDF, mocked Spark handle,
compiler, download, or numerical Python backend is used. Expected failures must
match the relevant contract phrase; arbitrary backend failures never count.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import importlib.metadata
import json
import math
import os
import sys
import tempfile
import time
import traceback
import zipfile
from collections.abc import Callable
from pathlib import Path
from typing import Any

import ds60_spark_tmbad
from ds60_spark_tmbad import ContractError, FittedModel, ModelSpec, PreparedRuntime, SparkTMBad
from pyspark.sql import DataFrame, SparkSession

CHECK_IDS = (
    "prepared-native-probe",
    "valid-normal-fit-and-response-free-prediction",
    "valid-zero-row-weight-control",
    "valid-poisson-initial-domain-control",
    "invalid-poisson-initial-domain-fatal",
    "null-numeric-refusal",
    "nan-numeric-refusal",
    "infinite-numeric-refusal",
    "lossy-long-refusal",
    "negative-weight-refusal",
    "all-zero-shared-weight-refusal",
    "duplicate-observation-id-refusal",
    "empty-training-refusal",
    "valid-independent-group-control",
    "all-zero-independent-group-weight-refusal",
    "valid-complete-unit-and-conditional-prediction",
    "oversized-complete-unit-refusal",
    "valid-ordered-unit-and-forecast-control",
    "duplicate-ar-order-refusal",
    "unsupported-target-refusal",
    "empty-future-refusal",
    "missing-conditional-history-api-refusal",
    "missing-conditional-history-group-refusal",
    "actual-unconverged-fit-control",
    "unconverged-python-prediction-refusal",
    "unconverged-jvm-prediction-refusal",
    "explicit-unconverged-diagnostic-control",
    "valid-source-bound-reload-control",
    "incompatible-model-reload-refusal",
    "incompatible-artifact-reload-refusal",
    "final-native-readiness-control",
)


def sha_file(path: Path, maximum: int = 256 * 1024 * 1024) -> str:
    if not path.is_file() or path.stat().st_size > maximum:
        raise AssertionError("Expected a bounded ordinary qualification artifact")
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            result.update(block)
    return result.hexdigest()


def installed_identity(wheel: Path | None) -> dict[str, Any]:
    dist = importlib.metadata.distribution("ds60-spark-tmbad")
    expected = Path(dist.locate_file("ds60_spark_tmbad/__init__.py")).resolve()
    actual = Path(ds60_spark_tmbad.__file__).resolve()
    if actual != expected or dist.version != ds60_spark_tmbad.__version__:
        raise AssertionError("Import must resolve to the matching installed distribution")
    if dist.read_text("WHEEL") is None:
        raise AssertionError("This gate requires an installed wheel distribution")
    direct = dist.read_text("direct_url.json")
    if direct is not None and json.loads(direct).get("dir_info", {}).get("editable", False):
        raise AssertionError("Editable installs are not installed-wheel acceptance")
    modules: dict[str, str] = {}
    for item in dist.files or ():
        name = str(item)
        if not name.startswith("ds60_spark_tmbad/") or not name.endswith(".py"):
            continue
        digest = sha_file(Path(dist.locate_file(item)))
        recorded = item.hash
        encoded = base64.urlsafe_b64encode(bytes.fromhex(digest)).decode("ascii").rstrip("=")
        if recorded is None or recorded.mode != "sha256" or recorded.value != encoded:
            raise AssertionError("Installed module bytes differ from wheel RECORD")
        modules[name] = digest
    if "ds60_spark_tmbad/__init__.py" not in modules:
        raise AssertionError("The wheel RECORD lacks its imported module")
    wheel_hash = None
    if wheel is not None:
        wheel_hash = sha_file(wheel, maximum=32 * 1024 * 1024)
        with zipfile.ZipFile(wheel) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise AssertionError("The wheel contains duplicate entries")
            selected = {
                name
                for name in names
                if name.startswith("ds60_spark_tmbad/") and name.endswith(".py")
            }
            if selected != set(modules):
                raise AssertionError("Provided wheel and installed module inventories differ")
            for name, digest in modules.items():
                if archive.getinfo(name).file_size > 1024 * 1024:
                    raise AssertionError("Wheel module exceeds the qualification bound")
                if hashlib.sha256(archive.read(name)).hexdigest() != digest:
                    raise AssertionError("Provided wheel and installed module bytes differ")
    return {
        "distribution": dist.metadata["Name"],
        "version": dist.version,
        "module_sha256": modules,
        "provided_wheel_sha256": wheel_hash,
        "provided_wheel_module_parity": wheel is not None,
        "editable": False,
    }


def near(actual: float, expected: float, tolerance: float = 1e-7) -> None:
    if not math.isfinite(actual) or not math.isclose(
        actual, expected, rel_tol=tolerance, abs_tol=tolerance
    ):
        raise AssertionError("Valid-control numerical oracle did not agree")


class Acceptance:
    def __init__(self, api: SparkTMBad, spark: SparkSession, report: dict[str, Any]) -> None:
        self.api = api
        self.spark = spark
        self.report = report
        self.current = "initialization"

    def record(self, check: str, **details: Any) -> None:
        self.current = check
        if check not in CHECK_IDS or any(item["id"] == check for item in self.report["checks"]):
            raise AssertionError("Unexpected or repeated failure-acceptance check")
        self.report["checks"].append({"id": check, "passed": True, **details})

    def refusal(
        self,
        check: str,
        operation: Callable[[], Any],
        fragments: tuple[str, ...],
        *,
        expected_type: type[Exception] | None = None,
    ) -> None:
        self.current = check
        try:
            operation()
        except Exception as error:
            if expected_type is not None and not isinstance(error, expected_type):
                raise AssertionError(f"Wrong failure type for {check}") from error
            # Preserve only the reviewed category, never raw rows or a large JVM trace.
            message = str(error).casefold()
            matched = next((phrase for phrase in fragments if phrase.casefold() in message), None)
            if matched is None:
                raise AssertionError(f"Unrelated failure cannot satisfy {check}") from error
            self.record(check, exception_type=type(error).__name__, matched_contract=matched)
        else:
            raise AssertionError(f"Invalid input unexpectedly succeeded: {check}")

    def sql(self, query: str) -> DataFrame:
        return self.spark.sql(query).repartition(2)

    def normal_fit(self, frame: DataFrame, weight: bool = False, **options: Any) -> FittedModel:
        return self.api.fit_shared(
            frame,
            ModelSpec(
                "normal", {"y": "y"}, id_columns=["row_id"], weight_column="w" if weight else None
            ),
            options={"initial_parameters": [2.5, 0.5 * math.log(1.25)], **options},
        )

    def run(self) -> None:
        self.current = "prepared-native-probe"
        probe = self.api.probe(self.spark, "normal")
        if probe.get("passed") is not True or probe.get(
            "artifact_identity"
        ) != self.api.runtime.identity("normal"):
            raise AssertionError("Prepared native probe did not bind the expected artifact")
        self.record("prepared-native-probe", execution=probe.get("execution"))
        observations = self.sql("SELECT id AS row_id, CAST(id+1 AS DOUBLE) AS y FROM range(4)")
        future = self.sql("SELECT id+100 AS row_id FROM range(2)")
        self.current = "valid-normal-fit-and-response-free-prediction"
        normal = self.normal_fit(observations)
        if not normal.model["fit"]["converged"] or normal.model["fit"]["objective_calls"] < 1:
            raise AssertionError("Analytic normal optimum was not evaluated and accepted")
        near(normal.model["parameters"][0], 2.5)
        near(math.exp(2 * normal.model["parameters"][1]), 1.25)
        predicted = (
            normal.predict(future, options={"target": "response", "columns": {}})
            .orderBy("row_id")
            .collect()
        )
        if [row.row_id for row in predicted] != [100, 101]:
            raise AssertionError("Valid prediction lost future identities")
        for row in predicted:
            near(row.tmbad_mean, 2.5)
            near(row.tmbad_sd, math.sqrt(1.25))
        self.record("valid-normal-fit-and-response-free-prediction", rows=4, prediction_rows=2)

        weighted = self.sql(
            "SELECT id AS row_id, CAST(id+1 AS DOUBLE) AS y,\n            "
            "CAST(CASE id WHEN 0 THEN 0 WHEN 2 THEN 2 ELSE 1 END AS DOUBLE) "
            "AS w FROM range(4)"
        )
        self.current = "valid-zero-row-weight-control"
        fitted_weighted = self.normal_fit(
            weighted, True, initial_parameters=[3.0, 0.5 * math.log(0.5)]
        )
        if not fitted_weighted.model["fit"]["converged"]:
            raise AssertionError("Weighted analytic optimum did not converge")
        near(fitted_weighted.model["parameters"][0], 3.0)
        near(math.exp(2 * fitted_weighted.model["parameters"][1]), 0.5)
        near(fitted_weighted.model["fit"]["weight_sum"], 4.0)
        self.record("valid-zero-row-weight-control", rows=4, positive_weight_mass=4)

        self.current = "valid-poisson-initial-domain-control"
        poisson = self.sql(
            "SELECT id AS row_id,\n            CAST(CASE WHEN id%2=0 THEN -1 "
            "ELSE 1 END AS DOUBLE) AS x,\n            CAST(1 AS DOUBLE) AS "
            "exposure, CAST(1 AS BIGINT) AS y FROM range(4)"
        )
        poisson_spec = ModelSpec(
            "poisson_exposure", {"x": "x", "exposure": "exposure", "y": "y"}, id_columns=["row_id"]
        )
        poisson_options = {"initial_parameters": [0.0, 0.0], "max_iterations": 1}
        poisson_fit = self.api.fit_shared(poisson, poisson_spec, options=poisson_options)
        if not poisson_fit.model["fit"]["converged"]:
            raise AssertionError("Valid Poisson control did not reach its analytic optimum")
        near(poisson_fit.model["fit"]["loss"], 4.0)
        for parameter in poisson_fit.model["parameters"]:
            near(parameter, 0.0)
        poisson_future = self.sql(
            "SELECT 100 AS row_id, CAST(0 AS DOUBLE) AS x, CAST(2 AS DOUBLE) AS exposure"
        )
        poisson_predictions = poisson_fit.predict(
            poisson_future,
            options={"target": "response", "columns": {"x": "x", "exposure": "exposure"}},
        ).collect()
        if len(poisson_predictions) != 1 or poisson_predictions[0].row_id != 100:
            raise AssertionError("Valid Poisson target identity differs")
        near(poisson_predictions[0].tmbad_mean, 2.0)
        near(poisson_predictions[0].tmbad_variance, 2.0)
        self.record("valid-poisson-initial-domain-control", observations=4, future_rows=1)
        invalid_poisson = self.sql(
            "SELECT id AS row_id,\n            CAST(CASE WHEN id%2=0 THEN -1 "
            "ELSE 1 END AS DOUBLE) AS x,\n            CAST(1 AS DOUBLE) AS "
            "exposure, CAST(CASE WHEN id=0 THEN -1 ELSE 1 END AS BIGINT) AS y "
            "FROM range(4)"
        )
        # This is the INITIAL objective evaluation, outside line-search candidate
        # handling. Returning any model, including a nonconverged one, is failure.
        self.refusal(
            "invalid-poisson-initial-domain-fatal",
            lambda: self.api.fit_shared(invalid_poisson, poisson_spec, options=poisson_options),
            ("Native candidate rejected after complete partition/ledger validation: DOMAIN_ERROR",),
        )

        for check, expression, fragment in (
            ("null-numeric-refusal", "CAST(NULL AS DOUBLE)", "Null numeric model input"),
            ("nan-numeric-refusal", "CAST('NaN' AS DOUBLE)", "Nonfinite numerical model input"),
            (
                "infinite-numeric-refusal",
                "CAST('Infinity' AS DOUBLE)",
                "Nonfinite numerical model input",
            ),
            (
                "lossy-long-refusal",
                "CAST(9007199254740993 AS BIGINT)",
                "Integral model input would lose floating-point precision",
            ),
        ):
            bad = self.sql(f"SELECT 0 AS row_id, {expression} AS y")
            self.refusal(check, lambda data=bad: self.normal_fit(data), (fragment,))
        negative = self.sql(
            "SELECT id AS row_id, CAST(id+1 AS DOUBLE) AS y, CAST(-1 AS DOUBLE) AS w FROM range(4)"
        )
        zeros = self.sql(
            "SELECT id AS row_id, CAST(id+1 AS DOUBLE) AS y, CAST(0 AS DOUBLE) AS w FROM range(4)"
        )
        self.refusal(
            "negative-weight-refusal",
            lambda: self.normal_fit(negative, True),
            ("Negative likelihood weight",),
        )
        self.refusal(
            "all-zero-shared-weight-refusal",
            lambda: self.normal_fit(zeros, True),
            ("Fitting requires positive effective data and bounded exact counts",),
        )
        duplicate = self.sql("SELECT 0 AS row_id, CAST(id+1 AS DOUBLE) AS y FROM range(4)")
        self.refusal(
            "duplicate-observation-id-refusal",
            lambda: self.normal_fit(duplicate),
            ("Duplicate observation identity",),
        )
        self.refusal(
            "empty-training-refusal",
            lambda: self.normal_fit(observations.limit(0)),
            (
                "Fitting requires positive effective data and bounded exact counts",
                "Input partition count exceeds the bounded summary contract",
            ),
        )

        groups = self.sql(
            "SELECT id AS row_id, CASE WHEN id<4 THEN 'A' ELSE 'B' END AS "
            "series,\n              CAST(id%4+1 AS DOUBLE) AS y, CAST(1 AS "
            "DOUBLE) AS w FROM range(8)"
        )
        group_spec = ModelSpec(
            "normal", {"y": "y"}, id_columns=["row_id"], group_columns=["series"], weight_column="w"
        )
        self.current = "valid-independent-group-control"
        group_models = self.api.fit_groups(
            groups, group_spec, options={"initial_parameters": [2.5, 0.5 * math.log(1.25)]}
        )
        # Exactly two derived model records, never observations or an unbounded model collection.
        model_rows = group_models.models.select(
            "series", "tmbad_converged", "tmbad_model_json"
        ).collect()
        if len(model_rows) != 2 or {row.series for row in model_rows} != {"A", "B"}:
            raise AssertionError("Independent model coverage differs")
        for row in model_rows:
            if not row.tmbad_converged:
                raise AssertionError("Independent analytic optimum did not converge")
            near(json.loads(row.tmbad_model_json)["parameters"][0], 2.5)
        self.record("valid-independent-group-control", groups=2, observations=8)
        zero_group = self.sql(
            "SELECT id AS row_id, CASE WHEN id<4 THEN 'A' ELSE 'B' END AS "
            "series,\n              CAST(id%4+1 AS DOUBLE) AS y, CAST(CASE "
            "WHEN id<4 THEN 1 ELSE 0 END AS DOUBLE) AS w FROM range(8)"
        )
        self.refusal(
            "all-zero-independent-group-weight-refusal",
            lambda: self.api.fit_groups(
                zero_group, group_spec, options={"initial_parameters": [2.5, 0.5 * math.log(1.25)]}
            ).models.count(),
            ("Independent fit has zero effective likelihood weight",),
        )

        unit = self.sql(
            "SELECT id AS row_id, CAST(FLOOR(id/4) AS STRING) AS series,\n     "
            "        CAST(FLOOR(id/4)+1+CASE id%4 WHEN 0 THEN -0.4 WHEN 1 "
            "THEN 0.4 WHEN 2 THEN -0.2 ELSE 0.2 END AS DOUBLE) AS y FROM "
            "range(20)"
        )
        unit_spec = ModelSpec(
            "gaussian_random_intercept", {"y": "y"}, id_columns=["row_id"], group_columns=["series"]
        )
        sigma2, tau2 = 2.0 / 15.0, 2.0 - (2.0 / 15.0) / 4.0
        unit_options = {"initial_parameters": [3.0, 0.5 * math.log(sigma2), 0.5 * math.log(tau2)]}
        self.current = "valid-complete-unit-and-conditional-prediction"
        unit_model = self.api.fit_shared(unit, unit_spec, options=unit_options)
        if not unit_model.model["fit"]["converged"] or unit_model.model["fit"]["unit_count"] != 5:
            raise AssertionError("Balanced complete-group optimum did not pass")
        unit_future = self.sql("SELECT 100 AS row_id, '0' AS series")
        history = unit.where("series='0'")
        conditional_options = {
            "target": "existing_group",
            "columns": {},
            "history_columns": {"y": "y"},
        }
        rows = unit_model.predict(
            unit_future, history=history, options=conditional_options
        ).collect()
        if len(rows) != 1 or rows[0].row_id != 100:
            raise AssertionError("Conditional prediction lost its requested row")
        near(rows[0].tmbad_mean, 3.0 + 4 * tau2 * (1.0 - 3.0) / (sigma2 + 4 * tau2))
        near(rows[0].tmbad_variance, sigma2 + sigma2 * tau2 / (sigma2 + 4 * tau2))
        self.record("valid-complete-unit-and-conditional-prediction", units=5, observations=20)
        maximum = self.api.runtime.descriptor("gaussian_random_intercept")["max_unit_rows"]
        oversized = self.sql(
            "SELECT id AS row_id, 'oversized' AS series, CAST(id%5 AS DOUBLE) "
            f"AS y FROM range({maximum + 1})"
        )
        self.refusal(
            "oversized-complete-unit-refusal",
            lambda: self.api.fit_shared(oversized, unit_spec, options=unit_options),
            ("Complete unit exceeds its declared row bound",),
        )

        ar = self.sql(
            "SELECT * FROM VALUES (0,0,'A',CAST(-1 AS "
            "DOUBLE)),(1,1,'A',CAST(0 AS DOUBLE)),(2,2,'A',CAST(1 AS DOUBLE)) "
            "AS t(row_id,time,series,y)"
        )
        ar_spec = ModelSpec(
            "ar1",
            {"time": "time", "y": "y"},
            id_columns=["row_id"],
            group_columns=["series"],
            order_columns=["time"],
        )
        ar_options = {"initial_parameters": [0.0, 0.0, 0.5 * math.log(2.0 / 3.0)]}
        self.current = "valid-ordered-unit-and-forecast-control"
        ar_model = self.api.fit_shared(ar, ar_spec, options=ar_options)
        if not ar_model.model["fit"]["converged"]:
            raise AssertionError("Ordered analytic stationary control did not converge")
        ar_future = self.sql(
            "SELECT CAST(id+100 AS INT) AS row_id, CAST(id+3 AS INT) AS time, "
            "'A' AS series FROM range(2)"
        )
        forecast_options = {
            "target": "conditional_history",
            "history_columns": {"time": "time", "y": "y"},
            "future_columns": {"time": "time"},
        }
        forecasted = (
            ar_model.forecast(ar, ar_future, options=forecast_options).orderBy("row_id").collect()
        )
        if [row.row_id for row in forecasted] != [100, 101]:
            raise AssertionError("Forecast identity/cardinality differs")
        for row in forecasted:
            near(row.tmbad_mean, 0.0)
            near(row.tmbad_variance, 2.0 / 3.0)
        self.record("valid-ordered-unit-and-forecast-control", observations=3, horizon=2)
        ar_duplicate = self.sql(
            "SELECT * FROM VALUES (0,0,'A',CAST(-1 AS "
            "DOUBLE)),(1,0,'A',CAST(0 AS DOUBLE)),(2,1,'A',CAST(1 AS DOUBLE)) "
            "AS t(row_id,time,series,y)"
        )
        self.refusal(
            "duplicate-ar-order-refusal",
            lambda: self.api.fit_shared(ar_duplicate, ar_spec, options=ar_options),
            ("Ordered unit has duplicate or nonincreasing order keys",),
        )
        self.refusal(
            "unsupported-target-refusal",
            lambda: normal.predict(
                future, options={"target": "unprepared_target", "columns": {}}
            ).count(),
            ("Model does not declare this prediction/forecast target",),
        )
        self.refusal(
            "empty-future-refusal",
            lambda: ar_model.forecast(ar, ar_future.limit(0), options=forecast_options).count(),
            (
                "Forecast future DataFrame must be nonempty",
                "Forecast/prediction partition count exceeds its bound",
            ),
        )
        self.refusal(
            "missing-conditional-history-api-refusal",
            lambda: unit_model.predict(
                unit_future, options={"target": "existing_group", "columns": {}}
            ).count(),
            ("Use predictConditional with explicit history for this target",),
        )
        unmatched = self.sql("SELECT 200 AS row_id, 'not-in-history' AS series")
        self.refusal(
            "missing-conditional-history-group-refusal",
            lambda: unit_model.predict(
                unmatched, history=history, options=conditional_options
            ).count(),
            ("Future group is missing required conditional history",),
        )

        self.current = "actual-unconverged-fit-control"
        stopped = self.normal_fit(
            observations, initial_parameters=[0.0, 0.0], max_iterations=1, function_tolerance=0.0
        )
        if stopped.model["fit"]["converged"] or stopped.model["fit"]["iterations"] != 1:
            raise AssertionError("The one-step control did not retain a genuinely unfinished fit")
        self.record("actual-unconverged-fit-control", status=stopped.model["fit"]["status"])
        output_options = {"target": "response", "columns": {}}
        self.refusal(
            "unconverged-python-prediction-refusal",
            lambda: stopped.predict(future, options=output_options).count(),
            ("Prediction requires a converged fit",),
            expected_type=ContractError,
        )
        # Exercise the real JVM guard too, without relying on the Python facade's early refusal.
        self.refusal(
            "unconverged-jvm-prediction-refusal",
            lambda: self.spark._jvm.io.ds60.spark.tmbad.PythonBridge.predict(
                future._jdf,
                stopped.to_json(),
                self.api.runtime.to_json(),
                json.dumps(output_options),
            ).count(),
            ("Unconverged fit cannot predict/forecast without explicit allow_unconverged",),
        )
        self.current = "explicit-unconverged-diagnostic-control"
        diagnostic = stopped.predict(
            future, options={**output_options, "allow_unconverged": True}
        ).collect()
        if len(diagnostic) != 2 or stopped.model["fit"]["converged"]:
            raise AssertionError("Diagnostic override changed the fit's scientific status")
        for row in diagnostic:
            near(row.tmbad_mean, stopped.model["parameters"][0])
            near(row.tmbad_sd, math.exp(stopped.model["parameters"][1]))
        self.record("explicit-unconverged-diagnostic-control", fit_remains_unconverged=True)

        with tempfile.TemporaryDirectory(prefix="spark-tmbad-failure-model-") as directory:
            path = Path(directory) / "normal.json"
            normal.save(path)
            self.current = "valid-source-bound-reload-control"
            restored = FittedModel.load(path, runtime=self.api.runtime)
            if (
                restored.to_json() != normal.to_json()
                or restored.predict(future, options=output_options).count() != 2
            ):
                raise AssertionError("A valid saved model did not remain usable")
            self.record("valid-source-bound-reload-control")
            changed = normal.model
            changed["model_digest"] = "0" * 64
            wrong_path = Path(directory) / "wrong-model.json"
            wrong_path.write_text(json.dumps(changed), encoding="utf-8")
            self.refusal(
                "incompatible-model-reload-refusal",
                lambda: FittedModel.load(wrong_path, runtime=self.api.runtime),
                ("Fitted model source digest does not match",),
                expected_type=ContractError,
            )
            artifact = self.api.runtime.manifest
            artifact["binary"]["sha256"] = "0" * 64
            wrong_runtime = PreparedRuntime(artifact)
            self.refusal(
                "incompatible-artifact-reload-refusal",
                lambda: FittedModel.load(path, runtime=wrong_runtime),
                ("Fitted model artifact identity does not match",),
                expected_type=ContractError,
            )
        self.current = "final-native-readiness-control"
        final = self.api.probe(self.spark, "normal")
        if final.get("passed") is not True or final.get(
            "artifact_identity"
        ) != self.api.runtime.identity("normal"):
            raise AssertionError("The native runtime did not remain usable after negative cases")
        self.record("final-native-readiness-control")
        observed = [item["id"] for item in self.report["checks"]]
        if observed != list(CHECK_IDS):
            raise AssertionError("Failure acceptance coverage is incomplete or out of order")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument(
        "--wheel", type=Path, help="Optionally verify exact supplied wheel module bytes"
    )
    args = parser.parse_args()
    started = time.monotonic()
    report: dict[str, Any] = {
        "schema_version": 1,
        "kind": "spark-tmbad-actual-spark-failures",
        "status": "failed",
        "scope": (
            "small actual Spark SQL fixtures and prepared native processes; no scale benchmark"
        ),
        "checks": [],
        "script_sha256": sha_file(Path(__file__)),
    }
    failure: BaseException | None = None
    spark: SparkSession | None = None
    acceptance: Acceptance | None = None
    try:
        if args.output.exists():
            raise FileExistsError("Use a new evidence output path; existing receipts are preserved")
        report["installed_python"] = installed_identity(args.wheel)
        runtime = PreparedRuntime.from_manifest(args.manifest)
        manifest = runtime.manifest
        if "jvm" not in manifest:
            raise AssertionError("Actual Spark acceptance requires the prepared JVM JAR identity")
        report["manifest_sha256"] = sha_file(args.manifest, maximum=4 * 1024 * 1024)
        report["artifact_identity"] = runtime.identity("normal")
        report["model_digests"] = {model["id"]: model["digest"] for model in manifest["models"]}
        spark = SparkSession.builder.appName("spark-tmbad-failure-acceptance").getOrCreate()
        spark.sparkContext.setLogLevel("WARN")
        if spark.version != "4.0.1":
            raise AssertionError("This gate requires the pinned Spark4.0.1 runtime")
        report["spark_version"] = spark.version
        report["spark_master"] = spark.sparkContext.master
        acceptance = Acceptance(SparkTMBad(runtime), spark, report)
        acceptance.run()
        runtime.verify_files()
        if sha_file(args.manifest, maximum=4 * 1024 * 1024) != report["manifest_sha256"]:
            raise AssertionError("Prepared manifest changed during acceptance")
        if sha_file(Path(__file__)) != report["script_sha256"]:
            raise AssertionError("Failure acceptance script changed during execution")
        if installed_identity(args.wheel) != report["installed_python"]:
            raise AssertionError("Installed Python source changed during acceptance")
        report["status"] = "passed"
    except BaseException as error:
        failure = error
        report["failed_check"] = acceptance.current if acceptance else "preflight"
        report["failure_type"] = type(error).__name__
    finally:
        if spark is not None:
            try:
                spark.stop()
            except Exception as error:
                report["spark_stop_failure_type"] = type(error).__name__
                if failure is None:
                    failure = error
                    report["status"] = "failed"
        report["elapsed_seconds"] = round(time.monotonic() - started, 3)
        encoded = json.dumps(report, sort_keys=True, allow_nan=False)
        if len(encoded.encode()) > 128 * 1024:
            raise AssertionError("Failure acceptance report exceeded its bound")
        try:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            temporary: Path | None = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="wb", dir=args.output.parent, delete=False
                ) as stream:
                    temporary = Path(stream.name)
                    stream.write((encoded + "\n").encode("utf-8"))
                    stream.flush()
                    os.fsync(stream.fileno())
                # Publish only complete evidence, without replacing an earlier receipt.
                os.link(temporary, args.output)
            finally:
                if temporary is not None:
                    temporary.unlink(missing_ok=True)
        except OSError as error:
            report["receipt_write_failure_type"] = type(error).__name__
            if failure is None:
                failure = error
                report["status"] = "failed"
        print(json.dumps(report, sort_keys=True, allow_nan=False))
    if failure is not None:
        traceback.print_exception(failure, file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

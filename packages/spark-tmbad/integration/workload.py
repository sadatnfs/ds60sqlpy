"""Real native normal fits and AR1 conditional-history forecasts via the Python facade."""

from __future__ import annotations

import json
import math
from pathlib import Path

from ds60_spark_tmbad import FittedModel, ModelSpec, PreparedRuntime, SparkTMBad


def close(actual, expected, tolerance=3e-5):
    if len(actual) != len(expected) or any(
        not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)
        for a, b in zip(actual, expected, strict=True)
    ):
        raise AssertionError(
            f"Native output {actual} differs from independent reference {expected}"
        )


def sql_frame(spark, rows, names):
    def literal(value):
        if isinstance(value, str):
            if not value.replace("_", "").isalnum():
                raise ValueError("Integration fixture uses bounded simple identifiers")
            return "'" + value + "'"
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
        ):
            raise ValueError("Integration fixture value must be finite")
        return repr(value)

    projection = ",".join(
        f"CAST(`{name}` AS "
        + ("STRING" if name == "series" else "BIGINT" if name in {"row_id", "time"} else "DOUBLE")
        + f") AS `{name}`"
        for name in names
    )
    values = ",".join("(" + ",".join(literal(row[name]) for name in names) + ")" for row in rows)
    return spark.sql(
        "SELECT " + projection + " FROM VALUES " + values + " AS fixture(" + ",".join(names) + ")"
    )


class Workload:
    def __init__(self, spark, rows, partitions):
        self.spark, self.rows, self.partitions = spark, rows, partitions
        self.runtime = PreparedRuntime.from_manifest("/opt/spark-tmbad/artifact.json")
        self.api = SparkTMBad(self.runtime)
        self.iteration = 0
        self.ar1 = None

    def training(self):
        return self.spark.range(0, self.rows, 1, self.partitions).selectExpr(
            "id AS row_id", "CAST(id % 16 AS DOUBLE) AS y"
        )

    def fit_and_predict(self, frame):
        model = self.api.fit_shared(
            frame,
            ModelSpec("normal", {"y": "y"}, id_columns=["row_id"]),
            options={
                "initial_parameters": [7.0, 1.5],
                "reduction": "weighted_mean",
                "gradient_tolerance": 1e-7,
                "function_tolerance": 0.0,
                "max_iterations": 100,
                "batch_rows": 1024,
            },
        )
        fit = model.model["fit"]
        if not fit["converged"] or fit["row_count"] != self.rows:
            raise AssertionError("Native fit must converge with all input rows")
        expected = [7.5, math.log(math.sqrt(21.25))]
        close(model.model["parameters"], expected)
        self.iteration += 1
        path = Path(f"/work/evidence/normal-fit-{self.iteration}.json")
        model.save(path)
        restored = FittedModel.load(path, runtime=self.runtime)
        future = self.spark.range(2).selectExpr("id + 100000 AS row_id")
        predicted = restored.predict(
            future, options={"target": "response", "columns": {}, "output_prefix": "check_"}
        )
        output = [row.asDict() for row in predicted.orderBy("row_id").collect()]
        if [row["row_id"] for row in output] != [100000, 100001]:
            raise AssertionError("Native point prediction lost row identities")
        for row in output:
            close([row["check_mean"], row["check_sd"]], [7.5, math.sqrt(21.25)])
        return {
            "model": "normal",
            "parameters": model.model["parameters"],
            "fit": fit,
            "prediction": output,
            "artifact_identity": self.runtime.identity("normal"),
            "expected_parameters": expected,
            "oracle": "analytic normal MLE",
        }

    def compare(self, baseline, recovered):
        close(baseline["parameters"], recovered["parameters"], 1e-9)
        if baseline["fit"]["data_ledger"] != recovered["fit"]["data_ledger"]:
            raise AssertionError("Worker loss changed the accepted native data ledger")

    def forecast(self):
        recipe = json.loads(Path("/integration/ar1-fixture.json").read_text())
        if self.ar1 is None:
            training = sql_frame(
                self.spark, recipe["training_rows"], ["row_id", "series", "time", "y"]
            )
            self.ar1 = self.api.fit_shared(
                training.repartition(self.partitions),
                ModelSpec(
                    "ar1",
                    {"time": "time", "y": "y"},
                    id_columns=["row_id"],
                    group_columns=["series"],
                    order_columns=["time"],
                ),
                options={
                    **recipe["fit_options"],
                    "initial_parameters": recipe["initial_parameters"],
                },
            )
            if not self.ar1.model["fit"]["converged"]:
                raise AssertionError("AR1 model did not converge")
        case = recipe["forecast_cases"][0]
        history = sql_frame(self.spark, case["history_rows"], ["row_id", "series", "time", "y"])
        future = sql_frame(self.spark, case["rows"], ["row_id", "series", "time"])
        predictions = self.ar1.forecast(
            history,
            future,
            options={
                "target": "conditional_history",
                "history_columns": {"time": "time", "y": "y"},
                "future_columns": {"time": "time"},
                "future_order_columns": ["time"],
                "output_prefix": "check_",
            },
        )
        output = [row.asDict() for row in predictions.orderBy("row_id").collect()]
        theta = self.ar1.model["parameters"]
        mu, phi, variance = theta[0], math.tanh(theta[1]), math.exp(2 * theta[2])
        last = case["history_rows"][-1]["y"]
        for horizon, row in enumerate(output, 1):
            expected_mean = mu + phi**horizon * (last - mu)
            expected_variance = variance * sum(phi ** (2 * j) for j in range(horizon))
            close(
                [row["check_mean"], row["check_variance"], row["check_sd"]],
                [expected_mean, expected_variance, math.sqrt(expected_variance)],
            )
        if len(output) != 3 or [row["row_id"] for row in output] != [1000, 1001, 1002]:
            raise AssertionError("Forecast lost or duplicated target rows")
        return {
            "kind": "AR1 conditional-history forecast",
            "fit": self.ar1.model["fit"],
            "parameters": theta,
            "future_has_response": "y" in future.columns,
            "forecasts": output,
            "oracle": "finite independent-innovation moment formulas",
            "uncertainty": "observation uncertainty conditional on fitted parameters",
        }

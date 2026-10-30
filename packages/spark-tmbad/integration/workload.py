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

    def named_target_check(self, frame):
        spec = ModelSpec("normal", {"y": "y"}, id_columns=["row_id"])
        regularization = {
            "schema_version": 1,
            "coordinate_system": "native_optimizer_parameters",
            "normalization": "summed_likelihood_target",
            "gaussian": {"mu": {"mean": 1.0, "precision": float(self.rows)}},
            "l1": {"mu": float(self.rows)},
        }
        records = []
        for reduction in ("sum", "weighted_mean"):
            target = {
                "regularization": regularization,
                "fixed_parameters": {"log_sigma": 0.0},
                "reduction": reduction,
            }
            denominator = self.rows if reduction == "weighted_mean" else 1
            fitted = self.api.fit_shared(
                frame,
                spec,
                options=target
                | {
                    "initial_parameters": [0.0, 0.0],
                    "max_iterations": 100,
                    "batch_rows": 1024,
                    "solver": {
                        "method": "proximal_gradient",
                        "initial_step": denominator / (2 * self.rows),
                        "kkt_tolerance": 1e-6,
                    },
                },
            )
            document = fitted.model
            path = Path(f"/work/evidence/named-fit-{self.iteration}-{reduction}.json")
            fitted.save(path)
            if not document["fit"]["converged"] or document["fit"]["row_count"] != self.rows:
                raise AssertionError(
                    "Distributed named target lost data or did not converge; "
                    f"retained {path.name}, status={document['fit']['status']}, "
                    f"rows={document['fit']['row_count']}"
                )
            # Sum y = 7.5*n. One global N(1,1/n) prior and n*abs(mu), with
            # fixed sigma=1, give soft_threshold((7.5*n+n)/(2*n), 1/2)=3.75.
            close(document["parameters"], [3.75, 0.0], 1e-10)
            if document["target"]["stationarity"]["summed_inf"] > 1e-6:
                raise AssertionError("Distributed exact L1 did not satisfy summed KKT")
            restored = FittedModel.load(path, runtime=self.runtime)
            future = self.spark.range(2).selectExpr("id + 200000 AS row_id")
            predictions = [
                row.asDict()
                for row in restored.predict(future, options={"target": "response", "columns": {}})
                .orderBy("row_id")
                .collect()
            ]
            if [row["row_id"] for row in predictions] != [200000, 200001]:
                raise AssertionError("Named-target prediction lost row identities")
            for row in predictions:
                close([row["tmbad_mean"], row["tmbad_sd"]], [3.75, 1.0], 1e-10)
            evaluated = self.api.evaluate_shared(frame, spec, [3.75, 0.0], options=target)
            close([evaluated["loss_components"]["total_reduced"]], [document["fit"]["loss"]], 1e-10)
            records.append(
                {
                    "reduction": reduction,
                    "model": document,
                    "evaluation": evaluated,
                    "prediction": predictions,
                }
            )
        close(
            [records[0]["model"]["fit"]["loss"] / self.rows],
            [records[1]["model"]["fit"]["loss"]],
            1e-10,
        )
        return records

    def compare_named_targets(self, baseline, recovered):
        if len(baseline) != 2 or len(recovered) != 2:
            raise AssertionError("Both named-target reductions are required")
        for before, after in zip(baseline, recovered, strict=True):
            if before["reduction"] != after["reduction"]:
                raise AssertionError("Named-target reduction changed after worker loss")
            close(before["model"]["parameters"], after["model"]["parameters"], 1e-12)
            if before["model"]["fit"]["data_ledger"] != after["model"]["fit"]["data_ledger"]:
                raise AssertionError("Worker loss changed the named-target data ledger")
            if (
                before["model"]["target"]["target_spec_digest"]
                != after["model"]["target"]["target_spec_digest"]
            ):
                raise AssertionError("Worker loss changed the named statistical target")

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

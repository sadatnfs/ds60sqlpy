"""Distributed Torch likelihood fitting and explicit future-covariate predictions."""

from __future__ import annotations

import math
from pathlib import Path

from ds60_spark_likelihood.ml import SparkLikelihoodEstimator, SparkLikelihoodModel


def close(actual, expected, tolerance=4e-4):
    if len(actual) != len(expected) or any(
        not math.isclose(a, b, rel_tol=tolerance, abs_tol=tolerance)
        for a, b in zip(actual, expected, strict=True)
    ):
        raise AssertionError(f"Torch output {actual} differs from independent reference {expected}")


class Workload:
    def __init__(self, spark, rows, partitions):
        self.spark, self.rows, self.partitions = spark, rows, partitions
        self.iteration = 0
        self.fitted = None

    def training(self):
        return self.spark.range(0, self.rows, 1, self.partitions).selectExpr(
            "id AS row_id",
            "CAST(1 AS DOUBLE) AS intercept",
            "CAST(id % 16 AS DOUBLE) AS x",
            "CAST(1.5 + 0.8 * (id % 16) + "
            "0.2 * (CAST(FLOOR(id / 16) AS BIGINT) % 4 - 1.5) AS DOUBLE) AS y",
        )

    def fit_and_predict(self, frame):
        estimator = SparkLikelihoodEstimator(
            modelId="linear_gaussian",
            modelConfig={"feature_count": 2},
            featureCols={"x0": "intercept", "x1": "x"},
            labelCol="y",
            initialParameters=[1.0, 0.7, -1.0],
            parameterBounds=[[-10.0, 10.0], [-10.0, 10.0], [-5.0, 3.0]],
            reduction="weighted_mean",
            tol=1e-6,
            maxIter=100,
            batchSize=1024,
        )
        model = estimator.fit(frame)
        if not model.fit_summary["converged"] or model.fit_summary["row_count"] != self.rows:
            raise AssertionError("Torch fit must converge with every row")
        expected = [1.5, 0.8, math.log(math.sqrt(0.05))]
        close(model.parameters, expected)
        self.iteration += 1
        path = Path(f"/work/evidence/linear-fit-{self.iteration}")
        model.save(str(path))
        self.fitted = SparkLikelihoodModel.load(str(path))
        output = self._predictions([2.0, 12.0])
        return {
            "model": "linear_gaussian",
            "parameters": list(model.parameters),
            "fit": model.fit_summary,
            "prediction": output,
            "expected_parameters": expected,
            "oracle": "balanced orthogonal residuals and analytic Gaussian regression MLE",
        }

    def _predictions(self, xs):
        future = self.spark.sql(
            "SELECT CAST(id AS BIGINT) AS row_id, CAST(1 AS DOUBLE) AS intercept, "
            "CAST(x AS DOUBLE) AS x "
            "FROM VALUES " + ",".join(f"({i}, {x})" for i, x in enumerate(xs)) + " AS inputs(id, x)"
        )
        output = [row.asDict() for row in self.fitted.transform(future).orderBy("row_id").collect()]
        if [row["row_id"] for row in output] != list(range(len(xs))):
            raise AssertionError("Torch predictions lost row identities")
        close([row["prediction"] for row in output], [1.5 + 0.8 * x for x in xs])
        return output

    def compare(self, baseline, recovered):
        close(baseline["parameters"], recovered["parameters"], 1e-8)
        if baseline["fit"]["row_count"] != recovered["fit"]["row_count"]:
            raise AssertionError("Worker loss changed the accepted row count")

    def forecast(self):
        return {
            "kind": "future-covariate point predictions",
            "future_has_response": False,
            "conditional_history_forecasting": False,
            "training": "distributed additive Torch likelihood, not DDP/FSDP",
            "predictions": self._predictions([16.0, 17.0]),
            "uncertainty": "point means only; no intervals or latent-history integration",
        }

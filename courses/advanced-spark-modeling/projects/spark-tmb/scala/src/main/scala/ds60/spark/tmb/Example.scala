package ds60.spark.tmb

import org.apache.spark.sql.{Row, SparkSession}
import org.apache.spark.sql.functions._

object Example {
  private val rejectedLabels = scala.collection.mutable.ArrayBuffer.empty[String]
  def close(actual: Double, expected: Double, tolerance: Double = 1e-7): Unit =
    require(math.abs(actual - expected) <= tolerance, s"$actual differs from $expected")
  def rejected(label: String)(body: => Unit): Unit = {
    val failed = try { body; false }
    catch { case _: IllegalArgumentException => true }
    require(failed, s"Invalid contract was accepted: $label")
    rejectedLabels += label
  }
  def rejectedMessage(label: String, expected: String)(body: => Unit): Unit = {
    val message: Option[String] = try { body; None }
    catch { case error: IllegalArgumentException => Some(error.getMessage) }
    require(message.exists(_.contains(expected)), s"Unexpected rejection for $label: $message")
    rejectedLabels += label
  }
  def normalOracle(values: Vector[Double], theta: Vector[Double]): Evaluation = {
    val mu = theta(0); val scale = math.exp(theta(1)); val variance = scale * scale
    val residual = values.map(_ - mu)
    Evaluation(
      values.size * (theta(1) + 0.5 * math
        .log(2 * math.Pi)) + residual.map(x => x * x).sum / (2 * variance),
      Vector(
        residual.map(-_ / variance).sum,
        values.size - residual.map(x => x * x / variance).sum
      ),
      values.size
    )
  }
  def optimizerCheck(): Unit = {
    def quadratic(theta: Vector[Double]): Evaluation = {
      val a = theta(0) - 1; val b = theta(1) + 2
      Evaluation(0.5 * (4 * a * a + 2 * a * b + 3 * b * b), Vector(4 * a + b, a + 3 * b), 1)
    }
    val fit = DriverOptimizer.fit(quadratic, Vector(-3, 4), tolerance = 1e-9)
    require(fit.converged)
    close(fit.parameters(0), 1, 1e-8); close(fit.parameters(1), -2, 1e-8)
    require(fit.trace.sliding(2).forall(pair => pair.size < 2 || pair(1)._1 <= pair(0)._1 + 1e-12))
    rejected("evaluation budget") {
      DriverOptimizer.fit(quadratic, Vector(-3, 4), maxEvaluations = 2)
    }
    rejected("invalid parameters") { DriverOptimizer.fit(quadratic, Vector(Double.NaN, 0)) }
  }
  def envelopeChecks(): Unit = {
    val request = ModelBridge
      .mapper()
      .createObjectNode()
      .put("schema_version", 1)
      .put("operation", "describe")
      .put("model_id", "normal_mean")
    val response = request.deepCopy()
    response.putObject("result")
    require(ModelBridge.validateEnvelope(response, request).isObject)
    val booleanVersion = response.deepCopy()
    booleanVersion.put("schema_version", true)
    rejectedMessage("boolean CLI envelope version", "Unsupported CLI response version") {
      ModelBridge.validateEnvelope(booleanVersion, request)
    }
    val extra = response.deepCopy()
    extra.put("unexpected", 1)
    rejectedMessage("extra CLI envelope field", "CLI response fields differ") {
      ModelBridge.validateEnvelope(extra, request)
    }
  }
  def main(args: Array[String]): Unit = {
    optimizerCheck()
    envelopeChecks()
    require(System.getProperty("java.specification.version") == "21", "This project targets JDK 21")
    val spark = SparkSession.builder
      .master("local[2]")
      .appName("scala-prepared-tmb-dataframe")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.task.maxFailures", "1")
      .config("spark.sql.ansi.enabled", "true")
      .getOrCreate()
    require(spark.version == "4.0.1")
    spark.sparkContext.setLogLevel("ERROR")
    try {
      val values = (0 until 12).map(i => (i % 4).toDouble + 0.5).toVector
      val frame = spark
        .range(0, 12, 1, 3)
        .withColumn("measurement", (col("id") % 4).cast("double") + 0.5)
        .withColumn("unrelated", lit("deliberately not projected"))
        .cache()
      frame.count()
      val theta = Vector(1.3, math.log(1.4))
      val oracle = normalOracle(values, theta)
      val report = ModelBridge.mapper().createObjectNode()
      report
        .put("schema_version", 1)
        .put("kind", "scala-dataframe-prepared-tmb")
        .put("spark", spark.version)
        .put("java", System.getProperty("java.version"))
        .put("remote_cluster", false)
        .put("gpu", false)
        .put("raw_observations_collected", false)
      val cases = report.putArray("partition_batch_cases")
      for ((partitions, batchSize) <- Vector((1, 4), (3, 2), (5, 64))) {
        val layout =
          if (partitions == 5) frame.repartition(partitions, col("id"))
          else frame.repartition(partitions)
        val objective = DataFrameObjective.prepare(
          layout,
          "id",
          "normal_mean",
          Map("y" -> "measurement"),
          batchSize
        )
        try {
          val actual = objective.evaluate(theta)
          close(actual.value, oracle.value, 1e-10)
          actual.gradient.zip(oracle.gradient).foreach { case (a, b) => close(a, b, 1e-10) }
          require(actual.rows == 12)
          if (partitions == 5)
            require(
              objective.ledger.map(_.rows).filter(_ > 0).distinct.size > 1,
              "Fixture must exercise genuinely unequal nonempty partitions"
            )
          val entry = cases.addObject()
          entry
            .put("partitions", partitions)
            .put("batch_size", batchSize)
            .put("actual_batches", objective.lastBatchCount)
            .put("rows", actual.rows)
            .put("loss", actual.value)
            .put("oracle_error", math.abs(actual.value - oracle.value))
          val counts = entry.putArray("partition_rows");
          objective.ledger.foreach(item => counts.add(item.rows))
        } finally objective.close()
        rejected("closed objective") { objective.evaluate(theta) }
      }
      require(
        frame.storageLevel != org.apache.spark.storage.StorageLevel.NONE,
        "Caller cache was released"
      )
      val fitting = DataFrameObjective.prepare(
        frame.repartition(2),
        "id",
        "normal_mean",
        Map("y" -> "measurement"),
        64
      )
      try {
        val fit =
          DriverOptimizer.fit(fitting.evaluate, Vector(0.0, math.log(2.0)), tolerance = 1e-6)
        require(fit.converged, s"Fit failed to reach stationarity: ${fit.gradientNorm}")
        close(fit.parameters(0), 2.0, 1e-6)
        close(fit.parameters(1), 0.5 * math.log(1.25), 1e-6)
        val result = report.putObject("fit")
        result
          .put("mu", fit.parameters(0))
          .put("log_sigma", fit.parameters(1))
          .put("gradient_inf_norm", fit.gradientNorm)
          .put("iterations", fit.iterations)
          .put("objective_evaluations", fit.evaluations)
          .put("converged", fit.converged)
        report
          .put("model_source_sha256", fitting.description.sourceSha)
          .put("model_library_sha256", fitting.description.librarySha)
          .put("registry_sha256", fitting.description.registrySha)
        report.set[com.fasterxml.jackson.databind.JsonNode](
          "abi",
          ModelBridge.mapper().readTree(fitting.description.abiJson)
        )
      } finally fitting.close()
      val emptyPartitions = DataFrameObjective.prepare(
        frame.filter(col("id") < 2).repartition(5),
        "id",
        "normal_mean",
        Map("y" -> "measurement"),
        64
      )
      try {
        require(emptyPartitions.ledger.exists(_.rows == 0))
        val evaluated = emptyPartitions.evaluate(theta)
        close(evaluated.value, normalOracle(values.take(2), theta).value, 1e-10)
        require(evaluated.rows == 2)
      } finally emptyPartitions.close()
      rejected("complete groups cannot be row-batched") { ModelBridge.describe("random_intercept") }
      rejected("unknown prepared model") { ModelBridge.describe("not_prepared") }
      rejected("missing projection") {
        DataFrameObjective.prepare(frame, "id", "normal_mean", Map.empty)
      }
      rejected("silent text conversion") {
        DataFrameObjective.prepare(frame, "id", "normal_mean", Map("y" -> "unrelated"))
      }
      rejected("duplicate observation identity") {
        DataFrameObjective.prepare(
          frame.withColumn("id", lit(0L)),
          "id",
          "normal_mean",
          Map("y" -> "measurement")
        )
      }
      val description = ModelBridge.describe("normal_mean")
      rejectedMessage("stale registry descriptor", "Prepared artifact/ABI changed") {
        ModelBridge.evaluate(
          description.copy(registrySha = "0" * 64),
          Vector(Row("a", 1.0), Row("b", 2.0)),
          theta
        )
      }
      rejected("null numeric data") {
        ModelBridge.evaluate(description, Vector(Row("id", null)), theta)
      }
      frame.unpersist(blocking = true)
      report
        .put("caller_cache_preserved", true)
        .put("empty_partitions_checked", true)
        .put("pure_optimizer_oracle", true)
        .put("passed", true)
      val rejections = report.putArray("rejected_cases"); rejectedLabels.foreach(rejections.add)
      println(ModelBridge.mapper().writeValueAsString(report))
    } finally spark.stop()
  }
}

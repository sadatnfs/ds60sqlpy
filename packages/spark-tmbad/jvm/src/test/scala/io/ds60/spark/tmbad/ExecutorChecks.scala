package io.ds60.spark.tmbad

import com.fasterxml.jackson.databind.JsonNode
import java.nio.file.{Files, Path}
import org.apache.spark.{BarrierTaskContext, SparkEnv}
import org.apache.spark.sql.SparkSession

/** Two same-host executor JVMs, not a multi-host or throughput benchmark. */
object ExecutorChecks {
  def main(args: Array[String]): Unit = {
    require(args.length == 2, "Usage: artifact.json report.json")
    val encoded = Files.readString(Path.of(args(0)))
    val artifact = PreparedArtifact.parse(encoded)
    val spark =
      SparkSession.builder().appName("Prepared TMBad separate executor qualification").getOrCreate()
    spark.sparkContext.setLogLevel("WARN")
    try {
      require(
        spark.sparkContext.master.startsWith("local-cluster[2,1,"),
        "Use two separate bounded executor JVMs"
      )
      val distribution = ArtifactFiles.prepare(spark.sparkContext, artifact, PythonBridge.getClass)
      val records = spark.sparkContext
        .parallelize(Vector(0, 1), 2)
        .barrier()
        .mapPartitions { source =>
          require(source.hasNext)
          artifact.requireLoadedJvm(classOf[NativeWorker])
          BarrierTaskContext.get().barrier()
          val worker = new NativeWorker(artifact, distribution.executable, 30)
          try {
            worker.handshake(); worker.finish()
            val row = Json.obj();
            row
              .put("executor_id", SparkEnv.get.executorId)
              .put("jvm_pid", ProcessHandle.current().pid())
              .put("build_id", artifact.buildId)
              .put("binary_sha256", artifact.binarySha256)
              .put("jvm_sha256", artifact.jvmSha256.get)
            Iterator(Json.write(row))
          } finally worker.close()
        }
        .collect()
        .map(Json.read)
      require(
        records.length == 2 && records.map(Json.text(_, "executor_id")).distinct.length == 2 &&
          records.map(_.get("jvm_pid").longValue()).distinct.length == 2,
        "Did not observe two separate executor JVM processes"
      )
      val observations =
        spark.sql("SELECT * FROM VALUES (0L,1D),(1L,3D),(2L,5D),(3L,7D) AS t(id,y)").repartition(2)
      val spec =
        """{"model_id":"normal","columns":{"y":"y"},"id_columns":["id"],"group_columns":[],"order_columns":[],"weight_column":null}"""
      val fitted = PythonBridge.fitShared(
        observations,
        spec,
        encoded,
        """{"initial_parameters":[3,0.8],"function_tolerance":0,"gradient_tolerance":0.00001}"""
      )
      val model = ModelDocument.parse(fitted, artifact)
      require(model.converged && math.abs(model.parameters.head - 4) < 1e-5)
      val future = spark.sql("SELECT * FROM VALUES (100L),(101L) AS f(id)").repartition(2)
      val predicted = PythonBridge
        .predict(future, fitted, encoded, """{"target":"response","columns":{}}""")
        .collect()
      val forecast = PythonBridge
        .forecast(
          observations.limit(0),
          future,
          fitted,
          encoded,
          """{"target":"response","history_columns":{},"future_columns":{}}"""
        )
        .collect()
      require(predicted.length == 2 && forecast.length == 2)
      (predicted ++ forecast).foreach(row =>
        require(math.abs(row.getAs[Double]("tmbad_mean") - 4) < 1e-5)
      )
      val result = Json.obj();
      result
        .put("kind", "spark-tmbad-separate-executor-checks")
        .put("passed", true)
        .put("scope", "two separate executor JVMs on one host; no multi-host/network-scale claim")
      val executions = result.putArray("executors"); records.foreach(executions.add)
      result.set[JsonNode]("artifact_identity", Json.read(artifact.identityJson))
      result.set[JsonNode]("fit", Json.read(fitted).get("fit"))
      result.put("prediction_rows", predicted.length).put("forecast_rows", forecast.length)
      Files.writeString(Path.of(args(1)), Json.write(result) + "\n")
      println("DS60_TMBAD_EXECUTORS_RESULT " + Json.write(result))
    } finally spark.stop()
  }
}

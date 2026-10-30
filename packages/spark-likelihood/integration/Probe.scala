// Original DS60 integration instrumentation. License follows the containing package.
package io.ds60.integration

import com.fasterxml.jackson.databind.ObjectMapper
import java.net.{HttpURLConnection, InetAddress, URI}
import java.nio.charset.StandardCharsets
import java.nio.ByteBuffer
import java.security.MessageDigest
import java.util.concurrent.ConcurrentLinkedQueue
import org.apache.spark.{SparkEnv, TaskContext}
import org.apache.spark.scheduler._
import org.apache.spark.sql.{DataFrame, Encoders, Row, SparkSession}
import scala.jdk.CollectionConverters._

object Probe {
  private val mapper = new ObjectMapper()
  private val events = new ConcurrentLinkedQueue[String]()
  private val limit = 10000
  @volatile private var overflow = false

  private def json(values: (String, Any)*): String = {
    val value = new java.util.LinkedHashMap[String, Any]()
    values.foreach { case (key, item) => value.put(key, item) }
    new ObjectMapper().writeValueAsString(value)
  }

  private def record(value: String): Unit = {
    if (events.size() >= limit) overflow = true
    else events.add(value)
  }

  def attach(spark: SparkSession): Unit = {
    spark.sparkContext.addSparkListener(new SparkListener {
      override def onTaskStart(event: SparkListenerTaskStart): Unit = {
        val t = event.taskInfo
        record(
          json(
            "kind" -> "task_start",
            "stage_id" -> event.stageId,
            "stage_attempt" -> event.stageAttemptId,
            "partition_id" -> t.partitionId,
            "task_id" -> t.taskId,
            "attempt" -> t.attemptNumber,
            "executor_id" -> t.executorId,
            "host" -> t.host
          )
        )
      }
      override def onTaskEnd(event: SparkListenerTaskEnd): Unit = {
        val t = event.taskInfo
        record(
          json(
            "kind" -> "task_end",
            "stage_id" -> event.stageId,
            "stage_attempt" -> event.stageAttemptId,
            "partition_id" -> t.partitionId,
            "task_id" -> t.taskId,
            "attempt" -> t.attemptNumber,
            "executor_id" -> t.executorId,
            "host" -> t.host,
            "successful" -> t.successful,
            "reason" -> event.reason.toString.take(400)
          )
        )
      }
      override def onExecutorRemoved(event: SparkListenerExecutorRemoved): Unit =
        record(
          json(
            "kind" -> "executor_removed",
            "executor_id" -> event.executorId,
            "reason" -> event.reason.take(400)
          )
        )
      override def onExecutorAdded(event: SparkListenerExecutorAdded): Unit =
        record(
          json(
            "kind" -> "executor_added",
            "executor_id" -> event.executorId,
            "host" -> event.executorInfo.executorHost
          )
        )
    })
  }

  def eventsJson(): String = {
    require(!overflow, "Integration listener event budget exceeded")
    "[" + events.iterator().asScala.mkString(",") + "]"
  }

  private def identity(
      kind: String,
      token: String,
      count: Long = 0L,
      sum: Long = 0L,
      squares: Long = 0L,
      digest: String = ""
  ): String = {
    val t = TaskContext.get()
    json(
      "kind" -> kind,
      "token" -> token,
      "host" -> InetAddress.getLocalHost.getHostName,
      "executor_id" -> SparkEnv.get.executorId,
      "pid" -> ProcessHandle.current().pid(),
      "stage_id" -> t.stageId(),
      "stage_attempt" -> t.stageAttemptNumber(),
      "partition_id" -> t.partitionId(),
      "attempt" -> t.attemptNumber(),
      "task_id" -> t.taskAttemptId(),
      "rows" -> count,
      "id_sum" -> sum,
      "id_sum_squares" -> squares,
      "id_sha256" -> digest
    )
  }

  private def send(endpoint: String, value: String): Unit = {
    val connection = URI.create(endpoint).toURL.openConnection().asInstanceOf[HttpURLConnection]
    connection.setConnectTimeout(10000)
    connection.setReadTimeout(180000)
    connection.setRequestMethod("POST")
    connection.setDoOutput(true)
    connection.setRequestProperty("Content-Type", "application/json")
    val bytes = value.getBytes(StandardCharsets.UTF_8)
    connection.setFixedLengthStreamingMode(bytes.length)
    try {
      val output = connection.getOutputStream
      try output.write(bytes)
      finally output.close()
      require(connection.getResponseCode == 200, "Integration control request failed")
      connection.getInputStream.close()
    } finally connection.disconnect()
  }

  def identities(spark: SparkSession): String = {
    val records = spark
      .range(0L, 2L, 1L, 2)
      .rdd
      .barrier()
      .mapPartitions { rows =>
        rows.foreach(_ => ())
        org.apache.spark.BarrierTaskContext.get().barrier()
        Iterator(identity("executor_identity", "identity"))
      }
      .collect()
    "[" + records.mkString(",") + "]"
  }

  def gated(frame: DataFrame, token: String): DataFrame = {
    require(Set("baseline", "loss").contains(token), "Unknown integration gate token")
    frame.mapPartitions { rows: Iterator[Row] =>
      send("http://driver:8787/event", identity("partition_start", token))
      if (token == "loss") send("http://driver:8787/gate", identity("gate_waiter", token))
      new Iterator[Row] {
        private var count = 0L
        private var sum = 0L
        private var squares = 0L
        private var sent = false
        private val digest = MessageDigest.getInstance("SHA-256")
        private val encoded = ByteBuffer.allocate(8)
        override def hasNext: Boolean = {
          val available = rows.hasNext
          if (!available && !sent) {
            send(
              "http://driver:8787/event",
              identity(
                "partition_complete",
                token,
                count,
                sum,
                squares,
                digest.digest().map(byte => f"${byte & 0xff}%02x").mkString
              )
            )
            sent = true
          }
          available
        }
        override def next(): Row = {
          val row = rows.next()
          val id = row.getLong(0)
          count += 1; sum += id; squares += id * id
          encoded.clear(); encoded.putLong(id); digest.update(encoded.array())
          row
        }
      }
    }(Encoders.row(frame.schema))
  }
}

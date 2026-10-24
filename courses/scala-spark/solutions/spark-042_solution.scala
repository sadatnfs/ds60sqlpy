import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._
import java.nio.file.{Files, Path, Paths, StandardOpenOption, StandardCopyOption}
import java.nio.charset.StandardCharsets
import java.util.UUID
import scala.jdk.CollectionConverters._
import org.apache.spark.sql.streaming.{StreamingQuery, Trigger}
import scala.collection.mutable.ArrayBuffer

object Main {
  val eventSchema = StructType(
    Seq(StructField("id", LongType, true), StructField("cents", LongType, true))
  )
  val ownedQueries = ArrayBuffer.empty[StreamingQuery]
  case class RunReceipt(id: String, runId: String, inputRows: Long, batches: Seq[Long])
  def deleteOwned(root: Path): Unit = {
    require(root.getFileName.toString.startsWith("spark-"))
    require(root.getParent == Paths.get(".").toAbsolutePath.normalize())
    val walk = Files.walk(root)
    try
      walk.iterator().asScala.toVector.sortBy(_.getNameCount).reverse.foreach(p => Files.delete(p))
    finally walk.close()
  }
  def publishFile(root: Path, input: Path, name: String, lines: Seq[String]): Unit = {
    require(name.matches("batch-[0-9]{2}\\.json"))
    require(lines.size <= 8 && lines.forall(_.length <= 256))
    Files.createDirectories(input)
    val staged = root.resolve("pending-" + UUID.randomUUID().toString + ".json")
    try {
      Files.writeString(
        staged,
        lines.mkString("\n") + "\n",
        StandardCharsets.UTF_8,
        StandardOpenOption.CREATE_NEW
      )
      Files.move(staged, input.resolve(name), StandardCopyOption.ATOMIC_MOVE)
    } finally Files.deleteIfExists(staged)
  }
  def runParquet(spark: SparkSession, input: Path, checkpoint: Path, output: Path): RunReceipt = {
    val source = spark.readStream
      .schema(eventSchema)
      .option("maxFilesPerTrigger", 1)
      .option("mode", "FAILFAST")
      .json(input.toString)
    val query = source.writeStream
      .format("parquet")
      .outputMode("append")
      .option("checkpointLocation", checkpoint.toString)
      .trigger(Trigger.AvailableNow())
      .start(output.toString)
    ownedQueries += query
    try {
      require(query.awaitTermination(45000L), "Finite query exceeded45-second deadline")
      require(query.exception.isEmpty, "Finite query failed")
      RunReceipt(
        query.id.toString,
        query.runId.toString,
        query.recentProgress.map(_.numInputRows).sum,
        query.recentProgress.map(_.batchId).toSeq
      )
    } finally { if (query.isActive) query.stop() }
  }
  def bag(spark: SparkSession, path: Path): Seq[String] = {
    val frame = spark.read.parquet(path.toString)
    require(
      frame.schema.fields.map(f => (f.name, f.dataType.simpleString)).toSeq == Seq(
        ("id", "bigint"),
        ("cents", "bigint")
      )
    )
    require(frame.count() <= 8L, "Tiny result bound exceeded")
    frame.orderBy("id", "cents").collect().map(r => s"${r.getLong(0)}:${r.getLong(1)}").toSeq
  }

  val productSchema = StructType(
    Seq(
      StructField("delivery", LongType, true),
      StructField("id", StringType, true),
      StructField("event_second", LongType, true),
      StructField("cents", LongType, true)
    )
  )
  case class ProductEvent(
      delivery: Long,
      id: Option[String],
      second: Option[Long],
      cents: Option[Long]
  )
  case class ProductState(
      accepted: Map[String, (Long, Long)],
      deliveries: Set[Long],
      duplicates: Long,
      late: Long,
      invalid: Long,
      maxEvent: Option[Long]
  )
  def emptyProduct: ProductState = ProductState(Map.empty, Set.empty, 0L, 0L, 0L, None)
  val productMapper = new com.fasterxml.jackson.databind.ObjectMapper()
  val productAttempts = ArrayBuffer.empty[Long]
  val productAttemptRows = ArrayBuffer.empty[Long]
  val productRuns = ArrayBuffer.empty[(String, String)]
  def productSha(text: String): String = java.security.MessageDigest
    .getInstance("SHA-256")
    .digest(text.getBytes(StandardCharsets.UTF_8))
    .map(b => f"${b & 255}%02x")
    .mkString
  def decodeEvents(text: String): Seq[ProductEvent] = {
    val array = productMapper.readTree(text); require(array.isArray && array.size() <= 8)
    array
      .elements()
      .asScala
      .map { row =>
        require(
          row.isObject && row.fieldNames().asScala.toSet == Set(
            "delivery",
            "id",
            "event_second",
            "cents"
          )
        )
        require(
          row.path("delivery").isIntegralNumber && row.path("delivery").longValue() >= 1L && row
            .path("delivery")
            .longValue() <= 12L
        )
        require(row.path("id").isNull || row.path("id").isTextual)
        require(row.path("event_second").isNull || row.path("event_second").isIntegralNumber)
        require(row.path("cents").isNull || row.path("cents").isIntegralNumber)
        ProductEvent(
          row.get("delivery").longValue(),
          if (row.get("id").isNull) None else Some(row.get("id").asText()),
          if (row.get("event_second").isNull) None else Some(row.get("event_second").longValue()),
          if (row.get("cents").isNull) None else Some(row.get("cents").longValue())
        )
      }
      .toSeq
  }
  def stateJson(state: ProductState): String = {
    val node = productMapper.createObjectNode(); val accepted = node.putArray("accepted")
    state.accepted.toSeq.sortBy(_._1).foreach { case (id, (second, cents)) =>
      val row = accepted.addObject(); row.put("cents", cents); row.put("event_second", second);
      row.put("id", id)
    }
    val deliveries = node.putArray("deliveries");
    state.deliveries.toSeq.sorted.foreach(x => deliveries.add(x))
    node.put("duplicates", state.duplicates); node.put("invalid", state.invalid);
    node.put("late", state.late)
    state.maxEvent match {
      case Some(value) => node.put("max_event_second", value);
      case None        => node.putNull("max_event_second")
    }
    node.put("total_cents", state.accepted.values.map(_._2).sum)
    productMapper.writeValueAsString(node)
  }
  def productPath(sink: Path, batchId: Long): Path = {
    require(batchId >= 0L && batchId <= 8L); sink.resolve(f"batch-$batchId%020d.json")
  }
  def loadProduct(sink: Path, batchId: Long): ProductState = {
    val path = productPath(sink, batchId);
    val node = productMapper.readTree(Files.readString(path, StandardCharsets.UTF_8))
    require(
      node.isObject && node.fieldNames().asScala.toSet == Set(
        "query_identity",
        "batch_id",
        "previous_sha256",
        "input_sha256",
        "input_json",
        "state_json"
      )
    )
    require(node.path("batch_id").isIntegralNumber && node.path("batch_id").longValue() == batchId)
    require(
      Seq("query_identity", "previous_sha256", "input_sha256", "input_json", "state_json").forall(
        k => node.path(k).isTextual
      )
    )
    require(node.get("query_identity").asText() == "late-product-v1")
    val previous = if (batchId == 0L) emptyProduct else loadProduct(sink, batchId - 1L)
    val previousHash =
      if (batchId == 0L) ""
      else productSha(Files.readString(productPath(sink, batchId - 1L), StandardCharsets.UTF_8))
    val input = node.get("input_json").asText()
    require(
      node.get("previous_sha256").asText() == previousHash && node
        .get("input_sha256")
        .asText() == productSha(input)
    )
    val expected = advancePolicy(previous, decodeEvents(input))
    require(
      node.get("state_json").asText() == stateJson(expected),
      "Committed product state differs from event ledger"
    )
    expected
  }
  def commitProduct(sink: Path, batchId: Long, input: String, failAfter: Boolean): ProductState = {
    val target = productPath(sink, batchId)
    if (Files.exists(target)) {
      val node = productMapper.readTree(Files.readString(target, StandardCharsets.UTF_8))
      require(
        node.path("input_json").isTextual && node.get("input_json").asText() == input,
        "Replayed batch content changed"
      )
      loadProduct(sink, batchId)
    } else {
      val previous = if (batchId == 0L) emptyProduct else loadProduct(sink, batchId - 1L)
      val next = advancePolicy(previous, decodeEvents(input))
      val node = productMapper.createObjectNode(); node.put("query_identity", "late-product-v1");
      node.put("batch_id", batchId)
      node.put(
        "previous_sha256",
        if (batchId == 0L) ""
        else productSha(Files.readString(productPath(sink, batchId - 1L), StandardCharsets.UTF_8))
      )
      node.put("input_sha256", productSha(input)); node.put("input_json", input);
      node.put("state_json", stateJson(next))
      val staged = sink.resolve("pending-" + UUID.randomUUID().toString + ".json")
      try {
        Files.writeString(
          staged,
          productMapper.writeValueAsString(node),
          StandardCharsets.UTF_8,
          StandardOpenOption.CREATE_NEW
        )
        Files.move(staged, target, StandardCopyOption.ATOMIC_MOVE)
        if (failAfter) throw new IllegalStateException("injected_after_publication")
        next
      } finally Files.deleteIfExists(staged)
    }
  }
  def runProduct(
      spark: SparkSession,
      input: Path,
      checkpoint: Path,
      sink: Path,
      failAfter: Boolean
  ): RunReceipt = {
    val binding = sink.resolve("binding.txt")
    val contract = input.toAbsolutePath.normalize().toString + "\n" + checkpoint.toAbsolutePath
      .normalize()
      .toString + "\nlate-product-v1;cutoff=previous_max-10;limit=12"
    if (Files.exists(binding))
      require(
        Files.readString(binding, StandardCharsets.UTF_8) == contract,
        "Product namespace binding mismatch"
      )
    else Files.writeString(binding, contract, StandardCharsets.UTF_8, StandardOpenOption.CREATE_NEW)
    val frame = spark.readStream
      .schema(productSchema)
      .option("maxFilesPerTrigger", 1)
      .option("mode", "FAILFAST")
      .json(input.toString)
    val query = frame.writeStream
      .option("checkpointLocation", checkpoint.toString)
      .trigger(Trigger.AvailableNow())
      .foreachBatch { (batch: DataFrame, batchId: Long) =>
        batch.persist()
        try {
          val encoded = canonicalProductInput(batch)
          productAttempts += batchId; productAttemptRows += decodeEvents(encoded).size.toLong
          commitProduct(sink, batchId, encoded, failAfter)
          ()
        } finally batch.unpersist()
      }
      .start()
    ownedQueries += query; productRuns += ((query.id.toString, query.runId.toString))
    try {
      require(query.awaitTermination(45000L), "Product deadline exceeded")
      require(query.exception.isEmpty)
      RunReceipt(
        query.id.toString,
        query.runId.toString,
        query.recentProgress.map(_.numInputRows).sum,
        query.recentProgress.map(_.batchId).toSeq
      )
    } finally { if (query.isActive) query.stop() }
  }

  def canonicalProductInput(frame: DataFrame): String = {
    require(
      frame.schema.fields.map(f => (f.name, f.dataType.simpleString)).toSeq == Seq(
        ("delivery", "bigint"),
        ("id", "string"),
        ("event_second", "bigint"),
        ("cents", "bigint")
      )
    )
    val countRows = frame.count(); require(countRows <= 8L)
    require(
      frame
        .filter(col("delivery").isNull || col("delivery") < 1L || col("delivery") > 12L)
        .count() == 0L
    )
    require(
      frame.select("delivery").distinct().count() == countRows,
      "Delivery IDs must be unique within a microbatch"
    )
    val array = productMapper.createArrayNode()
    frame.orderBy("delivery").collect().foreach { row =>
      val node = array.addObject()
      if (row.isNullAt(3)) node.putNull("cents") else node.put("cents", row.getLong(3))
      node.put("delivery", row.getLong(0))
      if (row.isNullAt(2)) node.putNull("event_second")
      else node.put("event_second", row.getLong(2))
      if (row.isNullAt(1)) node.putNull("id") else node.put("id", row.getString(1))
    }
    productMapper.writeValueAsString(array)
  }

  def advancePolicy(previous: ProductState, events: Seq[ProductEvent]): ProductState = {
    require(previous.deliveries.size + events.size <= 12, "Product occurrence budget exceeded")
    val cutoff = previous.maxEvent.map(_ - 10L)
    var next = previous
    for (event <- events.sortBy(_.delivery)) {
      require(
        !next.deliveries.contains(event.delivery),
        "Delivery identity repeated across logical batches"
      )
      next = next.copy(deliveries = next.deliveries + event.delivery)
      val valid = event.id.exists(_.matches("[A-Z]")) && event.second.exists(t =>
        t >= 0L && t <= 1000L
      ) && event.cents.exists(c => c >= 0L && c <= 1000L)
      if (!valid) next = next.copy(invalid = next.invalid + 1L)
      else {
        val id = event.id.get; val value = (event.second.get, event.cents.get)
        next.accepted.get(id) match {
          case Some(existing) if existing == value =>
            next = next.copy(duplicates = next.duplicates + 1L)
          case Some(_)                             => next = next.copy(invalid = next.invalid + 1L)
          case None if cutoff.exists(value._1 < _) => next = next.copy(late = next.late + 1L)
          case None                                =>
            next = next.copy(
              accepted = next.accepted + (id -> value),
              maxEvent = Some(next.maxEvent.fold(value._1)(old => math.max(old, value._1)))
            )
        }
      }
    }
    require(
      next.accepted.size.toLong + next.duplicates + next.late + next.invalid == next.deliveries.size.toLong
    )
    next
  }

  def failAfterCommit(spark: SparkSession, input: Path, checkpoint: Path, sink: Path): Unit = {
    var failed = false
    try runProduct(spark, input, checkpoint, sink, true)
    catch {
      case e: org.apache.spark.sql.streaming.StreamingQueryException
          if e.toString.contains("injected_after_publication") =>
        failed = true
    }
    require(failed, "Expected after-publication query failure")
  }

  def recoverProduct(spark: SparkSession, input: Path, checkpoint: Path, sink: Path): RunReceipt = {
    runProduct(spark, input, checkpoint, sink, false)
  }

  def finishProduct(
      spark: SparkSession,
      root: Path,
      input: Path,
      checkpoint: Path,
      sink: Path
  ): ProductState = {
    publishFile(
      root,
      input,
      "batch-02.json",
      Seq(
        """{"delivery":5,"id":"E","event_second":120,"cents":40}""",
        """{"delivery":6,"id":"D","event_second":95,"cents":0}""",
        """{"delivery":7,"id":"C","event_second":94,"cents":7}""",
        """{"delivery":8,"id":"B","event_second":105,"cents":20}"""
      )
    )
    runProduct(spark, input, checkpoint, sink, false)
    val afterB = loadProduct(sink, 1L)
    require(
      afterB.accepted.size == 4 && afterB.duplicates == 2L && afterB.late == 1L && afterB.invalid == 1L && afterB
        .accepted("D") == ((95L, 0L))
    )
    publishFile(
      root,
      input,
      "batch-03.json",
      Seq(
        """{"delivery":9,"id":"B","event_second":105,"cents":999}""",
        """{"delivery":10,"id":"F","event_second":110,"cents":5}"""
      )
    )
    runProduct(spark, input, checkpoint, sink, false)
    loadProduct(sink, 2L)
  }

  def handoffState(state: ProductState): String = {
    require(
      state.accepted.size.toLong + state.duplicates + state.late + state.invalid == state.deliveries.size.toLong
    )
    stateJson(state)
  }

  def main(args: Array[String]): Unit = {
    var ownedRoot: Path = null
    val spark = SparkSession
      .builder()
      .appName("ds60-spark-042")
      .master("local[2]")
      .config("spark.ui.enabled", "false")
      .config("spark.driver.host", "127.0.0.1")
      .config("spark.driver.bindAddress", "127.0.0.1")
      .config("spark.sql.shuffle.partitions", "2")
      .config("spark.sql.adaptive.enabled", "false")
      .config("spark.sql.ansi.enabled", "true")
      .config("spark.sql.session.timeZone", "UTC")
      .getOrCreate()
    try {
      require(spark.sparkContext.master == "local[2]", "local-only course session")
      spark.sparkContext.setLogLevel("ERROR")
      require(spark.version == "4.0.1", "Prepared Spark4.0.1 required")
      spark.conf.set("spark.sql.streaming.stopTimeout", "5000")
      ownedRoot = Files.createTempDirectory(Paths.get(".").toAbsolutePath.normalize(), "spark-042-")
      val input = ownedRoot.resolve("input"); val checkpoint = ownedRoot.resolve("checkpoint");
      val sink = Files.createDirectory(ownedRoot.resolve("sink"))
      publishFile(
        ownedRoot,
        input,
        "batch-01.json",
        Seq(
          """{"delivery":1,"id":"A","event_second":100,"cents":10}""",
          """{"delivery":2,"id":"B","event_second":105,"cents":20}""",
          """{"delivery":3,"id":"A","event_second":100,"cents":10}""",
          """{"delivery":4,"id":null,"event_second":106,"cents":30}"""
        )
      )
      val staticA = spark.read.schema(productSchema).json(input.toString)
      // Exercise 1: Validate and canonicalize each raw microbatch
      val firstInput = canonicalProductInput(staticA)
      assert(
        decodeEvents(firstInput).map(_.delivery) == Seq(1L, 2L, 3L, 4L) && decodeEvents(
          firstInput
        ).last.id.isEmpty
      )
      var budgetRejected = false
      try canonicalProductInput(staticA.union(staticA).union(staticA))
      catch { case _: IllegalArgumentException => budgetRejected = true }
      assert(budgetRejected)
      // Exercise 2: Implement the explicit state and lateness policy
      val firstState = advancePolicy(emptyProduct, decodeEvents(firstInput))
      assert(
        firstState.accepted == Map(
          "A" -> (100L, 10L),
          "B" -> (105L, 20L)
        ) && firstState.duplicates == 1L && firstState.invalid == 1L && firstState.late == 0L && firstState.maxEvent
          .contains(105L)
      )
      val invalidFuture =
        advancePolicy(firstState, Seq(ProductEvent(11L, Some("F"), Some(999L), Some(-1L))))
      assert(
        invalidFuture.maxEvent.contains(
          105L
        ) && invalidFuture.invalid == 2L && firstState.invalid == 1L
      )
      // Exercise 3: Inject failure after publication but before query completion
      failAfterCommit(spark, input, checkpoint, sink)
      assert(productAttempts.toSeq == Seq(0L) && productAttemptRows.toSeq == Seq(4L))
      assert(loadProduct(sink, 0L) == firstState && !ownedQueries.last.isActive)
      val committedZero = Files.readString(productPath(sink, 0L), StandardCharsets.UTF_8)
      // Exercise 4: Replay the committed batch without applying it twice
      val recovered = recoverProduct(spark, input, checkpoint, sink)
      assert(productAttempts.toSeq == Seq(0L, 0L) && productAttemptRows.toSeq == Seq(4L, 4L))
      assert(productRuns(0)._1 == productRuns(1)._1 && productRuns(0)._2 != productRuns(1)._2)
      assert(
        Files.readString(
          productPath(sink, 0L),
          StandardCharsets.UTF_8
        ) == committedZero && loadProduct(sink, 0L) == firstState
      )
      // Exercise 5: Process late, boundary, duplicate and conflicting events
      val finalState = finishProduct(spark, ownedRoot, input, checkpoint, sink)
      assert(
        finalState.accepted.keySet == Set("A", "B", "D", "E", "F") && finalState
          .accepted("F") == ((110L, 5L))
      )
      assert(
        finalState.duplicates == 2L && finalState.late == 1L && finalState.invalid == 2L && finalState.deliveries.size == 10 && finalState.accepted.values
          .map(_._2)
          .sum == 75L
      )
      // Exercise 6: Hand off correctness, recovery and resource evidence
      assert(
        handoffState(
          finalState
        ) == """{"accepted":[{"cents":10,"event_second":100,"id":"A"},{"cents":20,"event_second":105,"id":"B"},{"cents":0,"event_second":95,"id":"D"},{"cents":40,"event_second":120,"id":"E"},{"cents":5,"event_second":110,"id":"F"}],"deliveries":[1,2,3,4,5,6,7,8,9,10],"duplicates":2,"invalid":2,"late":1,"max_event_second":120,"total_cents":75}"""
      )
      assert(
        productAttempts.toSeq == Seq(0L, 0L, 1L, 2L) && productAttemptRows.toSeq == Seq(
          4L,
          4L,
          4L,
          2L
        ) && productAttemptRows.sum == 14L
      )
      val queryCount = ownedQueries.size; var bindingRejected = false
      try runProduct(spark, input, ownedRoot.resolve("unrelated-checkpoint"), sink, false)
      catch {
        case e: IllegalArgumentException if e.getMessage.contains("binding mismatch") =>
          bindingRejected = true
      }
      assert(
        bindingRejected && ownedQueries.size == queryCount && ownedQueries.forall(q => !q.isActive)
      )
      println(
        "product=" + handoffState(
          finalState
        ) + ";callback_rows=" + productAttemptRows.sum + ";logical_rows=" + finalState.deliveries.size + ";committed_batches=3"
      )
      println(
        "spark-042: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString
      )
    } finally {
      try {
        ownedQueries.foreach(q => if (q.isActive) q.stop())
        require(
          !ownedQueries.exists(_.isActive),
          "Do not remove scratch while an owned query is active"
        )
        if (ownedRoot != null) deleteOwned(ownedRoot)
      } finally { spark.stop() }
    }
  }
}

// Exercise 1: Validate and canonicalize each raw microbatch. Inputs/task: Require the explicit four-field schema, at most 8 rows and unique delivery IDs 1..12. Preserve NULL/business-invalid fields for classification and emit deterministic JSON. Expected: BatchA has four occurrences with IDsA, B, A, NULL;NULL is preserved in canonical input. An oversized batch is rejected before collection. Verify: Compare decoded delivery IDs 1..4 and the NULL marker;reject a12-row union.
// Exercise 2: Implement the explicit state and lateness policy. Inputs/task: Freeze cutoff at previous committed max_event_second minus 10. Validate domain, then classify existing equal ID payload as duplicate, conflicting payload as invalid, new old event as late, and remaining event as accepted. Expected: AfterA:accepted 2, duplicate 1, late 0, invalid 1, total 30, max 105. An invalid far-future row does not advance max time. Verify: Assert exact state and an invalid future control;preserve the original state value.
// Exercise 3: Inject failure after publication but before query completion. Inputs/task: Run the actual foreachBatch query with one injected exception after the atomic commit file becomes visible. Expected: The query fails with injected_after_publication;commit 0 is readable and contains the correct first-state ledger. Verify: Inspect the expected streaming exception, attempt 0 and unchanged source/checkpoint ownership.
// Exercise 4: Replay the committed batch without applying it twice. Inputs/task: Restart the same compatible query and checkpoint. Validate the existing batch input/content/chain and reuse its state. Expected: Attempts 0,0 and callback rows 4,4;commit 0 bytes and logical state remain unchanged. Verify: Compare query/run identities, exact bytes and all first-state counters.
// Exercise 5: Process late, boundary, duplicate and conflicting events. Inputs/task: PublishBatchB thenBatchC as separate immutable files and run each finite invocation against the same checkpoint. Expected: Final accepted IDsA, B, D, E, F, total 75;duplicate 2, late 1, invalid 2;10 logical occurrences. Zero-valuedD and cutoff-boundaryF remain accepted. Verify: Compare intermediateB counts and the final literal state;the high-timeE must not make same-batchD late.
// Exercise 6: Hand off correctness, recovery and resource evidence. Inputs/task: Return the exact final canonical state, record callback work 14 versus logical occurrences 10, and reject binding the existing sink to a different checkpoint. Expected: Literal golden state matches;attempt IDs 0,0,1,2;callback rows 4,4,4,2;only owned inactive queries are eligible for cleanup. Verify: Compare the complete state JSON and namespace-refusal negative;state the single-writer/local-filesystem limitations.

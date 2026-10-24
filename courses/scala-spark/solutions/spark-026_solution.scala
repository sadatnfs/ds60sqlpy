import org.apache.spark.sql.{Column, DataFrame, Row, SparkSession}
import org.apache.spark.sql.functions._
import org.apache.spark.sql.types._

object Main {
  def collected(frame: DataFrame): Seq[(Long, Option[String])] = frame
    .select("id", "normalized")
    .orderBy("id")
    .collect()
    .toSeq
    .map(r => (r.getLong(0), if (r.isNullAt(1)) None else Some(r.getString(1))))

  def normalizeLabel(value: String): String = {
    if (value == null) null
    else
      value
        .replaceAll("[ \t\r\n]+", " ")
        .replaceAll("^ +| +$", "")
        .map(ch => if (ch >= 'A' && ch <= 'Z') (ch + 32).toChar else ch)
  }

  def builtinLabels(raw: DataFrame): DataFrame = {
    raw.select(
      col("id"),
      trim(
        regexp_replace(
          translate(col("label"), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"),
          "[ \t\r\n]+",
          " "
        )
      ).as("normalized")
    )
  }

  def udfLabels(raw: DataFrame): DataFrame = {
    val normalize = udf((value: String) => normalizeLabel(value))
    raw.select(col("id"), normalize(col("label")).as("normalized"))
  }

  def planEvidence(frame: DataFrame): String = {
    frame.queryExecution.executedPlan.toString
  }

  def labelCategories(frame: DataFrame): Seq[(String, Long)] = {
    frame
      .withColumn(
        "category",
        when(col("normalized").isNull, "missing")
          .when(col("normalized") === "", "empty")
          .otherwise("text")
      )
      .groupBy("category")
      .count()
      .collect()
      .toSeq
      .map(r => (r.getString(0), r.getLong(1)))
      .sortBy(_._1)
  }

  def validateGolden(
      actual: Seq[(Long, Option[String])],
      expected: Seq[(Long, Option[String])]
  ): Unit = {
    require(actual == expected, "Golden label contract mismatch")
  }

  def main(args: Array[String]): Unit = {

    val spark = SparkSession
      .builder()
      .appName("ds60-spark-026")
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
      val schema = StructType(
        Seq(StructField("id", LongType, false), StructField("label", StringType, true))
      )
      val raw = spark.createDataFrame(
        spark.sparkContext.parallelize(
          Seq(
            Row(1L, null),
            Row(2L, ""),
            Row(3L, "   "),
            Row(4L, "  ALPHA  Beta "),
            Row(5L, "\tA\nB\r "),
            Row(6L, "CAFÉ"),
            Row(7L, "Straße"),
            Row(8L, "\u00a0A\u00a0"),
            Row(9L, "İI"),
            Row(10L, "🙂 OK"),
            Row(11L, "e\u0301"),
            Row(12L, "NULL")
          ),
          2
        ),
        schema
      )
      val expected = Seq(
        (1L, None),
        (2L, Some("")),
        (3L, Some("")),
        (4L, Some("alpha beta")),
        (5L, Some("a b")),
        (6L, Some("cafÉ")),
        (7L, Some("straße")),
        (8L, Some("\u00a0a\u00a0")),
        (9L, Some("İi")),
        (10L, Some("🙂 ok")),
        (11L, Some("e\u0301")),
        (12L, Some("null"))
      )
      // Exercise 1: Implement the pure scalar rule precisely
      val scalar = raw
        .orderBy("id")
        .collect()
        .toSeq
        .map(r =>
          (r.getLong(0), Option(normalizeLabel(if (r.isNullAt(1)) null else r.getString(1))))
        )
      assert(scalar == expected)
      // Exercise 2: Express the same rule with native Spark functions
      val builtin = builtinLabels(raw)
      assert(collected(builtin) == expected && builtin.schema("normalized").dataType == StringType)
      // Exercise 3: Wrap the scalar rule with a declared UDF return type
      val custom = udfLabels(raw)
      assert(collected(custom) == expected && custom.schema("normalized").dataType == StringType)
      // Exercise 4: Locate the execution boundary in physical evidence
      val builtinPlan = planEvidence(builtin); val customPlan = planEvidence(custom)
      assert(!builtinPlan.contains("BatchEvalPython") && !builtinPlan.contains("ArrowEvalPython"))
      assert(
        customPlan.contains("UDF") && !customPlan.contains("BatchEvalPython") && !customPlan
          .contains("ArrowEvalPython")
      )
      println("builtin_plan=" + builtinPlan + ";scala_udf_plan=" + customPlan)
      // Exercise 5: Preserve missing, empty and ordinary-text populations
      for (frame <- Seq(builtin, custom)) {
        assert(labelCategories(frame) == Seq(("empty", 2L), ("missing", 1L), ("text", 9L)))
        assert(frame.filter(col("normalized") === "null").select("id").first().getLong(0) == 12L)
        assert(frame.filter(col("normalized").isNull).select("id").first().getLong(0) == 1L)
      }
      // Exercise 6: Reject a plausible but semantically broader implementation
      validateGolden(collected(builtin), expected)
      val wrong = raw
        .orderBy("id")
        .collect()
        .toSeq
        .map(r =>
          (
            r.getLong(0),
            if (r.isNullAt(1)) None
            else Some(r.getString(1).trim.toLowerCase(java.util.Locale.ROOT))
          )
        )
      val mismatches = wrong.zip(expected).collect { case (a, b) if a != b => a._1 }.toSet
      assert(Set(4L, 5L, 6L, 9L).subsetOf(mismatches))
      var rejectedGolden = false
      try validateGolden(wrong, expected)
      catch { case _: IllegalArgumentException => rejectedGolden = true }
      assert(rejectedGolden)
      println("wrong_rule_mismatch_ids=" + mismatches.toSeq.sorted)
      println(
        "spark-026: six Scala reference contracts passed; Spark=" + spark.version + "; Scala=" + scala.util.Properties.versionNumberString
      )
    } finally {
      try { () }
      finally { spark.stop() }
    }
  }
}

// Exercise 1: Implement the pure scalar rule precisely. Inputs/task: ReturnNULL/None unchanged;collapse only space, tab, newline andcarriage return runs, trim ordinary spaces, and translateASCII A-Z to a-z. Preserve otherUnicode code points. Expected: All 12 golden outputs, includingcafÉ,İi, nonbreaking-space-wrapped a and unchanged decomposed e-plus-accent. Verify: Apply the scalar function to every raw fixture value and compare with all golden pairs.
// Exercise 2: Express the same rule with native Spark functions. Inputs/task: Produce id, normalized using translate, regexp_replace andtrim on the label column. PreserveNULL propagation and the exact golden values. Expected: The twelve ordered output pairs equal the golden fixture and normalized has string type. Verify: Assert the full pair list andStringType;do not accept agreement with only one UDF implementation.
// Exercise 3: Wrap the scalar rule with a declared UDF return type. Inputs/task: Create a ScalaString UDF or a PythonStringType scalar UDF with useArrow=False, then return id, normalized. Keep the function pure and validate all outputs. Expected: Every pair matches the same twelve golden values. Python uses the non-Arrow scalar path;Scala stays in the JVM. Verify: Assert all golden pairs and string result type for the enabled language-specific UDF.
// Exercise 4: Locate the execution boundary in physical evidence. Inputs/task: Return the physical plan strings for the built-in and language-specific UDF relations. Identify Python evaluation only where it is actually present. Expected: Python UDF plan containsBatchEvalPython;built-in contains noPython evaluator. Scala UDF expression is present withoutBatchEvalPython orArrowEvalPython. Verify: Assert the language-appropriate markers and print both plans;do not infer a speed ratio from them.
// Exercise 5: Preserve missing, empty and ordinary-text populations. Inputs/task: Classify normalized values as missing, empty or text and count each category. Separately select the identity whose normalized text equals the literal null. Expected: Missing 1, empty 2, text 9. Literal null text belongs only toID 12;unknown value belongs only toID 1. Verify: Assert all category counts and both exact identity selections for built-in and UDF results.
// Exercise 6: Reject a plausible but semantically broader implementation. Inputs/task: Validate a result against the full golden sequence. Deliberately apply general lowercasing and default trimming without interior-whitespace collapse, and require rejection. Expected: The wrong implementation disagrees at least onIDs 4,5,6,9. Python additionally removes the preserved nonbreaking spaces atID 8. Verify: Assert named mismatch identities and that the golden validator raises rather than accepting a visually plausible normalization.

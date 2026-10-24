object Main {

  def parseAmount(raw: Option[String]): Option[Long] = {
    raw
      .flatMap(text => Option(text))
      .map(_.trim)
      .filter(_.matches("[0-9]+"))
      .flatMap(_.toLongOption)
      .filter(amount => amount >= 0L && amount <= 1000000L)
  }

  def classify(raw: Option[String]): String = {
    raw match {
      case None    => "missing"
      case Some(_) => if (parseAmount(raw).isDefined) "observed" else "rejected"
    }
  }

  def observed(tokens: Seq[Option[String]]): Seq[Long] = {
    tokens.flatMap(parseAmount)
  }

  def ledger(tokens: Seq[Option[String]]): Map[String, Long] = {
    tokens.foldLeft(Map("observed" -> 0L, "missing" -> 0L, "rejected" -> 0L)) { (counts, token) =>
      val kind = classify(token)
      counts.updated(kind, counts(kind) + 1L)
    }
  }

  def displayAmount(raw: Option[String]): String = {
    parseAmount(raw).fold(classify(raw))(_.toString)
  }

  def feeOption(raw: Option[String]): Option[Long] = {
    parseAmount(raw).map(_ / 20L)
  }

  def expectIllegalArgument(body: => Any): Unit = {
    var caught = false
    try body
    catch { case _: IllegalArgumentException => caught = true }
    assert(caught, "Expected IllegalArgumentException")
  }
  def expectArithmetic(body: => Any): Unit = {
    var caught = false
    try body
    catch { case _: ArithmeticException => caught = true }
    assert(caught, "Expected ArithmeticException")
  }

  def main(args: Array[String]): Unit = {
    // Exercise 1: Parse a strict optional amount
    assert(parseAmount(Some("0")).contains(0L) && parseAmount(Some(" 25 ")).contains(25L))
    assert(parseAmount(None).isEmpty && parseAmount(Some("bad")).isEmpty)
    assert(
      Seq(null, "", "-1", "+1", "1.0", "1000001", "999999999999999999999999").forall(text =>
        parseAmount(Some(text)).isEmpty
      )
    )
    // Exercise 2: Separate absence from invalid supplied content
    val tokens: Seq[Option[String]] =
      Seq(Some("0"), Some("25"), None, Some("bad"), Some(null: String))
    assert(tokens.map(classify) == Seq("observed", "observed", "missing", "rejected", "rejected"))
    assert(parseAmount(None) == parseAmount(Some("bad")))
    // Exercise 3: Collect only observed numerical values
    assert(observed(tokens) == Seq(0L, 25L))
    assert(observed(tokens :+ Some("25")) == Seq(0L, 25L, 25L))
    assert(observed(Seq(None, Some("bad"))).isEmpty)
    // Exercise 4: Reconcile all input states
    val counts = ledger(tokens)
    assert(counts == Map("observed" -> 2L, "missing" -> 1L, "rejected" -> 2L))
    assert(counts.values.sum == tokens.size.toLong)
    assert(ledger(Seq.empty) == Map("observed" -> 0L, "missing" -> 0L, "rejected" -> 0L))
    // Exercise 5: Keep presentation distinct from measurement
    assert(displayAmount(Some("0")) == "0")
    assert(displayAmount(None) == "missing" && displayAmount(Some("bad")) == "rejected")
    assert(displayAmount(Some(" 25 ")) == "25")
    // Exercise 6: Compose a downstream calculation without losing absence
    assert(feeOption(Some("100")).contains(5L) && feeOption(Some("0")).contains(0L))
    assert(feeOption(None).isEmpty && feeOption(Some("bad")).isEmpty)
    println("spark-005: six reference contracts passed")
    println(
      "Scala=" + scala.util.Properties.versionNumberString + "; Java=" + System.getProperty(
        "java.version"
      )
    )
  }
}

// Exercise 1: Parse a strict optional amount. Inputs/task: Accept trimmed ASCII digits representing 0 through 1000000 cents. Return None for absent, blank, signed, decimal, overflowing or supplied-null tokens. Do not convert invalid input to zero or call unchecked Option.get. Expected: Some("0") gives Some(0L), Some(" 25 ") gives Some(25L), None and Some("bad") give None. Some(null), Some("-1"), Some("1.0") and values above the bound are rejected. Verify: Assert accepted zero and 25 independently, then test each invalid token and absence without an exception.
// Exercise 2: Separate absence from invalid supplied content. Inputs/task: Return observed for a valid supplied amount, missing for None, and rejected for any invalid Some token including Some(null). Keep the original input state available when classifying. Expected: Some("0"), Some("25"), None, Some("bad"), Some(null) map to observed, observed, missing, rejected, rejected. Verify: Assert the five classifications in order and show that parseAmount alone returns None for both missing and rejected cases.
// Exercise 3: Collect only observed numerical values. Inputs/task: Return valid parsed amounts in original order using flatMap. Preserve zero and duplicate amounts; do not substitute defaults for missing or rejected tokens. Expected: The five-token fixture yields Seq(0L,25L). Adding another Some("25") yields two 25-cent occurrences. Verify: Assert exact observed sequences and an all-missing/rejected fixture returning empty.
// Exercise 4: Reconcile all input states. Inputs/task: Return counts for all three keys observed, missing, rejected, including zero counts. Classify every original token and require the counts to sum to input size. Expected: The five-token fixture yields observed 2, missing 1, rejected 2. Empty input retains all three keys with count 0. Verify: Assert the full map, its summed count, and the explicit empty-ledger keys.
// Exercise 5: Keep presentation distinct from measurement. Inputs/task: Return a valid amount as decimal text, or the literal missing/rejected classification for unavailable values. Do not display every unavailable value as 0. Expected: Some("0") displays"0", None displays"missing", and Some("bad") displays"rejected". Whitespace around a valid 25 is normalized to"25". Verify: Assert all four display strings and verify that missing is not numerically indistinguishable from observed zero.
// Exercise 6: Compose a downstream calculation without losing absence. Inputs/task: Return the five-percent integer-cent fee for a valid parsed amount and None otherwise. Compose the calculation through Option rather than using getOrElse(0L) before the fee calculation. Expected: Some("100") gives Some(5L), Some("0") gives Some(0L), and None or Some("bad") remain None. Verify: Assert presence and exact fee for valid zero and 100, then absence for both invalid and missing inputs.

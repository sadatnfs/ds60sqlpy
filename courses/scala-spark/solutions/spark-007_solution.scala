object Main {
  final case class Record(id: String, status: String, amount: Long)

  def parseId(raw: String): Either[String, String] = {
    Option(raw).map(_.trim).filter(_.nonEmpty).toRight("missing_id")
  }

  def parseStatus(raw: String): Either[String, String] = {
    Option(raw)
      .map(_.trim)
      .filter(value => Set("paid", "void").contains(value))
      .toRight("unknown_status")
  }

  def parseAmount(raw: String): Either[String, Long] = {
    Option(raw)
      .map(_.trim)
      .filter(_.matches("[0-9]+"))
      .flatMap(_.toLongOption)
      .filter(value => value >= 0L && value <= 1000000L)
      .toRight("invalid_amount")
  }

  def parseRecord(raw: String): Either[String, Record] = {
    if (raw == null) Left("malformed_record")
    else {
      val fields = raw.split("\\|", -1)
      if (fields.length != 3) Left("malformed_record")
      else
        for {
          id <- parseId(fields(0))
          status <- parseStatus(fields(1))
          amount <- parseAmount(fields(2))
        } yield Record(id, status, amount)
    }
  }

  def partitionRecords(lines: Seq[String]): (Seq[Record], Seq[(Int, String, String)]) = {
    lines.zipWithIndex.foldLeft((Vector.empty[Record], Vector.empty[(Int, String, String)])) {
      case ((accepted, rejected), (raw, position)) =>
        parseRecord(raw) match {
          case Right(record) => (accepted :+ record, rejected)
          case Left(reason)  => (accepted, rejected :+ ((position, raw, reason)))
        }
    }
  }

  def paidTotal(records: Seq[Record]): (Long, Long) = {
    records.filter(_.status == "paid").foldLeft((0L, 0L)) { case ((count, total), record) =>
      (count + 1L, Math.addExact(total, record.amount))
    }
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
    // Exercise 1: Validate source identity explicitly
    assert(parseId(" a1 ") == Right("a1"))
    assert(Seq(null, "", "  ").forall(value => parseId(value) == Left("missing_id")))
    // Exercise 2: Reject unsupported domain states
    assert(parseStatus(" paid ") == Right("paid") && parseStatus("void") == Right("void"))
    assert(
      Seq("mystery", "PAID", null).forall(value => parseStatus(value) == Left("unknown_status"))
    )
    // Exercise 3: Preserve exact bounded cents
    assert(parseAmount("0") == Right(0L) && parseAmount("100") == Right(100L))
    assert(
      Seq("bad", "-1", "1.5", "1000001", "999999999999999999999", null).forall(value =>
        parseAmount(value) == Left("invalid_amount")
      )
    )
    // Exercise 4: Compose fields with declared error precedence
    assert(parseRecord("a1|paid|100") == Right(Record("a1", "paid", 100L)))
    assert(parseRecord("a2|paid|") == Left("invalid_amount"))
    assert(parseRecord("|mystery|bad") == Left("missing_id"))
    assert(parseRecord("a|paid") == Left("malformed_record"))
    // Exercise 5: Retain a complete rejection ledger
    val lines =
      Seq("a1|paid|100", "a2|paid|0", "a3|void|50", "|paid|20", "a5|paid|bad", "a6|mystery|10")
    val result = partitionRecords(lines)
    assert(result._1.map(_.id) == Seq("a1", "a2", "a3"))
    assert(result._2.map { case (position, _, reason) =>
      (position, reason)
    } == Seq((3, "missing_id"), (4, "invalid_amount"), (5, "unknown_status")))
    assert(result._1.size + result._2.size == lines.size)
    // Exercise 6: Separate valid records from eligible revenue
    assert(paidTotal(result._1) == (2L, 100L))
    assert(parseRecord("a4|void|bad") == Left("invalid_amount"))
    assert(paidTotal(Seq.empty) == (0L, 0L))
    println("spark-007: six reference contracts passed")
    println(
      "Scala=" + scala.util.Properties.versionNumberString + "; Java=" + System.getProperty(
        "java.version"
      )
    )
  }
}

// Exercise 1: Validate source identity explicitly. Inputs/task: Trim an ID token and return Right for nonempty text. Return Left(missing_id) for null, empty or whitespace-only tokens. Do not invent an identifier. Expected: " a1 " gives Right("a1");null,"" and"  " each give Left("missing_id"). Verify: Assert one normalized identity and all three missing representations without throwing.
// Exercise 2: Reject unsupported domain states. Inputs/task: Accept only trimmed lowercase paid or void. Return Left(unknown_status) for all other supplied values, including uppercase PAID and null. Do not silently case-fold unless the source contract explicitly permits it. Expected: " paid " and"void" return Right("paid") and Right("void");"mystery","PAID" and null are rejected. Verify: Assert both valid states and three unsupported forms; confirm that whitespace normalization is separate from case normalization.
// Exercise 3: Preserve exact bounded cents. Inputs/task: Accept trimmed ASCII digits representing 0 through 1000000 as a Long. Return Left(invalid_amount) for null, blank, signed, decimal, overflowing or out-of-domain text. Expected: "0" and"100" become Right(0L), Right(100L);"bad","-1","1.5","1000001" and a huge integer token are rejected. Verify: Assert zero separately from rejection, and test both lexical failure and numeric range failure.
// Exercise 4: Compose fields with declared error precedence. Inputs/task: Require exactly three pipe-separated fields and compose ID, status, amount validation in that order using a for comprehension. Return Left(malformed_record) for null or wrong field count. Preserve empty trailing fields for validation. Expected: a1|paid|100 becomes Right(Record(a1, paid,100));a2|paid| becomes invalid_amount;an empty-ID malformed-status record reports missing_id first;two fields report malformed_record. Verify: Assert a valid record, trailing-empty rejection, first-error precedence and field-count failure.
// Exercise 5: Retain a complete rejection ledger. Inputs/task: Parse every input line and return accepted records plus rejected(position, raw, reason) tuples. Position is the zero-based occurrence index; preserve encounter order in both outputs and never discard a Left. Expected: The six-line fixture has three accepted records and rejections at positions 3,4,5 with missing_id, invalid_amount, unknown_status. Accepted plus rejected equals six. Verify: Assert accepted IDs[a1, a2, a3], the exact rejected positions/reasons and count conservation.
// Exercise 6: Separate valid records from eligible revenue. Inputs/task: From already accepted records, return paid-event count and checked paid cents total. Retain an observed zero paid event in the count and exclude valid void records only at this business-report stage. Expected: The three accepted records yield paid count 2, total 100. A void record with malformed amount must have been rejected by parseRecord before this function can run. Verify: Assert the paid metrics and show that a4|void|bad produces Left(invalid_amount), not a silently skipped valid void.

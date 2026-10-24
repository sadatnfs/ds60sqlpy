object Main {
  final case class Record(id: String, status: String, amount: Long)

  def parseId(raw: String): Either[String, String] =
    throw new UnsupportedOperationException("Complete parseId")

  def parseStatus(raw: String): Either[String, String] =
    throw new UnsupportedOperationException("Complete parseStatus")

  def parseAmount(raw: String): Either[String, Long] =
    throw new UnsupportedOperationException("Complete parseAmount")

  def parseRecord(raw: String): Either[String, Record] =
    throw new UnsupportedOperationException("Complete parseRecord")

  def partitionRecords(lines: Seq[String]): (Seq[Record], Seq[(Int, String, String)]) =
    throw new UnsupportedOperationException("Complete partitionRecords")

  def paidTotal(records: Seq[Record]): (Long, Long) =
    throw new UnsupportedOperationException("Complete paidTotal")

  def main(args: Array[String]): Unit = {
    locally {
      val value: Either[String, Long] = Right(25L)
      val invalid: Either[String, Long] = Left("invalid_amount")
      assert(value.map(_ + 5L) == Right(30L))
      assert(invalid.map(_ + 5L) == Left("invalid_amount"))
      println(value.map(_ / 5L))
    }
    locally {
      val combined = for {
        amount <- (Right(20L): Either[String, Long])
        fee <- (Right(5L): Either[String, Long])
      } yield amount + fee
      assert(combined == Right(25L))
      val blocked = for {
        amount <- (Left("invalid_amount"): Either[String, Long])
        fee <- (Right(5L): Either[String, Long])
      } yield amount + fee
      assert(blocked == Left("invalid_amount"))
      println(combined)
    }
    println("spark-007: worked examples passed; six task implementations remain")
  }
}

// Exercise 1: Validate source identity explicitly. Inputs/task: Trim an ID token and return Right for nonempty text. Return Left(missing_id) for null, empty or whitespace-only tokens. Do not invent an identifier. Expected: " a1 " gives Right("a1");null,"" and"  " each give Left("missing_id"). Verify: Assert one normalized identity and all three missing representations without throwing.
// Exercise 2: Reject unsupported domain states. Inputs/task: Accept only trimmed lowercase paid or void. Return Left(unknown_status) for all other supplied values, including uppercase PAID and null. Do not silently case-fold unless the source contract explicitly permits it. Expected: " paid " and"void" return Right("paid") and Right("void");"mystery","PAID" and null are rejected. Verify: Assert both valid states and three unsupported forms; confirm that whitespace normalization is separate from case normalization.
// Exercise 3: Preserve exact bounded cents. Inputs/task: Accept trimmed ASCII digits representing 0 through 1000000 as a Long. Return Left(invalid_amount) for null, blank, signed, decimal, overflowing or out-of-domain text. Expected: "0" and"100" become Right(0L), Right(100L);"bad","-1","1.5","1000001" and a huge integer token are rejected. Verify: Assert zero separately from rejection, and test both lexical failure and numeric range failure.
// Exercise 4: Compose fields with declared error precedence. Inputs/task: Require exactly three pipe-separated fields and compose ID, status, amount validation in that order using a for comprehension. Return Left(malformed_record) for null or wrong field count. Preserve empty trailing fields for validation. Expected: a1|paid|100 becomes Right(Record(a1, paid,100));a2|paid| becomes invalid_amount;an empty-ID malformed-status record reports missing_id first;two fields report malformed_record. Verify: Assert a valid record, trailing-empty rejection, first-error precedence and field-count failure.
// Exercise 5: Retain a complete rejection ledger. Inputs/task: Parse every input line and return accepted records plus rejected(position, raw, reason) tuples. Position is the zero-based occurrence index; preserve encounter order in both outputs and never discard a Left. Expected: The six-line fixture has three accepted records and rejections at positions 3,4,5 with missing_id, invalid_amount, unknown_status. Accepted plus rejected equals six. Verify: Assert accepted IDs[a1, a2, a3], the exact rejected positions/reasons and count conservation.
// Exercise 6: Separate valid records from eligible revenue. Inputs/task: From already accepted records, return paid-event count and checked paid cents total. Retain an observed zero paid event in the count and exclude valid void records only at this business-report stage. Expected: The three accepted records yield paid count 2, total 100. A void record with malformed amount must have been rejected by parseRecord before this function can run. Verify: Assert the paid metrics and show that a4|void|bad produces Left(invalid_amount), not a silently skipped valid void.

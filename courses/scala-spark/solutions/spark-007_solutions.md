# spark-007: Explained reference solutions

Read the [guide](../guides/spark-007.md) and attempt the [learner source](../lessons/spark-007.scala) first. The [complete reference](spark-007_solution.scala) contains each implementation and its assertions. Values, identity, missingness and failure behavior are separate checks; compilation alone does not establish any of them.

## Exercises and reasoning

### Shared domain definitions

```scala
final case class Record(id: String, status: String, amount: Long)
```

### Exercise 1: Validate source identity explicitly

Trim an ID token and return Right for nonempty text. Return Left(missing_id) for null, empty or whitespace-only tokens. Do not invent an identifier.

**Expected:** " a1 " gives Right("a1"); null,"" and"  " each give Left("missing_id").

```scala
def parseId(raw: String): Either[String, String] = {
  Option(raw).map(_.trim).filter(_.nonEmpty).toRight("missing_id")
}
```

Identity normalization happens before the emptiness check, so whitespace is not accepted as a meaningful ID. Option protects a possible JVM null reference without treating it as text. toRight converts absence into a named validation reason, which can be retained in a rejection ledger. No generated row number is substituted for a missing business ID because that would create a different identity contract.

```scala
assert(parseId(" a1 ") == Right("a1"))
assert(Seq(null, "", "  ").forall(value => parseId(value) == Left("missing_id")))
```

### Exercise 2: Reject unsupported domain states

Accept only trimmed lowercase paid or void. Return Left(unknown_status) for all other supplied values, including uppercase PAID and null. Do not silently case-fold unless the source contract explicitly permits it.

**Expected:** " paid " and"void" return Right("paid") and Right("void");"mystery","PAID" and null are rejected.

```scala
def parseStatus(raw: String): Either[String, String] = {
  Option(raw)
    .map(_.trim)
    .filter(value => Set("paid", "void").contains(value))
    .toRight("unknown_status")
}
```

The accepted domain is explicit and finite. Trimming is allowed, but case folding would be an additional normalization policy that could conceal an upstream contract change. Unknown states remain rejected even if their amount looks valid. This is the ingestion counterpart of a sealed-state model: accepted strings have a known interpretation before downstream code chooses business behavior.

```scala
assert(parseStatus(" paid ") == Right("paid") && parseStatus("void") == Right("void"))
assert(Seq("mystery", "PAID", null).forall(value => parseStatus(value) == Left("unknown_status")))
```

### Exercise 3: Preserve exact bounded cents

Accept trimmed ASCII digits representing 0 through 1000000 as a Long. Return Left(invalid_amount) for null, blank, signed, decimal, overflowing or out-of-domain text.

**Expected:** "0" and"100" become Right(0L), Right(100L);"bad","-1","1.5","1000001" and a huge integer token are rejected.

```scala
def parseAmount(raw: String): Either[String, Long] = {
  Option(raw)
    .map(_.trim)
    .filter(_.matches("[0-9]+"))
    .flatMap(_.toLongOption)
    .filter(value => value >= 0L && value <= 1000000L)
    .toRight("invalid_amount")
}
```

Lexical validation defines which textual forms are meaningful before numeric conversion. toLongOption rejects representational overflow without an exception, and the final filter applies the narrower teaching-domain bound. Observed zero is a successful Right value, so invalid tokens cannot be confused with free or zero-valued events. Exact integer cents avoid an unnecessary floating-point round trip.

```scala
assert(parseAmount("0") == Right(0L) && parseAmount("100") == Right(100L))
assert(
  Seq("bad", "-1", "1.5", "1000001", "999999999999999999999", null).forall(value =>
    parseAmount(value) == Left("invalid_amount")
  )
)
```

### Exercise 4: Compose fields with declared error precedence

Require exactly three pipe-separated fields and compose ID, status, amount validation in that order using a for comprehension. Return Left(malformed_record) for null or wrong field count. Preserve empty trailing fields for validation.

**Expected:** a1|paid|100 becomes Right(Record(a1, paid,100)); a2|paid| becomes invalid_amount; an empty-ID malformed-status record reports missing_id first; two fields report malformed_record.

```scala
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
```

The arity guard prevents an indexing exception and distinguishes malformed record structure from a field-level error. Keeping trailing empty fields lets the amount parser report the actual missing-value problem. The for comprehension establishes fail-fast precedence: ID errors come before status and amount errors. An accumulating validator would be needed to report all failures on one record; this function deliberately returns one reproducible reason.

```scala
assert(parseRecord("a1|paid|100") == Right(Record("a1", "paid", 100L)))
assert(parseRecord("a2|paid|") == Left("invalid_amount"))
assert(parseRecord("|mystery|bad") == Left("missing_id"))
assert(parseRecord("a|paid") == Left("malformed_record"))
```

### Exercise 5: Retain a complete rejection ledger

Parse every input line and return accepted records plus rejected(position, raw, reason) tuples. Position is the zero-based occurrence index; preserve encounter order in both outputs and never discard a Left.

**Expected:** The six-line fixture has three accepted records and rejections at positions 3,4,5 with missing_id, invalid_amount, unknown_status. Accepted plus rejected equals six.

```scala
def partitionRecords(lines: Seq[String]): (Seq[Record], Seq[(Int, String, String)]) = {
  lines.zipWithIndex.foldLeft((Vector.empty[Record], Vector.empty[(Int, String, String)])) {
    case ((accepted, rejected), (raw, position)) =>
      parseRecord(raw) match {
        case Right(record) => (accepted :+ record, rejected)
        case Left(reason)  => (accepted, rejected :+ ((position, raw, reason)))
      }
  }
}
```

The fold carries accepted and rejected collections together so every source occurrence is assigned exactly one outcome. Position distinguishes repeated malformed lines even when they have no valid ID. The raw text remains available for diagnosis rather than being replaced by a sanitized value that hides the original failure. Vector append is used for predictable local accumulation; large distributed ingestion will need a separate partitioned data contract.

```scala
val lines =
  Seq("a1|paid|100", "a2|paid|0", "a3|void|50", "|paid|20", "a5|paid|bad", "a6|mystery|10")
val result = partitionRecords(lines)
assert(result._1.map(_.id) == Seq("a1", "a2", "a3"))
assert(result._2.map { case (position, _, reason) =>
  (position, reason)
} == Seq((3, "missing_id"), (4, "invalid_amount"), (5, "unknown_status")))
assert(result._1.size + result._2.size == lines.size)
```

### Exercise 6: Separate valid records from eligible revenue

From already accepted records, return paid-event count and checked paid cents total. Retain an observed zero paid event in the count and exclude valid void records only at this business-report stage.

**Expected:** The three accepted records yield paid count 2, total 100. A void record with malformed amount must have been rejected by parseRecord before this function can run.

```scala
def paidTotal(records: Seq[Record]): (Long, Long) = {
  records.filter(_.status == "paid").foldLeft((0L, 0L)) { case ((count, total), record) =>
    (count + 1L, Math.addExact(total, record.amount))
  }
}
```

Validity and reporting eligibility are separate decisions. The void record is valid data and remains in accepted counts, while only paid records contribute to this revenue metric. The zero paid record still counts as a real paid event. Validating amount before applying the status filter prevents malformed void rows from disappearing behind a business exclusion and keeps the ingestion ledger auditable.

```scala
assert(paidTotal(result._1) == (2L, 100L))
assert(parseRecord("a4|void|bad") == Left("invalid_amount"))
assert(paidTotal(Seq.empty) == (0L, 0L))
```

## Evidence and scope

Run the complete reference using the same prepared profile as the learner source. Its assertions check normal values, malformed or boundary inputs and conservation where relevant. The final version line records the actual compiler/runtime family used. The reference is an executable explanation, not a hidden grading service or proof that a distributed Spark job would have the same performance characteristics.

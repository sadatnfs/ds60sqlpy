# spark-005: Explained reference solutions

Attempt the [guide](../guides/spark-005.md) exercises first.

Reference: [complete Scala program](spark-005_solution.scala).

## Exercises and reasoning

### Exercise 1: Parse a strict optional amount

Accept trimmed ASCII digits representing 0 through 1000000 cents. Return None for absent, blank, signed, decimal, overflowing or supplied-null tokens. Do not convert invalid input to zero or call unchecked Option.get.

**Expected:** Some("0") gives Some(0L), Some(" 25 ") gives Some(25L), None and Some("bad") give None. Some(null), Some("-1"), Some("1.0") and values above the bound are rejected.

```scala
def parseAmount(raw: Option[String]): Option[Long] = {
  raw
    .flatMap(text => Option(text))
    .map(_.trim)
    .filter(_.matches("[0-9]+"))
    .flatMap(_.toLongOption)
    .filter(amount => amount >= 0L && amount <= 1000000L)
}
```

Each stage has a separate role: protect the inner null reference, normalize permitted whitespace, validate the lexical grammar, convert without an exception, and enforce the domain bound. A conversion method alone may accept signed forms that the contract excludes. Some(0L) survives every stage as an observed value. None remains a result state rather than an instruction to invent a zero measurement.

```scala
assert(parseAmount(Some("0")).contains(0L) && parseAmount(Some(" 25 ")).contains(25L))
assert(parseAmount(None).isEmpty && parseAmount(Some("bad")).isEmpty)
assert(
  Seq(null, "", "-1", "+1", "1.0", "1000001", "999999999999999999999999").forall(text =>
    parseAmount(Some(text)).isEmpty
  )
)
```

### Exercise 2: Separate absence from invalid supplied content

Return observed for a valid supplied amount, missing for None, and rejected for any invalid Some token including Some(null). Keep the original input state available when classifying.

**Expected:** Some("0"), Some("25"), None, Some("bad"), Some(null) map to observed, observed, missing, rejected, rejected.

```scala
def classify(raw: Option[String]): String = {
  raw match {
    case None    => "missing"
    case Some(_) => if (parseAmount(raw).isDefined) "observed" else "rejected"
  }
}
```

The original Option supplies provenance that the parsed Option no longer contains. A valid observed zero is classified as observed because isDefined examines presence, not numeric truthiness. Supplied null is rejected because the outer state was Some. The final assertion demonstrates the information loss in a parser returning only Option and motivates a richer validation result in a later lesson.

```scala
val tokens: Seq[Option[String]] = Seq(Some("0"), Some("25"), None, Some("bad"), Some(null: String))
assert(tokens.map(classify) == Seq("observed", "observed", "missing", "rejected", "rejected"))
assert(parseAmount(None) == parseAmount(Some("bad")))
```

### Exercise 3: Collect only observed numerical values

Return valid parsed amounts in original order using flatMap. Preserve zero and duplicate amounts; do not substitute defaults for missing or rejected tokens.

**Expected:** The five-token fixture yields `Seq(0L, 25L)`. Adding another Some("25") yields two 25-cent occurrences.

```scala
def observed(tokens: Seq[Option[String]]): Seq[Long] = {
  tokens.flatMap(parseAmount)
}
```

Each input parser contributes either one observed Long or no observed numerical value. Sequence flatMap combines those contributions while retaining order and duplicates. This numerical projection intentionally omits missing and rejected tokens, so it must be paired with the classification ledger rather than presented as the complete data product. The all-invalid case returns an empty sequence rather than a fabricated collection of zeros.

```scala
assert(observed(tokens) == Seq(0L, 25L))
assert(observed(tokens :+ Some("25")) == Seq(0L, 25L, 25L))
assert(observed(Seq(None, Some("bad"))).isEmpty)
```

### Exercise 4: Reconcile all input states

Return counts for all three keys observed, missing, rejected, including zero counts. Classify every original token and require the counts to sum to input size.

**Expected:** The five-token fixture yields observed 2, missing 1, rejected 2. Empty input retains all three keys with count 0.

```scala
def ledger(tokens: Seq[Option[String]]): Map[String, Long] = {
  tokens.foldLeft(Map("observed" -> 0L, "missing" -> 0L, "rejected" -> 0L)) { (counts, token) =>
    val kind = classify(token)
    counts.updated(kind, counts(kind) + 1L)
  }
}
```

Initializing every category keeps the report schema stable even when a category is absent or the input is empty. Every token updates exactly one category, so total count conservation is meaningful. The ledger explains why the observed sequence has only two entries. Reporting only its sum 25 would not reveal whether the other three tokens were absent, malformed or accidentally dropped.

```scala
val counts = ledger(tokens)
assert(counts == Map("observed" -> 2L, "missing" -> 1L, "rejected" -> 2L))
assert(counts.values.sum == tokens.size.toLong)
assert(ledger(Seq.empty) == Map("observed" -> 0L, "missing" -> 0L, "rejected" -> 0L))
```

### Exercise 5: Keep presentation distinct from measurement

Return a valid amount as decimal text, or the literal missing/rejected classification for unavailable values. Do not display every unavailable value as 0.

**Expected:** Some("0") displays"0", None displays"missing", and Some("bad") displays"rejected". Whitespace around a valid 25 is normalized to"25".

```scala
def displayAmount(raw: Option[String]): String = {
  parseAmount(raw).fold(classify(raw))(_.toString)
}
```

Option.fold chooses one of two explicit presentation branches without unchecked extraction. The fallback is a semantic label rather than a numeric default, so the user can distinguish observed zero from unavailable data. Formatting is performed after successful parsing, which means whitespace and leading zeros do not survive as accidental alternate numerical representations. The original token can still be retained separately for audit.

```scala
assert(displayAmount(Some("0")) == "0")
assert(displayAmount(None) == "missing" && displayAmount(Some("bad")) == "rejected")
assert(displayAmount(Some(" 25 ")) == "25")
```

### Exercise 6: Compose a downstream calculation without losing absence

Return the five-percent integer-cent fee for a valid parsed amount and None otherwise. Compose the calculation through Option rather than using getOrElse(0L) before the fee calculation.

**Expected:** Some("100") gives Some(5L), Some("0") gives Some(0L), and None or Some("bad") remain None.

```scala
def feeOption(raw: Option[String]): Option[Long] = {
  parseAmount(raw).map(_ / 20L)
}
```

The fee transformation runs only when parsing supplied a valid value. Missingness remains in the result type across the downstream calculation, while observed zero produces a present zero fee. A premature getOrElse(0L) would collapse those states and make later quality reporting impossible. The division policy is the same nonnegative rounded-down rule established in the collection lesson.

```scala
assert(feeOption(Some("100")).contains(5L) && feeOption(Some("0")).contains(0L))
assert(feeOption(None).isEmpty && feeOption(Some("bad")).isEmpty)
```

## Evidence and scope

The reference checks each parser and classifier against literal expectations from the token fixture: `Some(0L)` and `Some(25L)` for the valid tokens, `None` for absence and for each invalid token, the ledger `observed -> 2, missing -> 1, rejected -> 2`, and a ledger of three zero counts for an empty input. It also covers the boundary tokens that a casual parser accepts by mistake: a signed value, a decimal, a value above 1,000,000 cents and a supplied `null`. The fee check confirms `Some("100")` gives `Some(5L)` and that `None` and `Some("bad")` both stay `None`.

The success line `spark-005: six reference contracts passed` is followed by the Scala and Java versions of this run. Passing shows that no state was collapsed on these tokens; it does not prove the parser handles every Unicode digit or locale format, because the contract deliberately accepts only trimmed ASCII digits. Spark has the same distinction in a different form: a SQL NULL is absence, while a malformed string cast under ANSI mode is an error, and later lessons keep those apart the same way this ledger does.


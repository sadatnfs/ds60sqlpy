import scala.collection.mutable.ArrayBuffer

object Main {


  def strictPipeline(values: Seq[Int]): Seq[Int] = {
    require(values.forall(value => value >= -1000000 && value <= 1000000), "input outside bounded domain")
    values.filter(_ % 2 == 0).map(_ * 2)
  }

  def tracedIterator(values: Seq[Int], trace: ArrayBuffer[String]): Iterator[Int] = {
    require(values.forall(value => value >= -1000000 && value <= 1000000), "input outside bounded domain")
    values.iterator.filter { value =>
      trace += s"filter:$value"
      value % 2 == 0
    }.map { value =>
      trace += s"map:$value"
      value * 2
    }
  }

  def consumeTwice(values: Iterator[Int]): (Vector[Int], Vector[Int]) = {
    val first = values.toVector
    val second = values.toVector
    (first,second)
  }

  def freshFactory(values: Seq[Int]): () => Iterator[Int] = {
    require(values.forall(value => value >= -1000000 && value <= 1000000), "input outside bounded domain")
    () => values.iterator.filter(_ % 2 == 0).map(_ * 2)
  }

  def retryTotals(records: Seq[(String, Long)], attempts: Int): (Long, Long) = {
    require(attempts >= 0, "attempt count must be nonnegative")
    require(records.forall { case (id,amount) => id != null && id.trim.nonEmpty && amount >= 0L && amount <= 1000000L }, "invalid event domain")
    val groups = records.groupBy(_._1)
    require(groups.values.forall(rows => rows.map(_._2).distinct.size == 1), "conflicting payload for one event ID")
    val oneAttempt = records.foldLeft(0L)((total,row) => Math.addExact(total,row._2))
    val naive = Math.multiplyExact(oneAttempt,attempts.toLong)
    val logical = if (attempts == 0) 0L else groups.values.foldLeft(0L)((total,rows) => Math.addExact(total,rows.head._2))
    (naive,logical)
  }

  def boundedTake(values: Iterator[Int], limit: Int): Vector[Int] = {
    require(limit >= 0 && limit <= 1000, "prefix budget outside 0..1000")
    values.take(limit).toVector
  }

  def expectIllegalArgument(body: => Any): Unit = {
    var caught = false
    try body catch { case _: IllegalArgumentException => caught = true }
    assert(caught, "Expected IllegalArgumentException")
  }
  def expectArithmetic(body: => Any): Unit = {
    var caught = false
    try body catch { case _: ArithmeticException => caught = true }
    assert(caught, "Expected ArithmeticException")
  }

  def main(args: Array[String]): Unit = {
    // Exercise 1: Establish a pure strict result
    val raw = Seq(1,2,3,4)
    assert(strictPipeline(raw) == Seq(4,8) && raw == Seq(1,2,3,4))
    assert(strictPipeline(Seq(0,2,2)) == Seq(0,4,4) && strictPipeline(Seq.empty).isEmpty)
    expectIllegalArgument(strictPipeline(Seq(1000001)))
    // Exercise 2: Locate the evaluation boundary
    val trace = ArrayBuffer.empty[String]
    val iterator = tracedIterator(raw,trace)
    assert(trace.isEmpty)
    assert(iterator.take(1).toVector == Vector(4))
    assert(trace.toVector == Vector("filter:1","filter:2","map:2"))
    assert(iterator.toVector == Vector(8))
    assert(trace.toVector == Vector("filter:1","filter:2","map:2","filter:3","filter:4","map:4"))
    // Exercise 3: Expose one-shot traversal state
    assert(consumeTwice(Iterator(1,2,3)) == (Vector(1,2,3),Vector.empty[Int]))
    assert(consumeTwice(Iterator.empty) == (Vector.empty[Int],Vector.empty[Int]))
    // Exercise 4: Provide repeatability deliberately
    val factory = freshFactory(raw)
    val first = factory();val second = factory()
    assert(first.toVector == Vector(4,8) && second.toVector == Vector(4,8))
    assert(raw == Seq(1,2,3,4))
    // Exercise 5: Separate repeated delivery from logical identity
    val deliveries = Seq(("a",100L),("b",50L),("a",100L))
    assert(retryTotals(deliveries,2) == (500L,150L))
    assert(retryTotals(deliveries,0) == (0L,0L))
    expectIllegalArgument(retryTotals(Seq(("a",100L),("a",101L)),1))
    expectIllegalArgument(retryTotals(deliveries,-1))
    // Exercise 6: Consume only a declared bounded prefix
    var visits = 0
    val infinite = Iterator.from(1).map { value => visits += 1; value }
    assert(boundedTake(infinite,3) == Vector(1,2,3) && visits == 3)
    assert(infinite.next() == 4)
    val untouched = Iterator.from(1)
    assert(boundedTake(untouched,0).isEmpty && untouched.next() == 1)
    expectIllegalArgument(boundedTake(Iterator.from(1),1001))
    println("spark-010: six reference contracts passed")
    println("Scala=" + scala.util.Properties.versionNumberString + "; Java=" + System.getProperty("java.version"))
  }
}

// Exercise 1: Establish a pure strict result. Inputs/task: For inputs between-1000000 and 1000000, retain even values and double them in order. Preserve input and duplicates. Reject values outside the bound so Int multiplication is safe. Expected: Seq(1,2,3,4) becomes Seq(4,8);Seq(0,2,2) becomes Seq(0,4,4);empty remains empty. Verify: Assert the exact results, input preservation and the out-of-domain rejection.
// Exercise 2: Locate the evaluation boundary. Inputs/task: Return a lazy even-filter/double-map iterator with local trace messages filter:value and map:value. Validate the same numeric domain before construction. The trace should remain empty until consumption. Expected: Taking one output from 1,2,3,4 yields 4 with trace filter:1, filter:2, map:2. Consuming the rest yields 8 and appends filter:3, filter:4, map:4. Verify: Assert the empty initial trace, both exact output pieces and all six messages in order.
// Exercise 3: Expose one-shot traversal state. Inputs/task: Consume a supplied iterator into a Vector twice and return both results. Do not cache or recreate the iterator inside this function. Explain why this intentionally returns an empty second traversal. Expected: A fresh iterator over 1,2,3 yields (Vector(1,2,3), Vector.empty). An already empty iterator yields two empty Vectors. Verify: Assert both tuple components and the already-exhausted case.
// Exercise 4: Provide repeatability deliberately. Inputs/task: Return a factory creating a fresh bounded even-filter/double-map iterator on each call. Validate source values once and preserve them. Do not return the same iterator object repeatedly. Expected: Two factory calls both yield Vector(4,8) for 1,2,3,4, even after the first is exhausted. Verify: Consume two independently obtained iterators and assert both exact results;verify the immutable source remains unchanged.
// Exercise 5: Separate repeated delivery from logical identity. Inputs/task: For bounded nonnegative event amounts and nonblank IDs, compute naive delivered cents over attempts and logical once-per-ID cents when attempts>0. Reject conflicting amounts for one ID and negative attempt counts. This is a pure ledger calculation, not a real sink. Expected: Records(a,100),(b,50),(a,100) with two attempts give naive 500, logical 150. Zero attempts gives (0,0);same ID with 100 and 101 is rejected. Verify: Assert both totals, the zero-attempt identity and a conflicting-payload failure.
// Exercise 6: Consume only a declared bounded prefix. Inputs/task: Return at most limit values from an iterator, requiring 0<=limit<=1000. Support infinite iterators without collecting the whole source. Limit 0 must leave the next source value unconsumed. Expected: Taking three values from Iterator.from(1) yields 1,2,3 and leaves 4 next. Limit 0 yields empty and leaves 1 next;limit 1001 is rejected. Verify: Use a local next-value counter to assert three produced values, and test zero consumption and the upper-budget failure.

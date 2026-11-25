# cuda-117: explained solutions

Compare with your [worksheet](../lessons/cuda-117.md) attempt.

## Exercise 1: Calculate both counts

Row count 3 and non-null count 2.

**Approach.** Calculate both counts over `[2, null, 5]`: `COUNT(*)` is 3 because it counts rows, and `COUNT(value)` is 2 because it counts non-null values; `SUM(value)` is 7.

**Why it is correct here.** SQL defines `COUNT(*)` on rows and `COUNT(expr)` on non-null expression values, and aggregate functions such as SUM skip nulls.

**A plausible wrong approach.** Treating null as zero gives the same sum but makes `COUNT(value)` 3 and the average 7/3 instead of 3.5, which disagrees with Spark.

**How to verify.** The reference asserts row count 3, non-null count 2 and sum 7. Run the same aggregates in Spark on CPU and GPU and compare.

## Exercise 2: Handle all-null aggregate

Follow Spark SQL null-result semantics.

**Approach.** Handle an all-null aggregate: under Spark SQL semantics, `SUM` and `AVG` over only null values return null, while `COUNT(value)` returns 0.

**Why it is correct here.** Null means no defined value, so a sum over no values is null rather than zero. Count still has a defined answer.

**A plausible wrong approach.** Returning 0 for the sum of an all-null group makes a group with no data look like a group whose values cancel out.

**How to verify.** Create a group with only nulls and assert the documented null and zero results on both paths. Include a second group with mixed values so the test also confirms nulls are skipped there.

## Exercise 3: Compare decimal values

Use exact decimal type and scale.

**Approach.** Compare decimal values with an exact decimal type and scale: `Decimal('1.10') + Decimal('2.20')` equals `Decimal('3.30')`.

**Why it is correct here.** Decimals represent base-ten fractions exactly within their precision, so equality is exact. Spark also tracks result precision and scale.

**A plausible wrong approach.** Using float64 for the same values gives `3.3000000000000003`, which fails an exact comparison and suggests a bug that exists only in the test.

**How to verify.** The reference asserts the decimal equality. In Spark, check the result schema's precision and scale as well as the value.

## Exercise 4: Name timestamp timezone

Set and record session timezone.

**Approach.** Name the session timezone explicitly, such as `spark.sql.session.timeZone = UTC`, and record it with every timestamp result.

**Why it is correct here.** Spark renders and parses timestamps using the session timezone. Two runs with different defaults can show different values for the same instant.

**A plausible wrong approach.** Relying on the machine's default timezone gives results that depend on where the job runs. Executors and the driver may also disagree, producing values that differ between stages of one job.

**How to verify.** Run the same query under two timezone settings and confirm the stored instant is equal while the rendered strings differ as expected.

## Exercise 5: Choose float tolerances

Tie tolerance to dtype algorithm and scale.

**Approach.** Choose float tolerances based on dtype, algorithm and magnitude, such as a relative tolerance near float64 epsilon times the number of summed terms for a parallel sum.

**Why it is correct here.** GPU aggregations may sum in a different order, which changes rounding. Tolerance should cover that difference without hiding real errors.

**A plausible wrong approach.** Using exact equality for float sums fails on correct results, while using a very loose tolerance passes wrong ones.

**How to verify.** Compare CPU and GPU sums for a fixed dataset and confirm the differences fall within the chosen tolerance.

## Exercise 6: Design ordered result comparison

Sort by stable keys without erasing duplicate rows.

**Approach.** Design an ordered comparison: sort both results by stable keys, including all columns needed to order duplicates, before comparing, and keep duplicate rows.

**Why it is correct here.** Spark does not guarantee output order without `ORDER BY`, and GPU execution may produce a different order.

**A plausible wrong approach.** Converting results to sets before comparing removes duplicates and hides a missing or extra row.

**How to verify.** Compare sorted lists and also compare row counts. When duplicates are expected, compare per-key counts too, so a duplicated row and a missing row cannot cancel each other out.

## Self-check answers

1. **How do COUNT(*) and COUNT(value) differ?** COUNT(*) counts rows, including those whose value is null; COUNT(value) counts only non-null values.

2. **Why can a binary float not stand in for a decimal test?** Values like 1.10 have no exact binary representation, so the float result cannot verify the decimal's precision and scale.

3. **Why name the timezone in a timestamp test?** The same stored instant can format or compare differently under different session time zones.

## Reference observation

Rows 3, non-null 2, sum 7 and exact decimal 3.30.

Asserted by `courses/cuda/spark/references/cuda-117_cpu.py`.

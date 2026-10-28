# apache-016: Logical and physical plans

Tutorial mode. Stage: intermediate. Direct prerequisites: `apache-015`.

## Read plans as explanations of work

A query describes a required result. The engine can often transform its plan
without changing that result. A logical plan expresses relational operations such
as scans, filters, projections and aggregates. An optimized logical plan applies
rules that preserve the intended semantics. A physical plan chooses concrete
execution operators and partitioning. Understanding these layers helps explain
why two equivalent expressions can perform different amounts of work.

Projection pushdown asks a source for fewer columns. Predicate pushdown moves
eligible filtering work closer to a source or into a source's supported scan
contract. Aggregate placement changes which rows reach a reduction. These ideas
are related but not interchangeable. A plan that contains a filter does not by
itself prove that a Parquet reader skipped a particular row group, and a scan
showing projected columns is not a full measurement of bytes transferred.

`EXPLAIN` lets the learner inspect the engine's current plan representation. It
is an observation tied to a version and query, not a stable serialization format
for an application parser. This example prints plan rows and checks semantic
results independently. It avoids asserting an exact multiline plan string whose
formatting could change without a correctness change.

## Worked case A: a selective filter before aggregation

The first query keeps only east-region events with positive amounts and sums
their amounts. The expected total is 11. The guide traces the logical order:
identify eligible rows, project the necessary values, then aggregate them. The
engine may combine or push these operations while preserving the answer.

The fixture includes a west amount of 1000. That deliberately large distractor
makes an incorrectly moved or dropped filter visible. A result of 1011 would be
numerically plausible but semantically wrong. A small balanced fixture with equal
regional totals would be a weaker test because some filter mistakes could remain
hidden behind coincidentally equal answers.

Inspect the plan text beside the result. Names such as filter, projection and
aggregate identify conceptual responsibilities, but the exact optimized operator
sequence can depend on source capabilities and engine settings. The learner
should explain what must be true of every valid plan: west rows cannot contribute
to this total, and each eligible east amount contributes once. That invariant
survives a physical-operator rename.

## Worked case B: filtering groups is a different calculation

The second case groups all events by region, sums each group's amounts, then
retains groups whose total exceeds 100. This is a `HAVING` condition. It is not
equivalent to filtering individual amounts above 100 before grouping, nor to
filtering region east before aggregation. The expected surviving group is west
with total 1000.

The two calculations can be written as
\[\sum_{i:r_i=\mathrm{east},\,a_i>0}a_i\]
and
\[\{(g,\sum_{i:r_i=g}a_i):\sum_{i:r_i=g}a_i>100\}.\]
The first produces one chosen population's aggregate. The second uses a condition
on aggregate results to select groups. Moving the second predicate to individual
rows can change the result whenever many small rows jointly cross the threshold.
The program includes an additional many-small-values case to make that failure
observable rather than relying only on one large west row.

An optimizer is allowed to rewrite a query only when the transformation preserves
its semantics under the engine's type and null rules. Thinking in invariants helps
read plans without assuming that every visual rearrangement is either dangerous
or beneficial. A plan is evidence of intended work; an independently checked
result is evidence of behavior for the supplied fixture.

## Mistakes and useful measurements

Do not optimize from one cold wall-clock measurement of a tiny dataset. Imports,
file caches, compilation and thread startup can dominate such timings. First
verify correctness, then choose a representative workload and record the actual
configuration and metrics. Keep elapsed time, rows scanned, rows returned and
memory use separate; none is a universal substitute for the others.

**Interview discussion: can every WHERE predicate move below every join or
aggregate?** No. Movement depends on the referenced columns and preservation of
null extension, grouping and other semantics. A filter on a right-side column
below a left join can differ from the same filter above it. A condition on an
aggregate generally cannot become the same condition on individual rows. The
next chapter uses explicit duplicate and missing keys to make those cardinality
and null boundaries concrete.

## Complete worked source

This is a complete editable worked program for the declared prepared runtime. It uses bounded local fixtures and does not install packages or start distributed services.

```python
import pyarrow as pa
from datafusion import SessionConfig, SessionContext

context = SessionContext(SessionConfig().with_target_partitions(2))
context.register_record_batches(
    "events", [pa.table({"region": ["east", "east", "west"], "amount": [4, 7, 1000]}).to_batches()]
)
query = "SELECT SUM(amount) AS total FROM events WHERE region = 'east' AND amount > 0"
assert context.sql(query).to_arrow_table()["total"].to_pylist() == [11]
plans = context.sql("EXPLAIN " + query).to_arrow_table().to_pylist()
assert plans and all(isinstance(row["plan"], str) and row["plan"] for row in plans)
for row in plans:
    print(row["plan_type"], row["plan"])
groups = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM events GROUP BY region HAVING SUM(amount) > 100"
    )
    .to_arrow_table()
    .to_pylist()
)
assert groups == [{"region": "west", "total": 1000}]
context.register_record_batches(
    "small_values", [pa.table({"region": ["east", "east"], "amount": [60, 60]}).to_batches()]
)
correct = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM small_values "
        "GROUP BY region HAVING SUM(amount) > 100"
    )
    .to_arrow_table()
    .to_pylist()
)
incorrect = (
    context.sql(
        "SELECT region, SUM(amount) AS total FROM small_values WHERE amount > 100 GROUP BY region"
    )
    .to_arrow_table()
    .to_pylist()
)
assert correct == [{"region": "east", "total": 120}] and incorrect == []
print("Group filtering:", correct, "incorrect row-level rewrite:", incorrect)
```

## Primary references

- [DataFusion EXPLAIN](https://datafusion.apache.org/user-guide/sql/explain.html)
- [DataFusion query engine architecture](https://datafusion.apache.org/library-user-guide/query-optimizer.html)

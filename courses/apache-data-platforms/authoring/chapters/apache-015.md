## An embedded query engine has a session boundary

DataFusion is a query engine that an application can embed. The Python binding
connects Python code to its native engine and Arrow data representation. A
`SessionContext` holds the tables, functions and settings visible to that session.
Registering a table makes a name available for planning; it does not turn the
process into a distributed cluster or publish that name to every other session.
A second context starts with its own registration state unless the application
explicitly shares an appropriate catalog or provider.

A SQL string and a DataFrame expression can describe the same relational
calculation. Both can produce a plan before an execution action materializes
results. This distinction matters because defining a DataFrame is not proof that
all source data were scanned successfully. Errors can arise during parsing,
planning, source access or execution. The particular stage depends on the API and
operation, so diagnostic reports should retain the actual exception and context.

The program registers a small Arrow table using record batches. The outer list
supplied to `register_record_batches` describes input partitions; each inner list
contains batches within one partition. This is local execution in one process.
Several partitions do not imply several machines, independently durable copies,
or a distributed scheduler. Ballista later adds those separate responsibilities.

## Worked case A: SQL and expressions answer one defined question

The first case has four events with region and amount. It asks for total amount
by region after excluding nonpositive values. SQL expresses this with `WHERE`,
`GROUP BY` and an explicit `ORDER BY`. The DataFrame version creates a filter
expression, aggregates by the region column, and sorts the resulting frame.
The two outputs must agree with an independent Python accumulation over the
original fixture.

The arithmetic is small enough to inspect: east contributes 4 and 7, while west
contributes 9 and a nonpositive value that the filter removes. The result is east 11
and west 9. Changing the filter changes the contributing population. Changing the
order of returned groups does not change the relation, but sorting is necessary
when an exact sequence comparison is part of the test contract.

The code uses explicit output aliases for aggregate columns. An API-generated
expression name can change after a refactor or a library update. A named result
such as `total` makes the downstream contract more intentional. That does not
make every detail stable: the fixture still checks the actual output schema and
values when the prepared engine version changes.

## Worked case B: a session name is not a global table

The second case creates another context and attempts to query the registered
name without registering the table there. The expected failure demonstrates the
session boundary. A beginner might interpret this as data loss because the same
Python process still holds the Arrow table. The bytes have not disappeared; the
new engine session lacks the name-to-provider registration needed to resolve the
query.

Registering the same source in the second context makes the query succeed. This
is an explicit dependency, which is useful in reproducible tests: each case can
construct the names and fixtures it requires rather than relying on previous
notebook cells. It also prevents a stale registration from quietly pointing a
query at an older dataset with the same familiar name.

A related distinction is result materialization. `collect()` returns Arrow record
batches, while `to_arrow_table()` combines the result into a table abstraction.
Converting either to a Python list is appropriate for this four-row inspection,
but it is an application allocation. An unbounded result should be consumed in
bounded batches or limited by a reviewed query contract. An efficient engine
does not make collecting arbitrary data harmless.

## Mistakes and diagnostic questions

When a name cannot be found, inspect session registration and identifier spelling
before changing the data file. When SQL and expressions disagree, check filter
placement, null semantics, grouping columns and aliases before measuring speed.
When a result has a surprising order, determine whether order was specified.
Do not treat the physical number of input batches as a business grouping rule.

**Interview discussion: why expose both SQL and a DataFrame API?** SQL is a
compact declarative language familiar to analysts and supported by many tools.
Expressions can integrate naturally with application composition and typed data
objects. Both describe relational work for the engine; neither inherently proves
that a query is distributed, faster or safer. The useful evidence is the admitted
plan, the actual input/output contract and the execution behavior under a stated
resource boundary.

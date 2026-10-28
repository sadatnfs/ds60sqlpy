# apache-061: Multistage queries and capacity

Tutorial mode. Stage: advanced. Direct prerequisites: `apache-060`, `apache-057`.

## A distributed analytical query still has a resource contract

Pinot's multistage engine supports distributed execution patterns beyond a
simple broker-to-segment aggregation, including supported joins. That additional
capability introduces exchange, intermediate-state and scheduling costs. An
interactive query can have a short desired latency while still requiring enough
memory and network capacity to execute its chosen plan.

A join requires compatible key semantics. Integer 1, string "1" and a null key
are not automatically the same business identity. Duplicate dimension keys can
multiply fact rows and inflate aggregates without producing a syntax error.
Validate cardinality expectations before interpreting a successful join as a
correct enrichment.

The project's default checker uses the ordinary query engine and does not claim
multistage acceptance. Its Python query helper contains a separately selected
multistage option for a prepared extension. The actual broker/server configuration,
ports, release support and matching join result must be qualified together before
calling that extension ready. Documentation examples can describe features newer
than the pinned server.

## Worked case A: enrich a bounded fact table

Create a separate owned dimension table with exactly one row for east and one
for west, mapping them to named territories. Join the three known orders to that
dimension using the supported multistage SQL path. The independent oracle still
contains three order IDs and total amount 20. Its region-to-territory mapping
comes from the input contract rather than from the query being verified.

Now add a deliberate duplicate east dimension key in a different experimental
table. A conventional equality join can produce two matches for each east fact,
changing row count and aggregate. That is a semantic data-quality failure when
the intended relationship is many-to-one. DISTINCT can conceal some symptoms
while changing other valid results; enforce the dimension uniqueness contract
at its publication boundary instead.

Inspect the explain output for actual exchanges and join operators. A small local
join establishes that selected syntax and connectors cooperate for that fixture.
It does not demonstrate cross-rack resilience, stable performance at high
cardinality, or arbitrary relational optimizer parity with another engine.

## Worked case B: a bounded request can fail explicitly

Set a finite query timeout and a small result limit. Query an unknown column or
unsupported operation and require a structured response exception. HTTP success
alone is not query success: a response can contain an exceptions array describing
a compilation or execution failure. The checker must inspect both transport and
query status before accepting any partial result.

A LIMIT bounds returned rows, but often does not bound the upstream work needed
to sort, aggregate or join them. An ORDER BY over a large group set can still
require substantial intermediate state. Pair result bounds with input predicates,
query deadlines, admission controls and measured engine work when the workload
requires strict resource protection.

Cancellation is also a separate behavior. A client timing out does not necessarily
prove the server immediately stopped all work. Correlate query identity, broker
and server observations before claiming resource release. Never retry an unknown
expensive query outcome indefinitely merely because the caller did not receive
its final response.

## Diagnosis and interview discussion

Record input cardinalities, expected join multiplicity, selected engine, explain
plan, query options, response exceptions and resource observations. Attribute
latency to the full path, including queueing and serialization, rather than only
the arithmetic operator. Keep measured local timings separate from capacity
forecasts for larger hardware or a different data distribution.

**Interview discussion: why can LIMIT 10 still be expensive?** The engine may need
to process many rows or groups before it knows which ten belong in the result.
The join case establishes cardinality correctness, while the bounded-request
case explains the difference between result size, computational work and explicit
failure handling.

## Complete worked source

This is a project-only command notebook. Read and edit it in the classroom; run its explicitly labeled commands from the copied owned Docker workshop. The classroom does not execute these service commands.

# Pinot apache-061 command notebook

Use these commands only from the copied owned Pinot project described in its README.
The classroom Markdown pad does not execute Docker commands.

```bash
cat client.py
bash run.sh check
```

The default checker inspects response exceptions and bounded results. A multistage join needs the supported engine configured and separately qualified, with unique-dimension and duplicate-dimension oracles.

Native service acceptance and each advanced extension have distinct entries in
`QUALIFICATION.md`. Source/configuration presence is not an observed service result.

## Primary references

- [Multistage query engine](https://github.com/pinot-contrib/pinot-docs/blob/latest/build-with-pinot/querying-and-sql/multi-stage-query/README.md)
- [Query options](https://github.com/pinot-contrib/pinot-docs/blob/latest/build-with-pinot/querying-and-sql/query-execution-controls/query-options.md)
- [SQL reference](https://github.com/pinot-contrib/pinot-docs/blob/latest/build-with-pinot/querying-and-sql/README.md)

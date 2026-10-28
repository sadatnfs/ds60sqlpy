## Indexes exchange preparation and storage for query work

A Pinot segment can contain several indexes serving different access patterns.
A dictionary maps values to compact identifiers; an inverted index maps a value
to matching document positions; a range index helps suitable interval predicates;
a sorted layout can exploit ordering. A forward index supports value retrieval.
These structures overlap in purpose, but one index name is not a universal
substitute for every other structure.

Index selection should start with query shapes and data distribution. Equality
on a moderately selective region can benefit from an inverted index, while a
range over an amount column needs a different comparison. An index that matches
almost every row may save little scanning and still consume memory, storage and
ingestion work. Tiny fixtures demonstrate API and result semantics without
providing reliable performance rankings.

The owned table configuration prepares an inverted index on region and a range
index on amount. Its actual result checker can establish selective-query
correctness. Comparing physical plans and performance with a deliberately rebuilt
alternative table is a separate prepared extension. Never infer a measured speedup
from the presence of an index field in configuration.

## Worked case A: equality filtering with and without an index

The fixture contains east orders 1 and 3, and west order 2. Query east and require
IDs 1 and 3 before comparing work. Build a second owned table from the same exact
source with the inverted index omitted. Use a different logical table name and
segment output directory so the comparison does not overwrite or ambiguously
reload the first table's state.

The two tables should return the same values. Read the released engine's explain
output and relevant scanned-document diagnostics to determine whether the intended
access path was selected. Response time from one tiny request is dominated by
startup, scheduling, caching and measurement noise. Repeated controlled workloads
and data distributions are needed before drawing latency conclusions.

Selectivity is approximately \(s=m/n\), matching rows divided by eligible rows.
Here east has \(s=2/3\), which is intentionally easy to reason about but hardly
a compelling production index benchmark. A million-row table with a rare value,
a low-cardinality field and a skewed popular value create different tradeoffs.
Keep each case's distribution with its result and plan evidence.

## Worked case B: a range predicate composes with equality

The bounded query asks for region east and amount at least five. The independent
oracle returns only ID 3 with amount 7. Pinot must combine predicate semantics
correctly regardless of whether it intersects indexed candidates or evaluates
one condition after another. Verify exact identities and null handling rather
than accepting a plausible aggregate alone.

An explain plan can expose the chosen operators, but plan text is versioned
output rather than a stable business API. Check the meaningful operator and
predicate relationship without hard-coding incidental formatting. If a new
release changes the plan, investigate whether the access path or merely its
presentation changed before updating a test.

A sorted index also implies a data-ordering contract during segment construction.
Declaring sorted behavior without actually arranging compatible data can be
invalid or ineffective. Similarly, disabling a forward index can limit query
capabilities when another operation still needs original values. Review the full
read/write workload instead of optimizing one isolated filter.

## Diagnosis and interview discussion

Retain schema, table config, segment metadata, source distribution, query,
explain output and measured resource work. Existing segments may need a supported
reload or rebuild before a changed index configuration takes effect. Editing the
controller JSON alone is therefore weaker evidence than inspecting actual
segments after the intended operation.

**Interview discussion: why might an added inverted index fail to improve latency?**
It may be unselective, absent from old segments, unused by the selected plan or
irrelevant to the bottleneck. The two cases first preserve result equality and
then inspect physical work, making performance a measured claim instead of a
property inferred from configuration syntax.

## A partition specification is metadata, not a directory convention

Iceberg records how a source field maps to partition values. An identity transform
uses the field's value directly; date transforms, bucketing and truncation provide
other layouts when the prepared writer supports them. Query authors filter the
logical source column, and the planner derives useful partition predicates. This
is hidden partitioning: consumers do not need to repeat a directory field in every
query merely to make pruning work.

Partition evolution allows old files and new files to use different specifications.
Each file records its specification identity. Changing the current spec does not
repartition historical data automatically. A planner must interpret every candidate
file under the spec that actually produced it, and still evaluate any remaining
row-level predicate. Dropping that residual predicate can return incorrect rows
from an old unpartitioned file.

The prepared core deliberately uses identity transforms because they require no
additional native transform package. Some PyIceberg bucket transforms need a
separately prepared native extension. The lesson does not install dependencies
inside a pad or advertise every transform as executable merely because its class
can be imported. The same distinction matters when moving a table between engines.

## Worked case A: introduce region partitioning

The first append occurs while the table is unpartitioned. The program then adds
an identity partition on region and appends one east order and one west order.
The current snapshot now references files from two specifications. Filtering for
east must include the two original east rows and the newly appended east row,
while excluding both west rows.

The program inspects the spec IDs of planned files and checks the exact resulting
order IDs. The unpartitioned historical file remains a candidate because its
partition metadata cannot rule out east records. Row-level filtering then removes
its west record. The new west partition can be pruned by the region predicate.
A planned-file observation and a result oracle therefore establish different
parts of the mechanism.

Even for a three-row historical file, the distinction is structural. Large-table
cost depends on file sizes, statistics, delete files and actual scan behavior.
Counting planned files does not directly measure disk bytes or network requests.
The example reports those counts without converting them into invented benchmark
improvements.

## Worked case B: evolve to a different layout

The second evolution removes the region partition field and adds an identity
partition on order ID. A further append uses the third specification. The same
logical east predicate still returns the correct four order identities across
unpartitioned, region-partitioned and ID-partitioned data. The program checks that
three specs remain represented in metadata and that the result is unchanged by
an irrelevant physical-layout difference.

Identity partitioning on a nearly unique order ID would be a poor production
choice because it can create many small partitions and files. It is selected here
only to make the changed metadata obvious with a tiny fixture. A real design
would choose a transform using query predicates, data volume, skew and maintenance
cost, and would prepare the necessary writer capabilities separately.

Partition evolution can reduce future write or scan cost, but old files may
continue to dominate until an explicit rewrite is performed. Rewriting has its
own compute, commit and retention implications. It must preserve the logical
record set and account for concurrent writers. A metadata update alone is not a
completed compaction or repartitioning job.

## Diagnosis and interview discussion

Inspect current and historical specs, each file's spec ID, the query predicate
and residual filters. Do not derive logical data directly from directory names
or assume one globally current transform can decode every file. Diagnose small
files separately from key skew: both can hurt performance, but they require
different interventions.

**Interview discussion: why is partition evolution harder than changing a folder
name?** Readers must plan across files written under different transforms while
preserving the same logical schema and query semantics. These cases exercise
that real compatibility boundary and show why pruning is an optimization while
row-level correctness remains mandatory.

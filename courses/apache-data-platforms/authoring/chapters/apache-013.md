## The mechanism

A Parquet dataset can span several files and directories. A dataset scanner
combines a logical schema with file fragments and a requested computation.
Projection names the columns needed in the result. A filter restricts rows.
Partition expressions, file statistics and row-group statistics may permit the
scanner to exclude work, but an exclusion decision must remain compatible with
the query's semantics. A row that could satisfy the filter cannot be discarded
merely because its file's name looks inconvenient.

A Hive-style directory such as `region=east` supplies a partition value through
its path. The physical Parquet file need not repeat that value in every row.
The dataset reader reconstructs the logical column using a declared partition
schema. This is a layout convention, not proof that Apache Hive wrote the files
or that a Hive Metastore contains a table registration for them.

The program creates a bounded synthetic dataset in a temporary directory. It
never downloads a public dataset and removes its own files after the checks.
That keeps the causal question clear: how do projection, partition pruning and
residual filtering affect one known set of records? File-level observations are
reported separately from row-level answers.

## Worked case A: eliminate an impossible partition

The first case writes four records into east and west partition directories.
It opens a dataset with an explicit string partition field and requests only
`id` and `amount` for east. The expected answer is the two east records. The
program also asks the dataset which fragments can match the partition predicate.
There are two fragments in the full dataset and one candidate for east.

That reduction follows from a logical implication: a fragment known to satisfy
`region=west` cannot contain a row satisfying `region=east`. The partition
expression is enough to exclude it. If a dataset has missing or inconsistent
partition metadata, the scanner must be conservative instead of manufacturing
certainty from an incomplete directory listing.

Projection and filtering play different roles. The returned table omits `region`
because the result requests only two columns, yet the scanner still needs the
partition value to evaluate the filter. Seeing no region column in the result
does not mean the filter was ignored. The assertions verify both result schema
and row identity so this distinction is observable.

## Worked case B: retain a fragment but reject some of its rows

The second case adds `amount > 10` to the east predicate. The east fragment
remains a candidate because one of its rows may match. Only the row with amount 17
survives the complete row predicate; the east row with amount 4 does not. The
candidate-fragment count is still one, while the output-row count changes from
two to one. Pruning and residual evaluation therefore answer different questions.

The fixture deliberately contains two distinct amounts inside one partition.
If every partition contained a single uniform value, a mistaken implementation
that returned whole candidate files could look correct. The independent oracle
filters the original Python records and compares exact IDs and amounts with the
Arrow result. It does not simply repeat a scanner call and compare it with itself.

For a simple scan, a rough data-work model is
\[W\approx\sum_{f\in F_{candidate}}\sum_{c\in C_{needed}}B_{fc}+W_{decode}+W_{predicate}.\]
This is a reasoning model, not a timing equation: compression, page reads,
metadata caches, thread scheduling and filesystem behavior affect real cost.
The lesson records candidates and answers, then leaves performance measurement
to a separately controlled workload rather than inferring speed from four rows.

## Mistakes and diagnosis

Do not confuse a partition folder with an atomic table transaction. A reader
listing files while a writer modifies them can observe an inconsistent collection
unless a higher-level table protocol coordinates visibility. Do not conclude
that a filter was fully pushed down merely because a logical plan contains it.
Inspect the appropriate metadata and retain a correctness check for residual
rows. Do not infer a stable row order without an explicit sort; dataset scans
may return fragments in an implementation-dependent order.

## Interview discussion

**Does partition pruning replace filtering?** It excludes fragments whose known
partition conditions contradict the query. Remaining fragments still require
correct evaluation of any unresolved predicate, possibly helped by statistics
or page indexes. Iceberg later adds committed table snapshots and field-aware
metadata to this picture. Parquet files plus a directory convention alone do not
supply those transaction and evolution guarantees.

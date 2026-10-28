## A timestamp is incomplete without a clock and a meaning

Event time is when a source says an event happened. Ingestion time is when a
pipeline accepted it. Processing time is when one computation handled it.
These clocks answer different questions. A purchase made before midnight may
arrive after midnight and be processed hours later. Grouping it by the worker's
current date changes the analytical population whenever the job is rerun.

Use timezone-aware timestamps and document the business calendar separately from
storage conventions. UTC is convenient for interchange but does not turn a local
business day into a universal 24-hour interval. Daylight-saving transitions can
change interval length. This fixture stays entirely in UTC and uses half-open
intervals \([a,b)\), which include the start and exclude the end. Adjacent
windows then meet without counting their shared boundary twice.

Reproducibility also needs source identity. A file can be overwritten at the
same path, a catalog can advance to a new snapshot, and a correction can arrive
for an existing record. A report should record its selected version or as-of
rule as well as its SQL. Otherwise two people can execute identical code and
obtain different correct answers from different source states.

## Worked case A: a late order crosses the report cutoff

The first report counts event-time purchases for one UTC day using only revisions
ingested before a fixed cutoff. One purchase arrives promptly and another arrives
the next day. The report initially shows only the prompt amount. Moving the
cutoff later admits the delayed purchase without changing its event date. The
program checks both totals from explicit identities rather than from the current
system clock.

This is an as-of view over an append-only revision log. It is not a promise that
the source was complete at the cutoff. Completeness is a data contract, possibly
expressed through a source watermark, reconciliation or a business close policy.
A report can be reproducible and still be incomplete. That distinction matters
when comparing experimentation metrics, revenue recognition or model features.

The code parses ISO timestamps with explicit UTC offsets and never calls now.
Changing the date when the example runs therefore cannot change which rows it
selects. The source revision set is sorted by a declared sequence number within
each operation. In a real system, ordering conflicting revisions requires an
upstream version contract rather than trusting arrival order or wall clocks.

## Worked case B: a correction changes history deliberately

A later revision corrects the prompt purchase from amount 4 to amount 6. The
latest as-of view now totals 15 rather than 13, while the earlier report remains
reconstructible at its original cutoff. The correction is not an additional
purchase, so summing every revision would be wrong. The program chooses the
highest admitted revision for each order before calculating the daily total.

Two distinct operations can have the same timestamp. Sorting only by timestamp
would leave a tie ambiguous. The fixture uses an explicit integer revision and
rejects repeated operation/revision identities with differing payloads. A useful
production schema also distinguishes event deletion, cancellation and correction;
these are not interchangeable forms of a negative amount.

A bitemporal system generalizes the distinction between when information applies
and when the system knew it. The example contains the essential two dimensions,
event time and ingestion time, without claiming a complete bitemporal database.
Backfills must state which dimension they revise and whether downstream tables
are recomputed or versioned alongside the corrected source.

## Diagnosis and interview discussion

Keep original timestamps, timezone rules, source versions and processing run
identity. Investigate late-arrival distributions instead of silently discarding
late data. A Flink watermark helps decide when to emit a result, while an Iceberg
snapshot identifies table state; neither automatically specifies the other.
Link these mechanisms through an explicit correction and retention policy.

**Interview discussion: how can a historical metric change even though the query
has not changed?** New delayed records, corrected facts, overwritten dimensions
or a different as-of selection can all change its input. Reproduce the original
source version and cutoff first, then compare identified revisions. The two
worked cases separate arrival delay from a business correction and preserve a
clear explanation for each changed total.

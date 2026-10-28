## Event time is carried by the data

Processing time is the worker's clock. Event time is the timestamp assigned to an
observation by its source contract. They answer different questions. A purchase
can be processed late because of a network delay without changing when the purchase
occurred. Windows must state which clock defines their boundaries, which timestamp
unit is used and how events outside a completeness policy are handled.

A watermark is an estimate that event-time progress has passed a position. It is
not proof that no older event can arrive. A strategy such as maximum observed
timestamp minus a delay chooses a practical completeness/latency tradeoff. With
several input partitions, an idle partition can hold back combined progress unless
idleness is handled explicitly. Advancing a watermark too aggressively can make
legitimate delayed records late.

The workshop uses an actual bounded Flink source with explicitly controlled record
timestamps and watermark commands. It does not wait for wall-clock chance to create
a late event. Milliseconds are the declared unit, and two-second tumbling windows
use half-open intervals \([0,2000)\) and \([2000,4000)\). This makes every result
and rejection independently traceable.

## Worked case A: out-of-order records before progress advances

The timeline emits east records at 1000 and 1500 milliseconds, then a west record at 500.
Although the third record is older than the previous two, no watermark has yet
closed its window. All three belong to the first two-second window. The source
then advances its watermark to 2000. The actual window operator emits east total 11
from two records and west total 9 from one record.

The checker compares window start, end, key, count and amount, not only the grand
total. An implementation using processing time might accidentally produce a
plausible overall sum while assigning it to the wrong window. Keeping exact
boundaries in the oracle makes that mistake visible even on a tiny fixture.

Flink's window trigger uses its defined maximum timestamp convention at the window
end boundary. The source's chosen watermark passes that threshold deliberately.
This is a deterministic mechanism experiment, not a benchmark or a statement that
two seconds is an appropriate production delay policy for every dataset.

The fixed trace makes the accepted/late boundary explicit:

| Source action | Event time in ms | Amount | Observation |
| --- | ---: | ---: | --- |
| east order 1 | 1000 | 4 | first window, accepted |
| east order 3 | 1500 | 7 | first window, accepted |
| west order 2 | 500 | 9 | out of order, still accepted |
| watermark | 2000 | none | first window closes |
| east order 4 | 1000 | 5 | arrives after closure, late output |
| east order 5 | 2500 | 3 | second window, accepted |
| watermark | 4000 | none | second window closes |

## Worked case B: an event arrives after its window closed

After the watermark reaches 2000, the source emits another east record timestamped
1000 with amount 5. Its event time still belongs to the first window, but the
configured zero allowed-lateness policy has already closed that window. The job
routes the event to the explicitly named late side output. It must not silently
add the amount to an unrelated current window or discard it without an observation.

A later east record at 2500 with amount 3 belongs to the second window. Advancing
the watermark to 4000 closes that window with total 3. The checker expects three
normal window results and one identified late record. These are separate outputs
with different meanings, rather than a single sum that could conceal misplaced data.

Allowed lateness can permit updates to a window for some time after its first
result. Downstream systems must then understand correction or changelog semantics.
A side output can support a reconciliation workflow, but routing alone does not
reprocess the record or establish a business close policy. State the intended
correction path before selecting a lateness duration.

## Diagnosis and interview discussion

Record source timestamps, watermark progress, window boundaries, lateness policy
and output identities. Inspect partition-level progress and idleness when a
window appears stuck. A quiet input may be delaying progress without any record
being invalid. A final maximum watermark from a bounded source is different from
an unbounded production source promising completeness forever.

**Interview discussion: can an out-of-order event still be on time?** Yes. It can
arrive before the relevant watermark/lateness boundary closes its window. The two
cases use real Flink window processing to distinguish an older record accepted
before progress from a later arrival routed after closure, with exact interval
and identity checks.

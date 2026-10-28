## A consumer position and a committed offset are different state

A consumer advances its current position while fetching records. Its committed
offset records where a later consumer instance in that group should resume.
Committing offset n conventionally means the next record to read is n, not that
record n has just been processed. Every topic partition has its own offset space,
so one integer cannot describe progress through a multi-partition topic.

The order of effect and commit determines failure behavior. Processing a record
then committing can replay the effect if the process crashes between them.
Committing first can skip an effect if the process crashes afterward. At-least-once
processing therefore normally commits after a successful effect and makes that
effect idempotent or transactional within its intended boundary.

The real Java probe disables automatic commits, manually assigns the two known
fixture partitions and uses explicit bounded reads. This isolates offset behavior
without a timing-dependent membership experiment. Automatic subscription and
rebalancing are explained here as an additional mechanism, with no claim that
manual assignment exercises the coordinator's assignment transitions.

## Worked case A: close before committing and observe replay

Group A reads all three fixture records and closes without committing. A new
consumer with the same group ID reads them again. The oracle compares exact
key/value lists, rather than merely finding at least one row. The log retained
the records and the group had no committed progress that advanced past them.

This resembles a process interruption before its commit, but the probe uses an
orderly close with auto-commit disabled to make the boundary deterministic. It
does not claim an injected kernel crash or a filesystem durability test. A real
application can use this semantic observation to predict which side effects need
deduplication when a less orderly interruption happens.

The fixture's topic retention is long enough for the replay. A lagging consumer
cannot assume every historical offset remains readable forever. If retention or
compaction removed required records, an offset-reset policy could change behavior.
A recovery runbook must distinguish available replay from a source gap.

## Worked case B: commit next positions and reopen

A third read in group A commits the final next position for each partition. A
new consumer in that group now returns zero fixture records. An independent group
B still receives all three, proving that the commit changed group progress rather
than destructively consuming the source. The probe then removes only its uniquely
created temporary group metadata.

In a subscription-based group, a rebalance can move partition ownership to another
member. A handler must stop applying effects for revoked partitions, complete or
abort in-flight work according to its design, and commit only offsets that
correspond to completed work. Cooperative protocols and newer group coordination
change details, but do not remove the need to track per-partition completion.

Parallel record handling makes the boundary subtler. If offsets 5 and 7 finish
while 6 is still running, committing 8 can skip unfinished work after a crash.
Track the contiguous completed prefix for each partition rather than the largest
observed completion. The tiny probe processes synchronously; it does not pretend
to test every concurrent worker scheduling condition.

## Diagnosis and interview discussion

Inspect assigned partitions, current positions, committed offsets, source end
offsets and retention bounds. Lag is an offset-distance signal with workload and
record-size caveats; it is not automatically a wall-clock delay in seconds.
Distinguish a stuck application from an idle partition and compare logs with
actual progress rather than resetting offsets as the first response.

**Interview discussion: when should a consumer commit?** After the intended effect
has succeeded under a defined idempotency or transaction contract, and only through
the contiguous completed positions. These two actual reads show replay before
commit and no replay after commit, while the text identifies the additional
membership and concurrency behavior that this bounded manual-assignment probe
has not qualified.

## A data signal does not transport the dataset

An Airflow asset identifies a logical data product through an explicit URI.
A successful producer task can emit an update event, and a consumer DAG can use
that event as a scheduling condition. The event is orchestration metadata. It
does not copy the data, verify its entire quality contract or guarantee that a
consumer's credentials can read the underlying storage.

The workshop uses an explicitly synthetic asset URI for the owned daily-order
output. The producer publishes the signal only after its atomic partition write
succeeds. The consumer reads the actual retained files and records their source
identities in its own bounded summaries. This connects the scheduling event to
independent data readback without pretending the event itself contains the table.

Dynamic task mapping creates task instances from a runtime collection. It is
different from executing a Python loop at DAG parse time. Mapping can make a
workflow flexible, but an unbounded list can create excessive task metadata and
load. The fixture maps only two declared regions and uses a one-slot pool to
make its capacity policy explicit.

## Worked case A: a successful producer schedules a consumer

Unpause the asset consumer before running the finite producer DAG. After a producer
write emits an update, the actual scheduler creates consumer work. The asset-check
action inspects real consumer Dag Runs and their completed outputs. A source-file
change made outside the producer task would not automatically create the same
asset event in this fixture.

The consumer first captures one bounded immutable source manifest and passes its
reference to both mapped tasks. A retry reuses that run manifest rather than
recapturing newer data. Each region therefore uses the same source population,
even if a correction arrives between its task and the next mapped task. The
consumer records which available partition versions it observed.
Two producer days can emit updates at different times, so an early consumer may
see one day while a later consumer sees both. The receipt must identify that
population rather than compare every run blindly with a final all-days total.
Scheduling conditions and snapshot completeness are separate contracts.

A failed producer should not announce a successful update merely because some
partial file exists. The atomic writer and task success boundary reduce that
ambiguity in the local fixture. An external database or table system needs its
own commit mechanism and a producer rule that emits the signal only after the
intended state becomes visible.

## Worked case B: two mapped tasks share one pool slot

The consumer maps one summary task to east and one to west. Both mapped task
instances have the same logical task definition with different map indexes.
The one-slot pool limits their concurrent occupancy even though the executor
could have additional capacity. The checker inspects mapped task-instance states,
indexes and the pool's configured slot count, then reconciles their output values.

A pool is a resource-accounting control, not a CPU scheduler or a general rate
limiter for every external API. A task can occupy several slots if configured,
and deferrable behavior can affect accounting under a chosen policy. For a real
service, choose the pool based on the constrained dependency and measure its
load rather than naming a pool after a programming language.

XCom carries only small references or bounded summaries here. Passing a large
DataFrame through orchestration metadata would increase serialization and database
pressure and obscure where the authoritative data lives. The producer's storage
identity and the consumer's observed version remain in ordinary owned data files,
while Airflow tracks their task relationship.

## Mistakes, diagnosis and interview discussion

Check asset identity spelling, producer success, event creation, consumer schedule,
pool availability and task state separately. An event existing in metadata does
not prove a consumer is unpaused or has enough capacity. A mapped task waiting
for a pool slot is not the same failure as a task that started and rejected its
input.

**Interview discussion: why combine assets, mapping and pools?** Assets express
when a data-dependent workflow becomes eligible, mapping expresses bounded runtime
fanout, and pools constrain concurrent pressure on a dependency. These cases use
all three in the real scheduler while independently validating the files and
source versions that the tasks actually observed.

The [complete Airflow workshop](../../projects/airflow/README.md) provides the maintained files, preparation, lifecycle and exact qualification boundaries for these cases.

# Apache data platforms study guide

Every guide in this track ends with a complete worked source. Some of those
sources are Python programs that the classroom runs; the rest are Markdown
command notebooks for a separate Docker workshop. This page states the shared
rules for both once, so each guide can spend its words on its own mechanism.

## Worked programs

Units 001 to 003, 005 to 013, 015 to 020 and 039 to 044 end with a Python
program. Open the unit in `/classroom` and run it with the prepared
`data-platforms-python` profile, which already contains Arrow, DataFusion and
PyIceberg at the versions the [track README](README.md) lists.

- Each program builds its own small fixtures, in memory or in a temporary
  directory that is removed when the run ends.
- No program installs packages, downloads data or starts a distributed service.
  Where a guide discusses cluster behavior, the program models it with local
  data.
- The program you see in the guide is the same file as `examples/apache-0NN.py`.
  Edit a copy, rerun it and compare the printed values with the program's own
  assertions.

## Workshop notebooks

Units 004, 014, 021 to 038 and 045 to 088 end with a Markdown notebook.
The classroom shows those commands in an editable pad but never executes them,
and no worker has access to a container engine.

1. Copy the named project from `courses/apache-data-platforms/projects/` into a
   fresh directory under `work/`, as most notebooks' first commands do. Run
   actions from that copy, never from the maintained source tree.
2. Read the project's `README.md`, then `PREPARATION.md` and `QUALIFICATION.md`
   where they exist. They say which images are built locally, which features
   ran natively and which remain prepared only.
3. Run only the documented `run.sh` actions, in the documented order, and stop
   the project with its own `stop` or `down` action when you finish, if it
   has one.
4. Keep credentials, `Authorization` headers, recipient profiles and signed URL
   query strings out of the copied source, the pad and any saved evidence.

The [qualification ledger](authoring/ENVIRONMENTS.md) records which routes ran
on native ARM64 or AMD64 hosts. A route that ran on one architecture has not run
on the other.

## Evidence receipts

A workshop or capstone claim is only as good as the receipt you keep. A useful
receipt records:

- the source revision, file hashes and the exact input rows, schema and time
  units;
- the host platform, image identities and the owned namespace or directory;
- the table snapshot, source offsets, run identity or lineage identity that the
  result depends on;
- one positive result checked against an independent oracle and one negative
  case that was rejected for the expected reason;
- a read-only comparison of retained state after a stop, restart or restore;
- the cleanup result and where the evidence file is stored.

Name evidence files after the unit and action, for example
`apache-082-check.json`, and keep them outside the copied project so a
`destroy` action cannot remove them.

## The order fixture oracle

Many units share one small order fixture so results can be checked by hand.

| Order | Region | Amount |
| --- | --- | --- |
| 1 | east | 4 |
| 2 | west | 9 |
| 3 | east | 7 |

The total is 20, east is 11 and west is 9. When a later unit appends a fourth
west order of 2, the current total becomes 22 and west becomes 11, while a
snapshot or offset pinned before the append must still return 20. This oracle
only checks a pipeline whose deduplication, correction and visibility rules
you have written down; it does not prove a different pipeline correct.

## Prepared versus observed

Keep four kinds of statement apart when you write up a unit:

- **Present**: a file or configuration exists in the project.
- **Prepared**: an image or dependency was built and verified, but no service
  ran.
- **Compiled or unit tested**: code built and its local fixtures passed.
- **Observed**: the service ran and returned the receipt described above.

Only the last kind supports a claim that a feature works. A component that ran
alone does not establish a combined topology, such as Kafka feeding Flink and
Pinot, that was never started together.

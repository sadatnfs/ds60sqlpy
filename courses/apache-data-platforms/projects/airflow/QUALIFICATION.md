# Airflow qualification ledger

## Prepared environment

Airflow 3.3.2 has published Linux AMD64/ARM64 upstream image descriptors. Its
minimal Python 3.12 dependency set resolved to 127 hash-locked packages on both
native Linux architectures. The explicit existing-Core fallback was built and
executed on native Linux ARM64 in a separate virtual environment, without changing
the ordinary Core environment. The upstream-image route remains descriptor-only
on this authoring machine.

## Actual native Linux ARM64 acceptance

On 2026-10-27 the corrected source passed:

- Actual standalone scheduler, DAG processor, API server and triggerer health,
  inspecting component fields rather than accepting HTTP 200 alone.
- Two real scheduled full-day UTC intervals: January 1 through 2 and January 2
  through 3, with exact source-bound output and actual logical/run-after fields.
- Intentional first task failure and actual successful second attempts in metadata.
- Asset-triggered consumer runs, coherent immutable per-run source manifests,
  two mapped region tasks and the configured one-slot pool. Saved summaries were
  independently reconciled against their observed source versions.
- An explicit one-day correction from amount 4 to 6, first-day total 15, with the
  second day's bytes unchanged; old source observations remained interpretable.
- Real SDK resolution of the known local connection and rejection of an absent
  identifier, without recording credential values or claiming an external service.
- Native Chromium login and the directory displaying all four known DAGs, with
  external requests blocked. Login/directory also worked after replacement.
- Exact retained container on stop/resume, deliberate pool-slot edit retained,
  explicit restoration of the documented one-slot policy, replacement container
  after down/start and unchanged known run/task identities and saved data bytes.
  Readback did not rerun completed work.
- Confirmed cleanup of only the owned synthetic containers, network and volume
  after acceptance evidence was retained outside maintained sources.

## Important discovered contract

Initial daily shorthand produced zero-duration trigger intervals under this
release/configuration. The first run metadata was retained and explicitly rejected
by the strengthened interval oracle; history was not rewritten. The source now
selects CronDataIntervalTimetable explicitly and rejects zero, partial and multi-day
windows. Corrected qualification used fresh disposable state for the changed
schedule contract. A regression covers the original zero-duration case.

The first qualified logical date is January 1 and its full-day interval ends
January 2, while its generated run ID contains January 2. Run-ID text is not a safe
way to infer the source population. The UI can display a different timezone from
the UTC metadata used by the fixture.

Local runtime acceptance is ARM64 only; native AMD64 execution belongs to GitHub
runners. This standalone SQLite/SimpleAuth development topology does not establish
PostgreSQL metadata, multi-host workers, high availability or external provider
connections. Source, unit/policy tests, actual scheduler execution, browser delivery
and retained-state checks remain separate evidence categories.

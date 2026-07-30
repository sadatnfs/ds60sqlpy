# Day 58 — Final Capstone, Part 1: Ingestion and Data Quality

## Level and prerequisites

- **Level:** Advanced
- **Prerequisites:** [Day 57 — trends and anomalies](day57_project4_bi_part3.md)
- **Artifacts:** [learner SQL](../day58_final_capstone_part1.sql) ·
  [solution reasoning](../solutions/day58_solutions.md) ·
  [executable solution](../solutions/day58_solutions.sql)

## Learning objectives

- Preserve raw staged input while deriving validated, normalized fields.
- Package a repeatable stage/validate/upsert flow with observable counts.

## Vocabulary and concepts

- **Raw staging:** an input-preserving landing area before typed transformation.
- **Rejection reason:** a stable explanation for why a record was not accepted.
- **Upsert count:** affected rows under the interface's defined insert/update
  semantics.

## Worked example / walkthrough

For each timestamp format, test a format-specific regular expression before
casting. Keep raw text and parsed value together, collect explicit rejection
reasons, and upsert only accepted rows inside the rollback-only transaction.
Return staged, valid, invalid, and affected counts that reconcile.

## Exercises

Complete these in the [learner SQL](../day58_final_capstone_part1.sql):

1. Parse additional datetime formats safely.
2. Normalize/validate staged phone values.
3. Build a transactional ingest procedure with DQ counts.
4. Make source-duplicate winner selection deterministic.
5. Split accepted/rejected rows with reason codes and reconcile counts.
6. Normalize email before deduplication.
7. Distinguish missing from unrecognized countries and retain raw values.
8. Add source batch/row identity and make replay idempotent.
9. Quarantine malformed JSON without aborting the batch.
10. Reconcile staged, accepted, rejected, inserted, and updated outcomes.

Malformed inputs must become explained rejections.

## Self-check

- Can every normalized value be traced to preserved raw input?
- Do count summaries reconcile, and are schema additions kept out of an
  unreviewed tutorial upsert?

## Next step

Continue to [Day 59 — stakeholder analytics](day59_final_capstone_part2.md).

## Deep dive and reference

## Capstone focus

- Stage messy customer text without losing the raw input.
- Normalize names, email, country, segment, timestamps, JSON, and phone.
- Validate records, upsert accepted customers, and return a DQ summary.

## How the learner script works

The rollback-only starter creates `stg_customers_raw`, inserts three varied
records, parses three timestamp patterns, validates email/country, upserts valid
rows by unique email, reports invalid counts, and demonstrates a country map.

## Practice — match the learner prompts exactly

1. Extend the guarded timestamp parser for additional explicit formats.
2. Add a staged phone value, strip non-digits with regex, and return a
   `phone_valid` flag under a clearly stated numbering policy.
3. Create a PostgreSQL stored procedure that truncates/rebuilds a cleaned stage,
   validates it, upserts accepted customers, and returns upserted/invalid counts
   through `INOUT` parameters.

## Pipeline reasoning

- Guard every timestamp cast with a format-specific regex; ambiguous dates need
  an explicit locale policy.
- Preserve rejection reasons and raw text in a real pipeline.
- Normalize before comparing unique email values.
- `ON CONFLICT (email)` counts affected inserts/updates but does not distinguish
  them without additional logic.
- Invalid JSON falling back to `{}` is a course choice; production should retain
  the error.

## Schema and safety limits

`training.customers` has no phone column. Validate phone in staging, but do not
invent a destination. Persisting phone requires a reviewed schema migration.
The sample phone regex is intentionally narrow and is not global normalization.

Keep the entire demonstration in a transaction and roll it back. A procedure is
appropriate for side effects and can expose `INOUT` counts; a table-returning
function would be a different interface.

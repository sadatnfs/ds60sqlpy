# SQL-FOUND-01 — Relational Design, DDL, and Integrity Constraints

## Level and prerequisites

- **Level:** Foundation
- **Catalog prerequisites:** none
- **Prerequisites:** PostgreSQL setup and comfort running a `.sql` file with
  `psql`; no earlier SQL lesson is required.
- **Artifacts:** [learner SQL](../lessons/sql_found_01_relational_design.sql) ·
  [solution reasoning](../solutions/sql_found_01_relational_design_solutions.md) ·
  [executable solution](../solutions/sql_found_01_relational_design_solutions.sql)

Run this portable command from the repository root in Windows PowerShell,
macOS, or Linux:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/lessons/sql_found_01_relational_design.sql
```

The file creates `pro_relational_lab` inside a transaction and rolls it back.
Expected constraint failures are caught as notices; any unexpected error still
stops the script.

## Learning objectives

- State a table's grain, map one-to-one and one-to-many requirements to keys,
  and create a normalized schema.
- Choose database constraints for durable invariants and explain one deliberate
  denormalization.
- Predict and observe safe `NOT NULL`, `CHECK`, `UNIQUE`, primary-key, and
  foreign-key failures.

## Vocabulary and concepts

- **Grain:** exactly what one row represents. State it before naming columns.
- **Cardinality:** how many rows on one side may relate to rows on another side,
  such as one category to many physical items.
- **Natural key:** a meaningful value from the domain, such as an asset tag.
- **Surrogate key:** a generated identifier with no domain meaning.
- **Primary key:** the chosen unique, non-null identity for a row.
- **Foreign key:** a reference whose value must identify an allowed parent row.
- **Invariant:** a rule that must remain true for every valid database state.
- **Identity column:** a PostgreSQL-managed sequence value declared with
  `GENERATED ... AS IDENTITY`.
- **Generated column:** a stored value calculated from other columns in the same
  row; its expression must be immutable.
- **Normalization:** separating facts so each is stored at the appropriate
  grain and accidental update contradictions are reduced.
- **Deliberate denormalization:** intentionally copying or deriving a value for
  a stated historical, performance, or availability reason, with an explicit
  consistency rule.

## Worked example / walkthrough

The example begins with four requirements and turns each into a grain:

1. A member is one person who may borrow equipment.
2. A category is one reusable classification.
3. An equipment item is one physical asset and belongs to one category.
4. A loan is one checkout of one item to one member.

`members.member_id`, `equipment_items.item_id`, and `loans.loan_id` are identity
primary keys. Meaningful identifiers such as `email` and `asset_tag` also receive
`UNIQUE` constraints. The item and member identifiers in `loans` are foreign
keys, so an application bug cannot create an orphan checkout.

Constraints express the smallest durable rule:

- `NOT NULL` says absence is invalid.
- `CHECK` limits values or relationships within a row.
- `UNIQUE` prevents duplicate keys.
- `PRIMARY KEY` supplies row identity.
- `FOREIGN KEY` protects a relationship between tables.
- `DEFAULT` supplies a value only when the insert omits that column.

An ordinary PostgreSQL `UNIQUE` constraint allows multiple NULL values. NULL
means “unknown,” and unknown is not equal to unknown. PostgreSQL 15 and newer
also support `UNIQUE NULLS NOT DISTINCT` when the requirement says that at most
one unknown value is allowed.

The loan stores `daily_fee_at_checkout` even though the current item has
`daily_fee`. That is deliberate denormalization: the snapshot answers “what fee
was quoted then?” after the catalog fee changes. By contrast, copying the
category display name into every item would create a needless update anomaly.

The learner script catches expected exceptions inside small anonymous blocks.
The wrapper is only test scaffolding: the important event is PostgreSQL
rejecting the invalid statement while the outer transaction remains usable.

## Exercises

Complete all eight prompts at the bottom of the learner SQL. Begin by designing
`maintenance_visits` from prose, load a valid row, prove an invalid cost is
rejected, investigate NULL uniqueness, and justify whether the checkout fee
snapshot is deliberate denormalization; then continue through normalization,
outer joins, deletion policy, and catalog contracts. Keep your DDL inside the
existing transaction so a rerun begins cleanly.

Before typing, write the proposed grain and cardinality in comments. For every
constraint, complete the sentence: “This belongs in the database because
without it, ___ could become false regardless of which application wrote the
row.”

Work through these in order; each item names the evidence to leave in your
scratch SQL:

1. **Maintenance DDL:** translate every visit requirement into a column,
   constraint, key, default, or generated expression; annotate the table grain.
2. **Negative cost:** insert one valid visit, isolate the rejected insert in a
   nested block, and verify the expected SQLSTATE category.
3. **NULL uniqueness:** insert two NULL references, explain the observed rule,
   and write—but do not blindly apply—the stricter PostgreSQL 15+ alternative.
4. **Historical fee:** state the invariant, the historical question, and why the
   checkout snapshot is or is not deliberate denormalization.
5. **Many-to-many work:** model providers, technicians, and assignments with
   one declared grain and key per relation; do not use delimited text.
6. **Outer-join report:** retain never-borrowed equipment, make date ties
   deterministic, and test the result with an item that has no loan.
7. **Deletion policy:** choose and defend one referential action for each named
   relationship, including what happens to historical records.
8. **Contract introspection:** prove key, check, generated-value, and uniqueness
   properties from catalogs without depending on generated object names.

## Self-check

- Can you say what one row means for all five tables without using a vague word
  such as “data”?
- Does every foreign key point from the many side to a declared parent key?
- Can valid absence still use NULL without a fake empty string or zero?
- Do invalid dates, negative costs, duplicates, and orphan identifiers fail at
  the database boundary?
- Can you distinguish a current catalog value from a historical snapshot?
- Does the final `ROLLBACK` leave no `pro_relational_lab` schema behind?

## Common pitfalls

- Starting with columns before defining grain often creates mixed-grain tables.
- A surrogate primary key does not make a meaningful duplicate valid; add the
  natural `UNIQUE` rule when the domain requires it.
- `CHECK (value > 0)` permits NULL unless the column is also `NOT NULL`.
- `DEFAULT` does not replace an explicitly supplied NULL.
- Foreign keys do not automatically create an index on the referencing column.
- Money-like examples use fixed-scale `numeric`, not binary floating point.
- Generated columns are not a place for volatile values such as “today.”
- Normalization is a reasoning tool, not a command to split every table.

## Next step

Continue to [SQL-FOUND-02 — versioned schema migrations](sql_found_02_versioned_migrations.md)
to evolve a schema without rewriting deployment history. Then begin the
[numbered SQL track](../../postgres-60day/README.md) and query a larger supplied
model.

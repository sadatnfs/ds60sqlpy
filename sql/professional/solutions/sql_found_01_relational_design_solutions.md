# SQL-FOUND-01 Solutions — Relational Design

Run the complete disposable solution with:

```text
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f sql/professional/solutions/sql_found_01_relational_design_solutions.sql
```

It creates `pro_relational_lab` inside a transaction and rolls it back.

## Exercise 1 — Translate requirements into DDL

The grain is **one maintenance visit for one physical equipment item**. An item
can have many visits, while each visit names exactly one item, so the foreign
key belongs on `maintenance_visits`.

The executable solution uses an identity primary key for internal row identity
and keeps `external_reference` as a nullable natural identifier:

```sql
CREATE TABLE pro_relational_lab.maintenance_visits (
    visit_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    item_id bigint NOT NULL
        REFERENCES pro_relational_lab.equipment_items (item_id)
        ON DELETE RESTRICT,
    opened_on date NOT NULL DEFAULT CURRENT_DATE,
    completed_on date,
    provider_name text NOT NULL CHECK (btrim(provider_name) <> ''),
    service_note text NOT NULL CHECK (btrim(service_note) <> ''),
    cost numeric(10, 2) NOT NULL DEFAULT 0 CHECK (cost >= 0),
    external_reference text UNIQUE,
    service_days integer GENERATED ALWAYS AS
        (COALESCE(completed_on, opened_on) - opened_on) STORED,
    CONSTRAINT maintenance_completion_order_ck
        CHECK (completed_on IS NULL OR completed_on >= opened_on)
);
```

`service_days` is zero while a visit is open. Another valid design would leave
it NULL until completion by using
`completed_on - opened_on` without `COALESCE`. That is a product-semantic
choice, not merely a syntax choice.

## Exercise 2 — Prove an invalid cost is rejected

The solution inserts one valid completed visit, then attempts a negative cost
inside an exception-catching test block. Catching `check_violation` keeps the
outer transaction healthy. The block deliberately raises an unexpected
exception if the insert ever succeeds, so weakening or removing the constraint
causes the test to fail.

An application should still validate cost early for a helpful user experience,
but the database constraint is the final invariant because every writer—not
only that application—must obey it.

## Exercise 3 — NULL uniqueness

Two rows with `external_reference IS NULL` succeed under an ordinary `UNIQUE`
constraint. The database does not infer that the two unknown references are the
same reference.

If the rule were “at most one row may have no external reference,” PostgreSQL
15+ supports:

```sql
UNIQUE NULLS NOT DISTINCT (external_reference)
```

That is uncommon for external identifiers. Usually many visits legitimately
lack a provider reference, while every supplied non-NULL reference must be
unique.

## Exercise 4 — Deliberate denormalization

`daily_fee_at_checkout` is deliberate denormalization. The normalized current
fee belongs to the equipment item, but a historical loan must preserve the fee
quoted when the checkout occurred. The invariant is:

> Once a checkout is accepted, its quoted fee changes only through an explicit
> correction workflow; later catalog-price changes do not rewrite history.

This snapshot answers historical billing questions reliably. Copying a
category's display name into each equipment row would not provide that benefit
and would create an update anomaly when the category is renamed.

## Edge cases and alternatives

- If overlapping loans must be impossible, a same-day `UNIQUE` constraint is
  insufficient. A later temporal-modeling lesson can use date ranges and an
  exclusion constraint.
- Case-insensitive email uniqueness needs a defined normalization strategy,
  such as a unique index over `lower(email)`; email semantics should not be
  guessed casually.
- `ON DELETE RESTRICT` preserves history. Soft deletion or a status column can
  retire an item without deleting referenced facts.
- A generated value is convenient for row-local immutable arithmetic. Values
  depending on the current clock or another table need a query, snapshot, or
  reviewed update process instead.


# Day 43 Solutions — Logical Backup and Recovery

This day distinguishes client-side export from database recovery logic. The
answer uses `COPY ... TO STDOUT` so it works through the current connection and
models a restore with a temporary staging table. See
[`day43_solutions.sql`](day43_solutions.sql).

## Exercise 1 — Export and stage a subset

In interactive `psql`, `\copy` writes on the client machine:

```text
\copy (SELECT * FROM training.customers WHERE country = 'US' ORDER BY customer_id) TO 'customers_us.csv' WITH (FORMAT csv, HEADER true)
```

Replace that filename with a path the learner owns. Path syntax, directory
creation, and write permission are environment-specific on Windows, macOS, and
Linux; the repository cannot choose or create that destination safely.

The executable solution uses SQL-standard server output instead:

```sql
BEGIN;
SET search_path TO training, public;

COPY (
  SELECT customer_id, full_name, email, country, created_at, segment, attributes
  FROM customers
  WHERE country = 'US'
  ORDER BY customer_id
) TO STDOUT WITH (FORMAT csv, HEADER true);

CREATE TEMP TABLE customers_restore_stage AS
SELECT full_name, email, country, created_at, segment, attributes
FROM customers
WHERE country = 'US';

SELECT COUNT(*) AS staged_rows FROM customers_restore_stage;
ROLLBACK;
```

Expected shape: CSV rows are streamed to the client, and `staged_rows` equals
the number of US customers. A real import would create an explicit staging
table and run `\copy customers_restore_stage FROM ...`.

## Exercise 2 — Idempotent restore with conflict handling

Email is the current schema's unique business key for this exercise.

```sql
BEGIN;
SET search_path TO training, public;

CREATE TEMP TABLE customers_restore_stage AS
SELECT full_name, email, country, created_at, segment, attributes
FROM customers
WHERE country = 'US';

UPDATE customers_restore_stage
SET full_name = full_name || ' [restored]'
WHERE email = 'customer1@example.com';

INSERT INTO customers(full_name, email, country, created_at, segment, attributes)
SELECT full_name, email, country, created_at, segment, attributes
FROM customers_restore_stage
ON CONFLICT (email) DO UPDATE
SET full_name = EXCLUDED.full_name,
    country = EXCLUDED.country,
    segment = EXCLUDED.segment,
    attributes = EXCLUDED.attributes;

ROLLBACK;
```

The transaction proves both insert and update paths while leaving the course
data unchanged.

## Reasoning, safety, and pitfalls

- `COPY ... TO '/path'` reads or writes on the database server and usually needs
  elevated privileges. `\copy` reads or writes on the `psql` client.
- Restore into staging first; validate counts, keys, types, and representative
  rows before merging into the base table.
- `ON CONFLICT` is idempotent only when the conflict key represents the intended
  entity and update policy.
- Logical export is not point-in-time recovery. Production PITR requires base
  backups plus WAL archiving, which is outside this SQL-only exercise.

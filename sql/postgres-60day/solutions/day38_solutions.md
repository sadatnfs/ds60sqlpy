# Day 38 — Solutions: Transactions and Isolation

Isolation anomalies require genuinely concurrent database sessions. They cannot
be proven by running one `.sql` file serially. Open two VS Code terminals, name
them Session A and Session B, and paste each step only when instructed.

The following single-session check is safe to run independently and demonstrates
transaction-local isolation plus savepoint rollback:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
SET LOCAL search_path TO training, public;

SHOW TRANSACTION ISOLATION LEVEL;

CREATE TEMP TABLE savepoint_demo (
  id int PRIMARY KEY,
  qty int NOT NULL
);
INSERT INTO savepoint_demo VALUES (1, 10);

SAVEPOINT before_change;
UPDATE savepoint_demo
SET qty = qty + 100
WHERE id = 1;
ROLLBACK TO SAVEPOINT before_change;

SELECT id, qty
FROM savepoint_demo;

ROLLBACK;
```

Expected row: `(1, 10)`.

## Lab setup

Run this once in either terminal. The table is deliberately course-specific,
but it is persistent because temporary tables cannot be shared by two sessions.

```text
SET search_path TO training, public;
DROP TABLE IF EXISTS isolation_lab;
CREATE TABLE isolation_lab (
  id int PRIMARY KEY,
  qty int NOT NULL
);
INSERT INTO isolation_lab VALUES (1, 10), (2, 20);
```

## Exercise 1 — Non-repeatable read under `READ COMMITTED`

Session A:

```text
BEGIN ISOLATION LEVEL READ COMMITTED;
SET LOCAL search_path TO training, public;
SELECT qty FROM isolation_lab WHERE id = 1;  -- 10
```

While A remains open, Session B:

```text
BEGIN;
SET LOCAL search_path TO training, public;
UPDATE isolation_lab SET qty = 15 WHERE id = 1;
COMMIT;
```

Back in Session A:

```text
SELECT qty FROM isolation_lab WHERE id = 1;  -- now 15
ROLLBACK;
```

The two reads in A return different committed versions because
`READ COMMITTED` takes a new statement snapshot. Repeat the sequence with
`REPEATABLE READ`; A's second read remains `10` until A ends.

## Exercise 2 — Phantom rows between two counts

Reset, then start Session A:

```text
DELETE FROM training.isolation_lab WHERE id >= 3;
BEGIN ISOLATION LEVEL READ COMMITTED;
SELECT COUNT(*) FROM training.isolation_lab WHERE qty >= 20;  -- 1
```

Session B inserts a new qualifying row:

```text
BEGIN;
INSERT INTO training.isolation_lab(id, qty) VALUES (3, 30);
COMMIT;
```

Back in Session A:

```text
SELECT COUNT(*) FROM training.isolation_lab WHERE qty >= 20;  -- 2
ROLLBACK;
```

The new qualifying row is a phantom. Under `REPEATABLE READ`, Session A would
continue to see its original predicate result.

## Exercise 3 — Serialization failure under contention

Reset the two rows, then interleave these commands. Both transactions read the
same set before either writes it.

Session A:

```text
UPDATE training.isolation_lab SET qty = 10 WHERE id = 1;
UPDATE training.isolation_lab SET qty = 20 WHERE id = 2;
DELETE FROM training.isolation_lab WHERE id >= 3;
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(qty) FROM training.isolation_lab;
```

Session B:

```text
BEGIN ISOLATION LEVEL SERIALIZABLE;
SELECT SUM(qty) FROM training.isolation_lab;
```

Session A, then Session B:

```text
-- Session A
UPDATE training.isolation_lab SET qty = qty + 1 WHERE id = 1;

-- Session B
UPDATE training.isolation_lab SET qty = qty + 1 WHERE id = 2;

-- Session A
COMMIT;

-- Session B
COMMIT;
```

PostgreSQL must abort one transaction with SQLSTATE `40001` to prevent the
read/write dependency cycle. Real applications retry the entire transaction,
not just the final statement.

## Cleanup and cautions

After both sessions have no open transaction, run:

```text
DROP TABLE IF EXISTS training.isolation_lab;
```

Do not leave terminals “idle in transaction.” Results depend on exact
interleaving, and the setup state must be reset between experiments.

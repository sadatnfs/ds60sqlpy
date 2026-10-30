# sql-write-01: Explained change-application solutions

Use the [lesson guide](../companion-guides/sql_write_01_merge_and_upsert.md) and
attempt its six practice slots before comparing. The
[complete executable reference](sql_write_01_solutions.sql) creates the original
temporary stock/feed fixture, runs each answer in its own savepoint, compares
exact ordered target JSON with independently written expected rows and rolls
back. A command tag is useful execution evidence; the row-state assertions
establish additional facts about keys, quantities and versions.

## Exercise 1: Classify and apply the complete snapshot

**Inputs:** For sql-write-01 Exercise 1, use the original w17_practice_stock target and complete w17_practice_feed, each with one row per sku.
**Expected result/shape:** For sql-write-01 Exercise 1, return action, sku, quantity, source_version for the three changed keys A/C/Z, without promising RETURNING order; display final sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1). The target identity is sku.
**Verify:** For sql-write-01 Exercise 1, compare the three action/key pairs with the independently ordered target rows. B has no returned action but remains present; deletion returns Z's old values.

The identity match is on `sku`. A is matched and newer, B is matched but equal,
C is source-only and Z is target-only. The complete-source contract authorizes
deleting Z. The expected changed actions are UPDATE A, INSERT C and DELETE Z;
unchanged B has no changed-row output.

```sql
MERGE INTO w17_practice_stock AS t
  USING w17_practice_feed AS s ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED BY SOURCE THEN
    DELETE
  WHEN NOT MATCHED BY TARGET THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version) RETURNING
  merge_action () AS action, t.sku, t.quantity, t.source_version;
```

`USING` supplies the producer population, `ON` relates business identities and
`WHEN` selects eligible actions. The returned values describe changed target
rows, with old values for deletion. The executable reference does not require a
particular action-output order. Its independent final-state assertion requires
A twelve/version two, B three/version one and C one/version one, ordered by SKU.
This distinguishes no action from a missing business record.

**Verify:** Compare the returned action keys with that exact final target and
confirm that B remains present despite producing no action row.

## Exercise 2: Apply partial events without deleting absent keys

**Inputs:** For sql-write-01 Exercise 2, use the original target and only partial source events (A,12,2) and (C,1,1), with one row per sku.
**Expected result/shape:** For sql-write-01 Exercise 2, display sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1), (Z,5,1), one row per sku.
**Verify:** For sql-write-01 Exercise 2, require Z to remain at quantity five and version one. Absence from a partial feed is not a deletion event; inspect the key set as well as quantities.

A source containing only A and C does not justify deleting B or Z. Omit the
source-missing deletion action entirely. Matching still uses identity, while
the version condition determines whether an existing row can change.

```sql
MERGE INTO w17_practice_stock AS t
  USING ( VALUES ('A', 12, 2), ('C', 1, 1)) AS s (sku, quantity, source_version) ON t.sku = s.sku
  WHEN MATCHED AND s.source_version > t.source_version THEN
    UPDATE SET quantity = s.quantity, source_version = s.source_version
  WHEN NOT MATCHED THEN
    INSERT (sku, quantity, source_version) VALUES (s.sku, s.quantity, s.source_version);
```

The target now has A twelve/version two, B three/version one, C one/version one
and Z five/version one. A count of four alone would not prove correctness: the
wrong four keys or wrong versions could pass that check. The reference compares
each ordered key/value row. Its savepoint rollback then restores the original
three-key fixture before the next exercise. Keeping source-scope meaning in the
statement is more important than choosing a short spelling of the operation.

**Verify:** Require both unchanged absent keys B and Z, not merely the newly
inserted C or an increased total quantity.

## Exercise 3: Select an unambiguous source version before mutation

**Inputs:** For sql-write-01 Exercise 3, use the original target and source rows (A,12,2), (A,14,3), (C,1,1). Versions are unique within each sku, so the greatest version is an unambiguous winner.
**Expected result/shape:** For sql-write-01 Exercise 3, display sku, quantity, source_version ordered by sku as (A,14,3), (B,3,1), (C,1,1), (Z,5,1), one row per sku.
**Verify:** For sql-write-01 Exercise 3, show the deduplicated source with exactly one row per sku before mutation. Compare all four final key/value/version tuples; physical source order is not a conflict policy.

Two source rows for A can attempt to modify the same target. The lesson's
worked failure shows that `MERGE` does not implicitly choose whichever source
version happens to be encountered last. Resolve the source using the declared
unique version ordering first.

```sql
WITH ranked AS (
  SELECT
    sku,
    quantity,
    source_version,
    row_number() OVER (PARTITION BY sku ORDER BY source_version DESC) AS position
  FROM (
    VALUES ('A', 12, 2),
      ('A', 14, 3),
      ('C', 1, 1)) AS feed (sku, quantity, source_version))
SELECT
  sku,
  quantity,
  source_version
FROM
  ranked
WHERE
  position = 1
ORDER BY
  sku;
```

The selected source is A fourteen/version three and C one/version one. The full
reference uses that relation as `USING` input with the partial-feed actions
from Exercise 2. Its result retains B and Z. This ordering rule depends on the
stated uniqueness of versions within a SKU. If equal versions contain
conflicting values, adding an arbitrary tie-breaker would invent a business
policy. Reject the ambiguity or obtain an authorized immutable event/version
identity that determines the correct record.

**Verify:** Display one selected row per key before mutation, then check exact
A/B/C/Z target values and versions afterward.

## Exercise 4: Use the uniqueness-conflict path and reject stale proposals

**Inputs:** For sql-write-01 Exercise 4, use the original target with its sku primary key and partial events (A,14,3), (B,999,1), (D,4,1).
**Expected result/shape:** For sql-write-01 Exercise 4, rETURNING contains only changed keys A/D. Display final sku, quantity, source_version ordered by sku as (A,14,3), (B,3,1), (D,4,1), (Z,5,1), one row per sku.
**Verify:** For sql-write-01 Exercise 4, require B to retain quantity three and version one despite the stale proposed 999. Check Z remains five and distinguish a skipped update from a missing target.

The primary key provides a conflict target for each proposed SKU. `excluded`
contains the proposed values, while alias `t` refers to the existing target.
The version comparison is applied to the update action.

```sql
INSERT INTO w17_practice_stock AS t (sku, quantity, source_version)
VALUES
  ('A', 14, 3),
  ('B', 999, 1),
  ('D', 4, 1)
ON CONFLICT (sku)
  DO UPDATE SET
    quantity = excluded.quantity,
    source_version = excluded.source_version
  WHERE
    excluded.source_version > t.source_version
  RETURNING
    sku, quantity, source_version;
```

A advances and D is inserted. B's equal version means its proposed 999 is not
applied. The final target is A fourteen/version three, B three/version one,
D four/version one and Z five/version one. C is absent here because every
exercise begins with the original practice fixture, not the mutated state from
the worked examples. The changed-row result contains A and D; retaining a
visible key is essential when checking which facts actually changed.

**Verify:** Match both returned keys to the stored target, and check B and Z
independently so the mutation cannot be accepted on a plausible total alone.

## Exercise 5: Demonstrate convergence without inventing an execution guarantee

**Inputs:** For sql-write-01 Exercise 5, use the original target and complete three-row w17_practice_feed. Run the same conditional full-snapshot MERGE twice within one exercise slot.
**Expected result/shape:** For sql-write-01 Exercise 5, the first run changes A/C/Z and the second changes zero rows. After each run, sku, quantity, source_version ordered by sku is (A,12,2), (B,3,1), (C,1,1), one row per sku.
**Verify:** For sql-write-01 Exercise 5, inspect the actual second statement's ROW_COUNT and compare all ordered target tuples after both runs. An equal grand total cannot prove correct identities or convergence.

Run the complete-snapshot statement from Exercise 1 twice in the same practice
slot. On the first run A advances, C appears and Z disappears. On the second,
all existing source versions are equal, every source key is present and no
target key is missing from the source. Therefore no change action is selected.

The executable reference records the actual second `ROW_COUNT` inside a
provided PL/pgSQL check and requires zero. It independently checks that the
target remains A twelve/version two, B three/version one and C one/version one.
The row count alone would not identify an incorrect prior state; the exact
state assertion supplies that complementary evidence.

This is a converged-state observation for the declared fixture and version
policy. It is not proof of exactly-once delivery across a network, a general
concurrent race guarantee or the absence of side effects in unrelated triggers.

**Verify:** Retain the first changed-row observation, the second zero count and
the ordered final state under the same source identity.

## Exercise 6: Gate deletion before applying an incomplete snapshot

**Inputs:** For sql-write-01 Exercise 6, compare a declared expected snapshot count of three with an incomplete A/C source, then with the supplied complete A/B/C source. Row count is only one declared completeness condition.
**Expected result/shape:** For sql-write-01 Exercise 6, reject the incomplete source before MERGE and retain original (A,10,1), (B,3,1), (Z,5,1). After the complete source passes, display sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1), one row per sku.
**Verify:** For sql-write-01 Exercise 6, require the explicit incomplete-snapshot rejection before any target mutation. Compare the unchanged original rows, then demonstrate the passing gate and complete final key set; equal counts alone do not establish source authenticity.

The proposed source contains A and C but declares an expected population of
three rows. The reference checks that mismatch before running any source-missing
deletion. It raises the specific `incomplete-snapshot` condition inside a
controlled subtransaction and verifies that the original A/B/Z rows remain.

```sql
SELECT
  count(*) AS supplied_rows,
  3 AS declared_rows
FROM
  w17_practice_feed
WHERE
  sku IN ('A', 'C');
```

Supplying the complete three-row feed afterward satisfies the same count gate.
The full-snapshot mutation can then produce the accepted A/B/C state. The
reference checks both rejection and accepted follow-up paths rather than
assuming that any error establishes the desired boundary.

A count gate is a useful truncation detector, not a proof of complete business
coverage. A wrong three-row key set can still have count three. Real source
contracts may need identity manifests, expected scope, versions, checksums and
an explicit authoritative boundary. Keep those assumptions visible when using
absence to authorize deletion.

**Verify:** Demonstrate unchanged original rows after rejection and the exact
complete-snapshot rows only after the source gate succeeds.

## Final evidence review

The reference completes with `ROLLBACK`, leaving no course answer persisted.
Explain the input grain, action condition and output grain for each statement,
including when no row is returned. Distinguish a source-version policy, an
integrity constraint, a completeness claim and a concurrency guarantee. Each
requires evidence appropriate to its actual meaning.

# PostgreSQL 17 Change Application: MERGE and ON CONFLICT

**Stable ID:** `sql-write-01`. This is a PostgreSQL 17 advanced practice lesson.

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-write-01**. The
[launcher guide](../../../docs/one-command-classroom.md) covers first preparation, strict resume and
the saved project selection. No host Python or PostgreSQL installation is
required for this browser route.

1. Read the prerequisite and fixture notes before running the file. Use only
   the local disposable `advanced_sql_training` database. A simple snippet
   such as `SELECT 1;` needs no training-schema reset.
2. Choose **Whole SQL lesson (psql)** for the cataloged learner script. This
   preserves the lesson's reviewed psql directives, relative includes and
   transaction behavior. **SQL snippet** is appropriate for ordinary SQL
   statements, but is not a replacement for an entire script's setup.
3. When the lesson requires the course training data, use the explicit
   preparation action and read its reset acknowledgement. It replaces the
   course-owned `training` schema. Do not reset unrelated data or prepare
   every lesson by habit; stateful sequences have their own ordering.
4. Edit the learner copy in the classroom and save your prediction before
   running. Its whole-script workspace is
   `.learning/sql/sql-write-01/lesson/workspace/sql/professional/lessons/sql_write_01_merge_and_upsert.sql`.
   For browser work this path is inside the Docker learning volume, not a
   newly created host folder beside your checkout. The checked-in source
   remains the answer-free starting artifact.
5. Run the whole script and inspect the full transcript. The runner uses
   `psql -X -v ON_ERROR_STOP=1 -f`. SELECT output has columns, rows and a row
   count; DDL/DML has command tags; intentional checks may produce NOTICE
   messages. An unexpected ERROR or nonzero exit is a failure to diagnose,
   even when an earlier query printed plausible values.
6. Verify the lesson's expected grain, ordering, constraints and declared
   transaction or cleanup outcome. Keep required ROLLBACK statements.
   The warehouse sequence and other explicitly stateful exercises explain
   when state is committed. Read saved output without rerunning it when
   reviewing an earlier attempt.

If a relation is missing, inspect the lesson's required fixture and predecessor
rather than guessing a new table definition. If authentication or runtime
readiness fails, use `./classroom status` and the setup guide. Keep credentials
out of SQL, notebooks, screenshots and committed files. Repair the first error
before trusting partial output, and reveal separate solutions only when you
want to compare after an attempt.

### Optional contributor notebook route

For notebook work, deliberately prepare the Linux/WSL contributor environment
from [CONTRIBUTING.md](../../../CONTRIBUTING.md), including a compatible psql client and
the notebook dependencies. Generate this lesson's private workspace through
the maintained CLI:

```sh
uv run --no-sync python scripts/course.py sql notebook sql-write-01
```

Open the printed notebook path in that environment's JupyterLab. It uses the
same catalog-derived learner-copy layout in that contributor checkout and
executes the complete script through psql. Its host-side state is separate
from the Docker browser's named volume. Follow
[guided SQL notebooks](../../../docs/guided-sql-notebooks.md) for explicit local connection
selection and kernel setup. Notebook generation does not execute SQL or
authorize a reset.

## Level and prerequisites

- **Level:** Advanced.
- **Direct prerequisite:** `sql-found-02`, [companion guide](sql_found_02_versioned_migrations.md).
- **Direct prerequisite:** `sql-deep-05`, [companion guide](sql_deep_05.md).
- **Artifacts:** [learner](../lessons/sql_write_01_merge_and_upsert.sql) · [explanations](../solutions/sql_write_01_solutions.md) · [executable reference](../solutions/sql_write_01_solutions.sql).

This advanced lesson follows `sql-found-02` and `sql-deep-05`. You should already
understand primary keys, transactions, version-checked updates and the difference
between matching a business identity and filtering eligible rows. The supplied
fixture does not require a separate training-schema reset. The script checks
that it is running in the disposable PostgreSQL 17 database.

## Learning objectives

- Choose a change-application statement from a declared feed contract.
- Keep business identity separate from update eligibility.
- Read actual inserted, updated and deleted rows without assuming output order.
- Reject ambiguous source versions and incomplete deletion snapshots.
- Distinguish converged state from a general concurrency or exactly-once claim.

## Vocabulary and concepts

- **Business key:** The identifier for the fact being updated; `sku` identifies one stock record here.
- **Source version:** A producer-defined ordered version for that key. A larger number is newer under this fixture's contract.
- **Complete snapshot:** An authoritative representation of every in-scope current key at a declared source boundary.
- **Partial event feed:** A set of changes that does not say that absent keys were deleted.
- **Conflict target:** A uniqueness rule used by `INSERT ... ON CONFLICT` to identify an existing row.
- **Candidate change row:** A source/target relationship classified by the `MERGE` identity match before its action conditions are evaluated.

The initial target contains A with quantity ten/version one, B with three/version
one and Z with five/version one. The source contains A twelve/version two, B
three/version one and C one/version one. All quantities describe one synthetic
stock unit; versions are ordered integers, not wall-clock timestamps.

State the feed's meaning before selecting SQL. If the source is complete and
authoritative, Z's absence can authorize deletion. If it is a partial feed,
absence says nothing about Z. The same three visible source rows can therefore
lead to different legitimate final states under different source contracts.

## Syntax anatomy and action selection

`MERGE INTO target USING source ON identity` relates the two populations. In this
lesson `ON t.sku=s.sku` answers whether the business key already exists. A matched
row can then be eligible for an update only when its source version advances.
That second question belongs in `WHEN MATCHED AND ...`.

Putting the version comparison inside `ON` changes identity classification. An
equal-version B can appear unmatched by the target even though its primary key
already exists. An insert branch can then encounter a uniqueness error. Moving
an eligibility condition between `ON` and `WHEN` is therefore not a harmless
formatting preference.

Action clauses also have an order: the first applicable action is selected for a
candidate. A condition that claims a row earlier can prevent a later clause from
being used. Keep source-only deletion, target-missing insertion and matched-row
updates explicit rather than assuming the engine infers an intended sync policy.

## Worked example / walkthrough

### Worked case 1: Apply a complete authoritative snapshot

```sql
MERGE INTO w17_stock AS t
USING w17_feed AS s ON t.sku = s.sku
WHEN MATCHED AND s.source_version > t.source_version THEN
  UPDATE SET quantity = s.quantity, source_version = s.source_version
WHEN NOT MATCHED BY SOURCE THEN DELETE
WHEN NOT MATCHED BY TARGET THEN
  INSERT (sku, quantity, source_version)
  VALUES (s.sku, s.quantity, s.source_version)
RETURNING merge_action() AS action, t.sku, t.quantity, t.source_version;
```

The actual changed-row output contains A as UPDATE, C as INSERT and Z as DELETE.
B does not change because its version is equal. An unchanged row has no changed
`RETURNING` row. Insert/update output describes new target values; deleted Z
describes the deleted values. The statement does not promise a display order for
this action stream. The following ordered target query establishes the final
state: A twelve/version two, B three/version one and C one/version one.

This is a synchronization policy for the declared complete source. A row-count
manifest can catch truncation, but matching a count alone does not prove that the
correct keys were delivered or that the producer's boundary is authoritative.
Completeness needs evidence from the source system and its identity rules.

### Worked case 2: Apply partial changes through a uniqueness conflict

```sql
INSERT INTO w17_stock AS t (sku, quantity, source_version)
VALUES ('A', 14, 3), ('B', 999, 1), ('D', 4, 1)
ON CONFLICT (sku) DO UPDATE
SET quantity = excluded.quantity,
    source_version = excluded.source_version
WHERE excluded.source_version > t.source_version
RETURNING sku, quantity, source_version;
```

`excluded` describes the proposed values for a uniqueness conflict. A advances to
fourteen/version three. B's stale proposal of 999 is skipped by the update
condition. D is inserted. C remains present because this statement does not
interpret absence as deletion. In this worked sequence, the final keys are A,
B, C and D with quantities fourteen, three, one and four.

The learner script also attempts to modify A twice from two source rows in one
`MERGE`. PostgreSQL raises a cardinality violation. The explicitly handled
subtransaction preserves the earlier target state. Source row order is not a
latest-version selection policy. The practice repair selects one unique newest
source version per key before applying changes.

## Choosing a statement and a concurrency claim

`ON CONFLICT` uses the selected uniqueness mechanism for its insert/conflict
path. `MERGE` expresses several source/target action classes, including source
absence. They do not have identical guarantees under a concurrent target insert.
In particular, do not infer an automatic uniqueness-conflict retry policy from
`MERGE` syntax. Isolation, constraints and competing operations still matter.

This default lesson runs in one session. It demonstrates actual mutation,
version eligibility, cardinality errors and converged state. It does not claim to
have executed a two-session race or delivered an event exactly once across a
network. The separately owned concurrency lesson supplies that additional
execution surface when deliberately selected.

## Exercises

Each slot uses `w17_practice_stock` and its separate original fixture. Keep its
savepoint rollback so later exercises do not inherit a previous answer's changes.

1. **Prediction:** Name the changed actions and unchanged key for the complete source.
   **Inputs:** For sql-write-01 Exercise 1, use the original w17_practice_stock target and complete w17_practice_feed, each with one row per sku.
   **Expected result/shape:** For sql-write-01 Exercise 1, return action, sku, quantity, source_version for the three changed keys A/C/Z, without promising RETURNING order; display final sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1). The target identity is sku.
   **Verify:** For sql-write-01 Exercise 1, compare the three action/key pairs with the independently ordered target rows. B has no returned action but remains present; deletion returns Z's old values.
2. **Query writing:** Apply A twelve/version two and C one/version one as partial changes with `MERGE`.
   **Inputs:** For sql-write-01 Exercise 2, use the original target and only partial source events (A,12,2) and (C,1,1), with one row per sku.
   **Expected result/shape:** For sql-write-01 Exercise 2, display sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1), (Z,5,1), one row per sku.
   **Verify:** For sql-write-01 Exercise 2, require Z to remain at quantity five and version one. Absence from a partial feed is not a deletion event; inspect the key set as well as quantities.
3. **Debugging:** Resolve A's versions two and three before applying the source.
   **Inputs:** For sql-write-01 Exercise 3, use the original target and source rows (A,12,2), (A,14,3), (C,1,1). Versions are unique within each sku, so the greatest version is an unambiguous winner.
   **Expected result/shape:** For sql-write-01 Exercise 3, display sku, quantity, source_version ordered by sku as (A,14,3), (B,3,1), (C,1,1), (Z,5,1), one row per sku.
   **Verify:** For sql-write-01 Exercise 3, show the deduplicated source with exactly one row per sku before mutation. Compare all four final key/value/version tuples; physical source order is not a conflict policy.
4. **Query writing:** Apply the partial insert/conflict source to the original practice target.
   **Inputs:** For sql-write-01 Exercise 4, use the original target with its sku primary key and partial events (A,14,3), (B,999,1), (D,4,1).
   **Expected result/shape:** For sql-write-01 Exercise 4, rETURNING contains only changed keys A/D. Display final sku, quantity, source_version ordered by sku as (A,14,3), (B,3,1), (D,4,1), (Z,5,1), one row per sku.
   **Verify:** For sql-write-01 Exercise 4, require B to retain quantity three and version one despite the stale proposed 999. Check Z remains five and distinguish a skipped update from a missing target.
5. **Verification:** Apply the complete snapshot twice.
   **Inputs:** For sql-write-01 Exercise 5, use the original target and complete three-row w17_practice_feed. Run the same conditional full-snapshot MERGE twice within one exercise slot.
   **Expected result/shape:** For sql-write-01 Exercise 5, the first run changes A/C/Z and the second changes zero rows. After each run, sku, quantity, source_version ordered by sku is (A,12,2), (B,3,1), (C,1,1), one row per sku.
   **Verify:** For sql-write-01 Exercise 5, inspect the actual second statement's ROW_COUNT and compare all ordered target tuples after both runs. An equal grand total cannot prove correct identities or convergence.
6. **Extension:** Refuse a two-row source when its declared complete count is three.
   **Inputs:** For sql-write-01 Exercise 6, compare a declared expected snapshot count of three with an incomplete A/C source, then with the supplied complete A/B/C source. Row count is only one declared completeness condition.
   **Expected result/shape:** For sql-write-01 Exercise 6, reject the incomplete source before MERGE and retain original (A,10,1), (B,3,1), (Z,5,1). After the complete source passes, display sku, quantity, source_version ordered by sku as (A,12,2), (B,3,1), (C,1,1), one row per sku.
   **Verify:** For sql-write-01 Exercise 6, require the explicit incomplete-snapshot rejection before any target mutation. Compare the unchanged original rows, then demonstrate the passing gate and complete final key set; equal counts alone do not establish source authenticity.

## Common pitfalls

Treating a partial feed as a snapshot can delete valid keys. Hiding duplicates
with an unordered `DISTINCT` can choose an arbitrary version. Adding more `WHEN`
clauses cannot repair a wrong identity predicate. Inspect both source uniqueness
and target key meaning before changing action syntax.

If a statement fails, retain the first error and restore the exercise savepoint.
Do not continue from an unverified target state. The final `ROLLBACK` removes
these temporary mutations. Use `RETURNING` and ordered verification queries to
understand changes, rather than accepting a plausible command tag as proof.

## Self-check

- Explain why matching business identity in ON differs from testing version eligibility in WHEN. Give the target keys produced by the partial versus complete feed.
- Reconstruct which INSERT, UPDATE and DELETE rows actually appear in RETURNING, and why an unchanged target can remain without an action row.
- Demonstrate the duplicate-source error and the second-run zero-change assertion. State why neither an equal total nor convergence alone proves general concurrent exactly-once delivery.

## Next step

Continue to the [isolation and optimistic-concurrency lab](sql_concurrency_01_isolation_and_versions.md) when its prerequisites are met. Compare this lesson's converged target state with the evidence needed for concurrent requests. Use the [professional learning path](../README.md) to choose another independent advanced route.

## Further reading

- [PostgreSQL 17 MERGE](https://www.postgresql.org/docs/17/sql-merge.html)
- [PostgreSQL 17 INSERT and ON CONFLICT](https://www.postgresql.org/docs/17/sql-insert.html)
- [PostgreSQL 17 transaction isolation](https://www.postgresql.org/docs/17/transaction-iso.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-write-01: PostgreSQL 17 Change Application: MERGE and ON CONFLICT.
Read sql/professional/companion-guides/sql_write_01_merge_and_upsert.md and sql/professional/lessons/sql_write_01_merge_and_upsert.sql. Direct prerequisites: sql-found-02 and sql-deep-05.
Explain identity matching, version eligibility, complete snapshots, source cardinality and actual returned actions. Ask me to predict exact rows and values before my attempt, give progressive hints, review my evidence, then ask retrieval questions in my own words.
Do not read solutions/ until I ask or have attempted the relevant exercise. Use only the disposable advanced_sql_training PostgreSQL 17 database; keep the savepoint and final ROLLBACK boundaries. I use the unified classroom Whole SQL lesson (psql) mode.
Done when I can show expected ordered target rows, preserve a stale key, reject incomplete source before deletion and explain the limits of single-session concurrency evidence.
```

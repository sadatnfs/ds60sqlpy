# SQL-FOUND-01 Solutions — Relational Design


<!-- beginner-solution-enrichment -->
## How to study and run this solution

Open this explanation only after making an honest attempt. The executable
companion runs solely against the disposable `advanced_sql_training` database:

```powershell
# Windows PowerShell, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training -f "sql\professional\solutions\sql_found_01_relational_design_solutions.sql"
```

```bash
# macOS/Linux, from the repository root
psql -X -v ON_ERROR_STOP=1 -d advanced_sql_training \
  -f sql/professional/solutions/sql_found_01_relational_design_solutions.sql
```

`psql` prints each result/command tag in the terminal. Stop at the first
unexpected `ERROR`; later output cannot repair an earlier failed invariant.
Compare your own SQL, row grain, column names, row counts, `NULL` policy, and
ordering with the explanation before comparing syntax.

## Clause-by-clause reading map

The lesson's main concepts are Grain, Cardinality, Natural key, Surrogate key, Primary key, Foreign key. Its worked-model focus is:
The example begins with four requirements and turns each into a grain:

- Start at `FROM`/`JOIN` and state the intermediate row grain. Inspect join keys
  before adding aggregates; a one-to-many join is allowed to multiply rows only
  when the later contract accounts for it.
- Apply `WHERE` to input rows, `GROUP BY` to form buckets, and `HAVING` to
  completed groups. Window functions run over the surviving relation and
  normally preserve its row count.
- Read the `SELECT` list as the public result contract: keys establish grain,
  measures state calculations, and aliases explain meaning. `ORDER BY` is the
  only output-order guarantee; add a unique tie-breaker before `LIMIT`.
- Trace every common table expression (CTE) as a temporary named relation.
  Execute or inspect one stage at a time while debugging, but compare the final
  result with an independent control rather than trusting stage names.
- Keep SQL `NULL` as “missing/unknown/not applicable” until the metric contract
  chooses another representation. Guard division with `NULLIF`; disclose
  exclusions and distinguish zero from no row.
- For DDL/DML, a command tag proves only that PostgreSQL accepted a statement.
  Catalog checks, negative cases, row-count reconciliation, and the declared
  transaction boundary prove behavior and cleanup.

The exact final queries are not the only valid syntax. A join, subquery, CTE,
window, or conditional aggregate can be an alternative when it preserves the
same grain, `NULL` semantics, deterministic ordering, and safety. Prefer the
form whose intermediate relations a reviewer can verify; optimize only after
correctness is established with evidence.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 1 must make “Maintenance DDL: translate every visit requirement into a column, constraint, key, default, or generated expression; annotate the table grain” observable through the exact DDL/DML command tag plus one catalog/behavior check per object or invariant; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `ddl`, `pro_relational_lab.maintenance_visits`.
- **Independent verification:** For Exercise 1, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `ddl`, `pro_relational_lab.maintenance_visits`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 1: one row is one maintenance visit for one physical item.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 2 — Prove an invalid cost is rejected

The solution inserts one valid completed visit, then attempts a negative cost
inside an exception-catching test block. Catching `check_violation` keeps the
outer transaction healthy. The block deliberately raises an unexpected
exception if the insert ever succeeds, so weakening or removing the constraint
causes the test to fail.

An application should still validate cost early for a helpful user experience,
but the database constraint is the final invariant because every writer—not
only that application—must obey it.

### Reasoning and verification

- **Expected result/shape:** Exercise 2 needs a labeled transaction/session transcript that demonstrates “Negative cost: insert one valid visit, isolate the rejected insert in a nested block, and verify the expected SQLSTATE category”. Capture statement order, affected keys/counts, lock or snapshot state, and the expected SQLSTATE when an error is part of the exercise; finish with no open lesson transaction or leftover shared fixture. Named evidence columns/objects: `service`, `i`, `sqlstate`.
- **Independent verification:** For Exercise 2, replay the written Session A/Session B order against `advanced_sql_training`, compare the observed values/SQLSTATE with the prediction, then query/drop the disposable fixture and confirm neither session retains a transaction or lock. The executable solution's check is: Exercise 2: safely prove that the database rejects a negative cost.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

### Reasoning and verification

- **Expected result/shape:** Exercise 3 requires a written prediction and the observed result for “NULL uniqueness: insert two NULL references, explain the observed rule, and write—but do not blindly apply—the stricter PostgreSQL 15+ alternative”. Show both compared result shapes at one row per requested calendar/cohort bucket and grouping key, including their row counts, relevant `NULL` values, and stable sort keys. Named evidence columns/objects: `i`, `dates`, `mv`.
- **Independent verification:** For Exercise 3, run the two forms over the identical rows in `pro_relational_lab.maintenance_visits`, `pro_relational_lab.equipment_items`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 3: two NULL external references are valid with ordinary UNIQUE.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 4 — Deliberate denormalization

`daily_fee_at_checkout` is deliberate denormalization. The normalized current
fee belongs to the equipment item, but a historical loan must preserve the fee
quoted when the checkout occurred. The invariant is:

> Once a checkout is accepted, its quoted fee changes only through an explicit
> correction workflow; later catalog-price changes do not rewrite history.

This snapshot answers historical billing questions reliably. Copying a
category's display name into each equipment row would not provide that benefit
and would create an update anomaly when the category is renamed.

### Reasoning and verification

- **Expected result/shape:** Exercise 4 requires a written prediction and the observed result for “Historical fee: state the invariant, the historical question, and why the checkout snapshot is or is not deliberate denormalization”. Show both compared result shapes at one result row per key or group explicitly named in the prompt, including their row counts, relevant `NULL` values, and stable sort keys.
- **Independent verification:** For Exercise 4, run the two forms over the identical rows in `pro_relational_lab.members`, `pro_relational_lab.equipment_categories`, `pro_relational_lab.equipment_items`, `pro_relational_lab.loans`; compare the named columns, count, `NULL` placement, and order, then explain any difference between prediction and transcript. The executable solution's check is: Exercise 4: dailyfeeatcheckout belongs on a loan because it is the quoted historical value. A later equipment price change must not rewrite it.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 5 — Providers, technicians, and assignments

Use one row per provider, one row per technician, and one row per
visit/technician assignment. A provider-to-technician relationship may be
modeled separately if employment changes independently of a visit. The
assignment table needs a composite key such as `(visit_id, technician_id)` (or
an identity plus that unique constraint) so the same technician cannot be
silently assigned twice.

Delimited names fail because the database cannot enforce a technician foreign
key, distinguish a comma inside a name, or update/query one participant without
parsing text. The executable solution creates normalized tables and demonstrates
the join at one row per visit/technician assignment.

### Reasoning and verification

- **Expected result/shape:** Exercise 5 must make “Many-to-many work: model providers, technicians, and assignments with one declared grain and key per relation; do not use delimited text” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `mv`, `t`, `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`.
- **Independent verification:** For Exercise 5, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `mv`, `t`, `pro_relational_lab.providers`, `pro_relational_lab.technicians`, `pro_relational_lab.visit_technicians`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 5: names become referenced entities; the bridge grain is one technician assignment to one maintenance visit.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 6 — Preserve equipment with no loans

Start from `equipment_items`, LEFT JOIN `loans`, and aggregate by item. Put a
loan-side time filter in the `ON` clause when equipment with no qualifying loan
must remain. The latest date is `max(checked_out_on)` and count should use a
non-NULL loan key, not `count(*)`, which counts the preserved outer row.

If the report also needs columns from the latest loan, rank loans by
`checked_out_on DESC, loan_id DESC` before joining. The identity is the stated
tie-break; a date alone does not impose a total order.

### Reasoning and verification

- **Expected result/shape:** Exercise 6 must make “Outer-join report: retain never-borrowed equipment, make date ties deterministic, and test the result with an item that has no loan” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `IDENTITY`, `i`, `loan_count`, `latest_checkout`, `l`, `pro_relational_lab.loans`.
- **Independent verification:** For Exercise 6, inspect the relevant `pg_catalog` or `information_schema` rows for `IDENTITY`, `i`, `loan_count`, `latest_checkout`, `l`, `pro_relational_lab.loans`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 6: count a nullable-side key, not COUNT(), so never-loaned items correctly report zero. A loan-side date predicate would belong in ON.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 7 — Referential deletion policy

`category -> equipment` and `equipment -> loans` should normally RESTRICT
physical deletion because silently deleting assets or historical checkouts
destroys facts. `equipment -> maintenance_visits` should also RESTRICT under the
same audit requirement. Retire a category/item with status or effective dates.

CASCADE is appropriate for components that have no meaning outside their
parent, not merely because cleanup is easy. `SET NULL` is valid only when the
child remains truthful without its parent and the column is deliberately
nullable. Every choice is a domain rule and requires a deletion test.

### Reasoning and verification

- **Expected result/shape:** Exercise 7 must make “Deletion policy: choose and defend one referential action for each named relationship, including what happens to historical records” observable through the exact DDL/DML command tag plus one result row per key or group explicitly named in the prompt; include a catalog or behavior result for every named object/invariant, not only a successful statement. Named evidence columns/objects: `historical`.
- **Independent verification:** For Exercise 7, inspect the relevant `pg_catalog` or `information_schema` rows for `historical`, run one valid case and the prompt's invalid/boundary case, and confirm the lesson transaction or cleanup removes only its disposable state. The executable solution's check is: Exercise 7: RESTRICT preserves visits and loans as historical facts. CASCADE is used only for the assignment bridge, which has no meaning without a visit.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

## Exercise 8 — Catalog-level contract

Join `pg_constraint`, `pg_class`, `pg_namespace`, and `pg_attribute`, and inspect
constraint type plus `pg_get_constraintdef`. Inspect `pg_attribute.attgenerated`
and `pg_get_expr(pg_attrdef.adbin, ...)` for the generated expression. This
checks semantic properties without coupling a test to a generated name.

For NULL-aware uniqueness, inspect `pg_index.indnullsnotdistinct` on PostgreSQL
15+. The ordinary solution expects it to be false. A robust contract also
checks column order/types and the referenced relation/columns rather than
searching rendered text alone.

### Reasoning and verification

- **Expected result/shape:** Exercise 8 returns a table-shaped answer to “Contract introspection: prove key, check, generated-value, and uniqueness properties from catalogs without depending on generated object names” at one result row per key or group explicitly named in the prompt. Named evidence columns/objects: `constraint_definition`, `con`, `rel`, `n`, `column_name`, `generated_expression`, `def`. Include every key/measure named by the prompt, preserve `NULL` versus zero/absent-row meaning, and use a unique final sort key whenever rows are ranked or limited.
- **Independent verification:** For Exercise 8, prove uniqueness at one result row per key or group explicitly named in the prompt; reconcile the result's row count and any count/sum/amount with a simpler control over `pg_catalog.pg_constraint`, `pg_catalog.pg_class`, `pg_catalog.pg_namespace`, `pg_catalog.pg_attribute`, `pg_catalog.pg_attrdef`, and inspect the prompt's empty, tied, duplicate, or `NULL` boundary. The executable solution's check is: Exercise 8: inspect semantic catalog properties instead of generated names.
- **Intermediate relation check:** Run or inspect each CTE/subquery from the
  inside out. Record its keys and row count; the first stage that violates the
  declared grain is where debugging begins.
- **Clause check:** Explain why every `ON`, `WHERE`, grouping, window frame,
  projection, and final sort belongs where it is. Moving a predicate can change
  preserved rows; removing a tie-breaker can make output nondeterministic.
- **Alternative/trade-off:** A shorter formulation is valid only when it preserves the same grain, NULL behavior, deterministic order, and transaction boundary.
- **Edge case:** Recheck empty input, one qualifying row, `NULL` in a relevant
  value/key, duplicate join keys, and tied ordering values. State which cases
  are impossible because of a database constraint and which the query handles.

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

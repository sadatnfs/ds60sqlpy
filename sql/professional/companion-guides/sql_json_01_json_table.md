# PostgreSQL 17 JSON_TABLE: Typed Projection and Result Grain

**Stable ID:** `sql-json-01`. This is a PostgreSQL 17 advanced practice lesson.

## How to run this lesson

Start the Linux-container engine and run `./classroom` from the repository
root. On Windows, use Ubuntu in WSL 2 or the thin
`START_DOCKER_CLASSROOM.cmd` wrapper. Choose **PostgreSQL** on the shared
`/classroom` home, then open **sql-json-01**. The
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
   `.learning/sql/sql-json-01/lesson/workspace/sql/professional/lessons/sql_json_01_json_table.sql`.
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
uv run --no-sync python scripts/course.py sql notebook sql-json-01
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
- **Direct prerequisite:** `sql-types-01`, [companion guide](sql_types_01_native_types_search.md).
- **Direct prerequisite:** `sql-deep-02`, [companion guide](sql_deep_02.md).
- **Artifacts:** [learner](../lessons/sql_json_01_json_table.sql) · [explanations](../solutions/sql_json_01_solutions.md) · [executable reference](../solutions/sql_json_01_solutions.sql).

This advanced lesson follows `sql-types-01` and `sql-deep-02`. You should
understand JSONB extraction, SQL NULL, outer joins and aggregation grain. The
provided fixtures are temporary and independent of the training-schema data.
The full script checks the disposable database and PostgreSQL 17 capability,
then rolls back both worked examples and practice slots.

## Learning objectives

- Turn a declared JSON array into typed relational columns with `JSON_TABLE`.
- Explain the output grain before and after outer-row preservation.
- Distinguish missing paths, explicit JSON null and conversion errors.
- Retain quantity coverage when computing monetary results.
- Add parent-level measures once after reducing child rows to parent grain.

## Vocabulary and concepts

- **Row path:** The JSON path that chooses the contexts producing relational rows; `$.items[*]` selects item contexts here.
- **Column path:** A path evaluated relative to one selected row context, such as `$.sku` or `$.qty`.
- **Typed projection:** Converting selected JSON values into declared SQL types under an explicit empty/error policy.
- **Ordinality:** A one-based position assigned to generated rows. It is not a permanent business identity.
- **Null extension:** The placeholder row that a LEFT join supplies when an outer document has no matched item rows.
- **Coverage:** Evidence that the fields needed to interpret a complete result are available, rather than merely a partial sum being computable.

The main table has one row per `document_id`. Document one declares two items:
P has quantity two at price five, and Q has quantity one at price three. Its
document-level shipping fee is four. Document two declares an empty item array
and zero shipping. Document three has no items field and shipping two. These
states are intentionally different, even though both can yield no item rows.

## Syntax anatomy and query reasoning

`JSON_TABLE` is a row source. The row path selects contexts, and `COLUMNS`
defines the SQL view of each context. `FOR ORDINALITY` supplies a position
starting at one. Scalar columns name SQL types and extraction paths; their
`ON EMPTY` and `ON ERROR` clauses state how selected conditions are handled.

This fixture permits omitted quantity to mean one. It does not replace explicit
JSON null with one: null remains an unknown SQL quantity. Prices use one
declared currency and exact `numeric(10,2)` values. An invalid price or quantity
cannot become zero revenue by accident under the strict worked policy.

Typed projection is not a complete message-schema validator. For example, a
conversion may accept a numeric-looking string under its coercion rules. The
default lax path mode can also adapt shapes that an application intended to
reject. A producer contract may require additional checks on field presence,
root shape, array type, range, units and business identity before projection.

## Worked example / walkthrough

### Worked case 1: Choose item grain or preserve document grain

```sql
SELECT
  d.document_id,
  j.item_no,
  j.sku,
  j.qty,
  j.unit_price
FROM
  j17_documents AS d
  CROSS JOIN JSON_TABLE (d.payload, '$.items[*]' COLUMNS (item_no FOR ORDINALITY, sku text PATH '$.sku', qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, unit_price numeric(10, 2)
  PATH '$.price' ERROR ON EMPTY ERROR ON ERROR)) AS j
ORDER BY
  d.document_id,
  j.item_no;
```

The actual result has two rows: document one's P and Q. The output grain is one
generated item position within a document. Empty or absent item selections do
not produce cross-joined child rows. A document disappearing from this item
relation does not mean it was absent from the input table.

```sql
SELECT
  d.document_id,
  j.item_no,
  j.sku,
  j.qty,
  j.unit_price
FROM
  j17_documents AS d
  LEFT JOIN LATERAL JSON_TABLE (d.payload, '$.items[*]' COLUMNS (item_no FOR ORDINALITY, sku text PATH '$.sku', qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, unit_price numeric(10, 2)
  PATH '$.price' ERROR ON EMPTY ERROR ON ERROR)) AS j ON true
ORDER BY
  d.document_id,
  j.item_no;
```

The LEFT form produces four rows: two actual items and one null-extended row
for each of documents two and three. A placeholder does not become an item.
Count the generated `item_no`, rather than `COUNT(*)`, to measure actual child
rows. Keep `document_id` visible throughout the investigation so a change in
grain cannot be hidden by projecting only SKU or price.

The ordered pair `(document_id,item_no)` identifies positions in this snapshot.
JSONB array extraction by integer uses a different, zero-based indexing
interface. Reordering an array changes positions, so ordinality alone is not a
durable external item identifier across versions.

### Worked case 2: Missing, null and malformed values have different policies

```sql
SELECT
  j.item_no,
  j.qty,
  j.qty_present
FROM
  JSON_TABLE ('{"items":[{"qty":null},{}]}', '$.items[*]' COLUMNS (item_no FOR ORDINALITY, qty integer PATH '$.qty' DEFAULT 1 ON EMPTY ERROR ON ERROR, qty_present boolean EXISTS PATH '$.qty')) AS j
ORDER BY
  j.item_no;
```

The result is `(1,NULL,true)` followed by `(2,1,false)`. The first field exists
but its JSON null becomes SQL NULL in the scalar quantity. The second path is
empty, so the declared default supplies one. Presence and scalar value answer
different questions.

The script separately supplies quantity text `two` under `ERROR ON ERROR` and
handles the actual PostgreSQL conversion error `22P02`. The reference also
demonstrates `NULL ON ERROR`, which deliberately returns an unknown quantity
instead. Neither policy authorizes treating malformed text as zero. A caller
must know whether the resulting row is eligible for a complete business total.

## Preserve coverage when aggregating

The practice fixture adds document four with R at price seven and explicit null
quantity, plus S at price two with omitted quantity. Under this contract S has
quantity one. The known partial line value is therefore two, while the complete
order value remains unknown because R's quantity is unknown.

For a fully known order the line calculation is \(\sum_i q_i p_i\), with item
quantities \(q_i\) and unit prices \(p_i\). SQL `SUM` ignores NULL inputs. It can
therefore return a plausible partial value while omitting an unknown item.
Compute unknown counts separately and gate the accepted total on coverage.

Document two's declared empty array can represent a known zero under the stated
contract. Document three's absent array does not establish the same fact.
Inspect the original document with field-presence and array-type checks before
using `COALESCE`. An outer join preserves a parent identity, but cannot recover
meaning that the source never supplied.

Shipping demonstrates another grain boundary. Document one's known line value
is thirteen and its parent shipping fee is four, so its complete value is
seventeen. Summing the repeated fee at two-item grain would produce twenty-one.
Aggregate child values to one row per document first, then add the single parent
fee. A typed projection does not prevent this relational multiplication error.

## Exercises

Keep each supplied savepoint rollback and write the answer inside its slot.

1. **Prediction:** Compare CROSS and LEFT expansion for document IDs one through three.
   **Inputs:** For sql-json-01 Exercise 1, inspect document IDs 1, 2 and 3 in j17_practice_documents. They contain two items, an empty items array and an absent items field respectively.
   **Expected result/shape:** For sql-json-01 Exercise 1, cROSS yields two item rows; LEFT yields four outer-preserving rows. Display document_id, item_no, sku ordered by document_id, item_no. Actual child identity is (document_id,item_no); documents 2 and 3 have NULL item positions in the LEFT result.
   **Verify:** For sql-json-01 Exercise 1, count non-NULL item_no independently and inspect the original field presence and type. A preserved outer placeholder is not an item, and empty and absent arrays are different source states.
2. **Query writing:** Produce all typed actual item rows from the four-document practice fixture.
   **Inputs:** For sql-json-01 Exercise 2, project every declared items array in the four-document fixture. Missing qty defaults to one, explicit JSON null remains unknown, and prices use the declared exact numeric type.
   **Expected result/shape:** For sql-json-01 Exercise 2, display document_id, item_no, sku, qty, unit_price ordered by document_id, item_no as (1,1,P,2,5), (1,2,Q,1,3), (4,1,R,NULL,7), (4,2,S,1,2), one row per (document_id,item_no).
   **Verify:** For sql-json-01 Exercise 2, compare all projected values with the original array entries and assert four unique position pairs. R retains unknown quantity; S receives the declared absence default.
3. **Debugging:** Compare omitted quantity, JSON null and invalid quantity text under explicit policies.
   **Inputs:** For sql-json-01 Exercise 3, use the two-item worked literal with explicit JSON null and an omitted qty, then a separate literal whose qty is the text two.
   **Expected result/shape:** For sql-json-01 Exercise 3, for the two-item literal, display item_no, qty, qty_present ordered by item_no as (1,NULL,true), (2,1,false). Invalid text produces SQL NULL under NULL ON ERROR and SQLSTATE 22P02 under ERROR ON ERROR; each generated literal position is identified by item_no.
   **Verify:** For sql-json-01 Exercise 3, check presence separately from scalar value and catch only the intended conversion error. Neither policy permits silently converting a malformed quantity to zero revenue.
4. **Verification:** Count real items and unknown quantities while retaining every document.
   **Inputs:** For sql-json-01 Exercise 4, use a LEFT JSON_TABLE relation for all four source documents and count only generated item positions when measuring item or unknown-quantity rows.
   **Expected result/shape:** For sql-json-01 Exercise 4, display document_id, item_count, unknown_qty_count ordered by document_id as (1,2,0), (2,0,0), (3,0,0), (4,2,1), one row per document_id.
   **Verify:** For sql-json-01 Exercise 4, compare actual position counts with source array lengths. COUNT(*) would count an outer placeholder; unknown quantities count only rows with a non-NULL item_no.
5. **Query writing:** Report known partial line value and a separately accepted complete order value.
   **Inputs:** For sql-json-01 Exercise 5, use all four documents, one declared currency and the worked missing-qty policy. Preserve array presence/type and unknown item counts before accepting an order total.
   **Expected result/shape:** For sql-json-01 Exercise 5, display document_id, known_line_value, accepted_order_value, coverage_state ordered by document_id, one row per document_id. Accepted values are 13, 0, NULL, NULL; document 4 has known partial value 2 and incomplete coverage.
   **Verify:** For sql-json-01 Exercise 5, compare each item contribution and unknown count with the displayed line values before checking the coverage CASE. Document 3 lacks its array, document 4 has an unknown quantity, and a partial SUM must not become a complete accepted amount.
6. **Extension:** Add document-level shipping once after child aggregation.
   **Inputs:** For sql-json-01 Exercise 6, use accepted child totals and one shipping_fee from each original document. Aggregate child rows to document grain before adding the parent amount.
   **Expected result/shape:** For sql-json-01 Exercise 6, display document_id, accepted_total ordered by document_id as (1,17), (2,0), (3,NULL), (4,NULL), one row per document_id.
   **Verify:** For sql-json-01 Exercise 6, assert the deliberately incorrect output value 21 for document 1 when its fee is repeated at item grain, then assert accepted output 17 charges the parent fee four exactly once.

## Common pitfalls

Counting LEFT placeholders inflates item counts. Applying a default to every
NULL erases the distinction between omitted and explicitly unknown quantities.
Converting errors to NULL and then summing can hide rejected measurements.
Adding a parent amount to every child row repeats that amount.

Inspect document IDs, generated positions, scalar types, presence flags and
coverage counts before accepting aggregates. Use the full script's deliberate
transaction boundary while experimenting. On an unexpected error, preserve the
first diagnostic and restore the exercise savepoint rather than changing error
policies merely to obtain a numeric result.

## Self-check

- State the row identity and count in the original document table, CROSS item relation, LEFT relation and final document aggregate.
- Trace missing quantity, JSON null and malformed text through the declared policies. Explain which states establish a complete accepted amount.
- Reproduce seventeen versus the erroneous twenty-one for the parent shipping example, and show the independent item/presence evidence before adding the fee.

## Next step

Apply the resulting grain and coverage checks in [analytical query patterns](sql_analytics_01_query_patterns.md) when its prerequisites are met. Keep parent identity and completeness visible before calculating metrics. The [professional learning path](../README.md) lists the related operational and modelling routes.

## Further reading

- [PostgreSQL 17 SQL/JSON and JSON_TABLE](https://www.postgresql.org/docs/17/functions-json.html)
- [PostgreSQL 17 table expressions and LATERAL](https://www.postgresql.org/docs/17/queries-table-expressions.html)
- [PostgreSQL 17 aggregate functions](https://www.postgresql.org/docs/17/functions-aggregate.html)

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning to coach me through sql-json-01: PostgreSQL 17 JSON_TABLE: Typed Projection and Result Grain.
Read sql/professional/companion-guides/sql_json_01_json_table.md and sql/professional/lessons/sql_json_01_json_table.sql. Direct prerequisites: sql-types-01 and sql-deep-02.
Explain JSON row paths, typed columns, ordinality, missing/null/error policies, outer-row preservation and parent/child grain. Ask me to predict exact rows and values before my attempt, give progressive hints, review my evidence, then ask retrieval questions in my own words.
Do not read solutions/ until I ask or have attempted the relevant exercise. Use only the disposable advanced_sql_training PostgreSQL 17 database; keep the savepoint and final ROLLBACK boundaries. I use the unified classroom Whole SQL lesson (psql) mode.
Done when I can show exact item rows, preserve all parent identities, report incomplete quantities without inventing totals and add a parent fee once at the correct grain.
```

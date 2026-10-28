## A join has a multiplicity contract

A join is not simply a lookup that attaches one value to every row. If a left key
appears \(n_k\) times and a matching right key appears \(m_k\) times, an inner
join contributes \(n_km_k\) combinations for that key. This multiplicity is
central to analytics because an unintended duplicate dimension can multiply
revenue, event counts or training examples without producing a syntax error.

A left join also retains unmatched left rows, with missing values for right-side
columns. SQL null equality is different from ordinary equality between present
values: `NULL = NULL` is not true. A query that needs null-safe matching must say
so using an appropriate supported expression. The business meaning of a missing
key should be defined before choosing a null-safe join merely to make rows match.

This example uses real DataFusion SQL against registered Arrow inputs. The
fixtures are tiny, but they contain the structural cases that cause large-table
errors: unique matches, a missing dimension key, a duplicate right key, and a null
fact key. The expected result is derived from those relationships rather than
from an assumption that output count always equals input count.

## Worked case A: a valid many-to-one enrichment

The first case has three orders and a dimension with one row per known customer.
Two orders match a customer and one order has an unknown customer ID. A left join
returns all three orders, and the unknown customer's segment is null. Summing the
amount after the join gives the original total 20 because this dimension is
unique on its key.

The program checks that uniqueness explicitly before treating the operation as an
enrichment. A uniqueness check is not a universal property of a table name such
as customers. It is a property of the selected dataset and key, possibly further
qualified by effective date in a slowly changing dimension. Joining a historical
fact to every historical version of a customer would violate the intended
many-to-one relationship even if each version is individually valid.

Filtering the joined result to one segment introduces another choice. A `WHERE`
condition on the right-side segment removes unmatched rows because their segment
comparison is unknown rather than true. If the analytical question requires
retaining unknown customers, the query needs an explicit branch or different
placement of the condition. The join type alone does not guarantee that later
filters preserve its unmatched population.

## Worked case B: one duplicate changes the total

The second case adds another dimension row for customer 1. The order for that
customer now matches twice. The joined total rises from 20 to 24, and the row count
rises from 3 to 4. The engine is following the requested join semantics; it has not
invented revenue. The application supplied a dimension that violates the intended
key constraint.

An inner join would hide the unknown customer rather than solve this problem.
The duplicate still multiplies its match, while the unmatched fact disappears.
Both effects can accidentally cancel in a total, which is why testing only the
final aggregate is insufficient. The program checks row identities and expected
multiplicity as well as sums. A count can expose a structural error even when a
particular numeric column happens to contain zero.

A separate null-key example contrasts ordinary equality with `IS NOT DISTINCT
FROM`. The latter can match two missing keys, but that is not automatically a
valid business rule. Missing customer identifiers might represent unrelated
unknown people. Treating all of them as one customer can create a large and
misleading many-to-many group. The code demonstrates the SQL mechanism while
the prose keeps its interpretation explicit.

## Mistakes, controls and diagnosis

Before enrichment, define the required key uniqueness and record how unmatched
facts are handled. After joining, compare input and output counts, unmatched
counts and key multiplicities. For temporal dimensions, include the effective
interval and a rule for overlapping versions. Do not use `DISTINCT` as a general
repair for a multiplied join: it can remove legitimate repeated facts while
concealing the source constraint failure.

**Interview discussion: why can a join produce correct SQL and incorrect metrics?**
SQL specifies combinations of rows under its predicates. The intended metric may
require a many-to-one mapping, a temporal lookup or a preserved unmatched group.
Those additional assumptions must be expressed or validated. The worked cases
show both a valid enrichment and a deliberate constraint violation, with an
independent count/sum oracle that makes the difference visible.

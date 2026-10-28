## A join changes the row relationship

A join combines rows according to keys. Its result depends on key multiplicities, not merely on which key values are present. If one left row matches two right rows, that left row appears twice in an ordinary matching result. Summing a left-side measurement after the join can therefore inflate its total.

Define the grain of both inputs and the intended output. A one-to-one relationship needs uniqueness on both sides. A many-to-one relationship needs a unique lookup key on the lookup side. A many-to-many relationship may be legitimate, but its output multiplicity must be understood rather than treated as an accidental implementation detail.

DataFrames can validate key uniqueness during a join. That check does not prove the key is semantically correct, but it makes a declared cardinality assumption executable. Missing keys also need an explicit policy, especially when transferring habits from SQL's NULL semantics.

## Worked case A: expose and repair fanout

The left table has two entities with weights 100 and 200. The right table has two observations for entity 1. An ordinary left join repeats the first weight and changes the summed weight to 400. Requiring a unique right key rejects that join. Aggregating the right table to one row per entity before joining retains two entity rows and the original weight total 300.

{{WORKED_A}}

## Worked case B: missing-key policy

The second example includes a missing key in each input. The default explicit error prevents an implicit assumption about matching unknown identities. Choosing `matchmissing=:equal` deliberately joins those missing keys, while `:notequal` excludes them from matching. These policies have different meanings and should not be chosen only to eliminate an error message.

{{WORKED_B}}

## Validate before and after the join

Check key types, uniqueness, missingness and intended multiplicity before merging. Afterward, reconcile row counts, matched/unmatched keys and important totals. A syntactically valid join can still use the wrong date, tenant or entity level. A compound key should include every dimension needed to identify the relationship.

Aggregation before a join is appropriate only when it matches the intended question. Summing right-side observations may be meaningful for an entity total but wrong for a latest-value lookup. Temporal joins additionally need availability-time and tie-breaking rules, addressed in a later unit.

## Diagnose a plausible wrong total

A result can look reasonable while double-counting observations. Construct a tiny duplicate-key fixture and trace the exact output pairs. Do not use a blanket distinct operation to hide fanout without deciding which rows should be retained and why. Removing duplicates after aggregation can preserve the wrong arithmetic.

When missing keys are matched as equal, every missing row can match other missing rows and create additional fanout. The policy is not a declaration that all unknown entities are the same entity. Retain rejected and unmatched counts so downstream analyses can assess the effect of exclusions.

The programs demonstrate real joins with the prepared DataFrames package. Their checks establish specific cardinality and reconciliation properties on authored inputs. They do not validate an external data model or justify every preaggregation rule. Preserve the declared grains and relation when extending the example.

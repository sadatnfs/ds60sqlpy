# julia-016: Joins, key validation and duplicate fanout

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-015`.

Validate relational assumptions in DataFrames joins and reconcile totals before and after a merge.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A join changes the row relationship

A join combines rows according to keys. Its result depends on key multiplicities, not merely on which key values are present. If one left row matches two right rows, that left row appears twice in an ordinary matching result. Summing a left-side measurement after the join can therefore inflate its total.

Define the grain of both inputs and the intended output. A one-to-one relationship needs uniqueness on both sides. A many-to-one relationship needs a unique lookup key on the lookup side. A many-to-many relationship may be legitimate, but its output multiplicity must be understood rather than treated as an accidental implementation detail.

DataFrames can validate key uniqueness during a join. That check does not prove the key is semantically correct, but it makes a declared cardinality assumption executable. Missing keys also need an explicit policy, especially when transferring habits from SQL's NULL semantics.

## Worked case A: expose and repair fanout

The left table has two entities with weights 100 and 200. The right table has two observations for entity 1. An ordinary left join repeats the first weight and changes the summed weight to 400. Requiring a unique right key rejects that join. Aggregating the right table to one row per entity before joining retains two entity rows and the original weight total 300.

```julia
using Test
using DataFrames

function worked_a()
    entities = DataFrame(id = [1, 2], weight = [100, 200])
    observations = DataFrame(id = [1, 1], value = [10, 20])
    duplicated = leftjoin(entities, observations; on = :id)
    @test nrow(duplicated) == 3
    @test sum(duplicated.weight) == 400
    @test_throws ArgumentError leftjoin(entities, observations; on = :id, validate = (true, true))
    totals = combine(groupby(observations, :id), :value => sum => :value_total)
    reconciled = leftjoin(entities, totals; on = :id, validate = (true, true))
    @test nrow(reconciled) == 2
    @test sum(reconciled.weight) == 300
    @test sum(skipmissing(reconciled.value_total)) == 30
    println("Reconciled entity table: ", reconciled)
end

worked_a()
```

## Worked case B: missing-key policy

The second example includes a missing key in each input. The default explicit error prevents an implicit assumption about matching unknown identities. Choosing `matchmissing=:equal` deliberately joins those missing keys, while `:notequal` excludes them from matching. These policies have different meanings and should not be chosen only to eliminate an error message.

```julia
using Test
using DataFrames

function worked_b()
    left = DataFrame(id = [1, missing], label = ["known", "unknown"])
    right = DataFrame(id = [missing, 2], value = [7, 8])
    @test_throws ArgumentError innerjoin(left, right; on = :id)
    equal = innerjoin(left, right; on = :id, matchmissing = :equal)
    unequal = innerjoin(left, right; on = :id, matchmissing = :notequal)
    @test nrow(equal) == 1 && ismissing(equal.id[1])
    @test nrow(unequal) == 0
    println("Explicit missing-key matches: ", nrow(equal), "; excluded matches: ", nrow(unequal))
end

worked_b()
```

## Validate before and after the join

Check key types, uniqueness, missingness and intended multiplicity before merging. Afterward, reconcile row counts, matched/unmatched keys and important totals. A syntactically valid join can still use the wrong date, tenant or entity level. A compound key should include every dimension needed to identify the relationship.

Aggregation before a join is appropriate only when it matches the intended question. Summing right-side observations may be meaningful for an entity total but wrong for a latest-value lookup. Temporal joins additionally need availability-time and tie-breaking rules, addressed in a later unit.

## Diagnose a plausible wrong total

A result can look reasonable while double-counting observations. Construct a tiny duplicate-key fixture and trace the exact output pairs. Do not use a blanket distinct operation to hide fanout without deciding which rows should be retained and why. Removing duplicates after aggregation can preserve the wrong arithmetic.

When missing keys are matched as equal, every missing row can match other missing rows and create additional fanout. The policy is not a declaration that all unknown entities are the same entity. Retain rejected and unmatched counts so downstream analyses can assess the effect of exclusions.

The programs demonstrate real joins with the prepared DataFrames package. Their checks establish specific cardinality and reconciliation properties on authored inputs. They do not validate an external data model or justify every preaggregation rule. Preserve the declared grains and relation when extending the example.


## Six investigations

### 1. Trace the duplicate pair

Join the duplicated right-side entity 1 observations.

**Expected:** The left entity 1 weight appears twice.

**Hint:** Enumerate the matching row pairs.

### 2. Enforce a lookup contract

Require uniqueness on the right lookup key.

**Expected:** The duplicate-key input is rejected.

**Hint:** Use the join validation option.

### 3. Aggregate at a declared grain

Sum observations to one row per entity before the join.

**Expected:** Two entity rows and weight total 300 are preserved.

**Hint:** Choose an aggregation that matches the analytical question.

### 4. Choose missing-key behavior

Compare equal and nonmatching missing-key policies.

**Expected:** The fixture yields 1 or 0 matched rows.

**Hint:** Unknown keys do not imply identical entities.

### 5. Inspect unmatched keys

Use an outer join with an origin indicator.

**Expected:** The fixture exposes left-only, both and right-only rows.

**Hint:** Retain mismatch evidence.

### 6. Avoid cosmetic deduplication

Remove duplicate output rows without reviewing their cause.

**Expected:** The scientific meaning remains unresolved.

**Hint:** Reconcile the intended input/output grain first.

## Primary references

- [DataFrames join contracts](https://dataframes.juliadata.org/stable/man/joins/)
- [Existing SQL bag reasoning](../../../sql/professional/README.md)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

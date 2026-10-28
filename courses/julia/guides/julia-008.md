# julia-008: Tuples, named records, dictionaries and sets

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-004`, `julia-007`.

Choose collection representations according to identity, ordering, mutability and lookup needs.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A collection has a contract beyond its contents

A tuple is an immutable ordered collection whose element types can differ. A named tuple adds field names, making a small record easier to interpret. A dictionary maps keys to values, while a set records membership. These structures answer different questions and should not be selected only because they can all hold several values.

A one-element tuple needs a trailing comma to distinguish it from parentheses around an expression. Named tuples expose fields by name as well as position. Their field names and order are part of their type, which can support clear small record interfaces. They do not automatically make nested mutable values immutable.

Dictionary iteration order should not be used as an implicit scientific ordering rule. Sort keys or construct an explicit ordering when a report, comparison or serialization needs one. Missing keys also require a policy: lookup can fail, a default can be supplied, or a value can be inserted deliberately.

## Worked case A: a record with explicit fields

The first example groups a request ID, a score and an eligibility flag in a named tuple. It checks named access and destructures an ordinary tuple. A small returned record can be clearer than a positional vector whose columns must be remembered by the caller.

```julia
using Test

function worked_a()
    record = (id = "q1", score = 0.8, eligible = true)
    @test record.id == "q1"
    @test record.score == 0.8
    @test propertynames(record) == (:id, :score, :eligible)
    left, right = (2, 3)
    @test left + right == 5
    @test (7,) isa Tuple
    println("Named record: ", record)
end

worked_a()
```

## Worked case B: count categories and inspect membership

The dictionary example counts repeated categories with an explicit zero default. It then sorts the keys before presentation. A set removes duplicates for a membership question, which is different from counting their frequency. The program retains both views so deduplication cannot silently change the counting task.

```julia
using Test

function worked_b()
    counts = Dict{String,Int}()
    for label in ["b", "a", "b"]
        counts[label] = get(counts, label, 0) + 1
    end
    @test counts == Dict("a" => 1, "b" => 2)
    @test sort(collect(keys(counts))) == ["a", "b"]
    @test Set(["b", "a", "b"]) == Set(["a", "b"])
    println("Ordered counts: ", [(key, counts[key]) for key in sort(collect(keys(counts)))])
end

worked_b()
```

## Keys and equality

Dictionaries use an equality/hash contract that treats certain special values differently from ordinary numerical `==`. The earlier equality lesson introduced `isequal`. A NaN key can therefore be retrieved consistently, while signed zeros can remain distinct keys. This behavior is useful only when it matches the meaning assigned to those keys.

A mutable object used as a key can be difficult to reason about if its equality or hash-relevant state changes after insertion. Prefer stable identifiers for records and keep measurements as values. A row's current position is not a stable identifier when the dataset can be reordered.

## Diagnose a collection choice

If counts change after a conversion to a set, ask whether multiplicity was meaningful. If a report changes ordering between environments, inspect whether it relied on dictionary traversal. If a missing key is treated as zero, confirm that absent and observed-zero are interchangeable for that metric. They often are not.

A named tuple is well suited to a small fixed record, while a DataFrame later supplies a columnar table interface. Neither removes the need for a declared schema, units and missingness policy. Use the representation that makes the intended operations and invariants clear.

The examples check tuple syntax, record access, category counts, stable presentation and special-key behavior. They do not establish a universal speed ranking among structures. Later type and performance lessons explain how concrete element types and access patterns interact with compilation and allocation.


## Six investigations

### 1. Make one tuple element

Represent a single integer as a tuple.

**Expected:** Use(7,), including its comma.

**Hint:** Parentheses alone group an expression.

### 2. Name a returned record

Return an ID, score and eligibility field.

**Expected:** Callers can access fields by their names.

**Hint:** Prefer explicit semantic labels to remembered positions.

### 3. Preserve multiplicity

Count labels a,b,b before converting to a set.

**Expected:** Counts are 1 and 2 while the set has two distinct labels.

**Hint:** Frequency and membership are different questions.

### 4. Control presentation order

Print a dictionary in an explicitly sorted key order.

**Expected:** The report follows the chosen ordering rule.

**Hint:** Do not depend on traversal order.

### 5. Separate absent and zero

Compare a present zero-valued key with an absent key.

**Expected:** haskey distinguishes them.

**Hint:** A default value can conceal missingness.

### 6. Inspect special keys

Use NaN and both signed zeros as dictionary keys.

**Expected:** NaN is retrievable and the signed zeros remain distinct in this fixture.

**Hint:** Use the data-key equality contract.

## Primary references

- [Julia collections](https://docs.julialang.org/en/v1/base/collections/)
- [Named tuples and functions](https://docs.julialang.org/en/v1/manual/functions/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

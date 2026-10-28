# julia-015: DataFrames transformations and grouped summaries

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-013`, `julia-014`.

Transform a typed table and compute grouped summaries while preserving names, missingness and row counts.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A table needs a schema and a grain

A DataFrame organizes named columns into rows. Its grain states what one row represents. Column names and element types are useful schema information, but a table also needs semantic contracts such as unique request IDs, units and missingness rules. DataFrames does not infer those scientific meanings automatically.

Selection chooses columns or creates derived ones. A row-wise transformation applies a function to corresponding values from each row, while a column transformation receives a whole column. `ByRow` makes that distinction explicit. Grouping creates subsets for an aggregation rule; it does not itself decide whether groups should receive equal weights in a later scientific summary.

Indexing conventions affect copying. A selected column accessed with `!` can share its storage, while ordinary copied-column selection can provide a separate vector. Learn the documented contract and test caller-visible mutation rather than assuming that every table expression creates a snapshot.

## Worked case A: select and transform named columns

The first example retains a request ID and derives a scaled score. It explicitly requests copied columns for the selected output. A separate alias/copy trace shows why mutating a directly shared score column changes the source table. The resulting names and values are checked exactly.

```julia
using Test
using Statistics
using DataFrames

function observed_mean(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Finite scores required"))
    return isempty(observed) ? missing : mean(observed)
end

function worked_a()
    input = DataFrame(id = [1, 2, 3], score = [10, 20, 30])
    selected = select(input, :id, :score => ByRow(x -> x / 10) => :scaled; copycols = true)
    @test names(selected) == ["id", "scaled"]
    @test selected.scaled == [1, 2, 3]
    alias = input[!, :score]
    snapshot = input[:, :score]
    alias[1] = 99
    @test input.score[1] == 99
    @test snapshot[1] == 10
    println("Selected table: ", selected)
end

worked_a()
```

## Worked case B: summarize with missingness counts

The grouped example has two groups and one missing score. Each output group reports total rows, observed scores and the observed-value mean. Sorting group keys makes presentation deterministic. A mean alone would hide the difference between one observed score and two observed scores.

```julia
using Test
using Statistics
using DataFrames

function observed_mean(values)
    observed = collect(skipmissing(values))
    all(isfinite, observed) || throw(DomainError(observed, "Finite scores required"))
    return isempty(observed) ? missing : mean(observed)
end

function worked_b()
    input = DataFrame(group = ["a", "a", "b", "b"], score = [1, missing, 3, 5])
    summary = combine(
        groupby(input, :group; sort = true),
        nrow => :n_rows,
        :score => (x -> count(v -> !ismissing(v), x)) => :n_observed,
        :score => observed_mean => :mean_score,
    )
    @test summary.group == ["a", "b"]
    @test summary.n_rows == [2, 2]
    @test summary.n_observed == [1, 2]
    @test summary.mean_score == [1.0, 4.0]
    println("Grouped summary: ", summary)
end

worked_b()
```

## Whole-column and row-wise functions

A vector-valued function and a scalar row function have different shape contracts. Broadcasting a function over a column is not the same as passing the whole column to an aggregation. Inspect small outputs and names before assigning a derived field to a larger pipeline.

Keep original columns when they are needed for lineage or diagnosis. A chain of transformations should make it possible to reconstruct rejected rows and the meaning of each derived value. Reusing a familiar column name for a different unit or population creates a semantic error even if the code is valid.

## Diagnose a grouped result

Check input counts, group keys, missingness and the aggregation denominator. An all-missing group needs an explicit result policy. If later code averages group means, decide whether it should weight groups equally or by their relevant observation counts. Both can be meaningful but answer different questions.

A table transformation is not proof that data have the intended grain. Validate identifiers and join assumptions before aggregating. The next unit demonstrates how a many-to-many join can inflate totals while producing a well-formed DataFrame.

The examples use the prepared DataFrames package and small literal tables. No external file or service is read. They establish the stated indexing and transformation contracts, not a general claim that a particular chain is statistically valid or optimized for a large dataset.


## Six investigations

### 1. Name the derived field

Scale the score column by 10 using ByRow.

**Expected:** The output column contains 1,2,3 under the explicit name scaled.

**Hint:** Choose row-wise application deliberately.

### 2. Observe a shared column

Mutate input[!, :score].

**Expected:** The source DataFrame changes.

**Hint:** The indexing operation can return the stored column.

### 3. Retain a column snapshot

Copy the column before later source mutation.

**Expected:** The copied values remain unchanged.

**Hint:** Check identity and content separately.

### 4. Report group coverage

Summarize the group containing one missing score.

**Expected:** It reports 2 rows,1 observed score and mean 1.

**Hint:** A mean alone hides the denominator.

### 5. Handle an all-missing group

Apply observed_mean to only missing values.

**Expected:** The result is missing.

**Hint:** An empty observed set needs a stated policy.

### 6. Interpret a mean of means

Average the two group means with and without count weights.

**Expected:** The answers can differ.

**Hint:** State the target weighting.

## Primary references

- [DataFrames transformations](https://dataframes.juliadata.org/stable/man/split_apply_combine/)
- [DataFrames indexing](https://dataframes.juliadata.org/stable/lib/indexing/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

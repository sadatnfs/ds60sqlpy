# julia-005: Loops, ranges, comprehensions and scope

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-004`.

Trace finite iteration and scope rules while using explicit empty-input and indexing policies.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Iteration follows a collection contract

A loop visits values supplied by an iterable. A range can describe many values without storing a full array, while a comprehension constructs a collection from an iteration rule. A generator can feed a reduction without first materializing every result. These choices affect representation and memory, not just syntax.

Julia's ordinary ranges include their endpoint when the step reaches it. A descending range needs a negative step. An empty range can be valid and produce no iterations. Standard arrays use one-based indices, but generic algorithms should use `eachindex` or `axes` rather than assuming that every possible array type shares the same index origin.

A loop counter is not automatically a request ID or a data key. Keep positions distinct from identities when processing records. Reordering a dataset should not silently change the meaning of an identifier used for joins or evaluation.

## Worked case A: accumulate inside a function

The first helper sums a bounded range and handles an empty range naturally. The accumulator is local to the function. This avoids the soft-scope ambiguity that can surprise learners when a loop assigns to a global name in a script. Interactive REPL convenience rules are not a reliable model for every source-file execution context.

```julia
using Test

function sum_range(values)
    total = 0
    for value in values
        total += value
    end
    return total
end

function worked_a()
    @test sum_range(1:5) == 15
    @test sum_range(1:0) == 0
    @test collect(3:-1:1) == [3, 2, 1]
    println("Range sum: ", sum_range(1:5))
end

worked_a()
```

## Worked case B: transform and filter explicitly

The second case compares a comprehension with a generator reduction. It squares only the positive inputs. The selection predicate and transformation are visible in the expression. A separate enumeration example pairs each position with its value without treating the value as an index.

```julia
using Test

function sum_range(values)
    total = 0
    for value in values
        total += value
    end
    return total
end

function worked_b()
    values = [-2, 0, 3, 4]
    squares = [value^2 for value in values if value > 0]
    reduced = sum(value^2 for value in values if value > 0)
    @test squares == [9, 16]
    @test reduced == 25
    @test collect(enumerate([10, 20])) == [(1, 10), (2, 20)]
    println("Selected squares: ", squares)
end

worked_b()
```

## Scope and mutation

A new local binding inside a function does not rewrite a caller's scalar binding. Mutating a shared array is a different operation, covered in the array lesson. When debugging a loop, inspect both the binding that changes and the object it refers to. Reusing a short name for several roles can make a state transition difficult to explain.

Use a function boundary for reusable calculations. It makes inputs and outputs explicit, reduces dependence on ambient global state and gives the compiler a clearer specialization boundary. This is a design principle, not a claim that every loop is automatically fast or that every global is forbidden.

## Diagnose boundary behavior

Check zero iterations, one iteration, a descending sequence and a rejected input. An off-by-one error can change a denominator or miss the final observation while producing plausible numbers. Inclusive range syntax should be matched to the intended mathematical index set. If the algorithm expects exactly three observations, verify that count rather than relying on a visual reading of the loop.

A materialized comprehension is useful when later code needs the collection repeatedly. A generator is useful when only a reduction is needed. Neither form validates the data by itself. A filter that removes invalid or missing rows should also record how many rows were removed and why.

The examples use tiny deterministic inputs so iteration can be checked by hand. They establish the declared transformations and scope behavior, not an overall performance ranking among loop, comprehension and broadcast styles. Later units measure allocations and compilation under controlled protocols.


## Six investigations

### 1. Count an inclusive range

List values from 1:3.

**Expected:** The range contains 1,2,3.

**Hint:** Check both endpoints.

### 2. Use zero iterations

Run the accumulator over 1:0.

**Expected:** The result is its initial zero.

**Hint:** An empty iterable performs no loop body.

### 3. Descend explicitly

Construct 3,2,1 as a range.

**Expected:** Use 3:-1:1.

**Hint:** Specify the step direction.

### 4. Keep identity separate

Enumerate values 10 and 20.

**Expected:** Positions are 1 and 2; values remain 10 and 20.

**Hint:** Do not use a data value as an array index accidentally.

### 5. Avoid an unnecessary collection

Compute only the sum of selected squares.

**Expected:** A generator can supply the reduction directly.

**Hint:** Ask whether the intermediate array is needed later.

### 6. Trace scope

Move a reusable accumulation into a function with explicit input.

**Expected:** Its local state is recreated on every call.

**Hint:** Compare the function boundary with ambient script globals.

## Primary references

- [Julia control flow](https://docs.julialang.org/en/v1/manual/control-flow/)
- [Julia scope](https://docs.julialang.org/en/v1/manual/variables-and-scoping/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

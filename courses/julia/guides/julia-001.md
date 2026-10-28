# julia-001: First Julia scripts, values and observable output

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: No previous Julia experience.

Run a complete Julia script, trace bindings and distinguish a computed value from printed output.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## The execution model

Julia evaluates expressions to values. A value has a type, such as an integer, floating-point number or string. A name is a binding to a value. Assignment changes that binding; it is not a mathematical equation that must remain true after later assignments. This distinction is the first tool for explaining what a program actually did.

The classroom executes a source file called `main.jl` in a fresh Julia process. It does not preserve variables from an earlier Run. Saving a source draft or note is separate from retaining a running interpreter. A script also differs from the interactive REPL: a bare expression can be displayed automatically in the REPL, while a script generally needs `println` or another output operation to make a result visible.

The examples group instructions inside a named function. `function` starts its definition and `end` closes it. Calling the name with parentheses performs the instructions. The `worked_a()` line at the bottom makes that call explicit. `@test` checks a stated expectation and causes failure if it is false. You will study functions and tests in more depth later; here they provide a clear starting point and visible correctness checks.

## Worked case A: trace a calculation

The program binds two counts, adds them, and prints both a label and the result. `println` inserts a newline after its arguments. The type check shows that the sum is an integer in this prepared environment. Printing a value does not change the value or certify that the numbers represent the intended real-world quantity.

```julia
using Test

function worked_a()
    accepted = 35
    rejected = 7
    total = accepted + rejected
    @test total == 42
    @test total isa Int
    println("Total records: ", total)
end

worked_a()
```

## Worked case B: rebinding a scalar

The second program assigns one integer binding to another, then rebinds the original name. The second name retains the earlier integer. This example concerns immutable scalar values; arrays and other mutable objects require the aliasing rules introduced later. Do not generalize this scalar trace into a claim that assignment always copies a whole object.

```julia
using Test

function worked_b()
    first_value = 5
    retained = first_value
    first_value = 9
    @test retained == 5
    @test first_value == 9
    println("Retained scalar: ", retained, "; rebound scalar: ", first_value)
end

worked_b()
```

## Read an error as evidence

A misspelled name produces an undefined-variable error. A type mismatch can produce a method error when no applicable method exists. Julia's error report points to a source location and stack of calls. Start at the first relevant line in your submitted code, reproduce the failure with small inputs, and compare it with the expected intermediate values. Repeatedly pressing Run without changing the explanation does not provide new evidence.

Julia compiles specialized code for operations and argument types as it is needed. A first call can include compilation work that a later call in the same process avoids. The classroom's fresh-process boundary therefore matters for timing. The initial startup or first function call is not a clean measurement of steady-state numerical throughput. Performance lessons later separate these costs.

## A reproducible first investigation

Keep source, inputs, expected observations and actual output together. Use small literal data initially so a result can be checked by hand. Add a changed input only after the original trace is understood. A passing assertion confirms the statement for those inputs; it does not establish a general proof or the correctness of an external dataset.

The worker supplies Julia and its prepared scientific packages. No host Julia installation is required for ordinary classroom use. An optional external project can use its own Julia installation and project manifest, but that is a separate environment with its own package and version checks. These lessons name the classroom contract so a learner can reproduce the examples without hidden REPL state.


## Six investigations

### 1. Change a count

Use accepted 20 and rejected 3.

**Expected:** The total is 23.

**Hint:** Change one input and recompute the arithmetic.

### 2. Keep a scalar snapshot

Bind y to x=4, then rebind x to 10.

**Expected:** y remains 4.

**Hint:** Trace bindings separately.

### 3. Print deliberately

Compare a bare arithmetic expression with println in a script.

**Expected:** Only explicit output is guaranteed to appear in the script transcript.

**Hint:** Separate computation from presentation.

### 4. Inspect a type

Compare typeof(2) and typeof(2.5).

**Expected:** They are the environment integer type and Float64.

**Hint:** A literal selects a representation.

### 5. Diagnose a name

Misspell a variable in an owned copy of the program.

**Expected:** An undefined-variable error identifies the failed name and source location.

**Hint:** Inspect the first relevant submitted line.

### 6. Explain first-call timing

Time a first and repeated call in one process.

**Expected:** Their costs can include different amounts of compilation.

**Hint:** The classroom starts a new process for each Run.

## Primary references

- [Julia getting started](https://docs.julialang.org/en/v1/manual/getting-started/)
- [Julia variables](https://docs.julialang.org/en/v1/manual/variables/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

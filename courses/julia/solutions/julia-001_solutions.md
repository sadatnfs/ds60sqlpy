# julia-001: explained reference

The executable reference is `julia-001_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Treat each script as a fresh top-to-bottom evaluation. Read the source values, follow which name points at which value after every assignment, and only count something as output when `println` or `print` writes it. Timing questions are answered inside one process, because the classroom starts a new one for every Run.

## 1. Change a count

The output follows the current source values. A previous Run does not supply hidden counts.

**Expected observation:** The total is 23.

**Why it holds here:** Twenty accepted plus three rejected is 23, and the script recomputes that sum from the literals currently in the file each time it runs.

**Plausible wrong approach:** Editing the numbers but trusting the transcript from the previous Run reports the old total, because nothing from that earlier process is carried into the new one.

**How to verify:** Change the two literals, press Run, and confirm the printed total equals the new sum; `@test 20 + 3 == 23` states it as an assertion.

## 2. Keep a scalar snapshot

Integers are immutable values; rebinding x does not rewrite the earlier value associated with y.

**Expected observation:** y remains 4.

**Why it holds here:** `y = x` makes `y` name the value 4. Assigning 10 to `x` afterward moves only the name `x`, so `y` still names 4.

**Plausible wrong approach:** Picturing `y` as a live link to the variable `x` predicts that `y` becomes 10, which treats names as storage cells rather than labels on values.

**How to verify:** Print both names after the rebinding and expect `x = 10` and `y = 4`; adding `@test y == 4` makes the snapshot permanent.

## 3. Print deliberately

The REPL has display behavior that is not equivalent to running a source file.

**Expected observation:** Only explicit output is guaranteed to appear in the script transcript.

**Why it holds here:** A bare `2 + 3` line inside `main.jl` is evaluated and then discarded, since script mode has no automatic display; `println(2 + 3)` writes 5.

**Plausible wrong approach:** Copying a REPL session into a file and expecting each result to echo leaves an empty transcript and a wrong belief that the line failed.

**How to verify:** Run a file containing only `2 + 3`, then one containing `println(2 + 3)`, and compare the two transcripts line by line.

## 4. Inspect a type

The type describes the value representation and available methods, not whether the value is scientifically meaningful.

**Expected observation:** They are the environment integer type and Float64.

**Why it holds here:** The literal `2` has no decimal point, so it is the platform integer, `Int64` on the 64-bit classroom runtime; `2.5` is a `Float64` literal.

**Plausible wrong approach:** Assuming every number is a float, as in some other languages, leads to `typeof(2) == Float64`, which is false and hides integer overflow behavior.

**How to verify:** Print `typeof(2)` and `typeof(2.5)`; the reference asserts `typeof(2.5) == Float64` among its exercise checks.

## 5. Diagnose a name

The diagnostic is evidence about a missing binding, not a reason to reinstall the runtime.

**Expected observation:** An undefined-variable error identifies the failed name and source location.

**Why it holds here:** Misspelling `accepted` as `acepted` leaves a name with no binding, so Julia raises `UndefVarError` and points at the line that used it.

**Plausible wrong approach:** Reinstalling packages or restarting the runtime after this error treats a typo as an environment fault; the message already names the unbound identifier.

**How to verify:** Introduce the typo in an owned copy, read the first stack frame for the file and line, fix the spelling and confirm the run passes.

## 6. Explain first-call timing

Report the timing protocol; a cold call is not interchangeable with steady-state performance.

**Expected observation:** Their costs can include different amounts of compilation.

**Why it holds here:** The first call compiles a method for its argument types, so `@time f(1)` on first use includes compilation that the second call in the same process skips.

**Plausible wrong approach:** Timing one call per Run and comparing it with a repeated call elsewhere mixes cold and warm measurements, since every classroom Run starts cold.

**How to verify:** Call `@time f(1)` twice inside one script and compare the reported allocations and time; report which call each number came from.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-001: all reference checks passed`:

```julia
function exercise_checks()
    @test 0 + 0 == 0
    @test 10 - 3 == 7
    @test 6 * 7 == 42
    @test typeof(2.5) == Float64
    @test string(42) == "42"
    @test sprint(print, "score=", 3) == "score=3"
end
```

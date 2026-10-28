# julia-001: explained reference

The executable reference is `julia-001_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Change a count

The output follows the current source values. A previous Run does not supply hidden counts.

**Expected observation:** The total is 23.

## 2. Keep a scalar snapshot

Integers are immutable values; rebinding x does not rewrite the earlier value associated with y.

**Expected observation:** y remains 4.

## 3. Print deliberately

The REPL has display behavior that is not equivalent to running a source file.

**Expected observation:** Only explicit output is guaranteed to appear in the script transcript.

## 4. Inspect a type

The type describes the value representation and available methods, not whether the value is scientifically meaningful.

**Expected observation:** They are the environment integer type and Float64.

## 5. Diagnose a name

The diagnostic is evidence about a missing binding, not a reason to reinstall the runtime.

**Expected observation:** An undefined-variable error identifies the failed name and source location.

## 6. Explain first-call timing

Report the timing protocol; a cold call is not interchangeable with steady-state performance.

**Expected observation:** Their costs can include different amounts of compilation.

# julia-006: Functions, keywords, closures and argument sharing

## Starting point and outcome

Beginner; approximately 90 minutes. Direct prerequisites: `julia-005`.

Write reusable functions with explicit contracts and distinguish local rebinding from mutation of a passed object.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A function describes a reusable transformation

A function receives arguments and returns a value. Julia permits several methods for one function name; later lessons explain dispatch. First focus on the contract: valid inputs, the returned result, mutation and failure behavior. Explicit `return` statements can make that contract easy to read even though Julia also returns the final expression of a function body.

Positional arguments are supplied by their position. Keyword arguments name a choice such as a scale or threshold. Defaults are part of the API and should not be used to hide an important scientific assumption. A caller should be able to determine which configuration produced a result.

Functions can also receive other functions. A closure captures bindings from its surrounding scope. This is useful for a parameterized transformation, but mutable captured state can make repeated calls depend on prior calls. Keep a pure transformation separate from a stateful accumulator when reproducibility matters.

## Worked case A: a small configurable transformation

The affine helper applies a scale and shift to an input. A factory returns a closure with a fixed scale. The program checks both paths and demonstrates passing a function to `map`. The output is the returned value; printing it is a separate step.

```julia
using Test

affine(x; scale = 1, shift = 0) = scale * x + shift
make_scaler(scale) = x -> scale * x

function rebind(values)
    values = [99]
    return values
end

function change_first!(values)
    isempty(values) && throw(ArgumentError("A first element is required"))
    values[1] = 99
    return values
end

function worked_a()
    @test affine(3; scale = 2, shift = 1) == 7
    double = make_scaler(2)
    @test double(4) == 8
    @test map(double, [1, 2, 3]) == [2, 4, 6]
    println("Configured function result: ", affine(3; scale = 2, shift = 1))
end

worked_a()
```

## Worked case B: rebinding and mutation are different

Function arguments use sharing semantics: a mutable object can be observed by both caller and callee. Assigning a new array to the local argument name does not change the caller's binding. Updating an element of the passed array changes that shared object. A trailing exclamation mark in a function name conventionally signals mutation; it is a naming convention, not compiler enforcement.

```julia
using Test

affine(x; scale = 1, shift = 0) = scale * x + shift
make_scaler(scale) = x -> scale * x

function rebind(values)
    values = [99]
    return values
end

function change_first!(values)
    isempty(values) && throw(ArgumentError("A first element is required"))
    values[1] = 99
    return values
end

function worked_b()
    values = [1, 2]
    replacement = rebind(values)
    @test values == [1, 2]
    @test replacement == [99]
    returned = change_first!(values)
    @test values == [99, 2]
    @test returned === values
    println("Caller-visible mutation: ", values)
end

worked_b()
```

## Validate at the appropriate boundary

A function that assumes a nonempty vector should state and check that precondition. A reusable numerical helper should also avoid unnecessarily restrictive types that prevent compatible numeric representations. Parametric and generic methods later make these tradeoffs explicit. Validation should protect a real invariant rather than merely duplicate every downstream operation.

Default arguments can create additional methods, while keyword choices are processed differently from positional dispatch. Do not infer dispatch behavior merely from a keyword's type. If an algorithm needs distinct positional representations, name those method contracts deliberately and test ambiguous cases.

## Diagnose stateful behavior

If two calls produce different results for apparently identical inputs, inspect captured mutable values, global state, randomness and mutation. Copying a reference to an array is not the same as copying its contents. A closure that updates a captured counter is useful when state is intended, but it should not masquerade as a pure scoring function.

Use small tests to compare returned values and caller-visible state before and after a call. For a mutating operation, document which argument changes and whether the return value aliases it. A function can be correct while surprising callers who assumed it was nonmutating.

The examples establish basic function and sharing behavior. They do not claim that every higher-order abstraction is allocation-free or that mutation is always preferable. Later performance units evaluate those questions under a declared workload and with the same semantic checks retained.


## Six investigations

### 1. Use defaults

Call affine on 5 without keywords.

**Expected:** The result is 5.

**Hint:** Inspect both default parameters.

### 2. Override one choice

Set shift=-2 for input 5.

**Expected:** The result is 3.

**Hint:** Unspecified keywords retain their defaults.

### 3. Build a closure

Create a scale 3 function and apply it to 2.

**Expected:** The result is 6.

**Hint:** The returned function retains its scale binding.

### 4. Trace a rebound argument

Call rebind on a caller array.

**Expected:** The caller array remains unchanged.

**Hint:** The local name is assigned another array.

### 5. Trace a mutated argument

Call change_first! on a nonempty vector.

**Expected:** Its first element becomes 99 and the returned object aliases it.

**Hint:** Compare identity as well as contents.

### 6. Reject an empty mutation

Call change_first! on an empty vector.

**Expected:** An explicit ArgumentError is raised.

**Hint:** State the first-element precondition.

## Primary references

- [Julia function arguments](https://docs.julialang.org/en/v1/manual/functions/)
- [Julia methods](https://docs.julialang.org/en/v1/manual/methods/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

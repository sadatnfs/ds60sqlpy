## A function describes a reusable transformation

A function receives arguments and returns a value. Julia permits several methods for one function name; later lessons explain dispatch. First focus on the contract: valid inputs, the returned result, mutation and failure behavior. Explicit `return` statements can make that contract easy to read even though Julia also returns the final expression of a function body.

Positional arguments are supplied by their position. Keyword arguments name a choice such as a scale or threshold. Defaults are part of the API and should not be used to hide an important scientific assumption. A caller should be able to determine which configuration produced a result.

Functions can also receive other functions. A closure captures bindings from its surrounding scope. This is useful for a parameterized transformation, but mutable captured state can make repeated calls depend on prior calls. Keep a pure transformation separate from a stateful accumulator when reproducibility matters.

## Worked case A: a small configurable transformation

The affine helper applies a scale and shift to an input. A factory returns a closure with a fixed scale. The program checks both paths and demonstrates passing a function to `map`. The output is the returned value; printing it is a separate step.

{{WORKED_A}}

## Worked case B: rebinding and mutation are different

Function arguments use sharing semantics: a mutable object can be observed by both caller and callee. Assigning a new array to the local argument name does not change the caller's binding. Updating an element of the passed array changes that shared object. A trailing exclamation mark in a function name conventionally signals mutation; it is a naming convention, not compiler enforcement.

{{WORKED_B}}

## Validate at the appropriate boundary

A function that assumes a nonempty vector should state and check that precondition. A reusable numerical helper should also avoid unnecessarily restrictive types that prevent compatible numeric representations. Parametric and generic methods later make these tradeoffs explicit. Validation should protect a real invariant rather than merely duplicate every downstream operation.

Default arguments can create additional methods, while keyword choices are processed differently from positional dispatch. Do not infer dispatch behavior merely from a keyword's type. If an algorithm needs distinct positional representations, name those method contracts deliberately and test ambiguous cases.

## Diagnose stateful behavior

If two calls produce different results for apparently identical inputs, inspect captured mutable values, global state, randomness and mutation. Copying a reference to an array is not the same as copying its contents. A closure that updates a captured counter is useful when state is intended, but it should not masquerade as a pure scoring function.

Use small tests to compare returned values and caller-visible state before and after a call. For a mutating operation, document which argument changes and whether the return value aliases it. A function can be correct while surprising callers who assumed it was nonmutating.

The examples establish basic function and sharing behavior. They do not claim that every higher-order abstraction is allocation-free or that mutation is always preferable. Later performance units evaluate those questions under a declared workload and with the same semantic checks retained.

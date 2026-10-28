## Iteration follows a collection contract

A loop visits values supplied by an iterable. A range can describe many values without storing a full array, while a comprehension constructs a collection from an iteration rule. A generator can feed a reduction without first materializing every result. These choices affect representation and memory, not just syntax.

Julia's ordinary ranges include their endpoint when the step reaches it. A descending range needs a negative step. An empty range can be valid and produce no iterations. Standard arrays use one-based indices, but generic algorithms should use `eachindex` or `axes` rather than assuming that every possible array type shares the same index origin.

A loop counter is not automatically a request ID or a data key. Keep positions distinct from identities when processing records. Reordering a dataset should not silently change the meaning of an identifier used for joins or evaluation.

## Worked case A: accumulate inside a function

The first helper sums a bounded range and handles an empty range naturally. The accumulator is local to the function. This avoids the soft-scope ambiguity that can surprise learners when a loop assigns to a global name in a script. Interactive REPL convenience rules are not a reliable model for every source-file execution context.

{{WORKED_A}}

## Worked case B: transform and filter explicitly

The second case compares a comprehension with a generator reduction. It squares only the positive inputs. The selection predicate and transformation are visible in the expression. A separate enumeration example pairs each position with its value without treating the value as an index.

{{WORKED_B}}

## Scope and mutation

A new local binding inside a function does not rewrite a caller's scalar binding. Mutating a shared array is a different operation, covered in the array lesson. When debugging a loop, inspect both the binding that changes and the object it refers to. Reusing a short name for several roles can make a state transition difficult to explain.

Use a function boundary for reusable calculations. It makes inputs and outputs explicit, reduces dependence on ambient global state and gives the compiler a clearer specialization boundary. This is a design principle, not a claim that every loop is automatically fast or that every global is forbidden.

## Diagnose boundary behavior

Check zero iterations, one iteration, a descending sequence and a rejected input. An off-by-one error can change a denominator or miss the final observation while producing plausible numbers. Inclusive range syntax should be matched to the intended mathematical index set. If the algorithm expects exactly three observations, verify that count rather than relying on a visual reading of the loop.

A materialized comprehension is useful when later code needs the collection repeatedly. A generator is useful when only a reduction is needed. Neither form validates the data by itself. A filter that removes invalid or missing rows should also record how many rows were removed and why.

The examples use tiny deterministic inputs so iteration can be checked by hand. They establish the declared transformations and scope behavior, not an overall performance ranking among loop, comprehension and broadcast styles. Later units measure allocations and compilation under controlled protocols.

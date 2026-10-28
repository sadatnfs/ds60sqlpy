## A condition needs a Boolean

Julia conditions use Boolean values. An integer count or an arbitrary object is not automatically treated as true merely because it is nonzero or nonempty. This forces a decision rule to say what it means: compare a count to zero, test whether a collection is empty, or apply a named predicate.

`if`, `elseif`, `else` and `end` organize branches. Short-circuit operators can prevent an unsafe second operation when the first condition already determines the result. Their order matters when an expression has side effects or requires a guard, such as validating a denominator before dividing.

An assignment binds a name; `==` compares values under equality methods. `===` tests a stricter identity-style relation, while `isequal` is designed for consistent data-key equality, including special floating-point values. These operations have different purposes. A later dictionary lesson relies on the same distinction.

## Worked case A: guard a computation

The first helper checks that a denominator is positive before calculating a rate. A zero denominator returns an explicit missing-result sentinel, `nothing`, rather than a misleading zero rate. A counter demonstrates that the second part of a false short-circuit expression is not executed.

{{WORKED_A}}

## Worked case B: NaN and signed zero

Floating-point NaN is not equal to itself under `==`, while `isequal` treats NaN keys consistently. Positive and negative zero compare equal under `==`, but `isequal` distinguishes them. A Boolean condition involving `missing` remains unknown and is not a valid `if` condition. The program checks these behaviors directly.

{{WORKED_B}}

## Missing information is not a false result

A missing measurement, an absent return value and a numerical NaN can represent different states. This lesson introduces the distinction; a later unit treats missing-value arrays and aggregation. Do not convert every unknown condition to false just to make a branch run. Decide whether the application should reject incomplete input, defer a decision or use an explicitly justified fallback.

A short-circuit guard should state an invariant. For example, check that a collection is nonempty before accessing its first element. Catching an indexing exception afterward may be appropriate at a boundary, but it should not conceal a violated data contract. Keep validation separate from the scientific question answered by the computation.

## Diagnose a decision rule

Trace the predicate, the chosen branch and any side effects. A returned zero can be a real numeric result, whereas `nothing` can mean that no valid result was produced. Tests should distinguish those states. Comparing strings or floating values also requires the appropriate representation and tolerance policy from earlier units.

Avoid relying on an implementation accident such as one container's current ordering or one numeric type's conversion rules. Express the condition needed by the algorithm. A clear predicate makes failures easier to explain and makes later changes to data representations less likely to alter behavior silently.

The programs establish Julia's Boolean and equality behavior on small authored cases. They do not choose a universal policy for missing information. A reliable data-science application records that policy and tests normal, boundary and rejected inputs explicitly.

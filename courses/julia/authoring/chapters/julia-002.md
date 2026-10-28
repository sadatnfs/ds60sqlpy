## Representation is part of the calculation

The written number, its stored representation and the scientific quantity are related but different. Julia's ordinary integer literals use a machine integer type in this environment. Floating-point literals such as `0.1` use a binary approximation. A rational literal such as `1//10` represents an exact ratio of integers when its numerator and denominator remain representable.

Arithmetic can promote inputs to a common representation. That convenience does not make every conversion lossless. Dividing two integers with `/` produces a floating-point result, while `div` performs integer division. A rational uses `//`. Select the operation that matches the intended question instead of inferring meaning from the appearance of the result.

Machine integers have finite ranges. Ordinary integer arithmetic can wrap around on overflow. A checked operation raises an error instead, while `BigInt` provides arbitrary-precision integer arithmetic subject to available memory. These are different contracts. A count or identifier should not silently become negative because its representation overflowed.

## Worked case A: checked and arbitrary-precision integers

The first example adds one to the maximum signed 8-bit integer. Ordinary arithmetic wraps to the minimum value; the checked operation raises `OverflowError`. The arbitrary-precision calculation produces the mathematical answer 128. The small representation makes a failure that also matters for large counters easy to see.

{{WORKED_A}}

## Worked case B: approximate and exact decimal-looking values

Binary floating point does not represent most decimal fractions exactly. The familiar 0.1 plus 0.2 calculation therefore differs slightly from 0.3. An approximate comparison uses an explicit tolerance, while rational arithmetic represents the intended decimal fractions exactly. More bits in `BigFloat` can reduce approximation error, but binary arbitrary precision is not the same as exact decimal arithmetic.

{{WORKED_B}}

## Tolerances have units and purpose

An absolute tolerance is measured in the units of the compared quantity. A relative tolerance scales with magnitude. Neither should be widened merely to make a failed test pass. Derive a useful bound from rounding, the numerical algorithm and the precision required by the scientific decision. Near zero, a purely relative comparison may be unsuitable.

A conversion from a previously rounded Float64 to BigFloat cannot recover the decimal value that was lost before conversion. Construct higher-precision values from the intended literal or string under an explicit precision policy. Keep that policy local and avoid changing shared precision during concurrent numerical work.

## Diagnosis and transfer

When a total looks wrong, inspect input types, promotion, overflow and the operation used. Integer division can discard a remainder intentionally; an accidental use of it can bias a later average. Floating-point values can also carry infinities or NaNs, which need explicit handling rather than an assumption that every arithmetic result is finite.

For exact money or identifiers, choose a representation and rounding policy deliberately. A financial-looking decimal is not automatically safe as Float64. For scientific computation, Float64 is often useful but still requires conditioning and error analysis. Later numerical lessons separate representation error from approximation and model error.

The programs verify specific representation boundaries on tiny inputs. They do not establish that arbitrary-precision arithmetic is always faster or preferable, nor that approximate equality proves two scientific procedures equivalent. Preserve the intended units and mathematical operation alongside the stored type.

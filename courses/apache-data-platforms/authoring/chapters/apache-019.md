## A function has types, effects and an optimization boundary

A user-defined function extends SQL with application-specific behavior. It must
specify input types, an output type and a volatility contract. In the prepared
DataFusion Python API, a scalar UDF receives Arrow arrays and returns an Arrow
array. This is a batch interface, not an instruction to call Python once for every
row. A Python loop inside that callback can nevertheless reintroduce substantial
per-element overhead and Python allocation.

Volatility describes assumptions the optimizer may make. An immutable function
returns the same output for the same arguments and has no changing external state.
A function that reads the current time, a mutable file or a remote API cannot
honestly claim that property. Incorrect metadata can make constant folding or
expression reuse change the meaning of a query. Type declarations also need to
match the arrays the callback actually accepts and returns.

The worked source registers an actual typed DataFusion UDF backed by an Arrow
compute kernel. It compares the result with a native SQL expression. That is
useful when learning the extension boundary, but a simple multiplication normally
belongs in the native expression because the engine can understand and optimize
it without crossing a Python callback boundary.

## Worked case A: a vectorized unit conversion

The fixture represents integer distances in meters and includes a missing value.
The UDF multiplies present values by 100 to obtain centimeters. Arrow's compute
kernel propagates the null, preserving unknown distance instead of inventing zero.
The program checks exact outputs \([100,2500,\mathrm{null}]\) and equality with
the native expression. Units are part of the schema contract even though both
columns have the same machine integer type.

Registering a function does not change the source table or materialize the result.
The query still goes through plan construction and execution. The function name
is a registered SQL identifier, while the callback receives typed arrays.
Understanding that distinction helps diagnose an unknown-function error separately
from an exception raised after execution reaches the callback.

For a production extension, define overflow behavior and accepted ranges. The
small fixture deliberately stays far from the integer limit. Converting an
unbounded integer quantity can require checked arithmetic, a wider type or a
decimal representation. A correct answer for three values is not a proof that
every input representable by int64 can be multiplied safely.

## Worked case B: missing data is not a zero measurement

A second function uses fill_null before multiplication, deliberately replacing
missing input with zero. Both functions are executable and correctly typed, but
they answer different questions. The difference matters in aggregate statistics:
zero can change a denominator, distribution or operational threshold whereas a
missing observation may be excluded or handled separately.

The example compares their outputs and counts present results. It then attempts
to invoke the numeric UDF with a string. The engine must reject the unsupported
signature rather than silently treat text as a distance. The diagnostic is printed
as a real query error, while the source table remains unchanged. The exact wording
can vary by release; the meaningful condition is the incompatible type boundary.

A deliberately named row-loop callback shows the alternative implementation and
checks semantic equality on present and missing values. It is not benchmarked as
universally slower by an invented number. The reason to prefer Arrow kernels is
that they express batch operations in the prepared native library, reducing Python
object conversion and exposing a clearer null/type contract. Performance still
needs representative measurements.

## Diagnosis and interview discussion

Prefer built-in SQL or Arrow expressions when they express the transformation.
Use a UDF for a real extension requirement and document purity, units, null
handling and return shape. Avoid network requests or package installation inside
a callback: they make retries, offline behavior and bounded execution difficult
to reason about. A function's output must remain within the classroom resource
and result-size limits.

**Interview discussion: why might a UDF prevent an optimization?** The optimizer
can reason about known native expressions, while a custom callback can hide its
semantics behind declared types and volatility. It cannot generally infer which
rows the function rejects or whether a predicate can move through it. These cases
make the extension contract visible and separate semantic correctness from an
unmeasured performance claim.

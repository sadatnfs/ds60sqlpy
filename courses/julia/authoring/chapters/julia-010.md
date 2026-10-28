## A type can carry a data contract

A composite type groups named fields. A constructor creates an instance and can enforce invariants before an invalid object enters the rest of a program. The field types describe representations; they do not, by themselves, establish units, ranges or scientific meaning.

An immutable `struct` prevents reassignment of its fields after construction. A `mutable struct` allows field updates. Neither choice automatically validates every future state. A mutable object may need methods that preserve its invariants, while an immutable object can still contain a mutable array that another reference can change.

Use a new type when it makes an important contract explicit. A small named tuple may suffice for a temporary record, while a domain type can give operations a clear dispatch target. Avoid creating elaborate type hierarchies before identifying the behaviors and invariants that require them.

## Worked case A: a measurement constructor

The measurement type stores a finite Float64 value and one of two declared unit symbols. Its inner constructor validates both choices and performs the conversion deliberately. An immutable instance cannot later have its value field rebound. The type does not automatically convert centimeters into meters; any conversion method needs its own stated rule.

{{WORKED_A}}

## Worked case B: mutable fields inside an immutable object

The second example contrasts a mutable counter with an immutable wrapper around a vector. The counter's integer field can change. The wrapper's vector binding cannot be reassigned, but its referenced vector contents can change. This is a concrete reason to distinguish object immutability from deep immutability.

{{WORKED_B}}

## Constructors and operations

An inner constructor controls creation through `new`; an outer constructor can supply convenience conversions or defaults. Each public construction route should preserve the intended invariant. Do not add a convenience path that bypasses a range or unit check without an explicit reason.

Methods for an owned type can make behavior clear: convert a unit, validate a state or compute a quantity. Extending an existing function for a type you own is different from changing behavior for unrelated external types. Later dispatch lessons discuss why broad extensions can interfere with other packages.

## Diagnose state changes

When an instance appears to change unexpectedly, inspect nested mutable fields and aliases. Copying an outer object may still share inner storage. If a stable scientific snapshot is required, define how it is copied or serialized and preserve its version. Immutability of one field binding is insufficient evidence that a complete analysis input cannot change.

A constructor check also cannot prove that the supplied value was measured correctly. It can reject nonfinite values and unsupported units, but calibration, sampling and interpretation remain separate scientific questions. Keep code-level validity and scientific validity distinct.

The examples use small owned types and exact tests. They establish construction and mutation behavior, not a claim that every domain concept should become a custom type or that immutable data is always faster. Later performance work examines actual representations and workloads while preserving these semantic contracts.

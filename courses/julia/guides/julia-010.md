# julia-010: Composite types, constructors and nested mutability

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-009`.

Use owned types to represent data contracts and distinguish immutable bindings from recursively immutable state.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A type can carry a data contract

A composite type groups named fields. A constructor creates an instance and can enforce invariants before an invalid object enters the rest of a program. The field types describe representations; they do not, by themselves, establish units, ranges or scientific meaning.

An immutable `struct` prevents reassignment of its fields after construction. A `mutable struct` allows field updates. Neither choice automatically validates every future state. A mutable object may need methods that preserve its invariants, while an immutable object can still contain a mutable array that another reference can change.

Use a new type when it makes an important contract explicit. A small named tuple may suffice for a temporary record, while a domain type can give operations a clear dispatch target. Avoid creating elaborate type hierarchies before identifying the behaviors and invariants that require them.

## Worked case A: a measurement constructor

The measurement type stores a finite Float64 value and one of two declared unit symbols. Its inner constructor validates both choices and performs the conversion deliberately. An immutable instance cannot later have its value field rebound. The type does not automatically convert centimeters into meters; any conversion method needs its own stated rule.

```julia
using Test

struct Measurement
    value::Float64
    unit::Symbol
    function Measurement(value::Real, unit::Symbol)
        stored = Float64(value)
        isfinite(stored) || throw(ArgumentError("Finite stored value required"))
        unit in (:m, :cm) || throw(ArgumentError("Supported unit required"))
        return new(stored, unit)
    end
end

mutable struct Counter
    value::Int
end

struct VectorRecord
    values::Vector{Int}
end

function worked_a()
    measurement = Measurement(2, :m)
    @test measurement.value == 2.0
    @test measurement.unit == :m
    @test_throws ArgumentError Measurement(NaN, :m)
    @test_throws ArgumentError Measurement(1, :unknown)
    @test_throws ErrorException measurement.value = 3.0
    println("Validated measurement: ", measurement)
end

worked_a()
```

## Worked case B: mutable fields inside an immutable object

The second example contrasts a mutable counter with an immutable wrapper around a vector. The counter's integer field can change. The wrapper's vector binding cannot be reassigned, but its referenced vector contents can change. This is a concrete reason to distinguish object immutability from deep immutability.

```julia
using Test

struct Measurement
    value::Float64
    unit::Symbol
    function Measurement(value::Real, unit::Symbol)
        stored = Float64(value)
        isfinite(stored) || throw(ArgumentError("Finite stored value required"))
        unit in (:m, :cm) || throw(ArgumentError("Supported unit required"))
        return new(stored, unit)
    end
end

mutable struct Counter
    value::Int
end

struct VectorRecord
    values::Vector{Int}
end

function worked_b()
    counter = Counter(0)
    counter.value += 1
    @test counter.value == 1
    record = VectorRecord([1, 2])
    record.values[1] = 9
    @test record.values == [9, 2]
    @test_throws ErrorException record.values = [0]
    println("Nested mutable values: ", record.values)
end

worked_b()
```

## Constructors and operations

An inner constructor controls creation through `new`; an outer constructor can supply convenience conversions or defaults. Each public construction route should preserve the intended invariant. Do not add a convenience path that bypasses a range or unit check without an explicit reason.

Methods for an owned type can make behavior clear: convert a unit, validate a state or compute a quantity. Extending an existing function for a type you own is different from changing behavior for unrelated external types. Later dispatch lessons discuss why broad extensions can interfere with other packages.

## Diagnose state changes

When an instance appears to change unexpectedly, inspect nested mutable fields and aliases. Copying an outer object may still share inner storage. If a stable scientific snapshot is required, define how it is copied or serialized and preserve its version. Immutability of one field binding is insufficient evidence that a complete analysis input cannot change.

A constructor check also cannot prove that the supplied value was measured correctly. It can reject nonfinite values and unsupported units, but calibration, sampling and interpretation remain separate scientific questions. Keep code-level validity and scientific validity distinct.

The examples use small owned types and exact tests. They establish construction and mutation behavior, not a claim that every domain concept should become a custom type or that immutable data is always faster. Later performance work examines actual representations and workloads while preserving these semantic contracts.


## Six investigations

### 1. Validate a unit

Attempt to construct a measurement with an unsupported unit.

**Expected:** Construction fails explicitly.

**Hint:** Check the invariant before new creates the object.

### 2. Inspect conversion

Construct a measurement from integer 1.

**Expected:** Its stored value is Float64.

**Hint:** The constructor chooses that representation.

### 3. Try field reassignment

Reassign a field of an immutable measurement.

**Expected:** The operation is rejected.

**Hint:** The struct field binding is fixed after construction.

### 4. Mutate nested storage

Change the vector inside VectorRecord.

**Expected:** Its contents can change despite the immutable outer struct.

**Hint:** The vector itself is mutable.

### 5. Create a snapshot

Copy the vector before storing it in another record.

**Expected:** Later source-vector mutation does not affect that copied vector.

**Hint:** Choose the required storage independence explicitly.

### 6. Review a convenience constructor

Add a constructor with a default unit in an owned copy.

**Expected:** It preserves the same validation contract.

**Hint:** Route convenience paths through validated construction.

## Primary references

- [Julia composite types](https://docs.julialang.org/en/v1/manual/types/)
- [Julia constructors](https://docs.julialang.org/en/v1/manual/constructors/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

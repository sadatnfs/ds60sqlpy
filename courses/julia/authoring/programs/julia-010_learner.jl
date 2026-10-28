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

# === EXAMPLE A ===
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

# Task 1: Attempt to construct a measurement with an unsupported unit.
# Task 2: Construct a measurement from integer 1.
# Task 3: Reassign a field of an immutable measurement.
# Task 4: Change the vector inside VectorRecord.
# Task 5: Copy the vector before storing it in another record.
# Task 6: Add a constructor with a default unit in an owned copy.

# Write your independent changes below.

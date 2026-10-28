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

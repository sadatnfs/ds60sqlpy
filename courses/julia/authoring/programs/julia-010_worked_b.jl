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

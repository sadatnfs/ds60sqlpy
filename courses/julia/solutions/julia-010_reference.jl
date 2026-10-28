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

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test typeof(Measurement(1, :cm)) == Measurement
    @test fieldtypes(Measurement) == (Float64, Symbol)
    @test_throws MethodError Measurement("1", :m)
    a = [1]
    record = VectorRecord(a)
    a[1] = 3
    @test record.values[1] == 3
    separate = VectorRecord(copy(a))
    a[1] = 4
    @test separate.values[1] == 3
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-010: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

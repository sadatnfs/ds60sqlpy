using Test

affine(x; scale = 1, shift = 0) = scale * x + shift
make_scaler(scale) = x -> scale * x

function rebind(values)
    values = [99]
    return values
end

function change_first!(values)
    isempty(values) && throw(ArgumentError("A first element is required"))
    values[1] = 99
    return values
end

# === EXAMPLE A ===
function worked_a()
    @test affine(3; scale = 2, shift = 1) == 7
    double = make_scaler(2)
    @test double(4) == 8
    @test map(double, [1, 2, 3]) == [2, 4, 6]
    println("Configured function result: ", affine(3; scale = 2, shift = 1))
end

# === EXAMPLE B ===
function worked_b()
    values = [1, 2]
    replacement = rebind(values)
    @test values == [1, 2]
    @test replacement == [99]
    returned = change_first!(values)
    @test values == [99, 2]
    @test returned === values
    println("Caller-visible mutation: ", values)
end

# === EXERCISES ===
function exercise_checks()
    @test affine(5) == 5
    @test affine(5; shift = -2) == 3
    @test make_scaler(3)(2) == 6
    @test map(x -> x + 1, [0, 1]) == [1, 2]
    @test_throws ArgumentError change_first!(Int[])
    original = [1]
    replacement = rebind(original)
    @test replacement == [99]
    @test replacement !== original
    @test original == [1]
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-006: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

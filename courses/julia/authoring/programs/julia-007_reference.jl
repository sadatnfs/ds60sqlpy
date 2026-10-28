using Test

# === EXAMPLE A ===
function worked_a()
    values = collect(1:6)
    matrix = reshape(values, 2, 3)
    @test size(matrix) == (2, 3)
    @test matrix[:, 1] == [1, 2]
    @test matrix[1, 3] == 5
    @test length(matrix) == 6
    @test sum(matrix) == 21
    println("Matrix: ", matrix)
end

# === EXAMPLE B ===
function worked_b()
    values = [1, 2, 3]
    snapshot = values[1:2]
    window = @view values[1:2]
    snapshot[1] = 90
    @test values[1] == 1
    window[2] = 80
    @test values == [1, 80, 3]
    alias = values
    @test alias === values
    @test copy(values) !== values
    println("Source after view mutation: ", values)
end

# === EXERCISES ===
function exercise_checks()
    @test size(zeros(2, 1)) == (2, 1)
    @test size(zeros(2)) == (2,)
    @test eltype([1.0, 2.0]) == Float64
    @test_throws BoundsError [1, 2][0]
    nested = [[1], [2]]
    shallow = copy(nested)
    shallow[1][1] = 9
    @test nested[1][1] == 9
    deep = deepcopy(nested)
    deep[1][1] = 4
    @test nested[1][1] == 9
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-007: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

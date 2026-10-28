using Test
using LinearAlgebra
BLAS.set_num_threads(1)

function affine!(destination, matrix, input, bias)
    size(matrix, 2) == length(input) || throw(DimensionMismatch("Input width"))
    size(matrix, 1) == length(destination) == length(bias) ||
        throw(DimensionMismatch("Output height"))
    any(source -> Base.mightalias(destination, source), (matrix, input, bias)) &&
        throw(ArgumentError("Destination must not overlap inputs"))
    mul!(destination, matrix, input)
    destination .+= bias
    return destination
end

# === EXAMPLE A ===
function worked_a()
    matrix = [2.0 1.0; 0.0 3.0]
    input = [3.0, 4.0]
    bias = [1.0, -1.0]
    destination = zeros(2)
    @test affine!(destination, matrix, input, bias) === destination
    @test destination == [11, 11]
    @test input == [3, 4]
    affine!(destination, matrix, [1.0, 2.0], bias)
    @test destination == [5, 5]
    bytes = @allocated affine!(destination, matrix, input, bias)
    @test bytes >= 0
    println("Reused output: ", destination, "; measured allocation bytes: ", bytes)
end

# === EXAMPLE B ===
function worked_b()
    storage = [1.0, 2.0, 3.0, 4.0]
    middle = view(storage, 2:3)
    middle[1] = 20
    @test storage == [1, 20, 3, 4]
    matrix = Matrix{Float64}(I, 2, 2)
    destination = view(storage, 1:2)
    input = view(storage, 2:3)
    snapshot = copy(storage)
    @test_throws ArgumentError affine!(destination, matrix, input, zeros(2))
    @test storage == snapshot
    println("Overlapping call rejected before mutation")
end

# === EXERCISES ===
function exercise_checks()
    output = fill(7.0, 2)
    @test_throws DimensionMismatch affine!(output, ones(2, 3), ones(2), ones(2))
    @test output == [7, 7]
    @test_throws ArgumentError affine!(output, Matrix{Float64}(I, 2, 2), ones(2), output)
    @test affine!(zeros(2), [1.0 2.0; 3.0 4.0], [2.0, 1.0], [0.0, 0.0]) == [4, 10]
    original = [1.0, 2.0]
    separate = copy(original)
    separate[1] = 9
    @test original == [1, 2]
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-026: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

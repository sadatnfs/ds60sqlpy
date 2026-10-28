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

worked_b()

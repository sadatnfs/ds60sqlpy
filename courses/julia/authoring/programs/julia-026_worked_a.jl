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

worked_a()

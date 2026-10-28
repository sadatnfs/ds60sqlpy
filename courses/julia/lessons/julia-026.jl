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

worked_a()

# Task 1: Compute the two entries before running the first case.
# Task 2: Reuse the destination for input[1,2].
# Task 3: Pass a2-by -3 matrix and a length 2 input.
# Task 4: Explain why two different view objects can be unsafe.
# Task 5: Describe a safe interface for repeated calls that must permit overlapping
# inputs.
# Task 6: Explain why fewer measured bytes may not mean faster code.

# Write your independent changes below.

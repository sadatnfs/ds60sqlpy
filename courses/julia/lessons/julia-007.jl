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

worked_a()

# Task 1: Compare a length2 vector with a2-by-1 matrix.
# Task 2: Locate value5 in the reshaped matrix.
# Task 3: Mutate an ordinary slice from a vector.
# Task 4: Mutate a view of the same range.
# Task 5: Compare copy and deepcopy on a vector of vectors.
# Task 6: Read index0 from a standard two-element vector.

# Write your independent changes below.

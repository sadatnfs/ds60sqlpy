using Test

# === EXAMPLE A ===
function worked_a()
    matrix = [1 3 5; 2 4 6]
    rows = [10, 20]
    columns = reshape([100, 200, 300], 1, 3)
    result = matrix .+ rows .+ columns
    @test result == [111 213 315; 122 224 326]
    @test_throws DimensionMismatch matrix .+ [1, 2, 3, 4]
    println("Broadcast result: ", result)
end

worked_a()

# Task 1: Add one offset per column to a matrix.
# Task 2: Broadcast a length 4 vector with the 2-by -3 fixture.
# Task 3: Apply 2x+1 elementwise to a floating vector using dotted assignment.
# Task 4: Shift a vector left-to-right by reading the preceding updated element.
# Task 5: Read the shift input from an explicit copy.
# Task 6: Write 0.5 into an integer element through dotted assignment.

# Write your independent changes below.

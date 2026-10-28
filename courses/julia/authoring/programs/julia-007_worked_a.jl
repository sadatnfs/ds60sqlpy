using Test

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

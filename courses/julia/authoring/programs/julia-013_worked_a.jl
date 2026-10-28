using Test

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

using Test

function worked_b()
    values = [1.0, 2.0, 3.0]
    values .= 2 .* values .+ 1
    @test values == [3, 5, 7]
    sequential = [1, 2, 3, 4]
    for index = 2:length(sequential)
        sequential[index] = sequential[index-1]
    end
    snapshot = [1, 2, 3, 4]
    source = copy(snapshot)
    for index = 2:length(snapshot)
        snapshot[index] = source[index-1]
    end
    @test sequential == [1, 1, 1, 1]
    @test snapshot == [1, 1, 2, 3]
    println("Sequential versus snapshot: ", sequential, "; ", snapshot)
end

worked_b()

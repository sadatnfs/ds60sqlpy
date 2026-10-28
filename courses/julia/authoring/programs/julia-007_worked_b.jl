using Test

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

worked_b()

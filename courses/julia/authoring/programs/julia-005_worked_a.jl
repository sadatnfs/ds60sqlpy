using Test

function sum_range(values)
    total = 0
    for value in values
        total += value
    end
    return total
end

function worked_a()
    @test sum_range(1:5) == 15
    @test sum_range(1:0) == 0
    @test collect(3:-1:1) == [3, 2, 1]
    println("Range sum: ", sum_range(1:5))
end

worked_a()

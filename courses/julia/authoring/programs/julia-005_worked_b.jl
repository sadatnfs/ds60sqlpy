using Test

function sum_range(values)
    total = 0
    for value in values
        total += value
    end
    return total
end

function worked_b()
    values = [-2, 0, 3, 4]
    squares = [value^2 for value in values if value > 0]
    reduced = sum(value^2 for value in values if value > 0)
    @test squares == [9, 16]
    @test reduced == 25
    @test collect(enumerate([10, 20])) == [(1, 10), (2, 20)]
    println("Selected squares: ", squares)
end

worked_b()

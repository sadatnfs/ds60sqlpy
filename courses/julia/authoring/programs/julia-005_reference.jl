using Test

function sum_range(values)
    total = 0
    for value in values
        total += value
    end
    return total
end

# === EXAMPLE A ===
function worked_a()
    @test sum_range(1:5) == 15
    @test sum_range(1:0) == 0
    @test collect(3:-1:1) == [3, 2, 1]
    println("Range sum: ", sum_range(1:5))
end

# === EXAMPLE B ===
function worked_b()
    values = [-2, 0, 3, 4]
    squares = [value^2 for value in values if value > 0]
    reduced = sum(value^2 for value in values if value > 0)
    @test squares == [9, 16]
    @test reduced == 25
    @test collect(enumerate([10, 20])) == [(1, 10), (2, 20)]
    println("Selected squares: ", squares)
end

# === EXERCISES ===
function exercise_checks()
    @test sum_range(2:2) == 2
    @test sum_range(-2:2) == 0
    @test length(1:3) == 3
    @test [i for i = 1:0] == Int[]
    @test sum(i for i = 1:3) == 6
    @test collect(eachindex([4, 5])) == [1, 2]
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-005: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

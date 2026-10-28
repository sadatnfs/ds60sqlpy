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

worked_a()

# Task 1: List values from1:3.
# Task 2: Run the accumulator over1:0.
# Task 3: Construct3,2,1 as a range.
# Task 4: Enumerate values10 and20.
# Task 5: Compute only the sum of selected squares.
# Task 6: Move a reusable accumulation into a function with explicit input.

# Write your independent changes below.

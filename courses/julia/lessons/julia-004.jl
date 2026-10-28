using Test

function rate_or_nothing(numerator, denominator)
    denominator > 0 || return nothing
    return numerator / denominator
end

# === EXAMPLE A ===
function worked_a()
    @test rate_or_nothing(2, 4) == 0.5
    @test rate_or_nothing(0, 0) === nothing
    calls = Ref(0)
    bump() = (calls[] += 1; true)
    @test !(false && bump())
    @test calls[] == 0
    @test true && bump()
    @test calls[] == 1
    println("Guarded rate and short-circuit checks passed")
end

worked_a()

# Task 1: Compare rates0/5 and0/0 under the helper policy.
# Task 2: Use an integer directly as an if condition.
# Task 3: Guard the first element of a possibly empty array.
# Task 4: Use isequal for two NaN values.
# Task 5: Compare0.0 and-0.0 using both equality functions.
# Task 6: Evaluate a comparison involving missing.

# Write your independent changes below.

using Test

function rate_or_nothing(numerator, denominator)
    denominator > 0 || return nothing
    return numerator / denominator
end

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

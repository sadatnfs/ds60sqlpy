using Test

function rate_or_nothing(numerator, denominator)
    denominator > 0 || return nothing
    return numerator / denominator
end

function worked_b()
    @test !(NaN == NaN)
    @test isequal(NaN, NaN)
    @test 0.0 == -0.0
    @test !isequal(0.0, -0.0)
    @test ismissing(missing == 1)
    @test_throws TypeError if missing
        1
    else
        0
    end
    println("Special equality cases checked")
end

worked_b()

using Test

function worked_b()
    @test 0.1 + 0.2 != 0.3
    @test isapprox(0.1 + 0.2, 0.3; atol = 1e-15, rtol = 0)
    @test 1//10 + 2//10 == 3//10
    @test 7 / 2 == 3.5
    @test div(7, 2) == 3
    println("Floating sum: ", 0.1 + 0.2, "; rational sum: ", 1//10 + 2//10)
end

worked_b()

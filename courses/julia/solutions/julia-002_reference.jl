using Test

# === EXAMPLE A ===
function worked_a()
    top = typemax(Int8)
    @test top + Int8(1) == typemin(Int8)
    @test_throws OverflowError Base.Checked.checked_add(top, Int8(1))
    @test BigInt(top) + 1 == 128
    println("Wrapped: ", top + Int8(1), "; exact: ", BigInt(top) + 1)
end

# === EXAMPLE B ===
function worked_b()
    @test 0.1 + 0.2 != 0.3
    @test isapprox(0.1 + 0.2, 0.3; atol = 1e-15, rtol = 0)
    @test 1//10 + 2//10 == 3//10
    @test 7 / 2 == 3.5
    @test div(7, 2) == 3
    println("Floating sum: ", 0.1 + 0.2, "; rational sum: ", 1//10 + 2//10)
end

# === EXERCISES ===
function exercise_checks()
    @test rem(7, 2) == 1
    @test 2//4 == 1//2
    @test BigInt(2)^100 > typemax(Int)
    @test_throws InexactError Int8(128)
    @test typeof(1.0f0) == Float32
    @test !isfinite(Inf)
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-002: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

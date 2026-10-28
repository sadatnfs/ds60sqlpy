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

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test isempty(Int[])
    @test !isempty([0])
    @test rate_or_nothing(0, 5) == 0
    @test rate_or_nothing(2, -1) === nothing
    @test (3 > 2 ? "larger" : "other") == "larger"
    @test_throws TypeError if 1
        true
    else
        false
    end
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-004: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

using Test

# === EXAMPLE A ===
function worked_a()
    accepted = 35
    rejected = 7
    total = accepted + rejected
    @test total == 42
    @test total isa Int
    println("Total records: ", total)
end

# === EXAMPLE B ===
function worked_b()
    first_value = 5
    retained = first_value
    first_value = 9
    @test retained == 5
    @test first_value == 9
    println("Retained scalar: ", retained, "; rebound scalar: ", first_value)
end

# === EXERCISES ===
function exercise_checks()
    @test 0 + 0 == 0
    @test 10 - 3 == 7
    @test 6 * 7 == 42
    @test typeof(2.5) == Float64
    @test string(42) == "42"
    @test sprint(print, "score=", 3) == "score=3"
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-001: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

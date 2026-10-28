using Test

# === EXAMPLE A ===
function worked_a()
    record = (id = "q1", score = 0.8, eligible = true)
    @test record.id == "q1"
    @test record.score == 0.8
    @test propertynames(record) == (:id, :score, :eligible)
    left, right = (2, 3)
    @test left + right == 5
    @test (7,) isa Tuple
    println("Named record: ", record)
end

# === EXAMPLE B ===
function worked_b()
    counts = Dict{String,Int}()
    for label in ["b", "a", "b"]
        counts[label] = get(counts, label, 0) + 1
    end
    @test counts == Dict("a" => 1, "b" => 2)
    @test sort(collect(keys(counts))) == ["a", "b"]
    @test Set(["b", "a", "b"]) == Set(["a", "b"])
    println("Ordered counts: ", [(key, counts[key]) for key in sort(collect(keys(counts)))])
end

# === EXERCISES ===
function exercise_checks()
    values = Dict("a" => 0)
    @test haskey(values, "a")
    @test !haskey(values, "b")
    @test get(values, "b", -1) == -1
    @test_throws KeyError values["b"]
    special = Dict(NaN => "present", 0.0 => "positive", -0.0 => "negative")
    @test special[NaN] == "present"
    @test length(special) == 3
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-008: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

using Test
using DataFrames

# === EXAMPLE A ===
function worked_a()
    entities = DataFrame(id = [1, 2], weight = [100, 200])
    observations = DataFrame(id = [1, 1], value = [10, 20])
    duplicated = leftjoin(entities, observations; on = :id)
    @test nrow(duplicated) == 3
    @test sum(duplicated.weight) == 400
    @test_throws ArgumentError leftjoin(entities, observations; on = :id, validate = (true, true))
    totals = combine(groupby(observations, :id), :value => sum => :value_total)
    reconciled = leftjoin(entities, totals; on = :id, validate = (true, true))
    @test nrow(reconciled) == 2
    @test sum(reconciled.weight) == 300
    @test sum(skipmissing(reconciled.value_total)) == 30
    println("Reconciled entity table: ", reconciled)
end

# === EXAMPLE B ===
function worked_b()
    left = DataFrame(id = [1, missing], label = ["known", "unknown"])
    right = DataFrame(id = [missing, 2], value = [7, 8])
    @test_throws ArgumentError innerjoin(left, right; on = :id)
    equal = innerjoin(left, right; on = :id, matchmissing = :equal)
    unequal = innerjoin(left, right; on = :id, matchmissing = :notequal)
    @test nrow(equal) == 1 && ismissing(equal.id[1])
    @test nrow(unequal) == 0
    println("Explicit missing-key matches: ", nrow(equal), "; excluded matches: ", nrow(unequal))
end

# === EXERCISES ===
function exercise_checks()
    left = DataFrame(id = [1, 2], x = [10, 20])
    right = DataFrame(id = [2, 3], y = [30, 40])
    result = sort(outerjoin(left, right; on = :id, source = :origin), :id)
    @test result.id == [1, 2, 3]
    @test string.(result.origin) == ["left_only", "both", "right_only"]
    @test nrow(innerjoin(left, right; on = :id)) == 1
    @test nrow(antijoin(left, right; on = :id)) == 1
    @test sum(left.x) == 30
    @test nrow(leftjoin(left, right; on = :id, validate = (true, true))) == 2
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-016: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

using Test
using DataFrames

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

worked_b()

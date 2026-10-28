using Test
using DataFrames

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

worked_a()

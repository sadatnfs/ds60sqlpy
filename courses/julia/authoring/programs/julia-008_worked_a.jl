using Test

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

worked_a()

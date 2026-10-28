using Test

function worked_a()
    accepted = 35
    rejected = 7
    total = accepted + rejected
    @test total == 42
    @test total isa Int
    println("Total records: ", total)
end

worked_a()

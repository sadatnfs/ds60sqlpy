using Test

function worked_b()
    first_value = 5
    retained = first_value
    first_value = 9
    @test retained == 5
    @test first_value == 9
    println("Retained scalar: ", retained, "; rebound scalar: ", first_value)
end

worked_b()

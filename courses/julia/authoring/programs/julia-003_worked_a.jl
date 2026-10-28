using Test
using Unicode

function worked_a()
    text = "éλ"
    @test length(text) == 2
    @test ncodeunits(text) == 4
    @test collect(eachindex(text)) == [1, 3]
    @test [text[i] for i in eachindex(text)] == ['é', 'λ']
    @test_throws StringIndexError text[2]
    println("Characters: ", collect(text), "; indices: ", collect(eachindex(text)))
end

worked_a()

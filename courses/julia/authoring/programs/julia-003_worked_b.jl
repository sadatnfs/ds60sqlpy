using Test
using Unicode

function worked_b()
    combined = "é"
    composed = "é"
    @test combined != composed
    @test length(combined) == 2
    @test length(collect(Unicode.graphemes(combined))) == 1
    @test Unicode.normalize(combined, :NFC) == composed
    println("Raw lengths: ", length(combined), ", ", length(composed))
end

worked_b()

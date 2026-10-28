using Test
using Unicode

# === EXAMPLE A ===
function worked_a()
    text = "éλ"
    @test length(text) == 2
    @test ncodeunits(text) == 4
    @test collect(eachindex(text)) == [1, 3]
    @test [text[i] for i in eachindex(text)] == ['é', 'λ']
    @test_throws StringIndexError text[2]
    println("Characters: ", collect(text), "; indices: ", collect(eachindex(text)))
end

# === EXAMPLE B ===
function worked_b()
    combined = "é"
    composed = "é"
    @test combined != composed
    @test length(combined) == 2
    @test length(collect(Unicode.graphemes(combined))) == 1
    @test Unicode.normalize(combined, :NFC) == composed
    println("Raw lengths: ", length(combined), ", ", length(composed))
end

# === EXERCISES ===
function exercise_checks()
    @test isempty("")
    @test nextind("éλ", 1) == 3
    @test lowercase("DATA") == "data"
    @test join(["data", "science"], " ") == "data science"
    @test string("score=", 3) == "score=3"
    @test ncodeunits("ASCII") == length("ASCII")
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-003: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

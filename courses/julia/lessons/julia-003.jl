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

worked_a()

# Task 1: Move from the first to the second character in the UTF-8 fixture.
# Task 2: Compare characters and graphemes in the combining-accent example.
# Task 3: Apply NFC to the combining-accent fixture.
# Task 4: Check an empty string before selecting its first character.
# Task 5: Store offsets for a cited text passage.
# Task 6: Test an ASCII indexing algorithm with multibyte text.

# Write your independent changes below.

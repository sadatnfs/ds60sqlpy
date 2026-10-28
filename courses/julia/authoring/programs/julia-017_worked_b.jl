using Test
using CSV
using DataFrames
using Dates

function worked_b()
    @test_throws CSV.Error CSV.read(IOBuffer("count
wrong
"), DataFrame; types = Int, strict = true)
    original = DataFrame(id = ["001", "002"], note = ["contains,comma", "quoted \"value\""])
    output = IOBuffer()
    CSV.write(output, original)
    encoded = String(take!(output))
    restored = CSV.read(IOBuffer(encoded), DataFrame; types = String, strict = true)
    @test String.(restored.id) == original.id
    @test String.(restored.note) == original.note
    println("CSV round-trip preserved 2 authored records")
end

worked_b()

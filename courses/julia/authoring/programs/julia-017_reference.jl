using Test
using CSV
using DataFrames
using Dates

# === EXAMPLE A ===
function worked_a()
    text = "id,amount,date
001,2.5,2024-02-29
002,NA,2024-03-01
"
    table = CSV.read(
        IOBuffer(text),
        DataFrame;
        types = Dict(:id => String, :amount => Float64, :date => Date),
        missingstring = "NA",
        dateformat = "yyyy-mm-dd",
        strict = true,
    )
    @test String.(table.id) == ["001", "002"]
    @test table.amount[1] == 2.5
    @test ismissing(table.amount[2])
    @test table.date == [Date(2024, 2, 29), Date(2024, 3, 1)]
    println("Typed CSV table: ", table)
end

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    table = CSV.read(IOBuffer("value
1
2
"), DataFrame; types = Int, strict = true)
    @test sum(table.value) == 3
    @test nrow(table) == 2
    @test names(table) == ["value"]
    @test_throws CSV.Error CSV.read(IOBuffer("value
1.5
"), DataFrame; types = Int, strict = true)
    @test Date("2024-02-29", dateformat"yyyy-mm-dd") == Date(2024, 2, 29)
    @test_throws ArgumentError Date("2023-02-29", dateformat"yyyy-mm-dd")
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-017: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

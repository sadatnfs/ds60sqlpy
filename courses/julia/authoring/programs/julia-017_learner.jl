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

worked_a()

# Task 1: Read 001 as a declared string.
# Task 2: Parse the authored NA amount marker.
# Task 3: Parse 1.5 as a strict integer field.
# Task 4: Round-trip a string containing a comma or quotation marks.
# Task 5: Write to an IOBuffer and then read its contents.
# Task 6: A file parses successfully but has duplicate entity IDs.

# Write your independent changes below.

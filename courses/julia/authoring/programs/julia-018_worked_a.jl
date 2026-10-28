using Test
using Dates

function historical_value(rows, entity, at)
    eligible =
        [row for row in rows if row.entity == entity && row.event <= at && row.available <= at]
    isempty(eligible) && return missing
    ordered = sort(eligible; by = row -> (row.event, row.available, row.version))
    return last(ordered).value
end

function worked_a()
    start = Date(2024, 1, 31)
    @test start + Month(1) == Date(2024, 2, 29)
    @test start + Day(30) == Date(2024, 3, 1)
    february = start + Month(1)
    @test february + Month(1) == Date(2024, 3, 29)
    @test start + Month(1) + Month(1) == Date(2024, 3, 31)
    @test start + Month(2) == Date(2024, 3, 31)
    println("Calendar month and fixed days differ")
end

worked_a()

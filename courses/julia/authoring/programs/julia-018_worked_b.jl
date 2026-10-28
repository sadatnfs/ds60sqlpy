using Test
using Dates

function historical_value(rows, entity, at)
    eligible =
        [row for row in rows if row.entity == entity && row.event <= at && row.available <= at]
    isempty(eligible) && return missing
    ordered = sort(eligible; by = row -> (row.event, row.available, row.version))
    return last(ordered).value
end

function worked_b()
    rows = [
        (
            entity = "a",
            event = DateTime(2024, 1, 1),
            available = DateTime(2024, 1, 1),
            version = 1,
            value = 10,
        ),
        (
            entity = "a",
            event = DateTime(2024, 1, 2),
            available = DateTime(2024, 1, 4),
            version = 2,
            value = 20,
        ),
        (
            entity = "a",
            event = DateTime(2024, 1, 2),
            available = DateTime(2024, 1, 5),
            version = 3,
            value = 25,
        ),
    ]
    @test historical_value(rows, "a", DateTime(2024, 1, 3)) == 10
    @test historical_value(rows, "a", DateTime(2024, 1, 4)) == 20
    @test historical_value(rows, "a", DateTime(2024, 1, 5)) == 25
    @test ismissing(historical_value(rows, "b", DateTime(2024, 1, 5)))
    println("Historical values: 10, 20, 25 at the declared cutoffs")
end

worked_b()

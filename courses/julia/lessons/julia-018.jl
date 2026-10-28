using Test
using Dates

function historical_value(rows, entity, at)
    eligible =
        [row for row in rows if row.entity == entity && row.event <= at && row.available <= at]
    isempty(eligible) && return missing
    ordered = sort(eligible; by = row -> (row.event, row.available, row.version))
    return last(ordered).value
end

# === EXAMPLE A ===
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

# Task 1: Compare one month with thirty days from January 31 in the fixture.
# Task 2: Compare two successive month additions with one two-month addition.
# Task 3: Look up the feature on January 3.
# Task 4: Look up at the exact availability timestamp.
# Task 5: Look up an absent entity.
# Task 6: Receive a daylight-saving-ambiguous local timestamp.

# Write your independent changes below.

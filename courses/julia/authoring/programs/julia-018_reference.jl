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

# === EXAMPLE B ===
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

# === EXERCISES ===
function exercise_checks()
    @test Date(2024, 2, 28) + Day(1) == Date(2024, 2, 29)
    @test Date(2023, 2, 28) + Day(1) == Date(2023, 3, 1)
    @test DateTime(2024, 1, 1, 1) - DateTime(2024, 1, 1) == Millisecond(3_600_000)
    @test ismissing(historical_value(NamedTuple[], "a", DateTime(2024, 1, 1)))
    row = (
        entity = "a",
        event = DateTime(2024, 1, 2),
        available = DateTime(2024, 1, 4),
        version = 1,
        value = 7,
    )
    @test ismissing(historical_value([row], "a", DateTime(2024, 1, 3)))
    @test historical_value([row], "a", DateTime(2024, 1, 4)) == 7
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-018: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

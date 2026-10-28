using Test

# === EXAMPLE A ===
function worked_a()
    accepted = 35
    rejected = 7
    total = accepted + rejected
    @test total == 42
    @test total isa Int
    println("Total records: ", total)
end

worked_a()

# Task 1: Use accepted20 and rejected3.
# Task 2: Bind y to x=4, then rebind x to10.
# Task 3: Compare a bare arithmetic expression with println in a script.
# Task 4: Compare typeof(2) and typeof(2.5).
# Task 5: Misspell a variable in an owned copy of the program.
# Task 6: Time a first and repeated call in one process.

# Write your independent changes below.

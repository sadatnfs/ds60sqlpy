using Test

# === EXAMPLE A ===
function worked_a()
    top = typemax(Int8)
    @test top + Int8(1) == typemin(Int8)
    @test_throws OverflowError Base.Checked.checked_add(top, Int8(1))
    @test BigInt(top) + 1 == 128
    println("Wrapped: ", top + Int8(1), "; exact: ", BigInt(top) + 1)
end

worked_a()

# Task 1: Compute quotient and remainder for7 divided by2.
# Task 2: Convert128 to Int8.
# Task 3: Add1//10 and2//10.
# Task 4: Compare1.0f0 and1.0.
# Task 5: Compute BigInt(2)^100.
# Task 6: Justify an absolute tolerance for a measured quantity.

# Write your independent changes below.

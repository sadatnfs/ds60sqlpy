using Test

# === EXAMPLE A ===
function worked_a()
    record = (id = "q1", score = 0.8, eligible = true)
    @test record.id == "q1"
    @test record.score == 0.8
    @test propertynames(record) == (:id, :score, :eligible)
    left, right = (2, 3)
    @test left + right == 5
    @test (7,) isa Tuple
    println("Named record: ", record)
end

worked_a()

# Task 1: Represent a single integer as a tuple.
# Task 2: Return an ID, score and eligibility field.
# Task 3: Count labels a,b,b before converting to a set.
# Task 4: Print a dictionary in an explicitly sorted key order.
# Task 5: Compare a present zero-valued key with an absent key.
# Task 6: Use NaN and both signed zeros as dictionary keys.

# Write your independent changes below.

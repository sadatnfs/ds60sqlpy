using Test

affine(x; scale = 1, shift = 0) = scale * x + shift
make_scaler(scale) = x -> scale * x

function rebind(values)
    values = [99]
    return values
end

function change_first!(values)
    isempty(values) && throw(ArgumentError("A first element is required"))
    values[1] = 99
    return values
end

# === EXAMPLE A ===
function worked_a()
    @test affine(3; scale = 2, shift = 1) == 7
    double = make_scaler(2)
    @test double(4) == 8
    @test map(double, [1, 2, 3]) == [2, 4, 6]
    println("Configured function result: ", affine(3; scale = 2, shift = 1))
end

worked_a()

# Task 1: Call affine on5 without keywords.
# Task 2: Set shift=-2 for input5.
# Task 3: Create a scale3 function and apply it to2.
# Task 4: Call rebind on a caller array.
# Task 5: Call change_first! on a nonempty vector.
# Task 6: Call change_first! on an empty vector.

# Write your independent changes below.

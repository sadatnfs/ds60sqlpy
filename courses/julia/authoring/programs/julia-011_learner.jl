using Test

abstract type Shape end
struct Circle <: Shape
    radius::Float64
    function Circle(radius::Real)
        stored = Float64(radius)
        isfinite(stored) && stored >= 0 ||
            throw(ArgumentError("Finite nonnegative radius required"))
        return new(stored)
    end
end
struct Rectangle <: Shape
    width::Float64
    height::Float64
    function Rectangle(width::Real, height::Real)
        w, h = Float64(width), Float64(height)
        all(isfinite, (w, h)) && w >= 0 && h >= 0 ||
            throw(ArgumentError("Finite nonnegative dimensions required"))
        return new(w, h)
    end
end
area(shape::Circle) = pi * shape.radius^2
area(shape::Rectangle) = shape.width * shape.height
total_area(shapes) = sum((area(shape) for shape in shapes); init = 0.0)

classify(first::Integer, second) = :first_integer
classify(first, second::Integer) = :second_integer
classify(first::Integer, second::Integer) = :both_integers

# === EXAMPLE A ===
function worked_a()
    shapes = Shape[Circle(2), Rectangle(2, 3)]
    @test area(shapes[1]) ≈ 4pi
    @test area(shapes[2]) == 6
    @test total_area(shapes) ≈ 4pi + 6
    @test total_area(Shape[]) == 0
    println("Total area: ", total_area(shapes))
end

worked_a()

# Task 1: Construct a circle with radius 0.
# Task 2: Use a negative rectangle side.
# Task 3: Call classify with an integer in each position separately.
# Task 4: Call classify with two integers.
# Task 5: Pass two floating-point values to classify.
# Task 6: Sketch another Shape subtype and an area method.

# Write your independent changes below.

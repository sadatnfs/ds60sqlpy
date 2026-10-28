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

# === EXAMPLE B ===
function worked_b()
    @test classify(1, "x") == :first_integer
    @test classify("x", 1) == :second_integer
    @test classify(1, 2) == :both_integers
    @test_throws MethodError classify(1.0, 2.0)
    println("Intersection method: ", classify(1, 2))
end

# === EXERCISES ===
function exercise_checks()
    @test area(Circle(0)) == 0
    @test area(Rectangle(0, 5)) == 0
    @test_throws ArgumentError Circle(-1)
    @test_throws ArgumentError Rectangle(1, -1)
    @test Circle <: Shape
    @test isconcretetype(Circle) && !isconcretetype(Shape)
end

# === MAIN ===
function main()
    worked_a()
    worked_b()
    exercise_checks()
    println("julia-011: all reference checks passed")
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end

# julia-011: Multiple dispatch and method specificity

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-010`.

Design generic operations over owned types and resolve overlapping method signatures explicitly.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A function can have several methods

Julia selects a method using the types of its positional arguments. The selection can depend on several arguments, not only a distinguished receiver object. This makes generic operations convenient when behavior depends on combinations of representations.

An abstract type can describe a category without defining storage for every subtype. Concrete subtypes supply their own fields. A generic operation such as area can then have methods for the concrete shapes while a higher-level function calls that operation without hardcoding every case.

Method specificity matters when several signatures match. A more specific applicable method can be selected, but overlapping signatures may be ambiguous when neither is more specific than the other. Defining the intersection explicitly makes the intended behavior clear. An ambiguity should not be hidden by depending on method definition order.

## Worked case A: one operation over two shapes

The shape types validate nonnegative dimensions in their constructors. Two area methods implement the appropriate formulas, and a generic total uses them through the same operation name. The code tests a heterogeneous collection and an empty collection with an explicit additive identity.

```julia
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

function worked_a()
    shapes = Shape[Circle(2), Rectangle(2, 3)]
    @test area(shapes[1]) ≈ 4pi
    @test area(shapes[2]) == 6
    @test total_area(shapes) ≈ 4pi + 6
    @test total_area(Shape[]) == 0
    println("Total area: ", total_area(shapes))
end

worked_a()
```

## Worked case B: specify an intersection

One method handles an integer first argument and another handles an integer second argument. The pair with two integers lies in their overlap. A third, explicitly intersecting method resolves that case. A pair of unsupported argument types still produces a method error, which is more honest than an unexplained fallback value.

```julia
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

function worked_b()
    @test classify(1, "x") == :first_integer
    @test classify("x", 1) == :second_integer
    @test classify(1, 2) == :both_integers
    @test_throws MethodError classify(1.0, 2.0)
    println("Intersection method: ", classify(1, 2))
end

worked_b()
```

## Interfaces and ownership

A useful interface is a set of required operations and behavioral laws, not just an abstract-type declaration. A new shape type needs an area method and suitable invariants if it is to participate in the same algorithm. Later interface work can add iteration or indexing with independent tests of those laws.

Extend functions deliberately. Defining a method for an owned type is usually easier to reason about than adding broad behavior for types owned by other packages. Uncoordinated extensions can create ambiguities or alter another package's assumptions. Keep method signatures as specific as the intended contract requires.

## Diagnose dispatch

When a call fails, inspect the actual argument types and available methods. A visually similar value can have a different type after parsing or promotion. Do not fix a method error merely by adding an unrestricted catch-all method if the input violates the intended domain.

Conversely, an unnecessarily narrow annotation can reject compatible inputs without improving correctness. The next unit uses parametric methods to express useful constraints while retaining generic numerical behavior. Correct dispatch and good performance are related but distinct questions; a heterogeneous collection may be valid while offering different specialization opportunities.

These examples demonstrate real dispatch and constructor checks on small owned types. They do not establish that every problem needs inheritance, that keyword arguments select methods in the same way as positional arguments, or that adding more methods always improves an API. Preserve the operation's meaning across every supported representation.


## Six investigations

### 1. Add a zero-size shape

Construct a circle with radius 0.

**Expected:** Its area is 0.

**Hint:** Check the boundary without rejecting a valid degenerate shape.

### 2. Reject an invalid dimension

Use a negative rectangle side.

**Expected:** Construction raises ArgumentError.

**Hint:** Dispatch does not replace domain validation.

### 3. Trace both arguments

Call classify with an integer in each position separately.

**Expected:** Different methods handle the two cases.

**Hint:** Method selection uses the positional type tuple.

### 4. Resolve the overlap

Call classify with two integers.

**Expected:** The explicit intersection method is selected.

**Hint:** Neither one-sided signature alone expresses the complete overlap rule.

### 5. Keep an unsupported case visible

Pass two floating-point values to classify.

**Expected:** A MethodError is raised.

**Hint:** No method promises that case.

### 6. Extend an owned interface

Sketch another Shape subtype and an area method.

**Expected:** The generic total can use the operation if its laws hold.

**Hint:** An abstract type does not implement the behavior itself.

## Primary references

- [Julia methods and ambiguities](https://docs.julialang.org/en/v1/manual/methods/)
- [Julia interfaces](https://docs.julialang.org/en/v1/manual/interfaces/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

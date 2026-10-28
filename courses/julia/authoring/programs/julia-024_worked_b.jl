using Test
using .DS60Plots

function euler_decay(rate, steps)
    steps isa Integer && !(steps isa Bool) && steps > 0 && isfinite(rate) && rate >= 0 ||
        throw(ArgumentError("Positive steps and finite nonnegative rate required"))
    values = ones(steps+1)
    step = 1/steps
    for index = 1:steps
        values[index+1] = (1-rate*step)*values[index]
    end
    return collect(range(0.0, 1.0; length = steps+1)), values
end

function bisect(function_value, left, right; tolerance = 1e-10, maxiter = 100)
    isfinite(left) &&
    isfinite(right) &&
    left < right &&
    isfinite(tolerance) &&
    tolerance > 0 &&
    maxiter isa Integer &&
    !(maxiter isa Bool) &&
    maxiter > 0 || throw(ArgumentError("Valid bracket and budget required"))
    a, b = function_value(left), function_value(right)
    isfinite(a) && isfinite(b) || throw(ArgumentError("Finite endpoint values required"))
    a == 0 && return left
    b == 0 && return right
    signbit(a) != signbit(b) || throw(ArgumentError("A sign-changing bracket is required"))
    for _ = 1:maxiter
        middle = left/2 + right/2
        value = function_value(middle)
        isfinite(value) || throw(ArgumentError("Finite interior value required"))
        (right-left)/2 <= tolerance && return middle
        value == 0 && return middle
        if signbit(value) == signbit(a)
            left, a = middle, value
        else
            right, b = middle, value
        end
    end
    error("Iteration budget exhausted")
end

function worked_b()
    root = bisect(x -> x^2-2, 0.0, 2.0)
    @test abs(root-sqrt(2)) <= 1e-10
    @test abs(root^2-2) < 1e-8
    @test_throws ArgumentError bisect(x -> x^2+1, -1.0, 1.0)
    @test_throws ErrorException bisect(x -> x^2-2, 0.0, 2.0; maxiter = 1)
    println("Bracketed root: ", root)
end

worked_b()

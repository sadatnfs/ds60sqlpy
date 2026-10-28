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

# === EXAMPLE A ===
function worked_a()
    coarse_time, coarse = euler_decay(1.0, 4)
    fine_time, fine = euler_decay(1.0, 20)
    @test coarse[end] == (3/4)^4
    @test fine[end] ≈ (19/20)^20
    @test abs(fine[end]-exp(-1)) < abs(coarse[end]-exp(-1))
    _, unstable = euler_decay(3.0, 1)
    _, alternating = euler_decay(3.0, 2)
    @test unstable == [1, -2]
    @test alternating == [1, -0.5, 0.25]
    exact = exp.(-fine_time)
    data = [
        Dict("type"=>"scatter", "x"=>fine_time, "y"=>exact, "mode"=>"lines", "name"=>"Exact"),
        Dict(
            "type"=>"scatter",
            "x"=>coarse_time,
            "y"=>coarse,
            "mode"=>"lines+markers",
            "name"=>"Euler 4",
        ),
        Dict("type"=>"scatter", "x"=>fine_time, "y"=>fine, "mode"=>"lines", "name"=>"Euler 20"),
    ]
    layout = Dict(
        "title"=>"Explicit Euler error under a known decay model",
        "meta"=>Dict(
            "description"=>"For rate 1 over unit time, 20 Euler steps are closer to the analytic path than 4. Stability and positivity are separate conditions.",
            "table"=>Dict(
                "columns"=>["Time", "Exact state", "Euler 20 state"],
                "rows"=>[[fine_time[i], exact[i], fine[i]] for i in eachindex(fine)],
            ),
        ),
    )
    show_plotly(
        data;
        layout = layout,
        description = "Known decay solution and Euler approximations",
    )
    println("Final Euler errors: ", coarse[end]-exp(-1), "; ", fine[end]-exp(-1))
end

worked_a()

# Task 1: Compare Euler with 4 and 20 steps for rate 1.
# Task 2: Use rate 3 with 2 Euler steps.
# Task 3: Try x squared plus 1 on[-1,1].
# Task 4: Allow only one bisection iteration for square-root 2.
# Task 5: Integrate x squared using the two trapezoidal grids.
# Task 6: Compare a root-position tolerance with a function residual.

# Write your independent changes below.

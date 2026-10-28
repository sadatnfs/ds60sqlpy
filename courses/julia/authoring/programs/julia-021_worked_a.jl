using Test
using LinearAlgebra
using Statistics
BLAS.set_num_threads(1)

function fit_ridge(x, y, penalty)
    length(x) == length(y) && length(x) >= 2 ||
        throw(ArgumentError("Aligned training rows required"))
    all(isfinite, x) && all(isfinite, y) && isfinite(penalty) && penalty >= 0 ||
        throw(ArgumentError("Finite data and nonnegative penalty required"))
    design = hcat(ones(length(x)), Float64.(x))
    penalty == 0 && rank(design) < 2 && throw(ArgumentError("Unpenalized design is not identified"))
    augmented = vcat(design, reshape([0.0, sqrt(penalty)], 1, 2))
    return augmented \ vcat(Float64.(y), 0.0)
end
predict(coefficients, x) = coefficients[1] .+ coefficients[2] .* x
mse(predicted, actual) = mean(abs2, predicted .- actual)

function worked_a()
    x = collect(0.0:3.0)
    y = 1 .+ 2x
    coefficients = fit_ridge(x, y, 0)
    @test coefficients ≈ [1, 2]
    @test predict(coefficients, [4, 5]) ≈ [9, 11]
    @test mse(predict(coefficients, x), y) < 1e-20
    println("Recovered line: ", coefficients)
end

worked_a()

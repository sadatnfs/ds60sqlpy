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

function worked_b()
    x = collect(0.0:3.0)
    y = [1.0, 3.0, 5.0, 9.0]
    penalties = [0.0, 1.0, 2.0, 4.0]
    fits = [fit_ridge(x, y, penalty) for penalty in penalties]
    development_errors = [mse(predict(fit, [4, 5]), [9, 11]) for fit in fits]
    selected = argmin(development_errors)
    @test penalties[selected] == 2
    @test fits[selected] ≈ [12/7, 13/7]
    @test development_errors[selected] ≈ 1/98
    final_error = mse(predict(fits[selected], [6, 7]), [13, 15])
    @test final_error ≈ 5/98
    println("Selected penalty: ", penalties[selected], "; final error: ", final_error)
end

worked_b()

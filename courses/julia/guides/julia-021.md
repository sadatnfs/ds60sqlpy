# julia-021: Regression fitting, regularization and held-out assessment

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-018`, `julia-019`, `julia-020`.

Fit a small regression procedure with stable linear algebra and select regularization without using final outcomes.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## The fitted object includes a procedure

A regression example needs an observation unit, input schema, training rule and evaluation target. Correct matrix arithmetic cannot determine whether the rows are representative or the features were available at prediction time. The small fixture here makes the fitting and selection boundaries explicit before those scientific questions are generalized.

The design matrix contains an intercept column and one predictor. Ridge regularization penalizes the slope while leaving the intercept unpenalized. The objective is a squared residual sum plus \(\lambda\beta_1^2\). Its numerical scale depends on whether a sum or mean reduction is used, so the same numerical lambda is not automatically equivalent under another convention.

The implementation solves an augmented least-squares system instead of forming normal equations solely to invert them. Normal equations can square a conditioning problem. The fixture is tiny, but preserving a sound formulation makes it easier to extend without teaching an avoidable numerical shortcut.

## Worked case A: recover a known line

The first dataset follows an exact line. With no penalty, the fit recovers its intercept and slope and predicts two new input values. The known equation supplies an independent expected result. This is a software and arithmetic check, not a statistical confidence statement from noisy observational data.

```julia
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
```

## Worked case B: select on development data

The second training set contains an authored perturbation. Four candidate penalties are compared using development outcomes. The selected penalty is then evaluated on a separate final pair. Changing final labels must not change which penalty was selected. The program checks the selected value and exact rational expressions for its fitted coefficients and errors.

```julia
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
```

## Preserve information boundaries

Any learned transformation belongs inside the corresponding training or development procedure. Using all data to choose a normalization, feature set or threshold can leak information even when the final regression call receives only training rows. Time-dependent tasks also need the availability rules from the preceding unit.

A final test measures the selected procedure under its stated population and sampling assumptions. If it motivates another model change, it has been consumed for development or regression testing. Keep a separate assessment for the changed procedure instead of continuing to call the same labels untouched evidence.

## Diagnose a model result

Inspect coefficients, residuals, input ranges and leverage before treating a favorable error as reliable. A regularized model trades fit against a penalty chosen for a purpose. It does not make a poor data contract scientifically valid. An unpenalized rank-deficient design is rejected by this teaching helper rather than given an unexplained coefficient interpretation.

The two final test rows are far too few for a broad generalization claim. The exact expected errors are useful because the data were authored; real data would require suitable uncertainty, group/time splits and diagnostic work. Keep the small fixture's evidence boundary visible when transferring the code.

This unit uses only prepared standard linear algebra and statistics. More specialized Julia modeling packages require their own environment and API contracts. The following units add automatic differentiation and a prepared optimization library while retaining the same separation between numerical execution and scientific interpretation.


## Six investigations

### 1. Recover the known model

Fit the exact line without a penalty.

**Expected:** The coefficients are approximately[1,2].

**Hint:** Use the authored equation as an independent reference.

### 2. Trace penalty selection

Compare all four development errors in case B.

**Expected:** The selected penalty is 2.

**Hint:** Use only the development labels for the choice.

### 3. Inspect the selected fit

Derive the case B intercept and slope.

**Expected:** They are 12/7 and 13/7.

**Hint:** Use centered sums or the stated augmented system.

### 4. Keep the final set separate

Alter only the final labels after selection.

**Expected:** The chosen penalty must remain unchanged.

**Hint:** Trace data flow into argmin.

### 5. Reject nonidentification

Fit an unpenalized design with identical predictor values.

**Expected:** The teaching helper raises an explicit error.

**Hint:** A coefficient interpretation requires the declared rank condition.

### 6. Report scope

Use two final rows to describe the model.

**Expected:** Report the observed error without a broad accuracy guarantee.

**Hint:** The fixture was designed for arithmetic inspection.

## Primary references

- [Julia least-squares operations](https://docs.julialang.org/en/v1/stdlib/LinearAlgebra/)
- [Existing model procedure validation](../../../courses/statistics-ml/tutorials/learning/07-validation-as-a-procedure.md)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

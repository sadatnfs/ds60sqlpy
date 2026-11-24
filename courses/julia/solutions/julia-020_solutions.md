# julia-020: explained reference

The executable reference is `julia-020_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Make every random draw come from a named generator such as `Xoshiro(42)` and compare simulated summaries with exact distribution quantities. Worked example A samples 4000 draws from `Normal(2, 3)` and judges the sample mean with the scale 3 divided by sqrt(4000). Worked example B compares `Binomial(10, 0.2)` frequencies with exact masses.

## 1. State the parameterization

A familiar parameter name should be checked against the actual distribution API.

**Expected observation:** The mean is 2 and variance 9.

**Why it holds here:** Distributions.jl parameterizes `Normal(μ, σ)` by standard deviation, so `Normal(2, 3)` has mean 2 and variance 9.

**Plausible wrong approach:** Reading the second argument as variance, as some textbooks write N(μ, σ²), predicts variance 3 and a much narrower spread.

**How to verify:** Example A asserts `mean(distribution) == 2` and `var(distribution) == 9`.

## 2. Reproduce a sequence

This demonstrates reproducibility under the current implementation, not a universal cross-version promise.

**Expected observation:** They produce equal arrays in the stated runtime.

**Why it holds here:** Two `Xoshiro(42)` generators start in the same state, so drawing 4000 values from each yields identical arrays in this runtime.

**Plausible wrong approach:** Relying on the global default generator lets any earlier call elsewhere in the script change the sequence.

**How to verify:** Example A asserts `first == second`; the reference also asserts `rand(Xoshiro(3), 3) == before`.

## 3. Advance the generator

Reusing or recreating a generator defines different sampling procedures.

**Expected observation:** Its state advances and the arrays differ in the fixture.

**Why it holds here:** Each call to `rand(generator, 3)` advances the same generator, so the second batch continues the stream rather than repeating it.

**Plausible wrong approach:** Expecting the seed to be applied again on every call predicts equal batches and misreads how generator state works.

**How to verify:** The reference asserts `before != after` for consecutive draws from one `Xoshiro(3)`.

## 4. Scale Monte Carlo work

An individual realization can still deviate unpredictably; the scaling is a statement about the sampling model.

**Expected observation:** The theoretical mean standard-error scale halves.

**Why it holds here:** The standard error of the mean is σ divided by sqrt(n), so four times the draws multiplies it by 1/2.

**Plausible wrong approach:** Expecting the error to shrink by four confuses variance scaling with standard-error scaling.

**How to verify:** Compute `3 / sqrt(4000)` and `3 / sqrt(16000)` and confirm the ratio is exactly 2.

## 5. Inspect an extreme tail

Probability APIs have different numerical roles even when algebraic formulas look equivalent.

**Expected observation:** A stable tail API retains a small positive probability.

**Why it holds here:** At z = 10, `cdf(Normal(), 10)` rounds to 1.0 in `Float64`, so `1 - cdf` is 0, while `ccdf` computes the tiny tail directly.

**Plausible wrong approach:** Taking `log(1 - cdf(Normal(), 10))` gives negative infinity and breaks any likelihood that uses it.

**How to verify:** Example B checks that `ccdf(Normal(), 10.0)` lies between the two Mills-ratio bounds and that `logccdf` is finite.

## 6. Interpret the plot

The chart is a mechanism demonstration and does not establish a real population distribution.

**Expected observation:** Finite simulated frequencies fluctuate around the model probabilities.

**Why it holds here:** Two thousand draws give empirical frequencies that sum to 1 and scatter around the exact masses, such as `pdf(0) = 0.8^10`.

**Plausible wrong approach:** Treating a gap between a bar and its marker as a model failure ignores the sampling noise expected at this size.

**How to verify:** Example B asserts `sum(empirical) ≈ 1` and `pdf(distribution, 0) ≈ 0.8^10`; compare each gap with sqrt(p(1-p)/2000).

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-020: all reference checks passed`:

Closed forms anchor these checks: the standard normal is symmetric, so its cdf at 0 is 0.5 and its median is 0, and the log density at 0 is minus half of log 2 pi. A negative scale raises `DomainError`. The generator lines show that consecutive draws from one stream differ, while a fresh `Xoshiro(3)` reproduces the first three numbers.

```julia
function exercise_checks()
    @test cdf(Normal(), 0) == 0.5
    @test quantile(Normal(), 0.5) == 0
    @test logpdf(Normal(), 0) ≈ -log(2pi)/2
    @test_throws DomainError Normal(0, -1)
    generator = Xoshiro(3)
    before = rand(generator, 3)
    after = rand(generator, 3)
    @test before != after
    @test rand(Xoshiro(3), 3) == before
end
```

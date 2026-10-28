# julia-020: Distributions, random state and Monte Carlo evidence

## Starting point and outcome

Intermediate; approximately 150 minutes. Direct prerequisites: `julia-014`, `julia-019`.

Use explicit random generators, compare simulation with analytic quantities and preserve the distinction between numerical and sampling uncertainty.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## Randomness needs an explicit role

A random-number generator has state. Reusing an object advances that state, while constructing another generator with the same seed can reproduce a sequence under the same implementation. A seed is useful provenance, but it is not a promise of identical draws across every library version, algorithm or hardware environment.

A probability distribution describes a mathematical model. The Distributions package supplies operations such as moments, density, cumulative probability and sampling. Simulated data from a declared distribution can test an algorithm under known assumptions. It is not evidence that an external population follows that distribution.

Monte Carlo error comes from using finitely many draws. For independent draws with variance \(\sigma^2\), the standard error of their mean scales as \(\sigma/\sqrt{n}\). A larger sample improves this theoretical scale, but one particular larger sample is not guaranteed to be closer to the target than every smaller realization.

## Worked case A: compare a sample with a known model

The first example samples a Normal distribution with mean 2 and standard deviation 3 using an explicit generator. A second generator with the same seed reproduces those draws in this runtime. The program compares the sample mean with the analytic mean using a deliberately broad, stated Monte Carlo bound. It also reports the standard-error scale instead of claiming an exact estimate.

```julia
using Test
using Random
using Statistics
using Distributions
using .DS60Plots

function worked_a()
    distribution = Normal(2, 3)
    first = rand(MersenneTwister(42), distribution, 4000)
    second = rand(MersenneTwister(42), distribution, 4000)
    standard_error = 3 / sqrt(length(first))
    @test first == second
    @test mean(distribution) == 2
    @test var(distribution) == 9
    @test abs(mean(first) - 2) < 8standard_error
    println("Monte Carlo mean: ", mean(first), "; standard-error scale: ", standard_error)
end

worked_a()
```

## Worked case B: probabilities and stable tail calculations

The Binomial example has known mean and variance. An empirical frequency table from a second fixed generator is displayed beside its analytic probabilities through the classroom Plotly helper. The helper writes a bounded chart specification, description and exact table; it is not a standard Julia plotting package.

A normal-tail check also shows why subtracting a cumulative probability from one can lose precision in an extreme tail. The survival function and its logarithm are designed to retain that information. Independent Mills-ratio bounds provide a useful numerical check for the positive tail in this fixture.

```julia
using Test
using Random
using Statistics
using Distributions
using .DS60Plots

function worked_b()
    distribution = Binomial(10, 0.2)
    @test mean(distribution) == 2
    @test var(distribution) ≈ 1.6
    @test pdf(distribution, 0) ≈ 0.8^10
    sample = rand(MersenneTwister(7), distribution, 2000)
    values = collect(0:10)
    exact = pdf.(distribution, values)
    empirical = [count(==(value), sample) / length(sample) for value in values]
    @test sum(empirical) ≈ 1
    z = 10.0
    density = exp(-z^2 / 2) / sqrt(2pi)
    tail = ccdf(Normal(), z)
    @test density * z / (1 + z^2) < tail < density / z
    @test isfinite(logccdf(Normal(), z))
    rows = [[values[i], exact[i], empirical[i]] for i in eachindex(values)]
    data = [
        Dict("type" => "bar", "x" => values, "y" => exact, "name" => "Exact mass"),
        Dict(
            "type" => "scatter",
            "x" => values,
            "y" => empirical,
            "mode" => "markers",
            "name" => "Empirical frequency",
        ),
    ]
    layout = Dict(
        "title" => "Authored Binomial model and 2000 draws",
        "meta" => Dict(
            "description" => "A fixed-seed sample fluctuates around the declared Binomial(10, 0.2) probability mass. These are synthetic draws, not observed population data.",
            "table" => Dict(
                "columns" => ["Value", "Exact mass", "Empirical frequency"],
                "rows" => rows,
            ),
        ),
    )
    show_plotly(
        data;
        layout = layout,
        description = "Binomial simulation and analytic probabilities",
    )
    println("Stable normal-tail probability: ", tail)
end

worked_b()
```

## Reproducibility and inference

Record the distribution, parameters, generator, seed, sample size and Julia/package versions. Separate random variation from floating-point rounding and from a mismatch between the model and the real population. Reproducing a random draw does not establish that the model assumptions are appropriate.

Use independent replications or analytically justified uncertainty methods when assessing Monte Carlo procedures. Repeatedly choosing a seed that gives an attractive result changes the analysis. Retain the complete protocol and avoid treating a successful assertion on one seed as a universal statistical guarantee.

## Diagnose a probability result

Check the support and parameterization of the distribution. A standard deviation is not a variance, and a rate parameter is not always a scale parameter. Use `logpdf` or `logccdf` where appropriate instead of taking a logarithm after a tiny probability has already rounded to zero.

The examples establish explicit-state sampling, analytic comparisons and bounded plotting in the prepared environment. They do not validate a live data-generating process or qualify GPU/distributed simulation. Those extensions require their own numerical, statistical and runtime evidence.


## Six investigations

### 1. State the parameterization

Construct Normal(2,3).

**Expected:** The mean is 2 and variance 9.

**Hint:** The second argument is standard deviation.

### 2. Reproduce a sequence

Create two generators with the same seed and sample the same distribution.

**Expected:** They produce equal arrays in the stated runtime.

**Hint:** Keep generator state explicit.

### 3. Advance the generator

Draw twice from one generator object.

**Expected:** Its state advances and the arrays differ in the fixture.

**Hint:** A seed initializes state; it is not reapplied on every call.

### 4. Scale Monte Carlo work

Increase the draw count by a factor of 4 under independent sampling.

**Expected:** The theoretical mean standard-error scale halves.

**Hint:** Use sigma divided by square root of n.

### 5. Inspect an extreme tail

Compare a survival-function calculation with naive subtraction.

**Expected:** A stable tail API retains a small positive probability.

**Hint:** Avoid cancellation before taking a logarithm.

### 6. Interpret the plot

Compare empirical frequencies with the exact Binomial masses.

**Expected:** Finite simulated frequencies fluctuate around the model probabilities.

**Hint:** Keep the sample size and model assumptions visible.

## Primary references

- [Distributions.jl](https://juliastats.org/Distributions.jl/stable/)
- [Julia random generation](https://docs.julialang.org/en/v1/stdlib/Random/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

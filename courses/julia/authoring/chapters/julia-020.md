## Randomness needs an explicit role

A random-number generator has state. Reusing an object advances that state, while constructing another generator with the same seed can reproduce a sequence under the same implementation. A seed is useful provenance, but it is not a promise of identical draws across every library version, algorithm or hardware environment.

A probability distribution describes a mathematical model. The Distributions package supplies operations such as moments, density, cumulative probability and sampling. Simulated data from a declared distribution can test an algorithm under known assumptions. It is not evidence that an external population follows that distribution.

Monte Carlo error comes from using finitely many draws. For independent draws with variance \(\sigma^2\), the standard error of their mean scales as \(\sigma/\sqrt{n}\). A larger sample improves this theoretical scale, but one particular larger sample is not guaranteed to be closer to the target than every smaller realization.

## Worked case A: compare a sample with a known model

The first example samples a Normal distribution with mean 2 and standard deviation 3 using an explicit generator. A second generator with the same seed reproduces those draws in this runtime. The program compares the sample mean with the analytic mean using a deliberately broad, stated Monte Carlo bound. It also reports the standard-error scale instead of claiming an exact estimate.

{{WORKED_A}}

## Worked case B: probabilities and stable tail calculations

The Binomial example has known mean and variance. An empirical frequency table from a second fixed generator is displayed beside its analytic probabilities through the classroom Plotly helper. The helper writes a bounded chart specification, description and exact table; it is not a standard Julia plotting package.

A normal-tail check also shows why subtracting a cumulative probability from one can lose precision in an extreme tail. The survival function and its logarithm are designed to retain that information. Independent Mills-ratio bounds provide a useful numerical check for the positive tail in this fixture.

{{WORKED_B}}

## Reproducibility and inference

Record the distribution, parameters, generator, seed, sample size and Julia/package versions. Separate random variation from floating-point rounding and from a mismatch between the model and the real population. Reproducing a random draw does not establish that the model assumptions are appropriate.

Use independent replications or analytically justified uncertainty methods when assessing Monte Carlo procedures. Repeatedly choosing a seed that gives an attractive result changes the analysis. Retain the complete protocol and avoid treating a successful assertion on one seed as a universal statistical guarantee.

## Diagnose a probability result

Check the support and parameterization of the distribution. A standard deviation is not a variance, and a rate parameter is not always a scale parameter. Use `logpdf` or `logccdf` where appropriate instead of taking a logarithm after a tiny probability has already rounded to zero.

The examples establish explicit-state sampling, analytic comparisons and bounded plotting in the prepared environment. They do not validate a live data-generating process or qualify GPU/distributed simulation. Those extensions require their own numerical, statistical and runtime evidence.

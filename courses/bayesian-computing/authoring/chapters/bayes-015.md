## A decision can be sensitive to Monte Carlo error

Posterior sampling approximates integrals. A downstream optimizer can amplify a small approximation error when two actions have similar expected utilities. The stability of the selected action therefore needs its own review, even when posterior means appear plausible.

The example observes five count periods 2,3,2,5,4. A Gamma(2,1) prior uses the shape/rate convention. With Poisson observations and unit exposure, the exact posterior is Gamma(18,6), with mean three. Actual PyMC sampling approximates that posterior, providing a computational comparison with a known answer.

Future demand integrates the Poisson likelihood over this gamma posterior, yielding a negative-binomial predictive distribution under the stated parameterization. The program uses that exact distribution as a decision oracle, rather than trusting a finite simulation to choose the final action automatically.

## Worked case 1: optimize an exact posterior predictive cost

Underage costs four per unit and overage costs one. Candidate quantities range from zero through ten. The code evaluates expected cost under the exact predictive mass function, including enough count support that omitted tail mass is negligible for this fixture. The optimal quantity is four.

The posterior mean rate is three, which is not the optimal inventory quantity for this asymmetric loss. Parameter uncertainty and future count variation both enter the predictive decision. A point estimate alone cannot reproduce that calculation.

The exact result is conditional on the count model, prior, exposure and cost ratio. It does not establish that a real demand process is independent Poisson or that the same costs apply during a capacity shortage. Those scientific and operational assumptions should accompany the optimized quantity.

## Worked case 2: compare a short-chain simulation decision

The program also generates predictive demand from the sampled rates and computes empirical expected costs. Its selected quantity can differ by one from the exact oracle under the deliberately small sampling budget. The output explicitly reports whether it differs, the Monte Carlo cost discrepancy and the regret of that simulated action under the exact predictive model.

A different selected action does not require a dramatic error in the posterior mean. Near an optimum, two actions may have similar values, so noise can reverse their order. The example retains that disagreement as a diagnostic instead of increasing the budget or changing a seed until the desired action appears.

For this tractable case, the reported oracle action provides the final model-based choice. In an intractable case, investigate target-specific Monte Carlo errors, repeated runs, analytic integration of parts of the loss, common random numbers or other variance-reduction methods. The goal is sufficient precision for the decision, not a generic number of posterior draws.

## Diagnose each source of uncertainty separately

There is sampling uncertainty about the unknown rate, outcome randomness conditional on that rate, Monte Carlo error in approximating the posterior and predictive integrals, and uncertainty about the model and costs. These have different remedies. Collecting more data does not directly repair a poor sampler; drawing more samples does not validate a misspecified demand process.

A decision report should include the expected-value gap between plausible actions and how accurately that gap has been calculated. If the gap is negligible compared with operational costs or model uncertainty, a stable simpler action may be reasonable. That is a decision judgment that should be made explicitly.

The finite program uses a fixed seed for reproducibility, but a fixed seed is not a guarantee of accuracy. Review the actual diagnostics and the exact-oracle discrepancy. Short-run R-hat or effective-size summaries can look acceptable for one parameter while the expected loss difference remains imprecise.

## Answered scientific discussion

**Should an analyst always rerun until the simulated action matches an expected answer?** No. That selects favorable numerical noise. Use independent oracles where available, state a precision criterion and improve the computation transparently.

**What transfers to a larger optimization system?** Preserve posterior uncertainty through the relevant loss, evaluate the precision of action comparisons, record the chosen rule and retain a rollback or reassessment condition. A successful sampling command is only one component of that scientific decision process.

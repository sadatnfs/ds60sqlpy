## Treatment-confounder feedback changes the analysis

Longitudinal decisions occur repeatedly. A variable measured between decisions can be affected by earlier treatment and also influence later treatment and the final outcome. It is then both a mediator of an earlier intervention and a confounder for a later one. A single baseline adjustment formula generally does not describe this structure.

Use \(L_0\) for a baseline state, \(A_0\) for the first decision, \(L_1\) for an intermediate state, \(A_1\) for the second decision and \(Y\) for the final outcome. A dynamic policy \(d\) maps the observed history at each decision time into an action. Under consistency, sequential exchangeability and positivity, a two-step g-formula averages over the intermediate state distribution induced by that policy:

\[
\mathbb{E}[Y^d]=\sum_{l_0,l_1}
\mathbb{E}[Y\mid l_0,d_0(l_0),l_1,d_1(l_0,l_1)]
P(l_1\mid l_0,d_0(l_0))P(l_0).
\]

The order matters. The policy's first action changes the distribution of the later state. Reusing the untreated distribution of \(L_1\) while assigning treatment at both times would answer a different, partially controlled question.

## Worked case 1: enumerate static and dynamic regimes

The baseline state is binary with equal probabilities. The probability of the intermediate state is \(.2+.3L_0+.2A_0\). The final outcome mean is \(1+2A_0+3A_1+L_0+2L_1\). The program enumerates every baseline and intermediate state, applies the requested policy and averages the resulting outcome using the correct state probabilities.

Never treating has value 2.2. Always treating has value 7.6. The dynamic policy treats initially when the baseline state is one and later when the intermediate state is one; its value lies between the two static regimes. These exact values are calculations under a known mechanism, not fitted causal effects from observed data.

The callback accepts the decision time and the history available at that time. At time zero, no value of \(L_1\) has been observed. A policy that uses a future state for its initial decision is not an implementable dynamic regime. The signature makes that information boundary visible even in a small example.

## Worked case 2: freeze the intermediate distribution

The always-treated policy adds five units through the direct treatment terms. It also raises the probability of \(L_1=1\) by .2; because \(L_1\) adds two outcome units, that pathway contributes another .4. Adding only five to the never-treated value therefore understates the always-treated value by .4.

This difference illustrates why adjusting away a treatment-affected covariate is not a neutral statistical operation. The direct, indirect, controlled and total effects require separate definitions and assumptions. A regression coefficient conditioned on the intermediate state should not automatically be reported as the total effect of a sustained treatment regime.

The example uses two time points so every probability can be inspected. More time points increase the number of possible histories. Parametric g-computation then fits models for the changing covariates and outcomes and simulates trajectories under specified policies. Model misspecification can accumulate over time, and support can deteriorate for rarely observed action sequences.

## From enumeration to an analysis protocol

Define decision times, available history, treatment versions, adherence and follow-up before choosing an estimator. Determine whether death or another competing event terminates future treatment and how that changes the outcome definition. A regime requiring an action after a terminal event is not well-defined unless a different counterfactual question is explicitly constructed.

When fitting a g-formula, assess the natural-course simulation as a diagnostic: does the fitted system reproduce important observed trajectories when it follows observed treatment behavior? Agreement can reveal obvious model defects, but it does not verify absence of unmeasured confounding or guarantee accurate extrapolation under a new policy. Report both the simulated target and the diagnostics that support the computational model.

Avoid interpreting a single simulated trajectory as a prediction interval. Monte Carlo variation from a finite number of simulated histories is different from uncertainty in estimated model parameters and identification assumptions. Repeat simulation or use analytic enumeration to control numerical error, then address those other uncertainties separately.

## Answered scientific discussion

**Why not include every time-varying variable in one regression?** Some of those variables lie on treatment-induced pathways. Conditioning can block part of the effect or create selection. The g-formula models the ordered data-generating process and then averages over the policy-induced covariate distribution.

**Can a dynamic policy be preferable to always treating even with a smaller outcome mean?** Yes. Treatment may have costs, burdens or harms. Define the utility and constraints before comparing policies; maximizing the particular synthetic outcome is only one possible decision objective.

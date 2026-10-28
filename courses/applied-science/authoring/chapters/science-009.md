## Prediction quality depends on the decision

Squared error favors the conditional mean. Absolute error favors a conditional median. An asymmetric decision loss can favor another quantile. The choice is not merely a scoring convention: it expresses which mistakes matter for the downstream action.

Suppose quantity \(q\) is chosen before demand \(D\) is known. Underage costs \(c_u\) per missing unit and overage costs \(c_o\) per excess unit. The loss is

\[
L(q,D)=c_u(D-q)_+ + c_o(q-D)_+.
\]

For a continuous demand distribution, minimizing expected loss gives a quantile with level \(\tau=c_u/(c_u+c_o)\). With discrete demand, multiple quantities can share an optimum and the appropriate inequality formulation should be used. Costs, constraints and timing must be stated before this result is treated as a recommendation.

## Worked case 1: choose an asymmetric-loss quantity

The synthetic demand observations are 0,1,1,2,3,8. Underage costs four and overage costs one, giving \(\tau=.8\). The code evaluates every integer quantity from zero through eight and finds that three minimizes the empirical decision loss. It independently verifies the identity between this loss and a scaled pinball loss:

\[
\rho_\tau(u)=\max\{\tau u,(\tau-1)u\},\qquad
L(q,D)=(c_u+c_o)\rho_\tau(D-q).
\]

The empirical mean demand is 2.5. It is a sensible squared-error prediction but has a larger cost for this particular asymmetric decision. A model can therefore improve RMSE and still worsen the action that matters. Conversely, optimizing a quantile loss does not establish that the cost ratio or empirical demand distribution is correct for deployment.

The fixture has a large upper-tail observation to make the asymmetry visible. It contains only six observations, so the empirical optimum is unstable evidence about an external demand population. A proper deployment analysis would investigate parameter uncertainty, covariates, nonstationarity, capacity constraints and the reliability of the stated cost ratio.

## Worked case 2: aggregate coverage hides horizon failure

The program records interval coverage separately for two horizons. The first horizon covers all five synthetic outcomes; the second covers only two. Averaging the ten indicators obscures the different behavior. A headline coverage rate can similarly mix groups, seasons, horizons and operating regimes whose uncertainty properties differ.

Calibration asks whether predicted probabilities or intervals agree with appropriate outcome frequencies. Sharpness concerns how concentrated those predictions are. A very wide interval can achieve high empirical coverage while offering little decision value. A narrow interval can look informative while badly under-covering. Examine both, using evaluation units that match the repeated forecasting procedure.

Prediction intervals concern future outcomes, while confidence intervals concern an estimated parameter or mean. Parameter uncertainty is often only one contribution to predictive uncertainty. Using a narrow coefficient interval as a forecast interval can ignore irreducible outcome variation, temporal dependence or future covariate uncertainty.

## Evaluate a full forecast-to-decision procedure

Separate data used to fit a forecast distribution, data used to choose a cost-sensitive rule, and data used to evaluate the resulting policy. If the cost ratio or threshold is optimized against the final test outcomes, the reported decision performance is selected on its own assessment set.

Compare against an operational baseline, such as a fixed stock level or the current planning rule. Record not only average cost but also tail events, constraint violations and subgroup outcomes. A policy with slightly lower mean cost can still produce unacceptable service failures. Constraints may require optimization beyond the simple one-period quantile rule.

Stress-test the rule under changed costs and distributional scenarios. Demand may respond to the action, capacity can couple several products, and leftover units can carry into later periods. Those mechanisms change the decision problem. The simple newsvendor model is a useful derivation precisely because its assumptions can be stated and then deliberately relaxed.

## Answered scientific discussion

**Should the chosen quantity equal the .8 sample quantile returned by every library?** Quantile interpolation conventions differ for small discrete samples. Directly calculating the stated loss, as the program does, exposes ties and verifies the actual decision objective.

**Can a forecast be called calibrated from ten checks?** Ten outcomes provide a very coarse diagnostic. The table demonstrates how aggregation can conceal a problem; it is not a precise calibration assessment. Report uncertainty, dependence and the intended forecasting population before making a broad claim.

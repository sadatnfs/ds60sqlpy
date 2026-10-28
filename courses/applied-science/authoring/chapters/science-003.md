## Sensitivity is a question with an explicit scale

An assumption is not validated merely because a regression converged. Sensitivity analysis asks how much a specified violation would change a conclusion. Its value comes from defining the violation carefully enough that another person can inspect the scenario. A table of many model specifications is not automatically a sensitivity analysis if no specification corresponds to a meaningful alternative mechanism.

This tutorial uses a deliberately simple additive model. Let an omitted binary variable \(U\) shift outcomes by \(\gamma\), and let its prevalence differ between observed treatment groups by \(\Delta p\). Under this stylized structure, the omitted-variable contribution to the crude difference is \(\gamma\Delta p\). An adjusted scenario is

\[
\tau(\gamma,\Delta p)=\Delta_{\mathrm{observed}}-\gamma\Delta p.
\]

The expression requires an additive, constant confounder effect and an appropriate interpretation of the prevalence contrast. It is not a universal correction for arbitrary nonlinear models, multiple confounders or time-varying treatment. Its simplicity makes the assumption visible rather than making it universally valid.

## Worked case 1: locate a tipping point

The observed contrast is three. The program evaluates four prevalence differences and four confounder effects. If the prevalence difference is .5 and the confounder effect is six, the adjusted scenario is zero. A prevalence difference of .75 with the same strength reverses the sign. Zero prevalence imbalance leaves the observed contrast unchanged, providing an independent boundary check.

The grid is not a posterior distribution over plausible hidden confounding. Every cell is a user-specified scenario. Scientific judgment, external evidence or measured proxy variables may help assess whether a cell is plausible. The program deliberately prints the entire grid instead of selecting a single attractive corrected estimate.

A useful report identifies the smallest practically relevant effect, not only zero. An intervention costing more than its likely benefit can be unattractive while its effect remains positive. Thus a tipping point for a deployment decision may differ from a tipping point for statistical significance or sign. Confidence intervals should also reflect sampling uncertainty around the observed contrast; the deterministic grid isolates the assumed bias mechanism only.

## Worked case 2: a negative control reveals a problem

A **negative-control outcome** is chosen because the treatment cannot plausibly cause it under the proposed mechanism, while it may share sources of confounding or measurement bias with the outcome of interest. The program supplies a known zero-effect negative control that depends on an unmeasured variable. Its observed treatment contrast is positive. The association flags that the naive comparison is not automatically causal.

A negative control is not a magical correction variable. Its exclusion argument, timing and relationship to the relevant bias mechanism must be justified. A positive association can arise from shared confounding, selection, measurement error or a faulty exclusion claim. A null association can occur because the control is insensitive to the bias that matters. The appropriate conclusion is narrower: this diagnostic supports or challenges specific assumptions.

The final calculation introduces classical measurement-error attenuation. With reliability .5 and true slope two, the simplified attenuated slope is one. This mechanism is separate from unmeasured confounding. Combining the two requires a joint model rather than adding unrelated correction factors. It is useful to list each source of uncertainty and bias before deciding which sensitivity analysis addresses it.

## Build a defensible sensitivity record

Keep the observed estimate, the assumed bias model, parameter units, ranges and decision threshold in a small ledger. For each range, state whether it comes from substantive knowledge, validation data, a deliberately conservative bound or convenience. If a parameter describes an odds ratio while the formula expects an additive outcome difference, the resulting grid has no coherent interpretation.

Distinguish uncertainty about an estimate from uncertainty about a model. A bootstrap may approximate sampling variability under the observed data-generating structure. It does not automatically explore unmeasured confounding, incorrect outcome definitions or missing mechanisms. Sensitivity scenarios complement sampling intervals by making those additional assumptions explicit.

A useful visualization would put prevalence imbalance and confounder effect on the axes, shade the adjusted effect, and mark the decision boundary. Its caption must say that the surface is conditional on an additive bias model. Smooth colors should not make arbitrary assumptions appear empirically estimated.

## Answered scientific discussion

**Does robustness across several regressions establish causality?** It can show stability under those specifications. If every specification shares the same invalid adjustment set, that stability can coexist with substantial bias.

**What is a responsible conclusion here?** Report the observed result, the scenarios that change the decision, and the substantive case for or against those scenarios. The code verifies the stated arithmetic. It does not tell us which hidden-confounding scenario describes an external population.

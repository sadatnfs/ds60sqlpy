## Competing events change the meaning of risk

A competing event prevents the event of interest from occurring in the same way. For example, two mutually exclusive failure modes may terminate a component's lifetime. The probability of one cause depends on survival from all causes up to each event time, not only on that cause's hazard.

For event time \(t_j\), let \(d_{kj}\) count events from cause \(k\), and let \(n_j\) be the risk set. A cumulative-incidence increment is

\[
\Delta F_k(t_j)=S(t_j^-)\frac{d_{kj}}{n_j},
\qquad
S(t_j)=S(t_j^-)\left(1-\frac{\sum_k d_{kj}}{n_j}\right).
\]

The previous survival factor includes every failure cause. A cause-specific hazard describes an instantaneous rate among units still event-free; cumulative incidence describes an absolute probability. They answer related but different questions.

## Worked case 1: reconcile cause probabilities

Four units fail sequentially from causes 1,2,1,2, with no censoring. The program accumulates each cause's incidence while updating survival for all failures. The result is .5 for each cause and zero remaining survival. These values agree with the observed proportions because follow-up is complete, giving a simple independent oracle.

Now treat cause-two events as censoring and compute one minus a cause-one Kaplan-Meier survival curve. The result is .625, larger than the actual .5 cumulative incidence. This calculation estimates a different hypothetical quantity under additional assumptions. It is not the observed probability of cause-one failure in the presence of the competing event.

Cause-specific regression can still be useful, but predicted risks must combine the relevant cause-specific hazards. A subdistribution-hazard model uses a different risk-set construction and parameter interpretation. Choosing between them should follow the target and scientific assumptions, not a rule that one software command is always preferable.

## Worked case 2: test whether one coefficient fits two periods

The second fixture simulates 400 units with a binary covariate whose log hazard ratio is \(+1\) before time 1 and \(-1\) afterwards. Each unit's event time comes from inverting its piecewise-constant cumulative hazard, and every unit has an observed event. A single Cox model with one constant coefficient, fitted with statsmodels `PHReg`, reports a log hazard ratio of about 0.54. That number is a weighted compromise between two opposite effects; it describes neither period.

To test the constant-coefficient assumption directly, the program splits each unit's follow-up at time 1 into episodes. Every unit contributes \((0,\min(t,1)]\), with an event only if it failed by time 1, and a unit still at risk after time 1 contributes a second, delayed-entry episode \((1,t]\). The model then includes the covariate and its product with an after-split indicator:

\[
h(t\mid x)=h_0(t)\exp\{\beta_1x+\beta_2x\,\mathbf 1(t>1)\}.
\]

Here \(\beta_1\) is the log hazard ratio before time 1 and \(\beta_1+\beta_2\) the log hazard ratio afterwards, so \(\beta_2\) measures how far one constant coefficient fails to describe both periods. The fit gives \(\widehat\beta_1\approx0.86\) and \(\widehat\beta_2\approx-1.68\) with standard error about 0.30, a later log hazard ratio near \(-0.82\). The program asserts that the change is negative and more than three standard errors from zero. The estimates do not equal the generating values exactly because 400 simulated units give finite-sample error, and only 96 units remain at risk after time 1.

Scaled Schoenfeld residuals are the usual graphical companion to this test: in a Cox model they compare each event's covariate value with its risk-set expectation, and their smoothed trend against time approximates how the coefficient changes. The episode-split interaction is the formal version of one such pattern, with a declared change point. Choosing the split after looking at the residuals would make the test optimistic, so a scientific analysis should state the candidate time pattern in advance.

A lack of a visible pattern does not prove proportional hazards, especially with few events. It may be useful to estimate time interactions, stratify an appropriate variable or choose another model. Each alternative changes what can be interpreted directly. Stratification, for example, can allow different baseline hazards while sacrificing a single coefficient for the stratifying variable.

## Model evaluation follows the target

Discrimination, calibration and utility are distinct. Ranking event times correctly does not guarantee accurate cause-specific risk at a horizon. A model may be well calibrated overall while performing poorly in an important subgroup. Evaluate censoring-aware metrics with assumptions appropriate to their estimators and report the horizon and population.

Competing events also complicate causal questions. An intervention may affect the event of interest and the competing event simultaneously. An apparent reduction in one cause can arise through a change in competing-event occurrence. Controlled direct effects, separable effects and total effects require distinct definitions and assumptions. This tutorial establishes probability accounting, not identification of every intervention contrast.

Keep the event dictionary explicit. A terminal event, temporary loss of observation and a change of state that allows later transitions are different objects. If units can move through several states and return, a multi-state model may describe the process more faithfully than a single competing-risk endpoint.

## Answered scientific discussion

**Why must cause incidences and survival be reviewed together?** Their relationship checks whether probabilities describe mutually exclusive outcomes coherently. An impossible sum can reveal a data, risk-set or modeling error before any scientific interpretation is attempted.

**Does a significant proportional-hazards diagnostic tell us which model is correct?** It identifies evidence against a particular restriction. It does not select the replacement mechanism automatically. Use the scientific time process, observed patterns, validation and the desired prediction or effect target to choose a defensible continuation.

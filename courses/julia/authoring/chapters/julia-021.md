## The fitted object includes a procedure

A regression example needs an observation unit, input schema, training rule and evaluation target. Correct matrix arithmetic cannot determine whether the rows are representative or the features were available at prediction time. The small fixture here makes the fitting and selection boundaries explicit before those scientific questions are generalized.

The design matrix contains an intercept column and one predictor. Ridge regularization penalizes the slope while leaving the intercept unpenalized. The objective is a squared residual sum plus \(\lambda\beta_1^2\). Its numerical scale depends on whether a sum or mean reduction is used, so the same numerical lambda is not automatically equivalent under another convention.

The implementation solves an augmented least-squares system instead of forming normal equations solely to invert them. Normal equations can square a conditioning problem. The fixture is tiny, but preserving a sound formulation makes it easier to extend without teaching an avoidable numerical shortcut.

## Worked case A: recover a known line

The first dataset follows an exact line. With no penalty, the fit recovers its intercept and slope and predicts two new input values. The known equation supplies an independent expected result. This is a software and arithmetic check, not a statistical confidence statement from noisy observational data.

{{WORKED_A}}

## Worked case B: select on development data

The second training set contains an authored perturbation. Four candidate penalties are compared using development outcomes. The selected penalty is then evaluated on a separate final pair. Changing final labels must not change which penalty was selected. The program checks the selected value and exact rational expressions for its fitted coefficients and errors.

{{WORKED_B}}

## Preserve information boundaries

Any learned transformation belongs inside the corresponding training or development procedure. Using all data to choose a normalization, feature set or threshold can leak information even when the final regression call receives only training rows. Time-dependent tasks also need the availability rules from the preceding unit.

A final test measures the selected procedure under its stated population and sampling assumptions. If it motivates another model change, it has been consumed for development or regression testing. Keep a separate assessment for the changed procedure instead of continuing to call the same labels untouched evidence.

## Diagnose a model result

Inspect coefficients, residuals, input ranges and leverage before treating a favorable error as reliable. A regularized model trades fit against a penalty chosen for a purpose. It does not make a poor data contract scientifically valid. An unpenalized rank-deficient design is rejected by this teaching helper rather than given an unexplained coefficient interpretation.

The two final test rows are far too few for a broad generalization claim. The exact expected errors are useful because the data were authored; real data would require suitable uncertainty, group/time splits and diagnostic work. Keep the small fixture's evidence boundary visible when transferring the code.

This unit uses only prepared standard linear algebra and statistics. More specialized Julia modeling packages require their own environment and API contracts. The following units add automatic differentiation and a prepared optimization library while retaining the same separation between numerical execution and scientific interpretation.

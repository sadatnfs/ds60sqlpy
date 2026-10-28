## More features can change identification

When the number of predictors exceeds the number of observations, several coefficient vectors can produce the same fitted values. A numerical solver may select one vector by a convention or penalty, but that does not make every coefficient scientifically identified.

For a linear model \(y=X\beta+\epsilon\), the design matrix's rank determines which linear combinations are supported by the observed predictors. Ridge regression adds a quadratic penalty and, for positive \(\lambda\), solves

\[
\widehat\beta_\lambda=(X^{\mathsf T}X+\lambda I)^{-1}X^{\mathsf T}y.
\]

The code uses a linear solve. The penalty can stabilize prediction, but it introduces shrinkage and depends on feature scaling. A unique penalized solution is a consequence of the optimization problem, not proof that each predictor has a separate causal interpretation.

## Worked case 1: interpolation does not establish generalization

The synthetic design has 20 observations and 40 predictors, with signal in only the first three coordinates. A minimum-norm least-squares solution interpolates the training outcomes to numerical precision. Its ability to reproduce the observed labels is therefore a weak criterion for selecting a predictive procedure.

A ridge model with a prespecified penalty is evaluated on 50 independent synthetic feature rows. The test error remains positive despite the near-zero interpolation error available in training. The program does not claim that this penalty is optimal. It separates a numerical fitting property from a prediction property under a new sample.

The fixture has a known coefficient vector, making its noiseless test signal available as an oracle. In an external dataset, that signal is not observed. Evaluation typically concerns noisy outcomes, and a test set must match the intended prediction population. Choosing the penalty using those test outcomes would consume the test set as part of model selection.

## Worked case 2: duplicated predictors identify only a sum

The second design has two identical columns. Coefficients \((1,2)\) and \((2,1)\) produce exactly the same fitted values. The matrix has rank one. The code verifies both facts without an optimizer.

An algorithm may nevertheless report one coefficient vector with many decimal places. The reported precision does not resolve the underlying nonidentifiability. A symmetric penalty can select a symmetric solution, while another parameterization or constraint can select something else. Predictions along the observed feature relationship may be stable even when individual coefficients are not.

This distinction matters for feature importance and scientific interpretation. Correlated variables can exchange apparent importance, and selection can be unstable. A variable omitted by one fitted model is not necessarily irrelevant. Its information may be represented through correlated features, or the procedure may lack enough evidence to distinguish alternatives.

## Evaluate the full selection procedure

Preprocessing, feature filtering, scaling, hyperparameter search and model fitting belong inside the training side of an evaluation design. Applying a label-informed filter before cross-validation leaks information into every fold. Even unsupervised transformations should be considered in relation to the actual deployment procedure and data availability.

Nested evaluation can separate selection from assessment, but it does not eliminate uncertainty when the effective sample size is small. Report the resampling unit, selection budget, performance distribution and stability of decisions. Repeatedly inspecting the same evaluation results to invent new features creates additional selection beyond the nominal tuning loop.

High-dimensional inference after variable selection requires additional methods and assumptions. Ordinary regression intervals calculated after a data-driven selection step do not automatically have their usual interpretation. Debiased estimates, selective-inference approaches and sample splitting address different problems; each should be taught through a precise target and conditions rather than as a universal correction.

## Answered scientific discussion

**Can ridge make a singular scientific question identifiable?** It makes a specified penalized optimization problem well-posed. Scientific identification still depends on the information and assumptions supporting the target. The distinction is visible in the duplicated-column example.

**Why not report only test error and ignore coefficients?** That may be appropriate for a bounded prediction task. If a decision requires explanations, transport, causal effects or feature interventions, the instability and meaning of coefficients become relevant again. Define the use before deciding which model properties matter.

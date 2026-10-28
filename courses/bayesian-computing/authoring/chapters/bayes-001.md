## Begin with a generative question

Bayesian inference conditions a probability model on observations. The model describes possible unknown states and how observations arise under each state. A prior describes uncertainty before the specified evidence; a likelihood describes the observation mechanism. Their product is normalized to obtain a posterior. These ingredients should be explained in the language of the scientific question before they become library calls.

For a finite set of hypotheses \(H_j\) and evidence \(E\),

\[
P(H_j\mid E)=\frac{P(E\mid H_j)P(H_j)}{\sum_kP(E\mid H_k)P(H_k)}.
\]

The denominator is the model's probability of the evidence. It is not an arbitrary scaling constant when comparing models, although posterior ratios within one fixed model can often avoid calculating it explicitly. A posterior probability is conditional on the supplied model, including its hypothesis set and observation process.

## Worked case 1: update a fault-detector hypothesis

The synthetic hypotheses are normal operation and a fault, with prior probabilities .8 and .2. A positive signal has probabilities .1 and .9 under those hypotheses. The posterior fault probability is \(.18/(.08+.18)=9/13\), about .692. A 90% sensitivity-like number alone would not provide this posterior because the baseline prevalence and false-positive behavior also matter.

The program validates matching hypothesis shapes, normalized nonnegative prior mass and finite likelihood values. If the model assigns zero probability to the evidence under every hypothesis, normalization is impossible. Replacing the zero with an epsilon would conceal a model failure rather than provide a principled update.

Posterior odds provide a second independent calculation. Prior odds .25 are multiplied by a likelihood ratio of nine, yielding posterior odds 2.25. Converting those odds to a probability returns the same 9/13. This is a useful check of ordering and of which hypothesis belongs in the numerator.

## Worked case 2: repeated evidence is not automatically new evidence

If two signals are conditionally independent given the hypothesis, their likelihoods multiply. The posterior fault probability becomes 81/85, approximately .953. If the second signal is instead a perfect duplicate of the first recorded signal, it supplies no new information and the posterior remains 9/13.

Both calculations can be implemented without a software error. The difference is the dependence assumption. A duplicated database row, a cached model response or two metrics derived from the same underlying event can be counted as independent evidence accidentally. The posterior may then become much more confident without any corresponding increase in information.

Conditional independence is a modeling statement, not a property that follows from storing records in separate files. Two sensors can share a failure source, and repeated measurements can share a latent state. A richer model may need to represent those dependencies directly. It should not merely divide the likelihood by an unexplained correction factor after noticing an implausibly narrow posterior.

## What the probabilities do and do not mean

The prior is not necessarily a subjective guess without evidence. It may encode previous measurements, physical constraints, population information or a deliberate regularization choice. Its origin and scale should be stated. Reusing the same observations to construct a prior and then including them again in the likelihood can duplicate evidence unless the joint procedure is modeled explicitly.

The likelihood is also an assumption. Misclassification, selection, censoring and dependence belong to the observation process. A carefully chosen prior does not repair an incorrectly specified likelihood automatically. Posterior predictive checks later in the course examine whether the model reproduces relevant features of the observations.

The two-hypothesis fixture makes all alternatives visible. A real system may fail in a way absent from its modeled hypotheses. A high posterior probability for one listed hypothesis does not prove that the list is complete. Keep model adequacy and uncertainty within a model separate.

## Answered scientific discussion

**Why can a positive signal still leave substantial uncertainty?** The signal is combined with the prior frequency and its behavior under both hypotheses. Bayes' rule exposes that accounting instead of equating a classifier characteristic with a case-specific probability.

**What should be recorded before updating?** Record the hypotheses, prior, observation definition, likelihood and dependence assumptions. Then retain the exact evidence used. The program checks finite-probability arithmetic; an external application still needs evidence that the modeled observation mechanism is appropriate.

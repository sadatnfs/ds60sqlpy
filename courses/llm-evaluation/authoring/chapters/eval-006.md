## Preserve the pairing and the dependence

Two systems should answer the same eligible requests when the goal is a paired comparison. For request \(i\), define \(d_i=C_{B,i}-C_{A,i}\). The average difference answers a paired question and can have lower variance than comparing two independent sample means because request difficulty affects both systems. Dropping a failed response from only one system breaks that pairing and can create selection bias.

Dependence remains after pairing. Ten paraphrases of one question can share nearly all their difficulty and evidence. If families are sampled independently, a family-level mean difference can be the appropriate resampling unit. Decide whether the target weights families equally or requests equally; aggregation and resampling must both match that estimand.

A paired sign-randomization calculation changes the sign of each difference under a null that permits swapping system assignments within the relevant units. For an observed statistic \(T\), an exact two-sided tail probability on a finite randomization space is the fraction of allowed assignments with \(|T^*|\geq |T|\). That null requires a justified exchangeability or randomization argument. An arbitrary observational pair of deployed systems is not automatically a randomized experiment.

## Worked case A: enumerate the small null

With paired differences `[1,1,1,-1]`, the observed mean is 0.5. Enumerating all 16 sign assignments produces the exact finite reference distribution. Ten assignments have an absolute mean at least 0.5, giving 0.625. This deliberately modest result shows why a favorable average is not equivalent to strong evidence against the stated null.

The code enumerates rather than simulates, so there is no Monte Carlo error. Enumeration does not remove sampling uncertainty, selection bias, invalid exchangeability or multiple-comparison problems. It only computes this small reference distribution exactly.

{{WORKED_A}}

## Worked case B: a cluster bootstrap has limited information

Family means `[-1,1]` give an equal-family mean of zero. Drawing two families with replacement yields only the means-1,0,1, with probabilities one quarter, one half and one quarter. Using the empirical inverse-CDF quantile rule, the central 95% interval spans -1 to 1. Adding repeated rows within a family cannot create new independent families.

The case also contrasts the variance of row differences with the variability of family means. A narrow row-level interval can be misleading when the repeated rows share common causes. Conversely, aggregating to families changes the weighting if families have unequal sizes. Neither method is universally correct; the data-generating and sampling assumptions determine the choice.

{{WORKED_B}}

## Interpret uncertainty without changing its target

A bootstrap interval is conditional on the observed sample and the resampling design. With two families it has little ability to describe unseen family heterogeneity. More resamples only estimate the same empirical distribution more accurately. More independently sampled families provide new information. Distinguish these two kinds of additional work when planning an evaluation budget.

Report the number of pairs, family sizes, pairing losses and the complete interval construction. State whether the interval is percentile, basic, BCa or based on another approximation. Automatic software defaults are part of the analysis specification. If some categories have zero eligible observations, a bootstrap cannot manufacture their outcomes.

## Error diagnosis and scientific transfer

Check a few paired differences manually and then reconstruct the aggregate from the stored ledger. A nonzero difference between a row mean and a family mean can be a valid consequence of weights, not a numerical defect. An interval that changes dramatically when a single family is removed is evidence of limited independent support.

For an actual assistant comparison, retain both outputs, label versions, task families and the system-selection protocol. Use a held-out final set after choosing prompts and thresholds. The calculations here are tests of a finite authored case; a deployment conclusion also needs representative sampling, justified labeling and separate critical-risk evidence.

## A posterior predicts through a distribution

For independent Bernoulli outcomes with unknown success probability \(p\), a beta prior is conjugate. Starting from \(p\sim\operatorname{Beta}(a,b)\), observing \(s\) successes in \(n\) trials gives \(p\mid y\sim\operatorname{Beta}(a+s,b+n-s)\). Conjugacy provides exact calculations against which more general computation can be checked.

The prior's concentration controls how much it favors particular probability ranges. It is sometimes described using pseudo-count language, but those quantities are not necessarily real independent observations. The origin of a prior and the evidence already incorporated in it must remain explicit.

Posterior prediction averages the sampling model over posterior uncertainty. It is not generally equivalent to inserting a posterior mean into the likelihood. The distinction matters for tail probabilities, uncertainty and decisions.

## Worked case 1: derive the beta-binomial prediction

A Beta(2,2) prior and eight successes in ten trials produce a Beta(10,4) posterior. For \(K\) successes in five future trials, the integrated probability is

\[
P(K=k\mid y)=\binom{5}{k}\frac{B(10+k,4+5-k)}{B(10,4)}.
\]

The program calculates these probabilities using log gamma and log beta functions, avoiding unnecessarily large factorials. It checks that they sum to one and that the predictive mean is five times the posterior mean probability.

The integrated predictive variance is larger than the variance from a Binomial(5,10/14) distribution. The latter treats the estimated probability as known. The law of total variance makes the missing component visible:

\[
\operatorname{Var}(K\mid y)=
\mathbb{E}[\operatorname{Var}(K\mid p,y)\mid y]
+\operatorname{Var}(\mathbb{E}[K\mid p,y]\mid y).
\]

The second term represents uncertainty in the parameter that also affects future outcomes. More data can reduce it, but it is not removed simply because a posterior mean is easy to report.

## Worked case 2: duplicate a batch of observations

The same ten outcomes are now mistakenly counted twice. The resulting update is Beta(18,6). Its parameter variance is smaller than the correct Beta(10,4) variance, and its mean also changes because the prior has been given less relative weight. The program records both variances.

That update would be appropriate for a genuine additional independent batch with the same observed counts under the same model. It is inappropriate for duplicate rows, repeat ingestion or cached evidence representing the original batch. The mathematical formula cannot determine which situation occurred.

This is one reason to preserve record identities and the data-processing path used by a model. A posterior can become more confident after a pipeline bug that multiplies rows in a join. The code can be numerically correct while its likelihood counts the wrong number of independent outcomes.

## Examine the exchangeability assumption

The simple Bernoulli model uses one common probability. Outcomes varying systematically by group, time or exposure may need a richer model. A hierarchy can allow related probabilities while sharing information; a temporal model can represent changing behavior. A beta-binomial predictive distribution from one fixed probability should not be treated as a universal model for all overdispersed binary data.

Prediction also requires a target horizon and population. Five new trials from the same modeled process differ from five trials after a policy change or in a new population. An intervention can change both the success mechanism and which units are observed. Those changes need assumptions beyond the conjugate update.

Small exact models are valuable because their full probability distributions can be inspected. Compare the entire predictive mass function rather than only its mean. Two models can agree on an expected count while disagreeing on a rare but consequential outcome.

## Answered scientific discussion

**Is plug-in prediction always unacceptable?** It can be a useful approximation when parameter uncertainty is negligible for the decision. The approximation should be assessed rather than assumed. Here the exact distribution exposes the omitted variance directly.

**What does conjugacy buy us?** It provides an analytic posterior and a clear numerical oracle. It does not validate independent trials, stable probabilities, correct record counts or the relevance of the future prediction target.

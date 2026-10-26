# Generalization guarantees have a population and a hypothesis class

Tutorial ID: `statistics-learning-008`. Prerequisites: `statistics-learning-002`, `statistics-learning-007`, `statistics-019`. Complete program: [learning_08.py](examples/learning_08.py).

## Separate three errors

Approximation error comes from restricting the model family. Estimation error comes from choosing a model using a finite sample. Optimization error comes from not finding the desired empirical objective minimum. A flexible model can reduce approximation error while increasing estimation difficulty; a converged optimizer addresses only the last part. Distribution shift is another issue because the risk target itself may change.

Let \(R(h)=\mathbb E[\ell(h(X),Y)]\) be deployment risk and \(\widehat R_n(h)\) its average over independent identically distributed training observations. Assume loss lies in [0,1] and a finite hypothesis set \(\mathcal H\) of size \(M\) is fixed independently of those observations. Hoeffding plus a union bound gives

\[
\Pr\left(\sup_{h\in\mathcal H}|\widehat R_n(h)-R(h)|>\epsilon\right)
\le 2M e^{-2n\epsilon^2}.
\]

Solving at failure probability \(\delta\) yields \(\epsilon=\sqrt{\log(2M/\delta)/(2n)}\). Uniformity matters because the selected hypothesis depends on the data. For empirical risk minimization, adding and subtracting empirical risks gives excess risk at most \(2\epsilon\) relative to the best member of the fixed class on that event.

## Work a risk oracle

Generate \(X\) uniformly on [0,1] and \(Y\mid X=x\) as Bernoulli \(.2+.6x\). A threshold predicts one when \(x\ge t\). Integrating its two error regions gives

\[
R(t)=\int_0^t(.2+.6x)\,dx+\int_t^1(.8-.6x)\,dx
=.5-.6t+.6t^2.
\]

The best threshold is .5 with risk .35. The program fixes 41 thresholds before sampling 1,000 rows, selects empirical risk's minimum, and reports the actual risk from the integral. It checks the bound on this particular realization. The theorem's repeated-sample guarantee comes from its assumptions and proof, not from one successful numerical assertion.

## Beyond a finite list

Thresholds on a line can shatter one point but not every labeling of two ordered points, so their VC dimension is one. VC theory controls an infinite class using its possible label patterns rather than literally counting infinitely many functions. Rademacher complexity measures how strongly a class can correlate with random signs on a sample. These tools explain why capacity is a property of a function class and sample geometry, not just a count of fitted parameters.

Algorithmic stability asks how predictions or losses change when a training observation is replaced. Strongly regularized procedures can be stable under specified conditions. Stability bounds require their actual boundedness, convexity or other theorem assumptions; changing a seed and observing similar scores is only a diagnostic.

## A PAC-Bayes continuation

A fixed uniform prior over the 41 rules and a data-dependent Gibbs posterior define a randomized predictor. A standard bounded-loss PAC-Bayes inequality bounds binary KL between its empirical and true risk by

\[
\frac{\operatorname{KL}(Q\Vert P)+\log(2\sqrt n/\delta)}{n}.
\]

The displayed version uses iid observations, a sample-independent prior, bounded loss and the usual finite-class measurable setting, with \(n\ge8\) for the stated exponential-moment bound. Pinsker's inequality produces the looser risk upper bound used in the program. The posterior-weighted true risk is available through the oracle. This result concerns a random draw from \(Q\), not automatically its majority vote or the single best model. A prior selected using the same outcomes needs a different valid construction.

**Answered discussion: Does a small bound certify production?** Only for the stated distribution, loss and procedure. Unbounded losses, dependent users, reused evaluation data or shift break the simple argument. A numerically loose bound can still clarify which assumptions matter without replacing empirical validation.

References: [Understanding Machine Learning](https://www.cs.huji.ac.il/~shais/UnderstandingMachineLearning/understanding-machine-learning-theory-algorithms.pdf), [Maurer's tightened PAC-Bayes bound](https://arxiv.org/abs/cs/0411099). Continue to the [scientific cases](../science/README.md).

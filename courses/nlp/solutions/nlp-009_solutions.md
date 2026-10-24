# nlp-009: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Trace log odds

The count vector contributes four from urgent and minus one from thanks, then the intercept subtracts one-half. The resulting logit is 2.5. Applying a stable sigmoid yields the stated probability. Extreme finite logits approach zero or one without overflowing. This verifies arithmetic and numerical behavior, not a real confidence guarantee.

**Expected:** Logit 2.5 and probability approximately 0.92414182; finite outputs at logits +/-1000.

## Exercise 2: Freeze the vocabulary

Fitting creates a mapping from training tokens to columns. The evaluation token escalation has no column and is ignored under the declared policy. A fit_transform call on evaluation data would change the representation and invalidate the comparison. The reference checks vocabulary membership directly rather than relying only on final predictions.

**Expected:** Exactly six learned vocabulary terms; escalation absent; two stated probes predicted [1,0].

## Exercise 3: Compare regularization

Stronger L2 regularization penalizes large weights, so the small-C solution uses a smaller norm on this fixture. This is a controlled mechanism check. Model selection still needs independent development cases, and the most regularized model need not have the best task performance.

**Expected:** The \(C=0.1\) coefficient norm is smaller; record both norms and do not call either universally best.

## Exercise 4: Separate a threshold

Only the middle probability lies between the thresholds. The comparison must state whether equality triggers the positive action. In deployment the threshold should follow costs, capacity and calibration evidence, not be selected retrospectively on the final test labels.

**Expected:** Actions [false,false,true] and [false,true,true].

## Exercise 5: Inspect probability quality

The first array makes two highly confident mistakes and two confident correct predictions. Its losses are .01,.81,.81,.01, averaging .41. The second gives .16,.36,.36,.16, averaging .26. This demonstrates a proper scoring calculation; it does not establish that moving every probability toward .5 always improves a model.

**Expected:** Scores 0.41 and 0.26; invalid 1.2 raises ValueError.

## Exercise 6: Expose negation loss

The trained vocabulary lacks not, so both probe texts produce the same represented input. A deterministic model must then give the same score. A bigram representation can encode the distinction, but it needs labeled evidence to learn its meaning. Report the limitation rather than pretending a new feature guarantees correct negation handling.

**Expected:** The frozen unigram rows match; a separately fitted demonstration contains the not urgent bigram.

## Transfer and limits

A linear text classifier is a useful baseline because its calculation can be inspected from tokens to a score. The input unit here is one short support message and the label indicates whether it belongs to an urgent category. The task is classification under a defined annotation policy, not a claim that a particular word always implies real operational urgency. A customer can quote an urgent message, negate it or use unfamiliar language.

The representation maps each document to a vector x of token counts. A binary logistic model computes \(z=w^{\mathsf T}\cdot x+b\) and \(p=\frac{1}{1+\exp(-z)}\). The coefficient w_j changes the log odds by w_j for one additional occurrence of feature j, conditional on the other represented features. The bias b shifts the baseline score. The model learns these values by minimizing a classification loss plus a regularization penalty, not by counting how often a coefficient agrees with a causal explanation.

Separate three decisions: which features to represent, how to fit a score, and which score threshold triggers an action. A probability of 0.7 and a threshold of 0.8 produce a negative action without changing the probability estimate. Calibration asks whether predictions near 0.7 correspond to roughly 70 percent positives in the relevant population. Good ranking, calibrated probabilities and a useful decision rule are related but distinct properties.

## Mechanism review and counterexample

The Brier score is the mean of \({\left(p-y\right)}^{2}\) for binary outcomes. It evaluates probability quality, combining calibration and discrimination effects; it is not a pure calibration-only statistic. The reference compares two fixed probability arrays to explain scoring. It does not fit or claim a calibrated model from four observations. A real calibrator needs separate predictions and labels, usually through a held-out or cross-validated procedure that avoids fitting and judging on the same cases.

A bag-of-words model can ignore negation and word order. Because not is absent from the training vocabulary, urgent and not urgent map to the same vector in this fixture. Adding bigrams creates a feature for not urgent, but a feature name alone does not teach the correct label. You still need representative annotated examples and evaluation. Diagnose the error as a representation/training-data problem before increasing optimizer iterations.

Inspect false positives, false negatives, unknown-token rates and performance by text family. A good average score can hide failures on short messages, dialects or newly introduced product names. Coefficients describe the learned representation and corpus, not universal linguistic rules.

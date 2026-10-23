# nlp-008: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Aggregate by class

The class-zero documents contain three thanks events and no urgent events. Class one contains three urgent and one thanks. Each class contains two documents, so the prior is balanced despite unequal total token counts. Keeping those units separate is essential to the model.

**Expected:** Counts [[0,3],[3,1]] in class order[0,1]; priors [.5,.5].

## Exercise 2: Apply Laplace smoothing

Smoothing assigns a nonzero urgent probability to class zero despite no observed urgent events there. The denominator is class token total plus alpha times vocabulary size. Using the number of documents instead would not normalize the multinomial token distribution.

**Expected:** Likelihoods [[1/5,4/5],[4/6,2/6]], each summing to one.

## Exercise 3: Compute stable posteriors

The two unnormalized weights are 0.1 and one-third. Their sum is 13/30, giving the stated fractions. Logsumexp computes the same normalization without underflow. Matching one argmax alone would miss a wrong probability scale, so compare the full vector.

**Expected:** Posterior [3/13,10/13] for classes[0,1].

## Exercise 4: Verify library parity

The library is an implementation under specified defaults, not an oracle for the task itself. The independent counts and fractions verify that the estimator matches the intended mathematical model. This is stronger than comparing two calls to the same library function.

**Expected:** All three agree with the independent manual oracle.

## Exercise 5: Inspect prior and empty input

With no represented token evidence, only the class prior remains. For the changed population prior, the nonurgent prior advantage outweighs the urgent token likelihood ratio. Report this as a modeling assumption and validate whether a prior-only adjustment is justified for the deployment shift.

**Expected:** Empty evidence returns prior; changed prior makes class zero more probable.

## Exercise 6: Expose negation and overconfidence

The missing not coordinate makes the messages identical to the model. Conditional-independence violations can also multiply related evidence as if it were independent, yielding extreme probabilities. Richer features and calibration are possible repairs, but they need held-out evaluation rather than a claim that a more complex model automatically understands the text.

**Expected:** Identical represented inputs/posteriors; a written warning distinguishes class accuracy from probability calibration.

## Transfer and limits

Multinomial Naive Bayes is a compact probabilistic baseline for nonnegative text counts. It models the class prior and the distribution of token events within each class, then combines those pieces with Bayes' rule. Its conditional-independence assumption is strong, but the resulting classifier can be useful even when the language is not actually generated independently word by word.

The feature order is [urgent,thanks]. Four documents have count rows [2,1],[1,0],[0,2],[0,1] and labels [1,1,0,0]. We derive the fitted probabilities by hand and compare them with a real scikit-learn MultinomialNB. This establishes implementation parity on a known fixture, not a claim of calibrated confidence or deployment accuracy.

Separate the prior probability of a class from the likelihood of tokens under that class. A word can favor an urgent class while a strong nonurgent prior still makes the posterior nonurgent. Class imbalance and the target population therefore matter to the decision, not just the presence of a distinctive keyword.

## Mechanism review and counterexample

Conditional independence assumes token events are independent given the class in the modeled likelihood. Real phrases violate this through grammar, repetition and correlated vocabulary. The assumption can overcount related evidence, producing overconfident probabilities even when the decision boundary is useful. Evaluate probability calibration separately from classification accuracy.

A fixed vocabulary lacking not gives urgent and not urgent the same feature vector. Naive Bayes cannot recover information absent from the representation. Adding bigrams or a richer encoder can help only if training labels and evaluation cover the distinction. The model name is not a substitute for an error analysis.

Changing the class prior to [0.9,0.1] flips the stated urgent-only probe toward class zero, even though the token likelihoods stay fixed. Such a change is a model of a different population or decision setting, not a free accuracy trick. If label prevalence shifts, consider whether the conditional feature distributions also changed before applying a prior adjustment.

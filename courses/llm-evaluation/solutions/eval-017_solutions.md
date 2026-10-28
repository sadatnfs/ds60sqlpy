# eval-017: explained reference

The full reference is `eval-017_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Equal scores

Equal scores express no preference under the model; observing a chosen response still incurs positive negative log likelihood.

**Expected observation:** Preference probability 0.5 and loss log 2.

## 2. Shift both rewards

Pairwise labels cannot determine a common reward offset, including prompt-specific offsets when comparisons stay within prompts.

**Expected observation:** Loss and score gradient remain unchanged.

## 3. Reverse empirical counts

Reversing labels changes the sign of the fitted log odds, while finite counts still imply uncertainty.

**Expected observation:** The fitted preference probability is 0.25.

## 4. All wins and no losses

Regularization or a prior can produce a finite estimate, but it changes the model and must be stated.

**Expected observation:** No finite maximum-likelihood difference exists.

## 5. Test numerical stability

Stable softplus arithmetic preserves the large finite loss without underflowing a probability to zero first.

**Expected observation:** Loss remains finite at 2000.

## 6. Interpret a preference cycle

Their sum would need to be positive while algebraically equaling zero. Investigate stochasticity, annotator heterogeneity and multiple criteria.

**Expected observation:** A deterministic scalar ordering cannot satisfy all three.

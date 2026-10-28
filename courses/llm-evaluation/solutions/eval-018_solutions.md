# eval-018: explained reference

The full reference is `eval-018_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Verify the initial gradient

The check tests the implemented likelihood and reduction denominator independently of whether the labels are meaningful.

**Expected observation:** The two vectors match in float64.

## 2. Inspect the length coefficient

The authored design provides no systematic signal that longer is preferable, so the symmetric initialization and updates preserve the zero length direction.

**Expected observation:** The length coefficient remains approximately zero.

## 3. Reverse a comparison

This is a useful implementation invariant for a pairwise difference model.

**Expected observation:** The linear reward margin changes sign.

## 4. Find a training shortcut

An optimizer fits the provided associations. It cannot infer the intended target when the comparison design leaves that target confounded.

**Expected observation:** Length receives more weight than either evidence coordinate.

## 5. Recompute the final loss

A reported result should identify the model state that produced it, especially when comparing training and held-out measurements.

**Expected observation:** The final-state loss is distinct from the last pre-update loss.

## 6. State the model boundary

The exercise uses authored features. It does not train a language encoder, judge real responses or establish the preferences of an external population.

**Expected observation:** A real small CPU reward fit, with no natural-language capability claim.

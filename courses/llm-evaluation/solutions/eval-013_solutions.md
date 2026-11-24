# eval-013: explained reference

`eval-013_reference.py` asserts each answer below, from *Two noisy candidates* to *Reclassify a reused holdout*, on the authored selection bias and nested evaluation fixture only. Before applying a conclusion to other data, recheck the assumption that *Specify a tie rule* tests.

## 1. Two noisy candidates

Three combinations select+0.1 and one selects-0.1, giving(0.3-0.1)/4.

**Approach.** List the four combinations of noise in `product((-0.1, 0.1), repeat=2)`: (-0.1, -0.1), (-0.1, 0.1), (0.1, -0.1) and (0.1, 0.1). Take the maximum of each and average.

**Why it holds for this fixture.** Three combinations contain at least one +0.1, so their maximum is +0.1; only (-0.1, -0.1) has maximum -0.1. The mean is (0.1 + 0.1 + 0.1 - 0.1) / 4 = 0.05. Every candidate has true quality equal, yet selecting the best observed score adds 0.05 of pure noise.

**A tempting wrong approach.** Reporting the selected candidate's development score as its expected quality is the mistake. With one candidate the expected noise is 0; with two it is 0.05; case A shows four candidates give 0.0875. The bias grows with the number of candidates tried.

**How to verify.** Case A asserts the values for 1, 2 and 4 candidates equal `[0, 0.05, 0.0875]`, and the exercise checks assert `selection_optimism(2) > selection_optimism(1)`.

**Expected observation:** The mean maximum is 0.05.

## 2. Change only final outcomes

This invariant distinguishes assessment from a hidden second round of tuning.

**Approach.** Keep a development table fixed, change only the assessment table, and call `assess_procedure` twice. Compare the returned `choices` arrays.

**Why it holds for this fixture.** Choices come from `np.argmax(dev, axis=1)`, which never reads the assessment table. The reference uses development `[[0.9, 0.8]]` with assessment `[[0.0, 1.0]]` and still selects index 0, even though candidate 1 is far better on the assessment.

**A tempting wrong approach.** Swapping to the candidate that won on the assessment table looks like using the best information available. It turns the assessment set into a second development round and its score into a selected value with the same optimism as exercise 1.

**How to verify.** The reference asserts `assess_procedure([[0.9, 0.8]], [[0.0, 1.0]])[0].tolist() == [0]`. Any change to the assessment values should leave `choices` identical.

**Expected observation:** The selected candidate IDs do not change.

## 3. Specify a tie rule

Tie handling is part of a reproducible procedure; it should not depend on which final outcome is better.

**Approach.** Call `assess_procedure([[0.5, 0.5]], [[0.1, 0.9]])`. NumPy's `argmax` returns the first index among tied maxima.

**Why it holds for this fixture.** Both candidates score 0.5 in development, so index 0 is chosen and its assessment score 0.1 is reported, even though candidate 1 would have scored 0.9. The rule is fixed before assessment, so the result is reproducible.

**A tempting wrong approach.** Breaking ties by looking at the assessment score, so choosing 0.9, is the mistake. It is a small version of the optimistic procedure in exercise 4 and would bias reported performance upward whenever ties occur.

**How to verify.** The reference asserts `choices.tolist() == [0]` and `scores.tolist() == [0.1]`. Write the tie rule into the procedure description.

**Expected observation:** The reference chooses the first candidate deterministically.

## 4. Find the optimistic procedure

The larger score is explained by using outcome information twice, not by evidence that the original procedure improved.

**Approach.** In case B, take the maximum of each assessment row with `np.max(test, axis=1)` and average, then compare with the development-selected scores.

**Why it holds for this fixture.** The development choices are `[0, 1]`, which select assessment scores 0.4 and 0.5, a mean of 0.45. Picking the best assessment score per fold gives 0.8 and 0.9, a mean of 0.85. The 0.4 gap comes entirely from using assessment outcomes to choose.

**A tempting wrong approach.** Reporting 0.85 as the performance of the tuning procedure is the mistake. That number is what an oracle would get by peeking at the answers; the honest estimate of the procedure is 0.45.

**How to verify.** Case B asserts `np.isclose(selected.mean(), 0.45)` and `np.isclose(np.max(test, axis=1).mean(), 0.85)`.

**Expected observation:** Its same-table average is 0.85, but it is no longer protected assessment.

## 5. Place preprocessing

An outer holdout can leak through a transform even when the final estimator receives only training rows.

**Approach.** Fit any learned transform, such as normalization statistics or a calibration map, using only the rows that are training or development for that fold. Apply the frozen transform to the outer rows.

**Why it holds for this fixture.** A mean and scale computed from all rows, including the outer holdout, carry information about the holdout into the model, even if the classifier itself never trains on those rows. Each fold must refit the transform on its own inner data.

**A tempting wrong approach.** Normalizing the full dataset once before splitting is the common shortcut. Outer scores then reflect a procedure that saw the test distribution, and the leak is invisible in the code that fits the final estimator.

**How to verify.** No reference assertion covers this task. Check by computing the transform on the inner rows only and confirming its parameters change when the outer rows change but the inner rows do not; they should not change.

**Expected observation:** Inside the corresponding training/development partition.

## 6. Reclassify a reused holdout

Acquire a new protected assessment for the changed procedure rather than claiming the original untouched-test interpretation.

**Approach.** Once final-set errors drive a prompt edit, relabel that set as development or regression evidence for the new prompt and assemble a new protected set for the next claim.

**Why it holds for this fixture.** The revised prompt was chosen partly because it fixes those specific errors, so its score on that set is a selected value. The original untouched-test meaning no longer applies, the same logic as eval-010's held-out failure.

**A tempting wrong approach.** Keeping the set labeled as test and reporting the improved score is the mistake. The improvement may only reflect fitting the inspected errors, and the reported number will overstate performance on new requests.

**How to verify.** Record in the evidence log the date the set was opened for diagnosis and which revision used it. Confirm the new protected set shares no request or family IDs with the reused one.

**Expected observation:** The set becomes development or regression evidence for that revision.

# eval-011: explained reference

`eval-011_reference.py` asserts each answer below, from *Invert the swapped result* to *Freeze a recalibration mapping*, on the authored LLM as judge and position bias fixture only. Before applying a conclusion to other data, recheck the assumption that *Check maximally wrong probabilities* tests.

## 1. Invert the swapped result

A position-level label has no fixed model meaning until the display order is known.

**Approach.** Encode the case: candidate A is on the right, so `a_on_left` is `False`, and the left answer wins, so `left_wins` is 1. `identity_wins` maps that to `1 - 1 = 0` for A.

**Why it holds for this fixture.** The judge preferred the left slot, which held B. In identity terms, A lost. The reference checks the two-item version `identity_wins([0, 1], [True, False])`, where A loses both times: once on the left and once on the right.

**A tempting wrong approach.** Averaging position-level wins (the left won, so count a win) without the orientation is the mistake. Worked case A shows a judge that always picks the left side scoring 0.5 for A once orientations are balanced.

**How to verify.** The reference asserts `identity_wins([0, 1], [True, False]).tolist() == [0.0, 0.0]`. Case A asserts `identity_wins([1, 1], [True, False]).tolist() == [1.0, 0.0]`.

**Expected observation:** The identity score for A is 0.

## 2. Check perfect probabilities

Perfect probabilities have zero squared error and zero within-bin calibration gap on this fixture.

**Approach.** Call `calibration([1, 0], [1, 0])`. The probabilities exactly equal the labels.

**Why it holds for this fixture.** Each squared error is 0, so Brier is 0. Probability 1 falls in the upper bin with label 1, and 0 falls in the lower bin with label 0; each bin's mean probability equals its mean label, so ECE is 0.

**A tempting wrong approach.** Reading ECE 0 as proof of a good judge in general is the mistake. Two items cannot show calibration in the middle range, and a perfect score on a tiny authored fixture is a correctness check on the code, not a model property.

**How to verify.** The reference asserts `calibration([1, 0], [1, 0]) == (0.0, 0.0)`. A single item `calibration([1], [1])` also has Brier 0.

**Expected observation:** Brier and the stated ECE are 0.

## 3. Check maximally wrong probabilities

The example diagnoses probability failure even if a separate presentation metric remains favorable.

**Approach.** Call `calibration([0, 1], [1, 0])`. Every probability is the opposite of its label.

**Why it holds for this fixture.** Each squared error is 1, so Brier is 1. Probability 0 sits alone in the lower bin with label 1, a gap of 1, and probability 1 sits alone in the upper bin with label 0, also a gap of 1. Each bin holds half the items, so ECE is 0.5 + 0.5 = 1.

**A tempting wrong approach.** Assuming a judge with good pairwise win rates must have useful probabilities is the mistake. Preference accuracy and calibration are separate properties, and this fixture is wrong on calibration regardless of any ranking metric.

**How to verify.** The reference asserts `calibration([0, 1], [1, 0]) == (1.0, 1.0)`.

**Expected observation:** Both reported scores are 1.

## 4. Use a constant judge

A constant predictor can match the overall class frequency while providing no item-level ranking information.

**Approach.** Call `calibration([0.5] * 4, [1, 1, 0, 0])`. Every item receives probability 0.5 and half the labels are 1.

**Why it holds for this fixture.** Each squared error is 0.25, so Brier is 0.25. With edges 0, 0.5, 1 and `side="right"`, 0.5 falls in the upper bin, so all four items share one bin with mean probability 0.5 and mean label 0.5. The gap is 0, so ECE is 0.

**A tempting wrong approach.** Picking the judge with the lowest ECE is the mistake here. The constant predictor is perfectly calibrated and useless: it cannot tell any item from another. Case B's informative scores have ECE 0.15 but Brier 0.025, ten times better.

**How to verify.** Worked case B asserts `constant == (0.25, 0.0)` and the informative pair `brier` near 0.025 and `ece` near 0.15.

**Expected observation:** ECE 0 and Brier 0.25 under these bins.

## 5. Test verbosity invariance

A change diagnoses one presentation sensitivity. It does not prove all longer answers are favored or all length adjustments are valid.

**Approach.** Take one comparison, duplicate a paragraph in one answer without adding any claim, and rerun the judge in both orientations. Record identity wins before and after.

**Why it holds for this fixture.** If the duplicated answer now wins where it lost before, the judge responds to length or repetition, not content. Running both orientations separates this from the position effect shown in exercise 1.

**A tempting wrong approach.** Concluding from one flip that the judge always favors longer answers is too strong. One perturbation shows one sensitivity; length can also correlate with real completeness on other items, so a blanket length penalty is not justified either.

**How to verify.** No reference assertion covers this task. Record a table with item ID, orientation, original identity win and perturbed identity win, and count flips over several items before generalizing.

**Expected observation:** Record whether identity preference changes.

## 6. Freeze a recalibration mapping

Independent assessment is needed because a reliability diagram can be made attractive by fitting and evaluating on the same cases.

**Approach.** Fit any recalibration map, such as binning or a logistic fit, using only development labels. Freeze its parameters, then apply it to new families and compute Brier and ECE there.

**Why it holds for this fixture.** Fitting and evaluating on the same items lets the map memorize each bin's label rate, so ECE on those items drops toward zero by construction. Only items the map never saw can show whether it transfers.

**A tempting wrong approach.** Plotting a reliability diagram on the development set after fitting and presenting it as evidence of calibration is the mistake. It shows the fit, not generalization.

**How to verify.** Check that no final-set label appears in the data used for fitting (compare ID sets), then report Brier and ECE on the final families only, with the bin edges stated.

**Expected observation:** Final labels do not influence the fitted mapping.

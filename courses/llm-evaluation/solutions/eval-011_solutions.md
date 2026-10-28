# eval-011: explained reference

The full reference is `eval-011_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Invert the swapped result

A position-level label has no fixed model meaning until the display order is known.

**Expected observation:** The identity score for A is 0.

## 2. Check perfect probabilities

Perfect probabilities have zero squared error and zero within-bin calibration gap on this fixture.

**Expected observation:** Brier and the stated ECE are 0.

## 3. Check maximally wrong probabilities

The example diagnoses probability failure even if a separate presentation metric remains favorable.

**Expected observation:** Both reported scores are 1.

## 4. Use a constant judge

A constant predictor can match the overall class frequency while providing no item-level ranking information.

**Expected observation:** ECE 0 and Brier 0.25 under these bins.

## 5. Test verbosity invariance

A change diagnoses one presentation sensitivity. It does not prove all longer answers are favored or all length adjustments are valid.

**Expected observation:** Record whether identity preference changes.

## 6. Freeze a recalibration mapping

Independent assessment is needed because a reliability diagram can be made attractive by fitting and evaluating on the same cases.

**Expected observation:** Final labels do not influence the fitted mapping.

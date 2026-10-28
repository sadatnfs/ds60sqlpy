# eval-005: explained reference

The full reference is `eval-005_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Change the mixture

0.25(0.9)+0.75(0.5)=0.6. The model outcomes are unchanged; only the target population differs.

**Expected observation:** Target accuracy is 0.6.

## 2. Expose missing support

The outcome mean for that stratum is unidentified without additional data or explicit modeling assumptions.

**Expected observation:** The estimator rejects the mismatch.

## 3. Compare denominators

Horvitz-Thompson estimates the population total before dividing by N. Self-normalization divides by an estimated total weight and need not equal it.

**Expected observation:** \(0.2\) uses the known population size \(N=10\); \(1/3\) uses the sampled weight sum \(6\).

## 4. Increase weight concentration

A nominal sample of two is dominated by one weighted observation. ESS describes concentration but does not replace a clustering analysis.

**Expected observation:** The diagnostic ESS is below 1.03.

## 5. Audit zero probability

An event that cannot enter the sample cannot provide an observed outcome for this estimator.

**Expected observation:** The calculation must fail.

## 6. Compare systems fairly

Paired, consistently weighted differences prevent a traffic-mixture change from masquerading as a model improvement.

**Expected observation:** Both estimates use identical eligible IDs and target weights.

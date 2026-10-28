# eval-007: explained reference

The full reference is `eval-007_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. One comparison

With one prespecified comparison the threshold remains 0.05; this code uses <=.

**Expected observation:** The declared non-strict rule rejects.

## 2. Three equal findings

Three nominal findings are not three adjusted findings under this family definition.

**Expected observation:** None crosses equal Bonferroni thresholds.

## 3. Overspend the budget

The advertised family bound requires the total allocation to remain within its declared budget.

**Expected observation:** The monitoring plan is rejected.

## 4. Specify dependent looks

The formula 1-(1-alpha)^m uses independence; the union-bound inequality does not.

**Expected observation:** It does not; individual error bounds still need to hold.

## 5. Unknown result

Unknown evidence requires an explicit incomplete assessment, not a smaller multiplicity correction.

**Expected observation:** The decision function rejects it.

## 6. Separate value from significance

A release decision combines expected utility, uncertainty, constraints and costs; its logic must be recorded separately from a p-value.

**Expected observation:** The statistical result alone does not mandate deployment.

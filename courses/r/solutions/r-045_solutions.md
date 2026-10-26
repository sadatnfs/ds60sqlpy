# r-045: reference reasoning

Use the [complete reference](r-045_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference checks disjointness at the family level and refits inside each fold. Its perfect synthetic affine predictions test implementation mechanics, not the credibility of real-world validation. The training-only centering example isolates a preprocessing leak without mixing it with model error.

The final aggregation preserves both sums and counts, allowing the observation-weighted result to be reconstructed. Temporal ordering is checked independently. A complete applied study must also reserve model-selection decisions for development data and retain a final assessment that was not reused for tuning.

## Explained practice

### Exercise 1

Construct a group-disjoint split for four two-row families.

Assign A/B to training and C/D to assessment; assert no group intersection.

**Expected evidence:** Zero shared groups.

### Exercise 2

Demonstrate why an odd/even row split leaks the same families.

Every family appears in both partitions even though row IDs differ.

**Expected evidence:** Four shared families.

### Exercise 3

Perform leave-one-group-out prediction for the exact rule y=1+2x.

Each fold has disjoint families and recovers the exact authored affine relationship; retain fold counts and error sums.

**Expected evidence:** Near-zero error with explicit fold counts.

### Exercise 4

Diagnose centering with the full dataset before splitting.

Held-out covariates have influenced the fitted transformation. Recompute the center within each training partition.

**Expected evidence:** Training-only center restored.

### Exercise 5

Define the temporal split at day 4 in days 1 through 6.

Train on 1:4 and evaluate on 5:6; no future row is used to fit the earlier predictor.

**Expected evidence:** max(train day)<min(test day).

### Exercise 6

Aggregate folds with error sums 2 and 12 and counts 1 and 3.

The observation mean is 14/4=3.5; the equal-fold mean of 2 and 4 is 3.

**Expected evidence:** Both quantities labeled; observation mean 3.5.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.

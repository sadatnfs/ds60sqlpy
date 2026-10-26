# r-041: reference reasoning

Use the [complete reference](r-041_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference preserves the observed set explicitly. Selecting x[valid] avoids performing arithmetic on missing entries and makes the denominator count inspectable. The zero in the first fixture is a valid measurement, so removing it would create another selection error.

The grouped calculation retains enough information to reconstruct the observation-weighted mean. Averages of group averages change the weighting unless group counts are equal or equal group weighting is the intended question. The all-missing branch returns missing output deliberately; it does not turn absent evidence into a zero estimate.

The tail comparison uses the same five authored values for both summaries. Its conclusion is about their arithmetic sensitivity. Decisions about measurement error, eligibility or population inference require evidence not present in this small fixture.

## Explained practice

### Exercise 1

Predict the row, observed and missing counts for c(0, NA, 2, NA).

There are four rows, two observed values and two missing values; the observed mean is one.

**Expected evidence:** Counts 4,2,2; mean 1.

### Exercise 2

Add an observed value eight to c(1, NA, 4, 6, NA) and update the mean.

The observed sum becomes 19 and the observed count four, so the mean is 19/4.

**Expected evidence:** Observed count 4, mean 4.75.

### Exercise 3

Construct group summaries for A=c(1,NA) and B=c(4,6,NA), retaining observed counts.

A has one observed value and mean one; B has two and mean five. The overall observed mean is the count-weighted 11/3, not the equal-group mean three.

**Expected evidence:** A: count 1 / mean 1; B: count 2 / mean 5; overall 11/3.

### Exercise 4

Diagnose replacing every missing measurement with zero before averaging.

The replacement changes the data and denominator. For the five-row fixture it produces 11/5 rather than the observed-value mean 11/3. Neither is a justified population estimate without a missingness model.

**Expected evidence:** The two descriptive quantities differ and the assumption is stated.

### Exercise 5

Define and test the summary of c(NA_real_, NA_real_).

Return counts two/zero/two and an explicit NA_real_ mean; do not report zero as an observed average.

**Expected evidence:** Observed count 0; mean NA.

### Exercise 6

Compare mean and median after adding 100 to c(1,2,2,3), and explain the inferential limit.

Mean becomes 21.6 and median 2. The difference describes sensitivity to the tail; it does not establish that 100 is erroneous or that the sample represents a population.

**Expected evidence:** Correct summaries and a bounded interpretation.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.

# r-042: reference reasoning

Use the [complete reference](r-042_reference.R) with the guide's declared inputs and runtime. Every worked example is also a standalone script.

## Why the implementation has this shape

The reference uses different variance conventions for different objects. sd(x) estimates population spread from a sample, whereas the enumeration treats all bootstrap means as the complete conditional distribution. Neither result should be silently substituted for the other.

The shift test checks an invariant of centered spread. The count guard prevents an undefined sample-variance calculation from being interpreted as a usable estimate. Interval construction is shown explicitly, with its target and assumptions retained; no coverage claim is inferred from one synthetic realization.

## Explained practice

### Exercise 1

Derive the sample mean and estimated SE for c(2,4,6,8).

The mean is 5; sample variance 20/3; estimated SE is sqrt(5/3).

**Expected evidence:** Mean 5, SE squared 5/3.

### Exercise 2

Add three to every observation and compare the estimate and SE.

The mean becomes 8 while the standard error is unchanged.

**Expected evidence:** Mean 8; same SE.

### Exercise 3

Enumerate all four-draw bootstrap samples and verify their conditional variance.

The empirical variance is 5 and four independent draws produce mean variance 5/4.

**Expected evidence:** 256 means; conditional variance 1.25.

### Exercise 4

Diagnose dividing the observation standard deviation by n instead of sqrt(n).

The wrong formula shrinks uncertainty too quickly. For n4 it is half the correct SE.

**Expected evidence:** Wrong SE equals correct SE/2.

### Exercise 5

State a policy for estimating this SE from zero or one observation.

Reject the request explicitly instead of presenting NA as a successful uncertainty estimate.

**Expected evidence:** A defined error for count below 2.

### Exercise 6

Compare a Student t mean interval with a percentile interval from the exact bootstrap distribution.

Both describe uncertainty of a mean under different procedures; their agreement or disagreement on this fixture does not establish population coverage or a future-observation prediction interval.

**Expected evidence:** Correctly labeled intervals with declared quantile convention.

## What the checks establish

The reference contains explicit behavioral assertions for its small synthetic inputs. A passing run establishes those assertions in the reported environment. It does not prove correctness for every input, statistical validity for an unrelated population, or compatibility with untested package versions.

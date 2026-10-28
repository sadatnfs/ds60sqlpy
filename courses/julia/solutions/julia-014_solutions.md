# julia-014: explained reference

The executable reference is `julia-014_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Retain the denominator

The result describes the observed measurements, not an assumed completed dataset.

**Expected observation:** Total 3, observed 2 and mean 2.

## 2. Replace explicitly

The replacement policy changes the quantity being summarized.

**Expected observation:** The mean becomes 4/3.

## 3. Reject numerical failure

Unknown data and undefined floating arithmetic need distinct handling.

**Expected observation:** The finite-value guard rejects it.

## 4. Handle all-missing data

The output preserves unavailable information while retaining the eligible count.

**Expected observation:** The observed count is 0 and estimate is missing.

## 5. Distinguish absence

An absent return and a missing measurement should not be conflated accidentally.

**Expected observation:** The former returns 7; the latter retains nothing.

## 6. Assess a real policy

The missingness mechanism and decision target determine which policy is defensible.

**Expected observation:** State assumptions, affected population and uncertainty.

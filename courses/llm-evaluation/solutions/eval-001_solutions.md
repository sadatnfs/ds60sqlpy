# eval-001: explained reference

The full reference is `eval-001_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Reverse the comparison

An improvement sign is a convention. Correctness B minus A favors B when positive; swapping systems negates the result.

**Expected observation:** The values are +1 and -1.

## 2. Change the target mix

0.75(1)+0.25(-1)=0.5. The weights describe the target population, not a correction that is always preferable.

**Expected observation:** The weighted improvement is 0.5.

## 3. Duplicate an identifier

Counting an accidental duplicate twice changes both weights and apparent precision; reject it before estimation.

**Expected observation:** The paired-data validator rejects it.

## 4. Require complete gates

An absent result is unknown. Explicit completeness prevents an all([]) or missing-key success.

**Expected observation:** The result remains no-go.

## 5. Show missing-label coverage

The unchanged accuracy does not imply unchanged evidence. Half the eligible population now lacks labels.

**Expected observation:** Observed accuracy stays 1 while label coverage falls to 0.5.

## 6. Define an empty population

An empty evaluation cannot support a deployment claim; the program rejects it and the report should identify why coverage is empty.

**Expected observation:** Raise an error instead of returning perfect accuracy.

# eval-009: explained reference

The full reference is `eval-009_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. One supported claim

Perfect precision does not imply that the full answer has adequate evidence coverage.

**Expected observation:** Precision 1, coverage 1/3.

## 2. No citations

There are no links to judge, but no eligible claim has supported evidence.

**Expected observation:** Precision is missing; coverage is 0.

## 3. Unknown support relation

Retain missingness and acquire a label or use an explicit assessment-sampling protocol.

**Expected observation:** The helper rejects it.

## 4. Duplicate a citation

Duplicated markup should not increase the apparent amount of evidence.

**Expected observation:** The helper rejects it.

## 5. Use a newer document

A later correction cannot be treated as information the original system had at decision time.

**Expected observation:** That version is ineligible for the historical reconstruction.

## 6. Disentangle truth and support

Citation evaluation measures a relation to supplied evidence. It does not establish that all evidence is correct or current.

**Expected observation:** Support can be true while truth is false.

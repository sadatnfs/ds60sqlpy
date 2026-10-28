# eval-008: explained reference

The full reference is `eval-008_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Separate recall from nDCG

nDCG evaluates the quality of the available ranking positions. Recall asks what fraction of all known relevant documents was retrieved.

**Expected observation:** An ideal top two still omits one relevant document.

## 2. Return no relevant hit

Zero is meaningful here because relevant documents exist in the judged corpus but none was retrieved.

**Expected observation:** Recall, reciprocal rank and nDCG are 0.

## 3. Repeat a document

Counting duplicates as new hits can inflate recall or distort position metrics.

**Expected observation:** The fixture rejects duplicates.

## 4. Add an unjudged document

A separate assessment or a declared missing-judgment policy is needed before comparing systems fairly.

**Expected observation:** The calculation rejects it.

## 5. Empty relevant set

Report the affected query count and its interpretation instead of silently mixing undefined scores into a mean.

**Expected observation:** Recall and nDCG are reported as missing.

## 6. Preserve target weights

The weighting rule defines whose query distribution the result represents; it should be shared by every compared retriever.

**Expected observation:** They can differ without a coding error.

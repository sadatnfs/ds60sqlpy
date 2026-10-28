# eval-012: explained reference

The full reference is `eval-012_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Inspect each prompt

An overall favorable result does not imply improvement under every configuration.

**Expected observation:** The differences are -0.1 and +0.3.

## 2. Check reconstruction

This algebraic identity is a useful implementation check, independent of any inferential assumptions.

**Expected observation:** Every observed cell is recovered within floating tolerance.

## 3. Change the prompt target

A fixed-prompt deployment needs evidence for that prompt, not an attractive average over unused alternatives.

**Expected observation:** The candidate difference becomes-0.1.

## 4. Equalize selection budgets

A comparison of selection procedures differs from a comparison of one selected system with an untuned mean; final assessment must still be independent.

**Expected observation:** Both selected development scores are 0.9.

## 5. Count seed replication

This describes the three constructed seed scores. It does not quantify variation across an unseen population of task families.

**Expected observation:** The sample variance is 0.01.

## 6. Validate axes

Silently averaging an unidentified axis can mix model, prompt and replication factors and invalidate the comparison.

**Expected observation:** The tensor contract rejects it.

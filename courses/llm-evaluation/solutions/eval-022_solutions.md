# eval-022: explained reference

The full reference is `eval-022_reference.py`. Its assertions check the specific authored inputs. Read the assumptions and counterexamples before transferring a result.

## 1. Trace the expectation weights

An unweighted average over actions would cease to represent the old-policy expectation once the policy becomes nonuniform.

**Expected observation:** The total is 1.

## 2. Inspect frozen state

Current-policy updates must not move the denominator of their own importance ratio.

**Expected observation:** It is byte-for-byte numerically unchanged.

## 3. Separate critic and actor gradients

Without this graph boundary the implemented gradient would contain an unintended optimization route.

**Expected observation:** The actor cannot improve its objective by changing its baseline through that path.

## 4. Check symmetry

This invariant tests the small environment and update implementation independently of a particular random seed.

**Expected observation:** The learned probability rows mirror each other.

## 5. Optimize a bad proxy

Correct execution of PPO cannot validate a mistaken or exploitable reward definition.

**Expected observation:** Training reward exceeds 0.9 while task utility is below 0.1.

## 6. State the scale boundary

The run establishes a small CPU optimization mechanism, not a production language model or a guarantee of safe alignment.

**Expected observation:** Tokenization, sampled language rollouts, long-horizon credit, pretrained weights and serving are absent.

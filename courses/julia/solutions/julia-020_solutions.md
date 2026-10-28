# julia-020: explained reference

The executable reference is `julia-020_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. State the parameterization

A familiar parameter name should be checked against the actual distribution API.

**Expected observation:** The mean is 2 and variance 9.

## 2. Reproduce a sequence

This demonstrates reproducibility under the current implementation, not a universal cross-version promise.

**Expected observation:** They produce equal arrays in the stated runtime.

## 3. Advance the generator

Reusing or recreating a generator defines different sampling procedures.

**Expected observation:** Its state advances and the arrays differ in the fixture.

## 4. Scale Monte Carlo work

An individual realization can still deviate unpredictably; the scaling is a statement about the sampling model.

**Expected observation:** The theoretical mean standard-error scale halves.

## 5. Inspect an extreme tail

Probability APIs have different numerical roles even when algebraic formulas look equivalent.

**Expected observation:** A stable tail API retains a small positive probability.

## 6. Interpret the plot

The chart is a mechanism demonstration and does not establish a real population distribution.

**Expected observation:** Finite simulated frequencies fluctuate around the model probabilities.

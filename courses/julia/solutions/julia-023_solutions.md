# julia-023: explained reference

The executable reference is `julia-023_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Check the objective sign

Successful numerical progress cannot validate a mistaken objective definition.

**Expected observation:** The mathematical problem changes.

## 2. Verify the known optimum

The test supports this convex fixture rather than a blanket global-convergence claim.

**Expected observation:** Objective and gradient are zero.

## 3. Inspect the feasible set

Constraints are part of the problem, not an optional display filter.

**Expected observation:** The best feasible point is near 2.

## 4. Read convergence evidence

Independent mathematical checks make the optimization result more interpretable.

**Expected observation:** They agree with the known quadratic solution.

## 5. Scale a parameter

Conditioning improvements should retain the original interpretation and feasible decisions.

**Expected observation:** Update penalties and constraints consistently.

## 6. Assess a fitted model

A better fit can still reflect overfitting, leakage or a poor target.

**Expected observation:** Evaluate the frozen procedure on independent data.

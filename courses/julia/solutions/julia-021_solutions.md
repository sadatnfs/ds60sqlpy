# julia-021: explained reference

The executable reference is `julia-021_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Recover the known model

A correct numerical recovery validates this fixture, not a population inference.

**Expected observation:** The coefficients are approximately[1,2].

## 2. Trace penalty selection

The final outcomes remain assessment inputs rather than selection inputs.

**Expected observation:** The selected penalty is 2.

## 3. Inspect the selected fit

An independent derivation checks the implementation and penalty convention.

**Expected observation:** They are 12/7 and 13/7.

## 4. Keep the final set separate

If final labels change the selection, the procedure is leaking assessment information.

**Expected observation:** The chosen penalty must remain unchanged.

## 5. Reject nonidentification

A numerical solution selection rule should not be mistaken for scientific identification.

**Expected observation:** The teaching helper raises an explicit error.

## 6. Report scope

Real deployment evidence needs representative independent data, uncertainty and diagnostics.

**Expected observation:** Report the observed error without a broad accuracy guarantee.

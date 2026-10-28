# julia-002: explained reference

The executable reference is `julia-002_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Retain a remainder

Integer division answers another question from floating-point division.

**Expected observation:** The integer quotient is 3 and remainder 1.

## 2. Reject a narrowing conversion

A constructor conversion that cannot represent the value must not be confused with wrapping arithmetic.

**Expected observation:** The conversion raises InexactError.

## 3. Keep an exact ratio

This preserves the intended ratio instead of first rounding decimal-looking binary floats.

**Expected observation:** The result equals 3//10 exactly.

## 4. Choose a precision

More precision changes representation cost and error; it does not validate the model.

**Expected observation:** Their types are Float32 and Float64.

## 5. Check a large integer

Converting a wrapped machine result afterward cannot reconstruct the lost value.

**Expected observation:** The mathematical integer is retained beyond the machine Int range.

## 6. Explain a tolerance

Representation, conditioning and algorithmic error inform a tolerance; passing an arbitrary bound proves little.

**Expected observation:** The bound uses that quantity units and required accuracy.

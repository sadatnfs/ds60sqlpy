# julia-031: explained reference

The executable reference is `julia-031_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Inspect syntax

The representation describes a call; this inspection does not evaluate arbitrary input.

**Expected observation:** The head is:call and the function symbol is:+.

## 2. Detect duplicate evaluation

The test protects against duplicated side effects in generated syntax.

**Expected observation:** The counter would be 2.

## 3. Check name ownership

Generated temporary names must not capture unrelated caller bindings.

**Expected observation:** The macro-local binding is hygienic.

## 4. Trace UTF 8 bytes

Unicode text has multiple valid units; choose the unit required by the interface.

**Expected observation:** The byte count is 2 and character count is 1.

## 5. Reject embedded zeros

Explicit validation prevents a truncated prefix from being mistaken for the full length.

**Expected observation:** C strlen would stop at the first zero.

## 6. Review a native API

A successful synchronous call does not establish a safe retained-pointer integration.

**Expected observation:** ABI, lifetime, ownership, thread safety and release rules.

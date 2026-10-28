# julia-027: explained reference

The executable reference is `julia-027_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## 1. Use qualified access

Qualified access works even without bringing the export into the caller namespace.

**Expected observation:** The result is[-1,1].

## 2. Trace exports

Export controls convenient importing; module qualification is not a security boundary.

**Expected observation:** It does not enforce privacy.

## 3. Inspect the project fixture

Metadata, implementation and tests serve distinct roles.

**Expected observation:** Project.toml declares identity; src/TinyScale.jl defines behavior.

## 4. Debug relative paths

Source-relative paths avoid hidden dependence on where the command was launched.

**Expected observation:** It anchors the path at the source file.

## 5. Design reproducible dependencies

A lock graph supports reproduction but does not alone qualify scientific outputs or service availability.

**Expected observation:** They identify declared and resolved dependency state.

## 6. Transfer into a real package

A pure public kernel is independently testable; IO and package operations can have separate integration checks.

**Expected observation:** The core takes values and returns values without network calls.

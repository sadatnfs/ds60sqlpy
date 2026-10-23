# cpp-012: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A translation unit is a source file after its includes are expanded. A header shares declarations across translation units. A declaration states a name and type; a definition supplies storage or a function body. The linker connects references to definitions. The one-definition rule prevents incompatible or multiply defined entities.

## Worked example 1

```cpp
int add(int,int);
int add(int a,int b) { return a+b; }
```

Expected: One declaration and one matching definition form a valid single-file demonstration.

## Worked example 2

```cpp
int missing(int);
// Calling missing(2) without a definition reaches a link error.
```

Expected: A declared but undefined called symbol compiles to an object, then fails to link.

## Exercise 1: Separate declaration

Split add declaration, definition and caller using the supplied host-project recipe.

**Expected:** math.hpp, math.cpp and main.cpp build one executable returning 5.

**Reasoning:** The compiler sees declarations; the linker finds the body.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Compile one object

Compile main.cpp with -c before linking.

**Expected:** main.o exists even though the function body is in math.cpp.

**Reasoning:** -c stops before the final link stage.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Link the complete set

Link main.o and math.o.

**Expected:** Executable runs, exit 0 and value 5.

**Reasoning:** Both object files contribute definitions/references.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Diagnose missing object

Omit math.o deliberately.

**Expected:** Nonzero link status naming an unresolved add symbol.

**Reasoning:** Changing an include cannot supply a missing linked definition.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Diagnose duplicate definition

Put a non-inline add body in a header included by both files.

**Expected:** A duplicate-definition link failure; restore one source definition.

**Reasoning:** Include guards operate per translation unit.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer a library boundary

Add subtract declaration and definition and a caller test 5-3.

**Expected:** Result 2 with one definition and matching signature.

**Reasoning:** Changing parameter types creates a different overload, not the intended definition.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

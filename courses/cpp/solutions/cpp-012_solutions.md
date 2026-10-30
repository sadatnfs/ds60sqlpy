# cpp-012: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

A translation unit is a source file after its includes are expanded. A header shares declarations across translation units. A declaration states a name and type; a definition supplies storage or a function body. The linker connects references to definitions. The one-definition rule prevents incompatible or multiply defined entities.

## Detailed reasoning

The compiler checks each translation unit independently. main.cpp knows that add takes two ints because it includes math.hpp, but its object file can contain an unresolved reference. math.cpp contributes the matching definition. The linker combines both objects and resolves that reference. Removing math.o breaks the final phase without making main.cpp invalid C++. Defining the same ordinary function in both objects creates a different link defect. Keep these failures as two independent diagnostic cases.

<!-- depth:start -->
## Declarations, definitions and translation units

A declaration tells the compiler that a function exists with a particular type. A definition supplies its body. A call can be type-checked from a declaration alone, which is why one source file can call a function implemented in another. The linker later connects the compiled references with definitions. This division is the reason a compile success is not necessarily a complete build success.

The complete programs here contain both declaration and definition so each can be copied into main.cpp and run independently. The separate multifile fixture moves the declaration into math.hpp, the definition into math.cpp and the caller into main.cpp. Each cpp file becomes a translation unit after preprocessing. Including a header copies its declarations into the caller's translation unit; it does not automatically compile and link a separate cpp implementation.

Compile-only commands using -c produce object files. Linking the main object without the math object should fail with an unresolved symbol for the called function. Linking both should produce the executable. A duplicate non-inline definition in two translation units can instead produce a multiple-definition error. Those are different linkage defects, and neither is repaired by repeatedly editing a correct call expression.

Header guards prevent repeated inclusion within one translation unit. They do not make an ordinary function definition safe to duplicate across multiple translation units. Use a declaration in the public header and one implementation definition, or use an appropriate inline/template definition under its own language rules. The one-definition rule has more nuance than a simple text-count rule, but the small fixture illustrates the common boundary.

The browser C++ profile stages only one main.cpp. It cannot prove that a separate header/library package is usable just because the same functions work in a combined source. The host project exercise compiles the real files and deliberately omits or duplicates one implementation to inspect the phase-specific diagnostic. Save each command, exit status and first relevant symbol message.

## Debugging the contract

A syntax/type diagnostic with a source line is usually from compilation. An undefined reference or unresolved external after object generation points toward linking. Check that the intended implementation file and compatible declaration are present in the link command. A binary that runs after a failed build may be an older artifact; chain execution to build success or remove ambiguity with a fresh owned build directory. Do not claim a multifile result from the single-file browser run.
<!-- depth:end -->

## Worked example 1

```cpp
int add(int, int);
int add(int a, int b) { return a + b; }
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

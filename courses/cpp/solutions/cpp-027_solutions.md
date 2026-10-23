# cpp-027: explanations and reference observations

Attempt the learner tasks before opening this document. The executable reference checks the bounded normal and boundary examples; the six explanations below cover the deliberate changes and manual checks.

## Mechanism

Reproducibility means another environment can reconstruct the same declared build inputs. Vendoring keeps an approved source dependency locally. A CMake target names include paths, features and link requirements so consumers inherit the right settings. A lock records exact dependency identities but still needs an actual offline build check.

## Worked example 1

```cpp
static_assert(vendored::api_version==1);
```

Expected: The expected source API version is pinned at compilation.

## Worked example 2

```cpp
assert(vendored::add(2,3)==5);
```

Expected: A consumer still checks behavior instead of trusting a version label.

## Exercise 1: Inventory inputs

List compiler, C++ level, dependency source and build generator.

**Expected:** Four concrete identities, including dependency content hash.

**Reasoning:** A package name without a version is not a reproducible input.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 2: Build offline

Build the supplied local target in a fresh owned directory without network.

**Expected:** Configure/build/test complete without downloads.

**Reasoning:** Every required dependency must already be present.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 3: Expose target requirements

Create a CMake interface target with cxx_std_20.

**Expected:** Consumer inherits the required language feature.

**Reasoning:** Target properties propagate intentional usage requirements.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 4: Repair hidden fetch

Review a configure script that downloads latest.zip.

**Expected:** Replace with checked local source and pinned reviewed identity.

**Reasoning:** Latest changes over time and violates offline default.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 5: Check licensing

Package the dependency license with the source inventory.

**Expected:** License path present in the delivery tree.

**Reasoning:** Technical reproducibility does not erase distribution obligations.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

## Exercise 6: Transfer another platform

Record an untested architecture as unqualified.

**Expected:** Separate built platform from planned platforms.

**Reasoning:** Configuration files are not execution evidence.

**Verify:** Compare your saved evidence with the stated value or field and explain the difference before editing an expectation.

# cpp-027: explanations and reference observations

The [executable reference](cpp-027_solution.cpp) adds `add(0, 0) == 0` and `add(-2, 2) == 0`. The explanations cover version pinning and what qualifying another architecture would require. How to compare: [study guide](../STUDY-GUIDE.md#compare-with-the-solutions).

## Mechanism

Reproducibility means another environment can reconstruct the same declared build inputs. Vendoring keeps an approved source dependency locally. A CMake target names include paths, features and link requirements so consumers inherit the right settings. A lock records exact dependency identities but still needs an actual offline build check.

## Detailed reasoning

Rebuilding from local inputs requires more than listing a dependency name. Record the exact source content, relevant build options, compiler and architecture, then attempt a fresh build without fetching anything. Target-scoped include directories and features help another consumer inherit the contract. The tiny vendored namespace in the single-file example illustrates identity and behavior checks; it does not prove that a dependency package or offline installation was actually built.

<!-- depth:start -->
## Dependency identity and reproducible local builds

A dependency is part of the program's input, not merely a name in a build file. Reproducibility requires identifying the exact source or binary artifact, version, build options and relevant toolchain. A local vendored dependency can support offline builds when its complete reviewed inputs are present. A declaration that fetches a dependency at configure time still has a network requirement, even if the main source is local.

The tiny vendored namespace demonstrates a version constant and a behavior check. static_assert verifies the expected API version at compile time, and add(2, 3)==5 checks a concrete operation. Those checks do not prove that an external package was downloaded, installed or independently built. They deliberately separate the idea of dependency identity from a host packaging workflow.

For a real local target, public include paths and required compile features belong to the target interface when consumers need them. Private implementation details should not leak into every consumer. A consumer that builds only because it happens to inherit a global include path is not a clean dependency contract. Test it from a fresh build directory with only the documented target relationship.

Offline qualification means attempting the build without fetching missing inputs. A populated developer cache can hide an undeclared dependency. Record which artifacts were already present and distinguish an offline rebuild from the initial connected preparation. Hashes can identify bytes, but they do not by themselves establish publisher trust or acceptable licensing.

Updating a dependency requires both compatibility and behavior review. An API-version constant may remain unchanged while behavior or ABI differs. Retain representative boundary tests and actual consumer acceptance for the supported platform. A successful single-file demonstration does not certify every architecture or toolchain mentioned in a README.

## Debugging the contract

If a clean build fails while a long-lived build succeeds, inspect undeclared generated files, caches and global include paths. If configure unexpectedly contacts the network, look for fetch commands and missing vendored inputs. If a consumer links but behaves differently, check the actual artifact identity and ABI configuration. Do not repair an offline failure by silently installing or downloading a new dependency during the lesson.
<!-- depth:end -->

## Worked example 1

```cpp
static_assert(vendored::api_version == 1);
```

Expected: The expected source API version is pinned at compilation.

## Worked example 2

```cpp
assert(vendored::add(2, 3) == 5);
```

Expected: A consumer still checks behavior instead of trusting a version label.

## Exercise 1: Inventory inputs

List compiler, C++ level, dependency source and build generator.

**Expected:** Four concrete identities, including dependency content hash.

**Reasoning:** A package name without a version is not a reproducible input.

**Verify:** Check that each of the four entries is a value you can re-read later, such as the `g++ --version` output, `-std=c++20`, a `sha256sum` of the dependency archive and Ninja.

## Exercise 2: Build offline

Build the supplied local target in a fresh owned directory without network.

**Expected:** Configure/build/test complete without downloads.

**Reasoning:** Every required dependency must already be present.

**Verify:** Run configure, build and ctest with networking disabled, for example inside `docker run --network none`, and confirm all three steps succeed.

## Exercise 3: Expose target requirements

Create a CMake interface target with cxx_std_20.

**Expected:** Consumer inherits the required language feature.

**Reasoning:** Target properties propagate intentional usage requirements.

**Verify:** Link a consumer target to the interface target without setting its own standard, then confirm its compile command, shown by `ninja -v`, contains `-std=c++20` or `-std=gnu++20`.

## Exercise 4: Repair hidden fetch

Review a configure script that downloads latest.zip.

**Expected:** Replace with checked local source and pinned reviewed identity.

**Reasoning:** Latest changes over time and violates offline default.

**Verify:** Confirm the repaired script uses a local archive or directory and checks a recorded hash, and that configure still succeeds with networking disabled.

## Exercise 5: Check licensing

Package the dependency license with the source inventory.

**Expected:** License path present in the delivery tree.

**Reasoning:** Technical reproducibility does not erase distribution obligations.

**Verify:** List the delivery tree and confirm the license file exists at exactly the path your inventory names.

## Exercise 6: Transfer another platform

Record an untested architecture as unqualified.

**Expected:** Separate built platform from planned platforms.

**Reasoning:** Configuration files are not execution evidence.

**Verify:** Check that your record lists the architecture you actually built and ran, from `uname -m`, separately from planned ones marked unqualified until executed.

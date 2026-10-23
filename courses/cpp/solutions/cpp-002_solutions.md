# cpp-002: explanatory solutions

Compare after an attempt or an explicit reveal. The [guide](../guides/cpp-002.md) defines the learner contract. An authored reference is not a platform acceptance receipt.

## Vocabulary and concepts

A build target gives a stable name to a program and its source list. CMake configures a build directory; the generated build tool compiles and links the target. CTest runs registered tests. Keeping build output outside the source directory makes the editable files obvious and lets Debug and Release builds coexist.

The single-file worker uses fixed compiler flags and can compile this source, but that result is not a CMake or CTest receipt. The optional manual CMake project is [CMakeLists.txt](../fixtures/cpp-002/CMakeLists.txt); it requires already-qualified CMake3.28+ and Ninja. Do not install tools during Run. Use a fresh owned scratch project with the learner file copied as main.cpp beside that CMakeLists.txt. In Bash or PowerShell, the common commands are `cmake -S . -B build/pilot -G Ninja -DCMAKE_BUILD_TYPE=Debug`, `cmake --build build/pilot`, then `ctest --test-dir build/pilot --output-on-failure`. A missing tool is a capability failure, not a learner-language error.

- **include:** makes a library declaration available to this translation unit
- **main:** the program entry function returning an integer status
- **std::cout:** the standard C++ output stream
- **target:** a named build product and its declared sources
- **CTest:** the CMake test runner; it must actually execute the registered test

## Worked example / walkthrough

### Worked example 1: Print one line

The << operator inserts text into the stream. The semicolon ends the statement and \n is the newline escape.

```cpp
#include <iostream>

int main() {
    std::cout << "hello, learner\n";
    return 0;
}
```

**Expected:** stdout is exactly hello, learner followed by a newline; exit0.

### Worked example 2: Reject a failed process

Normal text and a failure status can coexist. This example is a deliberate failure, not an answer to normalize to success.

```cpp
#include <iostream>
int main() { std::cerr << "fixture rejected\n"; return 2; }
```

**Expected:** stderr fixture rejected plus newline; exit2, intentionally.

## Exercises and explanatory solutions

### Exercise 1: Compile a fixed source

**Inputs/evidence:** For cpp-002 Exercise 1, main.cpp with iostream include and int main.

**Expected result/shape:** For cpp-002 Exercise 1, compilation and linking succeed; no syntax/link diagnostic.

**Verify:** For cpp-002 Exercise 1, record the actual compiler and status, not a copied transcript.

The target must list main.cpp. A successful process requires an executable from the current source, so preserve the build command and result separately from output.

### Exercise 2: Verify exact output

**Inputs/evidence:** For cpp-002 Exercise 2, unmodified hello program.

**Expected result/shape:** For cpp-002 Exercise 2, stdout hello, learner\n; empty stderr; exit0.

**Verify:** For cpp-002 Exercise 2, compare bytes/line ending and status independently.

A screenshot containing hello is weaker than an exact line check. The explicit newline terminates the greeting, and an empty diagnostic stream avoids hiding an unrelated error.

### Exercise 3: Rebuild after a literal edit

**Inputs/evidence:** For cpp-002 Exercise 3, same source except greeting literal.

**Expected result/shape:** For cpp-002 Exercise 3, stdout hello, reviewer\n after the new build.

**Verify:** For cpp-002 Exercise 3, compare source edit, rebuild receipt and new output; do not run a stale executable.

Only the intended literal changes. If output remains old, first verify the target and build directory rather than editing several unrelated source lines.

### Exercise 4: Diagnose a missing semicolon

**Inputs/evidence:** For cpp-002 Exercise 4, a deliberately invalid source copy.

**Expected result/shape:** For cpp-002 Exercise 4, nonzero compile result with a useful source location; no new successful run.

**Verify:** For cpp-002 Exercise 4, retain the compiler category, repair the semicolon and confirm a fresh build.

The compiler may point at the following token because that is where the grammar becomes impossible. Read nearby source rather than matching a vendor-specific full message.

### Exercise 5: Inspect an intentional nonzero exit

**Inputs/evidence:** For cpp-002 Exercise 5, stderr fixture rejected; return2.

**Expected result/shape:** For cpp-002 Exercise 5, nonzero runtime result2 and the diagnostic; this is expected failure evidence.

**Verify:** For cpp-002 Exercise 5, distinguish the successful build from failed execution.

The compiler accepts valid code that deliberately returns 2. That demonstrates why build success and program success must remain separate phases.

### Exercise 6: Verify the named CMake target

**Inputs/evidence:** For cpp-002 Exercise 6, main.cpp and the supplied CMakeLists.txt.

**Expected result/shape:** For cpp-002 Exercise 6, configure/build succeed and CTest executes one test named greeting.

**Verify:** For cpp-002 Exercise 6, retain all three phase results; if CMake/Ninja is absent label this check unavailable.

The fixed compiler worker can establish language execution but cannot claim it invoked CMake. The CMake target requires C++20 and registers a separate output-checking CTest test.

## Retrieval review

Close the source. Explain the mechanism in your own words, name the boundary that a plausible wrong answer crosses, and predict a changed fixture before running again.

A complete review accounts for every named expected value and one deliberately incorrect alternative. A process exit by itself does not grade reasoning.

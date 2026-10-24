#include <iostream>

int main() {
  std::cout << "hello, learner\n";
  return 0;
}

// Exercise 1: Compile a fixed source. Inputs: main.cpp with iostream include and int main. Expected: compilation and linking succeed; no syntax/link diagnostic. Verify: record the actual compiler and status, not a copied transcript.
// Exercise 2: Verify exact output. Inputs: unmodified hello program. Expected: stdout hello, learner\n; empty stderr; exit0. Verify: compare bytes/line ending and status independently.
// Exercise 3: Rebuild after a literal edit. Inputs: same source except greeting literal. Expected: stdout hello, reviewer\n after the new build. Verify: compare source edit, rebuild receipt and new output; do not run a stale executable.
// Exercise 4: Diagnose a missing semicolon. Inputs: a deliberately invalid source copy. Expected: nonzero compile result with a useful source location; no new successful run. Verify: retain the compiler category, repair the semicolon and confirm a fresh build.
// Exercise 5: Inspect an intentional nonzero exit. Inputs: stderr fixture rejected;return2. Expected: nonzero runtime result2 and the diagnostic; this is expected failure evidence. Verify: distinguish the successful build from failed execution.
// Exercise 6: Verify the named CMake target. Inputs: main.cpp and the supplied CMakeLists.txt. Expected: configure/build succeed and CTest executes one test named greeting. Verify: retain all three phase results; if CMake/Ninja is absent label this check unavailable.

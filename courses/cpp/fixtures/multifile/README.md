# Multiple-file C++ fixture

This optional host project supports `cpp-012`, `cpp-013`, `cpp-023`, `cpp-027`, `cpp-028`, `cpp-039` and `cpp-041`. Copy the whole directory to a new learner-owned scratch directory. Read the [compile/run tutorial](../../compile-and-run.md) for shell variants, flags and statuses. No dependency is downloaded. Inject faults only in your copy.

The header declares two functions behind an include guard. The implementation defines each once. The caller uses always-active checks. Expected stdout is `add=5 subtract=2` plus newline and exit status 0.

Run each command separately in the copied directory:

```text
g++ -std=c++20 -Wall -Wextra -Wpedantic -c main.cpp -o main.o
g++ -std=c++20 -Wall -Wextra -Wpedantic -c math.cpp -o math.o
g++ main.o math.o -o math_check
```

On Windows name the final output math_check.exe and run `& .\math_check.exe` in PowerShell. On POSIX run `./math_check`. For the missing-definition case link only main.o to a distinct broken_check output and retain the nonzero link status. For duplicate-definition diagnosis compile a copied implementation as a second object and link both definitions. Restore the original before proceeding.

With an already prepared CMake 3.28+ and Ninja, follow the tutorial's configure/build/test commands. Expected CTest result: one executed passing `arithmetic_contract` test. Direct compilation is not a CMake receipt. The fixture also has local install/export rules for its static library,public header and executable. Follow the Docker-only configure/build/CTest/install route in the tutorial when native tools are absent. Dynamic loading remains a separate exercise.

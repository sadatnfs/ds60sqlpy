# A real multi-file C project

This fixture accompanies c-028 and c-040. It separates a public header, one
implementation, a small executable and meaningful API tests. It needs a prepared
Linux or WSL 2 C development environment. The ordinary classroom pad remains a
single `main.c` and does not run this Makefile.

## Read the contract first

`stats_sum` borrows a pointer and count, leaves input unchanged, and writes a result
only on success. It distinguishes invalid arguments from signed overflow. A null
input is valid only for a zero count. The caller retains ownership of every object.

The header has an include guard and a C++ linkage wrapper. The wrapper makes the C
symbol declaration usable by C++ callers, but does not by itself prove that a
different language has declared every type and ownership rule correctly.

## Build and inspect the stages

From this fixture directory:

```sh
make
./build/stats-demo
make test
make sanitize
```

Expected demo output is `total=12`. Tests cover ordinary sums, empty input, invalid
pointer/count combinations, positive and negative overflow, boundary acceptance,
input preservation and failure-atomic output.

The normal build compiles `main.c` and `stats.c` into separate objects before
linking them. Changing `stats.h` rebuilds both because both compilation units
depend on the shared contract. A missing implementation object is a link failure;
a malformed declaration is a compilation failure. Keep that distinction visible
when diagnosing a build.

The sanitizer target compiles and links with AddressSanitizer and
UndefinedBehaviorSanitizer. It runs the safe regression tests under instrumentation.
It requires compiler/runtime support; ordinary classroom execution does not imply
sanitizer acceptance.

To place generated artifacts outside the source tree:

```sh
make BUILD_DIR="$LESSON_BUILD_DIR" all test
```

Set `LESSON_BUILD_DIR` to your own disposable build directory. `make clean` removes
only the named generated artifacts, not source files or arbitrary directories.

## Extend the project deliberately

Add a checked mean function with an explicit empty-input policy, then add tests
that reject division by zero and overflow-prone accumulation. Keep reusable
calculation separate from file parsing and presentation. If you add an installed
library, declare its version and build preparation rather than downloading it
from a running learner program.

This project uses ISO C17 and standard library headers. The separate C lessons
label POSIX-only APIs such as pthreads and descriptors explicitly.

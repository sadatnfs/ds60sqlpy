# Reusable record library project

Copy this whole directory into a new learner-owned scratch folder for `cpp-028`. The public record.hpp exposes only the owned result and parsing declaration. record.cpp supplies the strict parser; consumer.cpp tests four independent input rows. Expected output is accepted=2 rejected=2 and status 0. No source or dependency is downloaded.

With a prepared GCC/Clang compiler, run separately from the copied directory:

```text
g++ -std=c++20 -Wall -Wextra -Wpedantic -c record.cpp -o record.o
g++ -std=c++20 -Wall -Wextra -Wpedantic -c consumer.cpp -o consumer.o
g++ record.o consumer.o -o record_consumer
```

Use record_consumer.exe on Windows and the platform-specific run/status commands in [the tutorial](../../compile-and-run.md). The complete CMake project defines a static library, a separate consumer and an always-active test. It also defines local install/export rules for headers and the target. With prepared CMake 3.28+ and Ninja:

```text
cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug
ctest --test-dir build/debug --output-on-failure
cmake --install build/debug --prefix install-test
```

Keep install-test inside the copied scratch project. The export target file is under install-test/lib/cmake/ds60Records. This local export is an exercise boundary, not a published package or dynamic-library ABI guarantee. Record actual configure/build/test/install outputs; do not infer them from direct compiler success. Fault injection removes the suffix-consumption check in a copy, after which the consumer must reject the regression through a nonzero result.

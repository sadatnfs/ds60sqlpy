# C++: from a source file to a running program

This tutorial is the run-path reference for `cpp-001` through `cpp-042`. Start with a fresh learner pad or an owned scratch folder. Reading source, compiling it, linking it, running it and explaining the result are different activities. Save evidence for the activity you actually performed.

## 1. What is main.cpp?

`main.cpp` is a plain UTF-8 text file containing C++ source. The `.cpp` suffix tells common compiler drivers to interpret it as C++; it is not an executable. The base name `main` is a convention used by this course worker. A local compiler can compile `hello.cpp` instead if the command names that actual file. A program normally has one entry function named `main`, regardless of the source filename.

Do not paste Markdown fences into a source pad. A guide can contain several independent examples, while one source file must form one valid translation unit. Two pasted `int main()` definitions cause a compilation error. A file named `main.cpp.txt` may not be discovered or interpreted as expected. Enable visible extensions in your file manager and inspect the exact filename.

```cpp
#include <iostream>

int main() {
    std::cout << "hello, learner\n";
    return 0;
}
```

Read the program from top to bottom. The include supplies standard stream declarations. `int` is the entry function's return type. Parentheses contain its parameter list, empty here. Braces enclose its body. `std::` names the standard-library namespace, and `cout` is the normal output stream. The `<<` operator inserts the string into that stream. Quotes delimit text; `\n` is the newline escape inside the text. A semicolon ends the statement. Returning 0 reports process success.

The include supplies declarations, `main` supplies an entry point, the stream statement produces a line during execution, and the return value reports status. A successful compiler message does not prove either runtime observation.

## 2. Start with the Docker classroom

Follow the [Docker classroom guide](../../docs/docker-classroom.md) for initial preparation. An installed local Linux-container engine and prepared classroom images replace the need for a host C++ compiler. First preparation needs network access; later prepared runs use local images. Image setup is a deliberate action, not a side effect of opening a lesson.

From the course folder containing `compose.classroom.yaml`, add C++ after preparing the lab:

```text
docker compose -f compose.classroom.yaml --profile cpp20 --parallel 1 --progress plain build cpp-worker
docker compose -f compose.classroom.yaml --profile python-core --profile cpp20 up -d --no-build --pull never --wait lab python-core-worker cpp-worker
```

These commands work in Windows Command Prompt, PowerShell and POSIX terminals. Open [the local classroom](http://127.0.0.1:8765/journeys), select C++, read the guide and open the learner source. Predict, edit, save the pad, then choose Run. The worker copies the saved source into a job-owned directory as `main.cpp`, compiles and links it, then runs the resulting program under its limits.

Read compilation diagnostics separately from stdout, stderr and the exit code. A syntax error means the new program was not built successfully. A timeout means the recorded phase exceeded its budget. Save the explanation as well as the source. The read-only preview is not the learner editor.

Classroom pads live in the learning volume, separate from a visible local source folder. Export evidence before moving machines and follow the classroom guide's stop/backup procedures. A successful example run does not finish six exercises or prove mastery. Only the existing `cpp-009` pilot has a registered independent ownership verifier; other lesson Runs execute the source without automatic exercise grading.

## 3. Optional native compilation

Use an already prepared GCC-compatible `g++` or `clang++` with C++20 support. Inspect `g++ --version` or `clang++ --version`; on macOS a command named g++ can invoke Clang. Command-not-found is a tooling issue, not a language error. Use Docker if a compatible compiler is unavailable. MSVC `cl` uses different flags and is not covered by the GCC/Clang command blocks below.

Make a fresh learner-owned folder, save the example as `main.cpp`, and open a terminal in that folder. Do not paste the shell prompt character into the command. Replace g++ with clang++ when that is your prepared compiler.

POSIX shell, including Bash or Zsh:

```sh
pwd
ls -l main.cpp
g++ -std=c++20 -O0 -g -Wall -Wextra -Wconversion -Wpedantic -pthread main.cpp -o hello
compile_status=$?
printf 'compile/link status: %s\n' "$compile_status"
if [ "$compile_status" -eq 0 ]; then
    ./hello
    run_status=$?
    printf 'run status: %s\n' "$run_status"
fi
```

Windows PowerShell with a prepared GCC-compatible compiler:

```powershell
Get-Location
Get-Item .\main.cpp
g++ -std=c++20 -O0 -g -Wall -Wextra -Wconversion -Wpedantic -pthread .\main.cpp -o .\hello.exe
$compileStatus = $LASTEXITCODE
Write-Output "compile/link status: $compileStatus"
if ($compileStatus -eq 0) {
    & .\hello.exe
    $runStatus = $LASTEXITCODE
    Write-Output "run status: $runStatus"
}
```

Expected: stdout `hello, learner` plus a newline, empty stderr, build status 0 and runtime status 0. Capture each status immediately because the next command can replace it. The conditional avoids running an old binary after a failed new build.

The driver normally performs preprocessing, compilation, assembly and linking. `-std=c++20` selects the language standard, `-O0` favors debugging, `-g` includes debug data, and the warning groups request useful diagnostics. `-pthread` selects supported thread compilation/link options. `-o hello` names the output; it is the letter o. Stage controls are documented in the [GCC driver manual](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html).

## 4. Paths, file formats and stale binaries

Relative paths start from the terminal's working directory. POSIX `./hello` and PowerShell `.\hello.exe` explicitly select the local executable. The program's `ifstream("readings.txt")` resolves a runtime file from the process working directory, not from the source file's old directory.

Quote paths containing spaces. POSIX: `g++ "my work/main.cpp" -o "my work/hello"`, then `"./my work/hello"`. PowerShell: `g++ ".\my work\main.cpp" -o ".\my work\hello.exe"`, then `& ".\my work\hello.exe"`. The call operator `&` in this form is PowerShell syntax.

Source is text. An `.o` object contains compiled code awaiting linking. A linked executable contains the program to start. A `.csv` input is data with a separately specified delimiter/field contract. Renaming one suffix does not convert its format. When sharing evidence, retain source and data as text, and treat compiled binaries as platform-specific artifacts.

Saving source does not update an old executable. If the new build fails, the prior output file can remain and print the prior greeting. Keep the exact source edit, build status and execution status together. An editor save notification is not a build receipt.

## 5. Diagnose the first failing phase

| Observation | Phase | Smallest useful check |
| --- | --- | --- |
| Expected semicolon near a line | Compilation | Inspect the preceding statement and braces |
| cout not declared | Compilation | Check iostream include and std namespace |
| Undefined reference/unresolved external | Linking | Check definition, signature and object/source list |
| Duplicate symbol/multiple definition | Linking | Check repeated non-inline definitions |
| Diagnostic text and exit 2 | Execution | Check runtime validation branch and input |
| File-open failure | Execution | Inspect working directory and resolved path |
| Timeout | Recorded build or execution phase | Inspect budget, loop conditions and workload |

In a scratch copy remove the output statement semicolon, build, retain the source location and phase, then repair and rebuild. Exact vendor wording can vary.

For a linker experiment, compile this separate source:

```cpp
int answer();
int main() { return answer(); }
```

`g++ -std=c++20 -c main.cpp -o main.o` stops before linking, so the declaration is enough. `g++ main.o -o hello` then fails because no definition of answer was linked. Supply exactly one matching definition, `int answer() { return 0; }`, and rebuild. The [GCC stage controls](https://gcc.gnu.org/onlinedocs/gcc/Overall-Options.html) explain this object/link separation.

A valid program can deliberately fail its runtime contract:

```cpp
#include <iostream>
int main() {
    std::cerr << "input rejected\n";
    return 2;
}
```

Expected: compilation/linking succeed, stdout is empty, stderr is `input rejected` plus newline, runtime exit is 2. Do not turn every nonzero result into success just to make a test green.

## 6. Multiple files and CMake

The browser stages one C++ file. It does not accept arbitrary sibling headers, source trees, CMake scripts or compiler flags. Files created by a lesson live inside its bounded job and are not automatically durable exported learner artifacts. Record their contents or checks in evidence. Single-file execution cannot qualify a shared library, package installation, debugger, sanitizer configuration or multifile build.

For `cpp-012` and later boundary exercises copy the complete [multifile fixture](fixtures/multifile/README.md) into a new learner-owned host project. `math.hpp` declares functions, `math.cpp` defines them, and `main.cpp` calls them. Adding a header declaration does not add a source definition to the link target.

CMake configures a build system from target definitions; it is not the compiler. With an already prepared CMake 3.28+ and Ninja, run these commands individually from the copied project root in either shell:

```text
cmake -S . -B build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
cmake --build build/debug
ctest --test-dir build/debug --output-on-failure
```

`-S` chooses source and `-B` generated build output. `add_executable` names the program sources, and `target_link_libraries` connects the caller to the library target. CTest actually executes registered checks. Debug and Release need separate build directories. See the [CMake 3.28 tutorial](https://cmake.org/cmake/help/v3.28/guide/tutorial/index.html).

Missing CMake/Ninja leaves the CMake row unavailable even when direct compilation works. Do not infer CMake or CTest acceptance from a source review or compiler success. Do not install tools automatically during Run.

## 7. Concurrency, instrumentation and evidence

Concurrent examples join their owned workers and use bounded fixture sizes. A cooperative stop flag/token must be checked by the worker body; it does not interrupt arbitrary code. AddressSanitizer/UBSan and ThreadSanitizer are separate optional instrumented host builds with matching runtime libraries. Their flags are not browser-pad options. Never run intentionally racy or invalid memory code through the ordinary profile to simulate a detector.

A native Clang pass does not qualify GCC Docker execution. One Docker architecture does not qualify every OS. Record compiler, architecture, flags, exact fixture, output, status and tooling limitations.

Before advancing, explain a source edit followed by a failed build and stale executable, a declaration compiled with no linked definition, and a valid program returning 2. These phase distinctions make later C++ diagnostics understandable.

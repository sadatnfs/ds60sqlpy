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

From the complete course folder, select the C++ profile through the maintained
launcher. Run the same command in a POSIX terminal on Linux, macOS or Windows
through WSL 2:

```sh
./classroom --profile cpp20
```

This selection includes Python Core and C++. It replaces the remembered profile
selection without stopping other workers that are already running; see
[profile selection](../../docs/docker-profiles.md) when retaining a larger set.
Open the exact `/classroom` URL printed by the launcher rather than assuming a
fixed host port. Select C++, read the guide and open the learner source. Predict,
edit, save the pad, then choose Run. The worker stages the submitted source as
`main.cpp`, compiles and links it, then runs the program under its limits.

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

The maintained Windows contributor route uses the POSIX block in WSL 2.
The following PowerShell comparison is self-contained for an already prepared
native GCC-compatible compiler. Native Windows compiler installation and
qualification are outside the classroom support contract:


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

Missing native CMake/Ninja leaves the native CMake route unavailable;the Docker-only route below uses the prepared image instead. Do not infer CMake or CTest acceptance from a source review or compiler success. Do not install tools automatically during Run.

### Docker-only CMake project route

Use this route when the host has Docker but no C++ compiler, CMake or Ninja. The already prepared `ds60sqlpy-worker-cpp20:0.4.1` image contains those tools. The commands override its worker entry point for a short, offline project operation. They do not require starting the classroom broker or mounting its token. Run from the repository root and use a local Linux-container engine. A remote Docker daemon cannot bind a folder from your local computer.

Choose either `record-library` or `multifile`. Make a **new copy** before editing. The example name ends in `-01`; choose a new unused suffix for another attempt. Never point the writable project mount at the whole repository, your home folder or an existing learner project. A failure to create the new directory is a stop condition, not permission to overwrite it.

On Linux, macOS or Windows through WSL 2, use a POSIX terminal:

```sh
cpp_fixture=record-library
cpp_project="$PWD/.learning/cpp-projects/${cpp_fixture}-01"
mkdir -p "$PWD/.learning/cpp-projects"
mkdir "$cpp_project" && cp -R "courses/cpp/fixtures/$cpp_fixture/." "$cpp_project/"
```

Stop if either creation or copy fails. The absolute `cpp_project` path identifies the host folder. Quoting preserves spaces. The `--mount` syntax below treats commas as separators, so choose a project path without commas. On Docker Desktop for macOS, ensure this folder is inside an already shared location. On Linux, the UID/GID arguments below keep created files owned by your current user. If the engine's configured file-sharing or security policy denies the mount, diagnose that host setup rather than making the container privileged.

```sh
cpp_image=ds60sqlpy-worker-cpp20:0.4.1
cpp_tool() {
    cpp_entrypoint="$1"
    shift
    docker run --rm --pull never --network none --read-only \
      --cap-drop ALL --security-opt no-new-privileges \
      --pids-limit 128 --cpus 2 --memory 1g \
      --user "$(id -u):$(id -g)" \
      --tmpfs /tmp:rw,exec,nosuid,size=256m \
      --mount "type=bind,source=$cpp_project,target=/project" \
      --workdir /project --entrypoint "$cpp_entrypoint" "$cpp_image" "$@"
}
cpp_tool cmake -S /project -B /project/build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug &&
cpp_tool cmake --build /project/build/debug --parallel 2 &&
cpp_tool ctest --test-dir /project/build/debug --output-on-failure &&
cpp_tool cmake --install /project/build/debug --prefix /project/install
```

Each `&&` requires the preceding phase to succeed. The final command status is available immediately as `$?`. A failure stops the chain, preserving the copied source and partial diagnostics for investigation. To capture a phase separately, run one `cpp_tool` command and inspect its status before continuing.

The maintained Windows route uses the POSIX blocks above inside WSL 2. The following optional PowerShell comparison requires separately prepared native Windows engine file sharing; that host workflow is outside classroom release qualification. Use the actual Windows path returned by `Join-Path`/`Resolve-Path`; do not translate it manually into `/c/...`. If you use WSL instead, use the POSIX block with paths visible to that WSL-integrated engine and keep that choice consistent for the whole build directory.

```powershell
$CppFixture = 'record-library'
$CppProject = Join-Path (Get-Location).Path ".learning/cpp-projects/$CppFixture-01"
if (Test-Path -LiteralPath $CppProject) { throw 'Choose a new unused project suffix.' }
New-Item -ItemType Directory -Path $CppProject -ErrorAction Stop | Out-Null
Copy-Item -Path "courses/cpp/fixtures/$CppFixture/*" -Destination $CppProject -Recurse -ErrorAction Stop
$CppProject = (Resolve-Path -LiteralPath $CppProject).Path
$CppImage = 'ds60sqlpy-worker-cpp20:0.4.1'
$CppDockerArgs = @(
    'run', '--rm', '--pull', 'never', '--network', 'none', '--read-only',
    '--cap-drop', 'ALL', '--security-opt', 'no-new-privileges',
    '--pids-limit', '128', '--cpus', '2', '--memory', '1g',
    '--user', '1000:1000', '--tmpfs', '/tmp:rw,exec,nosuid,size=256m',
    '--mount', "type=bind,source=$CppProject,target=/project",
    '--workdir', '/project'
)
function Invoke-CppTool {
    param(
        [string]$Tool,
        [Parameter(ValueFromRemainingArguments=$true)][string[]]$ToolArgs
    )
    & docker @CppDockerArgs --entrypoint $Tool $CppImage @ToolArgs
    if ($LASTEXITCODE -ne 0) { throw "Container tool $Tool failed with exit $LASTEXITCODE." }
}
Invoke-CppTool cmake -S /project -B /project/build/debug -G Ninja -DCMAKE_BUILD_TYPE=Debug
Invoke-CppTool cmake --build /project/build/debug --parallel 2
Invoke-CppTool ctest --test-dir /project/build/debug --output-on-failure
Invoke-CppTool cmake --install /project/build/debug --prefix /project/install
```

The Windows route uses a nonroot container identity and Docker Desktop's host-file sharing. If the prepared engine cannot write that shared folder under this identity, leave the operation failed and resolve the documented sharing setup. Do not silently switch to privileged mode or mount an engine socket. The single quoted mount argument supports spaces; use a path without commas. Docker's [bind-mount guide](https://docs.docker.com/engine/storage/bind-mounts/) explains why the source path belongs to the daemon host and why files persist outside a removed container.

Expected for `record-library`: CTest runs `record_contract` and reports one passing test. Installation writes `install/include/record.hpp`, `install/lib/libds60_records.a` and exported target files under `install/lib/cmake/ds60Records`. Expected for `multifile`: CTest runs `arithmetic_contract`, checks `add=5 subtract=2`, and reports one passing test. Installation writes `install/include/math.hpp`, `install/lib/libds60_math.a`, `install/bin/math_check` and exported target files under `install/lib/cmake/ds60Math`. To run that second workflow, choose `multifile` and a new project directory at the copy step; the configure/build/test/install commands stay the same.

The copied source, `build/debug/`, CTest log `build/debug/Testing/Temporary/LastTest.log`, and `install/` are durable files in the learner-owned host project. `--rm` removes only each temporary container. It does not delete the bind-mounted project. The installed binaries and static libraries are Linux artifacts for the container architecture, even on Windows or macOS; do not try to launch them as native Windows `.exe` or macOS binaries. Run them inside the same prepared image, for example `cpp_tool /project/install/bin/math_check` or `Invoke-CppTool /project/install/bin/math_check` after the multifile installation.

Use a separate `build/release` and install prefix for a Release comparison. Never reuse a native CMake cache inside Docker or a Docker cache on another architecture. A fresh directory preserves the compiler/path identity. Installing into `/project/install` is a local packaging exercise, not a system-wide installation. See the [CMake install interface](https://cmake.org/cmake/help/v3.28/manual/cmake.1.html#install-a-project) for the build/install distinction.

This project route is separate from the browser pad, which still accepts one C++ translation unit. Save your project edits and phase logs with the project; they are not automatically copied into the classroom learner pad or its progress record.

## 7. Concurrency, instrumentation and evidence

Concurrent examples join their owned workers and use bounded fixture sizes. A cooperative stop flag/token must be checked by the worker body; it does not interrupt arbitrary code. AddressSanitizer/UBSan and ThreadSanitizer are separate optional instrumented host builds with matching runtime libraries. Their flags are not browser-pad options. Never run intentionally racy or invalid memory code through the ordinary profile to simulate a detector.

A native Clang pass does not qualify GCC Docker execution. One Docker architecture does not qualify every OS. Record compiler, architecture, flags, exact fixture, output, status and tooling limitations.

Before advancing, explain a source edit followed by a failed build and stale executable, a declaration compiled with no linked definition, and a valid program returning 2. These phase distinctions make later C++ diagnostics understandable.

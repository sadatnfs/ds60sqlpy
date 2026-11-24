# julia-027: explained reference

The executable reference is `julia-027_reference.jl`. Its checks cover the stated authored inputs; they are not a claim of general scientific validity or mastery.

## Approach

Modules are namespaces, files are source text, and project files record dependencies; keep the three apart. `LocalStats.center` subtracts the mean and rejects empty input. Worked example B writes a tiny `TinyScale` project into a temporary directory and includes its test file into a fresh module with no network or package resolution.

## 1. Use qualified access

Qualified access works even without bringing the export into the caller namespace.

**Expected observation:** The result is `[-1, 1]`.

**Why it holds here:** The mean of `[2, 4]` is 3, so subtracting it gives `[-1, 1]`, reached through the module name `LocalStats`.

**Plausible wrong approach:** Calling `center` without qualification or `using .LocalStats` fails with `UndefVarError`, since the name lives inside the module.

**How to verify:** The reference asserts `LocalStats.center([2, 4]) == [-1, 1]` and `LocalStats.center([5]) == [0]`.

## 2. Trace exports

Export controls convenient importing; module qualification is not a security boundary.

**Expected observation:** It does not enforce privacy.

**Why it holds here:** `export center` only decides what `using` brings in; any unexported name is still reachable as `LocalStats.name`.

**Plausible wrong approach:** Leaving a helper unexported to hide a secret assumes access control that Julia modules do not provide.

**How to verify:** Check `:center in names(LocalStats)` and confirm an unexported helper is still callable with a qualified name.

## 3. Inspect the project fixture

Metadata, implementation and tests serve distinct roles.

**Expected observation:** Project.toml declares identity; src/TinyScale.jl defines behavior.

**Why it holds here:** `Project.toml` holds the name, UUID and version, `src/TinyScale.jl` defines `twice`, and `test/runtests.jl` exercises it.

**Plausible wrong approach:** Putting test assertions in the source module makes every import run them and mixes behavior with verification.

**How to verify:** Example B asserts `isfile(joinpath(root, "Project.toml"))` and that including the tests returns `true`.

## 4. Debug relative paths

Source-relative paths avoid hidden dependence on where the command was launched.

**Expected observation:** It anchors the path at the source file.

**Why it holds here:** `@__DIR__` expands to the directory of the file that contains it, so the path to `../src/TinyScale.jl` works from any working directory.

**Plausible wrong approach:** Writing `include("src/TinyScale.jl")` works only when the process starts in the project root.

**How to verify:** Run the test file from another directory and confirm it still loads; the reference shows a missing path raising `SystemError`.

## 5. Design reproducible dependencies

A lock graph supports reproduction but does not alone qualify scientific outputs or service availability.

**Expected observation:** They identify declared and resolved dependency state.

**Why it holds here:** A manifest records resolved package versions, which helps reproduce code, but it does not record hardware, data files or remote services.

**Plausible wrong approach:** Claiming a result is reproducible because a manifest is committed ignores changes in input data or BLAS threads.

**How to verify:** List the extra facts, such as data checksum and thread count, alongside the manifest.

## 6. Transfer into a real package

A pure public kernel is independently testable; IO and package operations can have separate integration checks.

**Expected observation:** The core takes values and returns values without network calls.

**Why it holds here:** A pure function that takes a vector of numbers and returns results can be tested without files, while reading CSV stays in a thin IO layer.

**Plausible wrong approach:** Reading the file inside the numerical function forces every unit test to create files and couples failures in IO with math errors.

**How to verify:** Write one unit test that calls the core with literal values and one integration test that reads a small file.

## Reference checks

The reference's `exercise_checks` function runs these assertions before `main` prints `julia-027: all reference checks passed`:

The module lines use qualified access and also confirm that `center` is listed among exported names. The final `SystemError` shows that a missing source path fails at include time instead of later, at first use. The `joinpath` comparison is a reminder that file paths and module names are different strings, so renaming one does not rename the other.

```julia
function exercise_checks()
    @test LocalStats.center([2, 4]) == [-1, 1]
    @test LocalStats.center([5]) == [0]
    @test isdefined(LocalStats, :center)
    @test :center in names(LocalStats)
    @test joinpath("src", "TinyScale.jl") != "TinyScale.jl"
    @test_throws SystemError Base.include(
        Module(:MissingFixture),
        joinpath(tempdir(), "ds60-no-such-owned-source.jl"),
    )
end
```

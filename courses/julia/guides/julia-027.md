# julia-027: Modules, source loading and reproducible projects

## Starting point and outcome

Advanced; approximately 150 minutes. Direct prerequisites: `julia-009`, `julia-011`.

Separate namespaces from source files, execute a tiny owned multi-file project offline, and distinguish locked dependencies from code loading.

## Classroom execution

Choose **Julia language and scientific computing** in `/classroom`, open this unit, and select its prepared `julia` runtime. The worker starts a fresh `main.jl` process with two Julia threads, a fixed package environment, no startup file and offline package settings. Both worked examples are complete under that environment. Save your current pad before replacing it. No package, model or dataset is fetched by a lesson.

## A namespace and a file are different things

A `module` creates a namespace with its own bindings. `export` declares names that a caller can bring into scope with `using`; it does not make other names private or inaccessible. Qualified access such as `LocalStats.center` makes ownership visible. `import` is useful when deliberately extending another module's function, while defining your own function with the same short name can instead create a different generic function.

A source file is just stored program text. `include(path)` evaluates that text in the target module and returns the final expression's value. It can run arbitrary top-level code, so include only reviewed owned sources. Repeated inclusion can redefine methods or types. Source loading is not a security sandbox, dependency resolver or idempotent database migration.

A relative `using .LocalStats` refers to a module already available in the current namespace. The leading dot matters. An unqualified package name instead participates in Julia's code-loading and environment rules. Keep these concepts separate when debugging a missing-name error.

### Worked case A: a small reusable namespace

The first complete program defines a module with one exported transformation. Centering subtracts the arithmetic mean: for observations \(x_1,\ldots,x_n\), \(z_i=x_i-\bar{x}\). The sum is approximately zero in floating arithmetic. Empty input is rejected because the intended mean is undefined.

```julia
using Test
using Statistics

module LocalStats
using Statistics
export center
function center(values)
    isempty(values) && throw(ArgumentError("At least one value is required"))
    return values .- mean(values)
end
end

function worked_a()
    original = [1.0, 2.0, 3.0]
    centered = LocalStats.center(original)
    @test centered == [-1, 0, 1]
    @test original == [1, 2, 3]
    @test sum(centered) == 0
    @test_throws ArgumentError LocalStats.center(Float64[])
    println("Qualified module result: ", centered)
end

worked_a()
```

The test does not demand exact zero for every floating dataset. It uses a small exact fixture to show the contract, and later units use tolerances for scientific calculations. Mutation is avoided here: the returned centered vector has separate storage.

## Project structure and dependency state

A reusable package convention places `Project.toml` beside `src/PackageName.jl` and `test/runtests.jl`. The project declares identity, direct dependencies and compatibility. A Manifest records a resolved dependency graph, including versions and source identities. A copied Manifest helps reproduce that graph but does not vendor every external binary, guarantee identical hardware arithmetic or authorize network access.

The classroom already has a prepared read-only project. Do not run `Pkg.add`, alter its Manifest or download a package inside a lesson. A real new project can be developed later in an explicitly owned writable environment. Commit source, Project and the appropriate lock state according to that project's deployment policy. Keep secrets, machine paths and learner data out of the package.

### Worked case B: exercise a real multi-file layout

The second example creates a tiny package-shaped directory in an owned temporary directory, writes source and a test entrypoint, then includes that test into a fresh module. It executes actual files without dependency resolution or downloads. The reference deliberately calls this source-loading evidence, not a full `Pkg.test` or registry-publication qualification.

```julia
using Test
using Statistics

module LocalStats
using Statistics
export center
function center(values)
    isempty(values) && throw(ArgumentError("At least one value is required"))
    return values .- mean(values)
end
end

function worked_b()
    mktempdir() do root
        mkpath(joinpath(root, "src"))
        mkpath(joinpath(root, "test"))
        write(
            joinpath(root, "Project.toml"),
            "name = \"TinyScale\"\nuuid = \"7c087348-1b29-4e97-8d15-e711b29d8d5a\"\nversion = \"0.1.0\"\n",
        )
        write(
            joinpath(root, "src", "TinyScale.jl"),
            "module TinyScale\nexport twice\ntwice(x) = 2x\nend\n",
        )
        write(
            joinpath(root, "test", "runtests.jl"),
            "using Test\nBase.include(@__MODULE__, joinpath(@__DIR__, \"..\", \"src\", \"TinyScale.jl\"))\nusing .TinyScale\n@test twice(3) == 6\n@test twice(-2) == -4\ntrue\n",
        )
        target = Module(:OwnedFixture)
        result = Base.include(target, joinpath(root, "test", "runtests.jl"))
        @test result === true
        @test isfile(joinpath(root, "Project.toml"))
        println("Owned source and test files executed without package resolution")
    end
end

worked_b()
```

## Loading boundaries and failure diagnosis

Top-level method definitions may introduce world-age considerations when code is dynamically loaded inside an already-running function. The fixture performs its assertions inside the included test file so those definitions and calls are evaluated coherently. Avoid building production plugin systems around arbitrary repeated eval; prefer explicit module boundaries and documented extension points.

A missing `export` usually does not mean the function was not defined. Inspect the qualified name. A missing file is a path problem; compute project-relative paths with `joinpath` and `@__DIR__` rather than assuming the process working directory. A package-not-found error concerns the active environment and loading rules, not necessarily the source syntax.

## Transfer to a maintained scientific library

Separate a pure numerical kernel from CSV preparation, plotting and command-line entrypoints. Pure functions are easier to test without files or services. Write tests against public behavior, including shape and invalid-input contracts. Record the Julia version and dependency graph used for a release, and qualify the real package workflow in its owned environment. The classroom fixture teaches the structural pieces while preserving the offline prepared runtime that makes these lessons reproducible.


## Six investigations

### 1. Use qualified access

Call LocalStats.center on[2,4].

**Expected:** The result is[-1,1].

**Hint:** The module owns the name.

### 2. Trace exports

Explain whether export makes other names private.

**Expected:** It does not enforce privacy.

**Hint:** Compare name lookup with access control.

### 3. Inspect the project fixture

Identify which file declares identity and which defines twice.

**Expected:** Project.toml declares identity; src/TinyScale.jl defines behavior.

**Hint:** The test file consumes the source.

### 4. Debug relative paths

Explain why @__DIR__ is used in the test entrypoint.

**Expected:** It anchors the path at the source file.

**Hint:** The process working directory may differ.

### 5. Design reproducible dependencies

List what Project and Manifest do and do not establish.

**Expected:** They identify declared and resolved dependency state.

**Hint:** Hardware, data and external services need separate records.

### 6. Transfer into a real package

Separate a CSV workflow into numerical core, IO and tests.

**Expected:** The core takes values and returns values without network calls.

**Hint:** Keep side effects at explicit boundaries.

## Primary references

- [Julia modules](https://docs.julialang.org/en/v1/manual/modules/)
- [Julia code loading](https://docs.julialang.org/en/v1/manual/code-loading/)
- [Creating packages](https://pkgdocs.julialang.org/v1/creating-packages/)

## Study companion

Use the repository learning-companion skill with this lesson ID, your prediction and your actual source/output. Ask for a diagnosis of the first incorrect type, shape, state transition or assumption. Keep observed execution distinct from a timing claim, inferred mathematical result or external deployment.

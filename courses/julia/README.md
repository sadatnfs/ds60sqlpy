# Julia language and scientific computing

A complete 32-unit progression from first scripts to numerical work, data contracts, generic functions, concurrency and reproducible scientific analysis. The classroom uses the prepared Linux Julia profile, with no package downloads during a lesson.

Start with the [main classroom instructions](../../README.md). Julia source is staged as `main.jl` in a fresh process. Code, notes and receipts are saved by the classroom; scratch files disappear after the run. Optional projects and unfamiliar external ecosystems need their own preparation.

| Unit | Stage | Topic |
| --- | --- | --- |
| [julia-001](guides/julia-001.md) | beginner | First Julia scripts, values and observable output |
| [julia-002](guides/julia-002.md) | beginner | Numbers, promotion, overflow and exactness |
| [julia-003](guides/julia-003.md) | beginner | Strings, Unicode and indexing boundaries |
| [julia-004](guides/julia-004.md) | beginner | Conditions, equality and explicit missing decisions |
| [julia-005](guides/julia-005.md) | beginner | Loops, ranges, comprehensions and scope |
| [julia-006](guides/julia-006.md) | beginner | Functions, keywords, closures and argument sharing |
| [julia-007](guides/julia-007.md) | beginner | Arrays, shapes, copies and views |
| [julia-008](guides/julia-008.md) | beginner | Tuples, named records, dictionaries and sets |
| [julia-009](guides/julia-009.md) | beginner | Errors, tests and explicit input contracts |
| [julia-010](guides/julia-010.md) | intermediate | Composite types, constructors and nested mutability |
| [julia-011](guides/julia-011.md) | intermediate | Multiple dispatch and method specificity |
| [julia-012](guides/julia-012.md) | intermediate | Parametric types and generic numerical code |
| [julia-013](guides/julia-013.md) | intermediate | Broadcasting, axes and mutation order |
| [julia-014](guides/julia-014.md) | intermediate | Missing values, absence and nonfinite measurements |
| [julia-015](guides/julia-015.md) | intermediate | DataFrames transformations and grouped summaries |
| [julia-016](guides/julia-016.md) | intermediate | Joins, key validation and duplicate fanout |
| [julia-017](guides/julia-017.md) | intermediate | Typed CSV input and round-trip data contracts |
| [julia-018](guides/julia-018.md) | intermediate | Dates, availability time and historical features |
| [julia-019](guides/julia-019.md) | intermediate | Linear algebra, conditioning and nonunique solutions |
| [julia-020](guides/julia-020.md) | intermediate | Distributions, random state and Monte Carlo evidence |
| [julia-021](guides/julia-021.md) | advanced | Regression fitting, regularization and held-out assessment |
| [julia-022](guides/julia-022.md) | advanced | Forward-mode automatic differentiation |
| [julia-023](guides/julia-023.md) | advanced | Optimization objectives, constraints and convergence |
| [julia-024](guides/julia-024.md) | advanced | Numerical methods, stability and error contracts |
| [julia-025](guides/julia-025.md) | advanced | Inference, profiling and measured performance |
| [julia-026](guides/julia-026.md) | advanced | Allocation, mutation and alias-safe numerical work |
| [julia-027](guides/julia-027.md) | advanced | Modules, source loading and reproducible projects |
| [julia-028](guides/julia-028.md) | advanced | Property testing and reproducible numerical evidence |
| [julia-029](guides/julia-029.md) | advanced | Tasks, channels and bounded asynchronous pipelines |
| [julia-030](guides/julia-030.md) | advanced | Threads, ownership and deterministic reductions |
| [julia-031](guides/julia-031.md) | advanced | Expressions, hygienic macros and C interoperability |
| [julia-032](guides/julia-032.md) | advanced | Scientific capstone: an auditable offline modeling report |

## Prepared environment and boundaries

The Julia profile uses a locked project containing CSV, DataFrames, Distributions, ForwardDiff, Optim and JSON3. The classroom-specific `DS60Plots` helper writes bounded Plotly figures for browser display; it is not a standard Julia plotting package. Standard libraries support tests, dates, Unicode, arrays and linear algebra. GPU packages, distributed clusters and external services are separate optional projects. A successful source run does not establish numerical conditioning, statistical validity or universal performance. See [authoring](authoring/README.md) for maintained source and checks.

# R: programming, statistical computing and visualization

This 60-lesson course starts with expressions and vectors, then develops functions, data contracts, object systems, analytical software, statistical modeling and visualization. It covers base R, S3, S4, R6, S7, base graphics, ggplot2 and Plotly using original small offline examples.

## Start in the Docker classroom

From the repository root:

```bash
./classroom --profiles r-statistics
```

Choose **R** in the classroom directory. The launcher prepares missing local images and retains this project selection for later resumes. Keep the same custom project name if you use one. See the [front README](../../README.md) for Docker setup on macOS/Linux and Windows through WSL 2. You do not need a host R installation.

Use the classroom's R language pad and prepared r-statistics profile. Each run evaluates one main.R script in a fresh offline R process. Define every required input in the script; earlier runs do not leave live variables behind. Save source and notes separately from run receipts. No package installation or data download is needed for these examples.

Base plot calls are captured as PNG figures. Explicitly print ggplot2 and Plotly objects in scripts: print(chart). The classroom retains at most two figures per run; Plotly figures use the prepared interactive browser renderer. A temporary file created inside a run is not automatically a persistent download. Keep the supplied examples self-contained and use the saved source, notes and supported figure/result views for retained work.

## Course map

Each chapter states its direct prerequisites and includes two independent worked programs, six varied tasks, hints, a complete reference and explained answers. A chapter number is a stable identifier, not a daily schedule.

### Part 1: Values, vectors and structured data

| Lesson | Outcome |
| --- | --- |
| [r-001: Run an R script and inspect its result](guides/r-001.md) | Run a self-contained calculation and distinguish printed output, saved source and a successful check. |
| [r-002: Numbers, types and approximate equality](guides/r-002.md) | Inspect numeric types and choose an equality check that matches the numerical contract. |
| [r-003: Atomic vectors, lengths and recycling](guides/r-003.md) | Write vectorized calculations while rejecting accidental recycling and unintended coercion. |
| [r-004: Logical vectors, comparisons and three-valued reasoning](guides/r-004.md) | Build explicit selection predicates and handle unknown values without turning them into false evidence. |
| [r-005: Index by position, name and an explicit mask](guides/r-005.md) | Select and replace vector elements without confusing positions, exclusions and unknown masks. |
| [r-006: Missing values, NULL, NaN and infinity](guides/r-006.md) | Choose and test a missingness policy that preserves the distinction between absence, undefined arithmetic and zero. |
| [r-007: Names, attributes and ordinary value semantics](guides/r-007.md) | Explain why ordinary vector updates differ from mutations of reference objects and why attributes matter. |
| [r-008: Matrices, dimensions and linear algebra operators](guides/r-008.md) | Construct and subset matrices while distinguishing elementwise arithmetic from a matrix product. |
| [r-009: Lists and nested records without accidental flattening](guides/r-009.md) | Read and update nested records while preserving heterogeneous fields and validating required components. |
| [r-010: Data frames, column types and record identity](guides/r-010.md) | Create a typed table, select records safely and verify its grain and key instead of relying on row positions. |

### Part 2: Functions, files and reliable programs

| Lesson | Outcome |
| --- | --- |
| [r-011: Branching, loops and empty-input behavior](guides/r-011.md) | Implement bounded loops with explicit scalar conditions, empty-input behavior and predictable output shape. |
| [r-012: Functions, arguments and return contracts](guides/r-012.md) | Define reusable functions with validated inputs, explicit defaults and testable return values. |
| [r-013: Lexical scope, closures and lazy arguments](guides/r-013.md) | Explain captured configuration and lazy argument timing without relying on hidden global state. |
| [r-014: Functional iteration, typed results and the base pipe](guides/r-014.md) | Map a validated computation over records and retain predictable output types with readable data flow. |
| [r-015: Errors, warnings and structured recovery](guides/r-015.md) | Recover from expected input failures without concealing programming defects or dropping diagnostics. |
| [r-016: Strings, encodings and explicit text parsing](guides/r-016.md) | Normalize and parse small text records with explicit patterns while preserving identifiers and Unicode meaning. |
| [r-017: Factors, levels and model interpretation](guides/r-017.md) | Represent categories explicitly and avoid interpreting internal factor codes as measurements. |
| [r-018: Dates, instants and explicit time zones](guides/r-018.md) | Parse dates and timestamps with explicit formats and zones, distinguishing calendar labels from elapsed time. |
| [r-019: Local files, CSV, JSON and RDS contracts](guides/r-019.md) | Round-trip small local data through appropriate formats while verifying types, missingness and cleanup. |
| [r-020: Debugging, regression checks and reproducible scripts](guides/r-020.md) | Reduce a defect to a small case and build behavioral checks that cover ordinary, boundary and rejected inputs. |

### Part 3: Object systems and maintainable analytical software

| Lesson | Outcome |
| --- | --- |
| [r-021: S3 value objects, validation and generic dispatch](guides/r-021.md) | Build a validated S3 measurement value, dispatch a domain-specific generic and reject malformed objects at the public boundary. |
| [r-022: S4 slots, validity and multiple dispatch](guides/r-022.md) | Define an S4 measurement with cross-slot invariants and select methods using both argument classes. |
| [r-023: R6 identity, encapsulation and cloning](guides/r-023.md) | Trace shared R6 identity, protect state through methods and distinguish shallow from nested-R6 deep cloning. |
| [r-024: S7 properties, validators and generic methods](guides/r-024.md) | Use the pinned S7 property and method API to construct valid values, reject invalid replacement and dispatch across two typed arguments. |
| [r-025: Object interoperability and public data contracts](guides/r-025.md) | Convert S3, S4, R6 and S7 values through validated adapters and inspect ggplot2 through public build interfaces. |
| [r-026: Namespaces, dependency declarations and package boundaries](guides/r-026.md) | Use exported namespace-qualified functions and inspect a local package source layout without confusing sourced definitions with an installed package. |
| [r-027: Profile equivalent work and account for allocations](guides/r-027.md) | Compare numerically equivalent R implementations, collect bounded timing and profiling evidence, and explain its measurement limits. |
| [r-028: Bounded local parallelism and task-owned random streams](guides/r-028.md) | Execute fixed independent tasks with two local PSOCK workers, preserve deterministic task results and close worker processes on every ordinary exit path. |
| [r-029: Reproducibility, RNG scope and analysis metadata](guides/r-029.md) | Run repeatable stochastic calculations without leaking caller RNG state and record a bounded configuration, input digest and software-version ledger. |
| [r-030: Analytical-package capstone with explicit value and data contracts](guides/r-030.md) | Assemble a tested analytical value object with unique record identity, explicit missingness, compatible aggregation and a documented package continuation. |

### Part 4: Data transformation and reproducible workflows

| Lesson | Outcome |
| --- | --- |
| [r-031: Transform records with explicit selection and ordering](guides/r-031.md) | Build an auditable table transformation whose row population, units and key alignment remain inspectable. |
| [r-032: Grouped summaries and sufficient aggregation state](guides/r-032.md) | Aggregate groups while preserving missingness counts and enough state to reconstruct the intended overall mean. |
| [r-033: Joins, key uniqueness and unmatched records](guides/r-033.md) | Perform a validated many-to-one lookup and detect duplicate or unmatched keys before they change totals. |
| [r-034: Long and wide tables with explicit cell keys](guides/r-034.md) | Reshape repeated measurements only after validating the observation key and deciding how missing cells are represented. |
| [r-035: Validate ingestion and preserve rejected-record evidence](guides/r-035.md) | Validate a small ingestion boundary without silently coercing, dropping or repairing invalid records. |
| [r-036: Chunked aggregation and memory-aware data contracts](guides/r-036.md) | Combine chunk-level sufficient statistics correctly and distinguish a memory strategy from a performance claim. |
| [r-037: Simulation, Monte Carlo error and reproducible randomness](guides/r-037.md) | Use a small simulation to investigate a probability while separating simulation error from model uncertainty. |
| [r-038: Finite probability tables and conditional reasoning](guides/r-038.md) | Compute and reconcile conditional probabilities from a finite original table without confusing the conditioning direction. |
| [r-039: Formulas, design matrices and identifiability](guides/r-039.md) | Inspect the numeric design implied by a formula before interpreting coefficients or fitting a model. |
| [r-040: An auditable analytical pipeline capstone](guides/r-040.md) | Deliver a self-contained analysis that validates inputs, joins metadata, summarizes groups and reports a bounded conclusion. |

### Part 5: Statistical analysis and model validation

| Lesson | Outcome |
| --- | --- |
| [r-041: Explore distributions and preserve missingness](guides/r-041.md) | Produce a descriptive summary whose observation counts, missing-value policy and distributional limits are explicit. |
| [r-042: Estimation, standard errors and resampling targets](guides/r-042.md) | Calculate and interpret distinct uncertainty quantities while keeping the resampling population and assumptions explicit. |
| [r-043: Linear models, design matrices and diagnostic limits](guides/r-043.md) | Connect an R model formula to its numerical design matrix, fitted coefficients and diagnostic assumptions. |
| [r-044: Binomial GLMs, probabilities and calibration](guides/r-044.md) | Translate a logistic model between its link scale, probabilities and evaluation quantities without confusing their interpretations. |
| [r-045: Structured validation and training-only preprocessing](guides/r-045.md) | Construct validation procedures whose partitions and preprocessing match the intended transfer claim. |
| [r-046: PCA, scaling and reconstruction](guides/r-046.md) | Fit and inspect PCA while preserving its preprocessing, orientation and interpretation contracts. |
| [r-047: Decision trees, complexity and held-out decisions](guides/r-047.md) | Fit a small rpart classifier and distinguish its partition, probability output, complexity policy and generalization limits. |
| [r-048: Censoring, risk sets and survival models](guides/r-048.md) | Construct survival outcomes and inspect Kaplan-Meier and Cox calculations without treating censored observations as observed event times. |
| [r-049: Time series, ARIMA and rolling-origin evidence](guides/r-049.md) | Fit and evaluate a small time-series model while preserving temporal information boundaries and forecast targets. |
| [r-050: Scientific synthesis and reproducible model comparison](guides/r-050.md) | Produce a small analytical report that connects the scientific question, model comparison, numerical evidence and limits. |

### Part 6: Base graphics, ggplot2 and interactive Plotly

| Lesson | Outcome |
| --- | --- |
| [r-051: Base graphics, coordinates and owned devices](guides/r-051.md) | Construct a labeled base-R graphic and manage an explicitly owned file device without confusing drawing with browser delivery. |
| [r-052: Multiple panels, uncertainty and scale contracts](guides/r-052.md) | Build a compact uncertainty display whose panels, interval target and axis choices support a valid comparison. |
| [r-053: ggplot2 data mappings and layers](guides/r-053.md) | Construct and inspect a ggplot whose data, mappings and layer-specific responsibilities are explicit. |
| [r-054: ggplot2 statistics, geometries and grouping](guides/r-054.md) | Choose a statistic and grouping contract that matches whether the input contains raw observations or precomputed summaries. |
| [r-055: Scales, coordinates and facets change different contracts](guides/r-055.md) | Choose scale, coordinate and facet policies while explaining how each affects calculations and visual comparisons. |
| [r-056: Statistical graphics for model diagnosis](guides/r-056.md) | Construct diagnostic graphics from fitted quantities and explain which model concerns they can investigate without treating a plot as proof. |
| [r-057: Plotly traces and layout from explicit data](guides/r-057.md) | Construct and inspect a small Plotly figure whose trace data and layout correspond to a declared analytical view. |
| [r-058: Hover, view controls and accessible alternatives](guides/r-058.md) | Encode a bounded interactive view while preserving observation identity and a non-hover-dependent explanation. |
| [r-059: ggplotly translation and validation boundaries](guides/r-059.md) | Translate a supported ggplot to Plotly and verify retained data while identifying the visual and interaction properties that still require review. |
| [r-060: Capstone: an analytical visualization with an evidence record](guides/r-060.md) | Build a linked numerical, static and interactive analysis whose denominators, identities, uncertainty and delivery limits can be reviewed. |

## Prepared packages and external projects

The ordinary worker is CPU-based and offline. Prepared packages include ggplot2, Plotly, R6, S7, jsonlite and R's statistical/recommended libraries. Lessons do not install packages, fetch remote data or require RStudio. The package-development chapters explain a real multi-file package workflow as an optional contributor project; the classroom pad remains a single-script execution surface.

Learn modeling assumptions and scientific interpretation with the [statistics tutorial](../statistics-ml/README.md). Python and JAX provide complementary executable approaches. A successful R program is evidence about the stated computation, not evidence that an observational association is causal or a model will generalize.

## Maintain or extend the subject

Read [AGENTS.md](AGENTS.md) and the [authoring contract](authoring/README.md). The JSON units are the durable teaching sources; references and Markdown are generated from the same code fields to prevent drift.

# DAX: semantic models, context and analytical reasoning

This 60-lesson course teaches DAX through original small models, editable source, worked-result tables and explicit context traces. Start with table grain and basic arithmetic; the later stages examine time intelligence, cohorts, reusable expressions, model security and delivery.

## Open the classroom

From the repository root, run:

```bash
./classroom
```

Choose **DAX** in the classroom directory. Docker serves the reading and saved-work interface; this subject does not need a worker image, NVIDIA hardware, Power BI installation, account or connection. See the [main setup guide](../../README.md) for Docker and WSL 2 installation.

## Editing and evidence

This is an offline DAX editing lesson. No DAX compiler, semantic-model engine, Power BI account or network connection is required. Worked tables describe the named reference and model, not execution of your draft. Save, compare and export source; do not interpret a comparison or completion marker as a passed program run.

Read the guide beside its editable `.dax` starter. Save a draft and notes, compare the supplied reference when useful, and export source for your own records. A worked-reference table stays tied to its named reference and model even after you edit your draft. It is not a Run result. Completion records study progress, not verified mastery.

The [fixture handbook](models/README.md) exposes the tiny original CSVs. The [reference-results sidecar](reference-results.json) identifies every case and binds the exact reference and model bytes with SHA-256. No checked-in file is evidence that a DAX engine, model role or external service was executed.

## Course map

Prerequisites are direct concept dependencies, not a requirement to finish every earlier row. Revisit the named prerequisites when an expression's context is unclear.

### Stage 1: Models, grain and a first query

| Lesson | Outcome |
| --- | --- |
| [dax-001: A semantic model, a question and a worked result](guides/dax-001.md) | Explain what a revenue number means by identifying the model, grain and eligible rows. |
| [dax-002: Grain, keys and why rows are not orders](guides/dax-002.md) | Distinguish sales lines, orders and customers before selecting an aggregation. |
| [dax-003: A star schema and the path of a filter](guides/dax-003.md) | Trace a dimension selection through an active relationship to the exact contributing fact rows. |
| [dax-004: Relationships are filter rules, not materialized joins](guides/dax-004.md) | Predict asymmetric filter propagation and identify when a SQL join analogy breaks. |
| [dax-005: DAX query shape, names and deterministic result tables](guides/dax-005.md) | Distinguish scalar expressions, table expressions and named model measures in a readable query. |
| [dax-006: Model quality capstone: duplicates, missing keys and unknown members](guides/dax-006.md) | Produce a model-quality ledger that separates an invalid dimension key from an unmatched fact key. |

### Stage 2: Values, BLANK and reusable measures

| Lesson | Outcome |
| --- | --- |
| [dax-007: Scalar types, operators and measurement units](guides/dax-007.md) | Keep a numeric measure numeric and explain why its display label is a separate concern. |
| [dax-008: BLANK, zero and the difference between missing and false](guides/dax-008.md) | Explain coercion and choose a deliberate missing-value display policy. |
| [dax-009: Calculated columns, measures and evaluation lifetime](guides/dax-009.md) | Separate a row's stored calculation from a scalar reevaluated for a query context. |
| [dax-010: Additive sums and distinct populations](guides/dax-010.md) | Choose an aggregation whose input grain and total behavior match the metric definition. |
| [dax-011: DIVIDE, weighted averages and zero denominators](guides/dax-011.md) | Derive a ratio at its declared population and distinguish an undefined ratio from zero. |
| [dax-012: VAR and RETURN: values are not context-sensitive macros](guides/dax-012.md) | Predict when a variable freezes a value and when a measure is reevaluated in modified context. |

### Stage 3: Row context, filter context and CALCULATE

| Lesson | Outcome |
| --- | --- |
| [dax-013: Row context is not a filter on related facts](guides/dax-013.md) | Explain why iterating Product does not by itself filter a raw Sales aggregation. |
| [dax-014: Filter context is the full question, not just one slicer](guides/dax-014.md) | Record a complete context ledger and explain two cells with the same measure definition. |
| [dax-015: CALCULATE replaces a filter on the same column](guides/dax-015.md) | Predict replacement on one column while retaining unrelated filters. |
| [dax-016: Filter arguments are not an imperative sequence](guides/dax-016.md) | Explain why sibling filter arguments differ from deliberately nested evaluation. |
| [dax-017: Explicit and implicit context transition](guides/dax-017.md) | Trace a raw aggregation and a measure reference inside an iterator without treating context transition as a row pointer. |
| [dax-018: Measure predicates need an explicit candidate table](guides/dax-018.md) | Build a measure-dependent selection by evaluating the measure for each candidate member. |

### Stage 4: Filters, iterators and nonadditive totals

| Lesson | Outcome |
| --- | --- |
| [dax-019: KEEPFILTERS expresses an intersection policy](guides/dax-019.md) | Choose between forcing a value and respecting an existing selection on the same column. |
| [dax-020: REMOVEFILTERS and the exact denominator population](guides/dax-020.md) | State which filters a share denominator removes and which it retains. |
| [dax-021: SUMX and AVERAGEX choose both an expression and a population](guides/dax-021.md) | Derive an iterator result and explain how blank rows affect its denominator. |
| [dax-022: Variables inside and outside an iterator](guides/dax-022.md) | Locate a variable's binding context and avoid repeating one total for every member. |
| [dax-023: Grand totals reevaluate the measure](guides/dax-023.md) | Reconcile row values and a grand-total ratio without forcing the total to sum visible cells. |
| [dax-024: Selected totals and the limits of ALLSELECTED intuition](guides/dax-024.md) | Differentiate share of an explicitly selected population from share of all model products. |

### Stage 5: Virtual tables, lineage and relationships

| Lesson | Outcome |
| --- | --- |
| [dax-025: VALUES, DISTINCT and the model's unknown member](guides/dax-025.md) | Reconcile unmatched facts without confusing the stored dimension with its semantic blank member. |
| [dax-026: Virtual tables have row-retention and column contracts](guides/dax-026.md) | Predict which rows survive a projection, an extension and a grouped summary. |
| [dax-027: Lineage and TREATAS: equal values can filter differently](guides/dax-027.md) | Explain why a virtual column's model identity matters in addition to its visible values. |
| [dax-028: Set operations, duplicates and argument order](guides/dax-028.md) | Distinguish membership operations from bag concatenation and preserve a deliberate key population. |
| [dax-029: Active and inactive date roles with USERELATIONSHIP](guides/dax-029.md) | Reconcile order-date and ship-date totals without changing the fact amounts. |
| [dax-030: Bridge tables and overlapping audiences](guides/dax-030.md) | Model overlapping customer groups and reconcile unique reach without enabling ambiguous filter paths. |

### Stage 6: Dates, periods and temporal meaning

| Lesson | Outcome |
| --- | --- |
| [dax-031: A complete date dimension is not a list of sale dates](guides/dax-031.md) | Distinguish calendar coverage, observed facts and data-availability boundaries. |
| [dax-032: Year-to-date means a specific included-date set](guides/dax-032.md) | Derive a YTD measure by enumerating its date boundary and eligible fact rows. |
| [dax-033: Prior periods and comparable completeness](guides/dax-033.md) | Separate a full-period comparison from an as-of comparison and explain the sign change. |
| [dax-034: Rolling windows: calendar days versus event days](guides/dax-034.md) | Explain why a mean over observed sale days differs from revenue per eligible calendar day. |
| [dax-035: Fiscal labels, boundaries and as-of totals](guides/dax-035.md) | Define a fiscal year explicitly and distinguish fiscal-to-date from a completed fiscal year. |
| [dax-036: Calendar-based time intelligence is a metadata-dependent continuation](guides/dax-036.md) | Explain why a calendar reference can represent a different year definition than a classic date column. |

### Stage 7: Analytical patterns and decision units

| Lesson | Outcome |
| --- | --- |
| [dax-037: Ranking, ties and an exact-sized Top N](guides/dax-037.md) | Specify tie behavior separately from deterministic ordering and selection size. |
| [dax-038: Window positions, ordering and row identity](guides/dax-038.md) | Distinguish a positional row window from a calendar interval and identify the ordering contract. |
| [dax-039: Inventory balances are semi-additive](guides/dax-039.md) | Choose a time aggregation that matches a balance rather than summing repeated states. |
| [dax-040: Cohorts, retention denominators and unobserved ages](guides/dax-040.md) | Separate enrolled members, active members and unavailable follow-up periods. |
| [dax-041: Budget comparisons require compatible grains](guides/dax-041.md) | Align actuals with a monthly category budget without copying a whole-month target into a daily metric. |
| [dax-042: Currency conversion belongs at the rate's grain](guides/dax-042.md) | Convert compatible transactions before aggregation and diagnose a misleading latest-rate shortcut. |

### Stage 8: Reusable logic and calculation scope

| Lesson | Outcome |
| --- | --- |
| [dax-043: Measure composition, dependency graphs and numeric formatting](guides/dax-043.md) | Build a small reusable measure family with explicit units and dependency boundaries. |
| [dax-044: Calculation items transform selected measures](guides/dax-044.md) | Describe a reusable transformation while preventing it from changing incompatible measures. |
| [dax-045: Precedence and dynamic format strings](guides/dax-045.md) | Expand interacting calculation items and distinguish numeric transformation from display selection. |
| [dax-046: DAX UDFs: explicit parameters and a reusable scalar rule](guides/dax-046.md) | Define a small reusable function with a clear parameter domain and default behavior. |
| [dax-047: UDF value versus expression parameters](guides/dax-047.md) | Predict whether a UDF receives a precomputed value or an expression evaluated under its own modifier. |
| [dax-048: Visual calculations operate on a visual's aggregated shape](guides/dax-048.md) | Distinguish a visual running total from a reusable semantic-model measure. |

### Stage 9: Performance interpretation and equivalent rewrites

| Lesson | Outcome |
| --- | --- |
| [dax-049: Formula work, columnar scans and cardinality](guides/dax-049.md) | Separate an expression's semantics, model cardinality and observed engine performance. |
| [dax-050: Intermediate tables can grow before aggregation](guides/dax-050.md) | Estimate candidate-table size without confusing a logical table with measured physical work. |
| [dax-051: A faster-looking rewrite must preserve filter semantics](guides/dax-051.md) | Find a context where two similar predicates differ before treating one as an optimization. |
| [dax-052: Expanded tables and existing combinations](guides/dax-052.md) | Explain why broad filter removal and same-table combinations need model-aware reasoning. |
| [dax-053: Read timing evidence without inventing a benchmark](guides/dax-053.md) | Interpret a supplied timing scenario while separating it from an actual DAX execution receipt. |
| [dax-054: Optimization capstone: prove the grouping assumption first](guides/dax-054.md) | Review a grouped cost rewrite under explicit assumptions before proposing a performance measurement. |

### Stage 10: Security, delivery and integrated capstones

| Lesson | Outcome |
| --- | --- |
| [dax-055: Storage modes, freshness and capability boundaries](guides/dax-055.md) | Separate a metric's definition from data freshness, storage mode and external capability. |
| [dax-056: A report filter is not row-level security](guides/dax-056.md) | Distinguish a removable analytical filter from an engine-enforced role restriction. |
| [dax-057: Dynamic RLS needs a complete identity and mapping contract](guides/dax-057.md) | Reason about a dynamic region policy, including unmapped identities and policy-table exposure. |
| [dax-058: Commercial-model capstone: reconcile adjustments and targets](guides/dax-058.md) | Produce a reviewable commercial metric specification with explicit populations and adjustment policies. |
| [dax-059: Experiment and cohort capstone: preserve the assigned unit](guides/dax-059.md) | Build an experiment-quality semantic report without treating repeated events or displayed estimates as causal proof. |
| [dax-060: Delivery capstone: a model specification and an evidence ledger](guides/dax-060.md) | Assemble a reviewable model change with expected role/context results and explicit unperformed deployment checks. |

## Platform and feature boundaries

Ordinary DAX syntax, model definitions, calculation-item definitions, user-defined functions and visual calculations are different artifacts. Guides state their scope instead of treating every expression as an interchangeable query. Version-sensitive features have dated notes and primary references. Calendar-based time intelligence and value-filter behavior are marked according to their reviewed documentation; the UDF lessons state their compatibility requirement.

Security cases are expectations under specified synthetic role policies. Timing cases explicitly use supplied scenario numbers. Neither is a real security or performance test. Optional external model validation requires a compatible engine, a deliberately prepared model and its own observed evidence; it is not required to complete this offline route.

For SQL table/query foundations, use the classroom's SQL subject. For data analysis, probability and model evaluation, use Python, R and the statistics tutorial. Their executable outputs do not turn an unrelated DAX draft into an executed program.

## Maintaining this course

Read [AGENTS.md](AGENTS.md) and the [authoring contract](authoring/README.md). The course generator owns its manifests, guides, references, starters and fixture handbook. Shared HTML readers are generated separately by the repository tools.

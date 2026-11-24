"Stage nine: interpret work and measurements without inventing engine receipts."

from .common import explain, lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        49,
        "Formula work, columnar scans and cardinality",
        ["formula engine", "storage engine", "columnar storage", "cardinality", "measurement"],
        ("Separate an expression's semantics, model cardinality and observed engine performance."),
        (
            "DAX performance involves both expression evaluation and "
            "the storage operations serving it. Formula-engine work "
            "coordinates expressions and intermediate results; "
            "storage-engine work can scan and aggregate encoded "
            "columns. This is a useful conceptual split, not a promise "
            "that a source function maps to exactly one physical "
            "operation in every engine version or storage "
            "mode.\n\nColumn cardinality is one input to model size and "
            "work. ProductKey has three distinct values across eight "
            "Sales rows, while SaleID has eight distinct values. "
            "Repeated low-cardinality attributes and unique "
            "identifiers have different encoding opportunities. The "
            "actual memory cost also depends on type, ordering, "
            "compression, dictionaries and engine implementation, so "
            "row and distinct counts do not themselves measure "
            "bytes.\n\nA star schema stores descriptive product "
            "attributes separately from fact events. That can support "
            "clear filtering and reduce repeated descriptive data, but "
            "semantic correctness comes first. Do not remove a "
            "necessary unique fact key or meaningful precision merely "
            "to reduce cardinality. An optimization claim needs a "
            "defined workload, equivalent results and actual "
            "measurements on the intended model."
        ),
        (
            "The two queries expose simple cardinality facts that can "
            "be derived from the supplied CSVs. They do not return "
            "server timings or an engine plan. The lesson's conceptual "
            "pipeline is query/context interpretation, "
            "candidate/storage operations, intermediate results and "
            "final aggregation; physical optimization may combine or "
            "reorder work."
        ),
        [
            r(
                "Fact-column cardinalities",
                (
                    'EVALUATE ROW ( "SalesRows", COUNTROWS ( Sales ), '
                    '"ProductKeys", DISTINCTCOUNT ( Sales[ProductKey] ), '
                    '"OrderDates", DISTINCTCOUNT ( Sales[OrderDate] ), '
                    '"SaleIDs", DISTINCTCOUNT ( Sales[SaleID] ) )'
                ),
                [
                    ("SalesRows", "integer"),
                    ("ProductKeys", "integer"),
                    ("OrderDates", "integer"),
                    ("SaleIDs", "integer"),
                ],
                [[8, 3, 7, 8]],
                (
                    "Clean retail fact; no filters; counts describe source "
                    "cardinality, not physical scan metrics."
                ),
                [
                    "There are eight unique sale lines.",
                    "Three product keys repeat across them, and S1/S2 share one order date.",
                    "Distinct counts are 3 products,7 order dates and 8 SaleIDs.",
                ],
                (
                    "A unique identifier has high cardinality here because it "
                    "preserves necessary line identity. Its cost must be "
                    "weighed against correctness and lineage requirements."
                ),
            ),
            r(
                "Dimension attributes have another grain",
                (
                    'EVALUATE ROW ( "ProductRows", COUNTROWS ( Product ), '
                    '"Categories", DISTINCTCOUNT ( Product[Category] ), '
                    '"Colors", DISTINCTCOUNT ( Product[Color] ) )'
                ),
                [("ProductRows", "integer"), ("Categories", "integer"), ("Colors", "integer")],
                [[4, 3, 3]],
                "Product dimension, including the unsold Bag member.",
                [
                    "Four product rows describe four catalog keys.",
                    "Categories are Paper, Home, Travel and colors are Blue, Red, Green.",
                    "The dimension's domain includes valid attributes absent from current sales.",
                ],
                (
                    "A dimension count is not inferred from fact activity. "
                    "Removing unsold members to shrink a model can change the "
                    "intended reporting population."
                ),
            ),
        ],
        [
            t(
                "Predict SaleID cardinality after adding one valid new line.",
                "Its key must be unique at the declared grain.",
                (
                    "Row count and distinct SaleID count both increase by one; "
                    "other column cardinalities depend on the new values."
                ),
            ),
            t(
                "Replace a long descriptive fact label with a dimension key conceptually.",
                "Keep the mapping and relationship semantics intact.",
                (
                    "The logical model can avoid repeated descriptive values, "
                    "but actual storage savings require measurement rather "
                    "than a fixed claimed ratio."
                ),
            ),
            t(
                "Write a performance-claim checklist.",
                "Separate correctness, workload and measurement.",
                (
                    "Record model/source identity, storage mode, "
                    "representative filters, result parity, engine/version, "
                    "hardware, cache state and repeated observed timings."
                ),
            ),
            t(
                "Diagnose saying SUMX is always slow and SUM is always fast.",
                "Source syntax is not a complete physical plan.",
                (
                    "Use the simplest correct expression, inspect actual "
                    "engine work and measure the intended workload; do not "
                    "infer universal speed from a function name."
                ),
            ),
            t(
                "Explain why deleting SaleID can be a correctness regression.",
                (
                    "The key supports row identity, duplicate detection and "
                    "context-transition reasoning."
                ),
                (
                    "A storage change must preserve the business grain and "
                    "required diagnostics, not merely reduce a distinct-count "
                    "statistic."
                ),
            ),
            t(
                "Transfer cardinality reasoning to timestamps.",
                "Precision can create many distinct values but may be analytically required.",
                (
                    "Choose the temporal grain from the measurement "
                    "requirement, then consider model design and encoding "
                    "rather than arbitrarily truncating events."
                ),
            ),
        ],
        sources=[
            ("https://learn.microsoft.com/en-us/power-bi/guidance/import-modeling-data-reduction"),
            "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema",
        ],
    ),
    lesson(
        50,
        "Intermediate tables can grow before aggregation",
        [
            "materialization",
            "CROSSJOIN",
            "observed combinations",
            "intermediate grain",
            "cardinality",
        ],
        (
            "Estimate candidate-table size without confusing a logical "
            "table with measured physical work."
        ),
        (
            "A final one-row answer can be produced from a much larger "
            "intermediate population. CROSSJOIN forms combinations of "
            "its input tables, while grouping observed facts can "
            "produce only combinations that actually occur. Before "
            "writing an iterator over a virtual table, state its grain "
            "and estimate its candidate size.\n\nOur four products and "
            "four customers form sixteen possible pairs, but only six "
            "distinct product/customer pairs appear in Sales. Adding "
            "every one of 731 calendar dates produces 11696 possible "
            "product/customer/date combinations, while the eight fact "
            "lines contain eight distinct observed combinations at "
            "that three-column grain. The gap is a logical cardinality "
            "observation, not a claim that an engine necessarily "
            "materializes every candidate.\n\nSome queries legitimately "
            "require a complete scaffold, including zero-activity "
            "cells. Others need only observed combinations. Choosing "
            "the smaller table without considering missing and "
            "eligible populations can change the answer. Performance "
            "review must therefore preserve the intended population "
            "before comparing any physical-plan or timing evidence."
        ),
        (
            "CROSSJOIN returns combinations of the supplied distinct "
            "dimension values. SUMMARIZE over Sales returns observed "
            "fact groups at the specified grain. The output counts are "
            "hand-reconciled from the fixture; they are not counters "
            "captured from a real query plan."
        ),
        [
            r(
                "Possible customer/product pairs",
                (
                    'EVALUATE ROW ( "CandidatePairs", COUNTROWS ( CROSSJOIN ( '
                    "VALUES ( Product[ProductKey] ), VALUES ( "
                    'Customer[CustomerKey] ) ) ), "ObservedPairs", COUNTROWS ( '
                    "SUMMARIZE ( Sales, Sales[ProductKey], Sales[CustomerKey] "
                    ") ) )"
                ),
                [("CandidatePairs", "integer"), ("ObservedPairs", "integer")],
                [[16, 6]],
                (
                    "No filters; dimension population 4 products by 4 "
                    "customers; observed pair grain from Sales."
                ),
                [
                    "The full dimension product is 4 times 4 = 16 pairs.",
                    "Observed pairs are (1, 10), (2, 10), (3, 20), (2, 30), (1, 20), (3, 30).",
                    (
                        "Repeated purchases of the same pair do not add a new "
                        "pair, leaving six observed groups."
                    ),
                ],
                (
                    "The ten unobserved pairs may matter for a coverage report "
                    "even though they contribute no current revenue. Their "
                    "inclusion is a question of semantics."
                ),
            ),
            r(
                "Adding a complete calendar dimension",
                (
                    'EVALUATE ROW ( "CandidateCells", COUNTROWS ( CROSSJOIN ( '
                    "VALUES ( Product[ProductKey] ), VALUES ( "
                    "Customer[CustomerKey] ), VALUES ( 'Date'[Date] ) ) ), "
                    '"ObservedCells", COUNTROWS ( SUMMARIZE ( Sales, '
                    "Sales[ProductKey], Sales[CustomerKey], Sales[OrderDate] ) "
                    ") )"
                ),
                [("CandidateCells", "integer"), ("ObservedCells", "integer")],
                [[11696, 8]],
                (
                    "Whole two-year Date dimension has 731 days; compare "
                    "possible versus observed product/customer/date cells."
                ),
                [
                    "The possible-cell count is 4 * 4 * 731 = 11696.",
                    (
                        "Each of the eight sales lines has a distinct "
                        "product/customer/order-date combination in this fixture."
                    ),
                    "The observed grouping therefore has eight cells.",
                ],
                (
                    "These are logical table sizes. Engine optimizations may "
                    "avoid constructing the full product, and a source-only "
                    "exercise cannot establish the physical materialization or "
                    "elapsed time."
                ),
            ),
        ],
        [
            t(
                "Predict candidate pairs after adding one unsold product.",
                "The customer dimension still has four members.",
                "The full candidate grid becomes 5 * 4 = 20; observed pairs can remain six.",
            ),
            t(
                "Restrict the calendar to January 2025.",
                "The selected Date dimension has 31 days.",
                (
                    "The candidate grid becomes 4 * 4 * 31 = 496; the observed "
                    "fact combinations in that month must be counted "
                    "separately."
                ),
            ),
            t(
                "Choose a population for a complete customer/product coverage matrix.",
                "Unobserved combinations can be part of the requested output.",
                (
                    "Use a deliberate full scaffold with explicit missing/zero "
                    "semantics if coverage requires it; an observed-only "
                    "grouping would omit requested cells."
                ),
            ),
            t(
                ("Diagnose claiming a 11696-row physical scan from this result alone."),
                "Logical expression cardinality is not a captured execution plan.",
                (
                    "A real engine can prune or combine work. Obtain qualified "
                    "plan/timing evidence before making a physical-performance "
                    "claim."
                ),
            ),
            t(
                (
                    "Explain whether observed combinations always preserve "
                    "zero-activity denominators."
                ),
                "A missing fact group may still represent an eligible unit.",
                (
                    "No. Denominators for eligibility or coverage may require "
                    "dimension members that never produced facts."
                ),
            ),
            t(
                "Transfer the analysis to a product-by-store-by-day model.",
                "Multiply declared dimension sizes before choosing an iterator scaffold.",
                (
                    "Estimate potential combinations, identify which are "
                    "meaningful and preserve the required zero/missing "
                    "populations while measuring actual implementation cost "
                    "separately."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/crossjoin-function-dax",
            "https://learn.microsoft.com/en-us/dax/summarize-function-dax",
        ],
    ),
    lesson(
        51,
        "A faster-looking rewrite must preserve filter semantics",
        [
            "semantic equivalence",
            "FILTER",
            "Boolean predicate",
            "KEEPFILTERS",
            "regression context",
        ],
        (
            "Find a context where two similar predicates differ before "
            "treating one as an optimization."
        ),
        (
            "Replacing a table filter with a simple column predicate "
            "can change filter replacement behavior. "
            "FILTER(Sales,Sales[Quantity]>=2) iterates Sales as "
            "visible in its incoming context. A plain Boolean filter "
            "on Quantity in CALCULATE can replace an existing Quantity "
            "filter. They can agree on an unfiltered fixture while "
            "disagreeing on a selected population.\n\nWith no incoming "
            "filters, both constructions select lines with quantity at "
            "least two, totaling 163. Under an incoming Quantity=1 "
            "selection, the visible Sales rows contain no line "
            "satisfying the table predicate, so the table-filter form "
            "returns BLANK. The plain column predicate replaces that "
            "Quantity selection and admits the larger-quantity lines, "
            "returning 163 instead.\n\nKEEPFILTERS on the column "
            "predicate expresses intersection and matches the empty "
            "result in this stated context. That is useful evidence "
            "for this case, not a universal equivalence theorem for "
            "every table expression, relationship or expanded-table "
            "effect. A performance refactor needs a semantic test grid "
            "before any timing result can justify it."
        ),
        (
            "The three expressions differ in how they form and apply "
            "their filter. Case A is an ordinary agreement case. Case "
            "B supplies the counterexample with an existing "
            "same-column selection. No runtime performance is measured "
            "by either query."
        ),
        [
            r(
                "An unfiltered agreement case",
                (
                    'EVALUATE ROW ( "TableFilter", CALCULATE ( [NetRevenue], '
                    'FILTER ( Sales, Sales[Quantity] >= 2 ) ), "ColumnFilter", '
                    "CALCULATE ( [NetRevenue], Sales[Quantity] >= 2 ), "
                    '"IntersectingColumn", CALCULATE ( [NetRevenue], '
                    "KEEPFILTERS ( Sales[Quantity] >= 2 ) ) )"
                ),
                [
                    ("TableFilter", "number"),
                    ("ColumnFilter", "number"),
                    ("IntersectingColumn", "number"),
                ],
                [[163, 163, 163]],
                "No existing Quantity filter; all three forms select quantity at least two.",
                [
                    "S2 and S6 have quantity 1 and contribute 4 + 20 = 24.",
                    "Removing those lines from 187 leaves 163.",
                    "The three forms agree in this incoming context.",
                ],
                (
                    "Agreement on an unfiltered example does not establish "
                    "interchangeability under interactive selections."
                ),
            ),
            r(
                "The same-column selection exposes a difference",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "TableFilter", CALCULATE '
                    "( [NetRevenue], FILTER ( Sales, Sales[Quantity] >= 2 ) ), "
                    '"ColumnFilter", CALCULATE ( [NetRevenue], Sales[Quantity] '
                    '>= 2 ), "IntersectingColumn", CALCULATE ( [NetRevenue], '
                    "KEEPFILTERS ( Sales[Quantity] >= 2 ) ) ), Sales[Quantity] "
                    "= 1 )"
                ),
                [
                    ("TableFilter", "number"),
                    ("ColumnFilter", "number"),
                    ("IntersectingColumn", "number"),
                ],
                [[None, 163, None]],
                (
                    "Incoming Sales.Quantity=1; compare filtering current rows "
                    "with replacing or intersecting that column selection."
                ),
                [
                    "The incoming visible fact rows are S2 and S6, both quantity 1.",
                    (
                        "FILTER over those rows finds no quantity>=2 line, while "
                        "the plain Boolean predicate replaces the original "
                        "selection."
                    ),
                    (
                        "KEEPFILTERS intersects incompatible quantity conditions "
                        "and also yields BLANK."
                    ),
                ],
                (
                    "A rewrite that changes BLANK to 163 is not an "
                    "optimization of the same calculation. It is a change in "
                    "the question."
                ),
            ),
        ],
        [
            t(
                "Predict the three results under an incoming Quantity>=2 selection.",
                "The original population already satisfies the predicate.",
                (
                    "All three return 163 in this fixture, another agreement "
                    "case that does not replace the counterexample."
                ),
            ),
            t(
                "Change the predicate to Quantity>=3.",
                "Identify S4 and S5.",
                "Without other filters the retained revenue is 27 + 20 = 47.",
            ),
            t(
                "Write a minimum semantic regression grid.",
                "Include selections that agree, overlap and conflict with the predicate.",
                (
                    "Check unfiltered, same-column disjoint/overlapping "
                    "filters, unrelated dimensions, blanks, totals and missing "
                    "members before comparing timings."
                ),
            ),
            t(
                "Diagnose choosing a rewrite because it returns a larger nonblank number.",
                "A changed result is not evidence of better performance or correctness.",
                (
                    "Validate the metric definition and incoming context "
                    "first; retain the counterexample as a regression."
                ),
            ),
            t(
                ("Explain why KEEP FILTERS is not an automatic proof for arbitrary table filters."),
                "Whole-table filters can carry additional columns and expanded-table effects.",
                (
                    "Prove the intended equivalence for the actual "
                    "expression/model; do not generalize this one-column "
                    "example beyond its assumptions."
                ),
            ),
            t(
                "Transfer the review to a SQL query optimization.",
                "Result parity needs population, multiplicity, null and boundary checks.",
                (
                    "A faster query that drops duplicate events or changes "
                    "missing-value policy is not a semantics-preserving "
                    "optimization."
                ),
            ),
        ],
        sources=[
            (
                "https://learn.microsoft.com/en-us/dax/best-practices/dax-a"
                "void-avoid-filter-as-filter-argument"
            ),
            "https://learn.microsoft.com/en-us/dax/keepfilters-function-dax",
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
        ],
    ),
    lesson(
        52,
        "Expanded tables and existing combinations",
        ["expanded table", "ALL", "auto-exist", "value-filter behavior", "model scope"],
        (
            "Explain why broad filter removal and same-table "
            "combinations need model-aware reasoning."
        ),
        (
            "A regular fact table participates in an expanded-table "
            "model that includes related one-side attributes. Removing "
            "filters with a broad fact-table modifier can therefore "
            "clear filters from related dimensions, not merely a "
            "visible fact column. In this clean regular star, "
            "ALL(Sales) can remove the Customer and Date restrictions "
            "that shaped the measure.\n\nAnother subtlety is existing "
            "combinations of values on one table. Paper and Home are "
            "valid categories, and Red is a valid color, but Home/Red "
            "is not a stored Product combination. Query optimization "
            "and value-filter behavior can combine same-table "
            "selections through existing combinations. The label "
            "auto-exist describes this family of behavior; it is not a "
            "universal instruction that every query or model version "
            "uses the same coalescing policy.\n\nThe second worked case "
            "enumerates requested versus existing combinations without "
            "claiming to reproduce a particular engine's hidden "
            "filtering plan. When a denominator involving ALL behaves "
            "unexpectedly, record the exact query shape, model "
            "value-filter setting and retained combinations, then "
            "qualify it on the intended engine. Do not replace that "
            "analysis with the slogan that ALL always ignores every "
            "filter."
        ),
        (
            "Case A compares an expanded fact-table modifier with a "
            "narrow amount-column removal. Case B counts an explicitly "
            "requested Cartesian pair set and the existing Product "
            "pairs satisfying those requests. The latter is a logical "
            "domain inspection, not a captured auto-exist execution "
            "trace."
        ),
        [
            r(
                "Fact-table removal reaches related dimensions",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Original", [NetRevenue], '
                    '"ClearExpandedSales", CALCULATE ( [NetRevenue], ALL ( '
                    'Sales ) ), "ClearAmountOnly", CALCULATE ( [NetRevenue], '
                    "REMOVEFILTERS ( Sales[NetAmount] ) ) ), Customer[Region] "
                    "= \"North\", 'Date'[Year] = 2025 )"
                ),
                [
                    ("Original", "number"),
                    ("ClearExpandedSales", "number"),
                    ("ClearAmountOnly", "number"),
                ],
                [[83, 187, 83]],
                (
                    "Regular Import-style star; starting filters are North and "
                    "order year 2025; no bidirectional or limited "
                    "relationships."
                ),
                [
                    "The starting context totals 83.",
                    (
                        "ALL(Sales) as a modifier clears filters over its expanded "
                        "table, restoring the whole-model 187."
                    ),
                    (
                        "Removing only Sales.NetAmount does not remove "
                        "Customer.Region or Date.Year, so the result stays 83."
                    ),
                ],
                (
                    "The scope of a table modifier matters. A relationship or "
                    "storage-mode redesign can change assumptions and requires "
                    "fresh semantic checks."
                ),
            ),
            r(
                "Requested values are not all existing pairs",
                (
                    "EVALUATE\nVAR RequestedCategories = DATATABLE ( "
                    '"WantedCategory", STRING, { { "Paper" }, { "Home" } } '
                    ')\nVAR RequestedColors = DATATABLE ( "WantedColor", '
                    'STRING, { { "Red" } } )\nRETURN ROW ( "RequestedPairs", '
                    "COUNTROWS ( CROSSJOIN ( RequestedCategories, "
                    'RequestedColors ) ), "ExistingPairs", COUNTROWS ( '
                    "SUMMARIZE ( FILTER ( Product, Product[Category] IN { "
                    '"Paper", "Home" } && Product[Color] = "Red" ), '
                    "Product[Category], Product[Color] ) ) )"
                ),
                [("RequestedPairs", "integer"), ("ExistingPairs", "integer")],
                [[2, 1]],
                (
                    "Explicit domain comparison: requested Paper/Red and "
                    "Home/Red versus stored Product combinations."
                ),
                [
                    (
                        "Two requested categories times one requested color gives "
                        "two candidate pairs."
                    ),
                    "Only Paper/Red exists in Product, represented by Pen.",
                    "Home/Red is not a stored combination; the existing pair count is one.",
                ],
                (
                    "This explains information that can matter when filters "
                    "are coalesced. It does not by itself determine every ALL "
                    "or ALLSELECTED result under every value-filter "
                    "configuration."
                ),
            ),
        ],
        [
            t(
                "Predict ALL(Product) under the North/year 2025 starting context.",
                "Only Product filters are removed there.",
                (
                    "With no initial Product restriction, the measure remains "
                    "83; unrelated Customer and Date filters remain."
                ),
            ),
            t(
                "Change requested color from Red to Blue.",
                "BothPaper/Blue and Home/Blue exist.",
                "Requested and existing pair counts both become two.",
            ),
            t(
                "Write a denominator-debugging ledger.",
                "Include model setting and table scope, not only the function name.",
                (
                    "Record incoming filters, regular/limited relationships, "
                    "expanded-table scope, requested versus surviving "
                    "combinations and the exact query's value-filter behavior."
                ),
            ),
            t(
                "Diagnose using ALL(Sales) to remove only a product-color selection.",
                "The modifier is broader than the stated requirement.",
                (
                    "It can remove related dimension filters that should "
                    "remain. Prefer a deliberately scoped modifier when that "
                    "is the intended question."
                ),
            ),
            t(
                (
                    "Explain why an Independent versus Coalesced value-filter "
                    "setting needs explicit qualification."
                ),
                "A source formula alone does not identify every model behavior.",
                (
                    "Record the setting and engine/version, then test "
                    "same-table filter combinations and totals; do not invent "
                    "an execution result from the setting's name."
                ),
            ),
            t(
                "Transfer the domain check to size/color inventory selections.",
                "Individually valid labels can form a nonexistent pair.",
                (
                    "Keep requested values, existing combinations and "
                    "unavailable inventory distinct, especially when "
                    "calculating shares or removing only one filter."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/all-function-dax",
            "https://learn.microsoft.com/en-us/dax/summarizecolumns-function-dax",
            ("https://learn.microsoft.com/en-us/power-bi/transform-model/value-filter-behavior"),
        ],
    ),
    lesson(
        53,
        "Read timing evidence without inventing a benchmark",
        ["cache state", "repeated trials", "median", "variance", "synthetic evidence"],
        (
            "Interpret a supplied timing scenario while separating it "
            "from an actual DAX execution receipt."
        ),
        (
            "Performance evidence needs provenance: exact source, "
            "model, engine/version, hardware, workload filters, cache "
            "state and repeated measurements. Cold and warm queries "
            "can measure different work. Comparing one cold result "
            "with another warm result is not a fair formula "
            "comparison. A screenshot of a small duration without its "
            "context cannot establish a general speedup.\n\nThe numbers "
            "in this lesson are explicitly fabricated teaching "
            "observations embedded in DATATABLE. No DAX engine "
            "produced them. They let you practice summarizing supplied "
            "records and spotting misleading claims without requiring "
            "an external tool or fabricating a runtime receipt. Their "
            "means and medians are hand-derived arithmetic, just like "
            "the other reference tables.\n\nA candidate can have a lower "
            "best observed time yet a worse average because of a slow "
            "trial. That does not automatically condemn it either: "
            "investigate noise, workload differences, contention and "
            "repeatability. Keep semantic parity and representative "
            "workload coverage ahead of choosing the most attractive "
            "timing statistic."
        ),
        (
            "AVERAGEX, MINX and MEDIANX summarize literal trial "
            "tables. These functions are used to analyze provided "
            "values, not to time the current query. A real Performance "
            "Analyzer or server-timing trace would need its own "
            "recorded provenance and distinction between visual "
            "rendering, query time and other work."
        ),
        [
            r(
                "Cold and warm are different conditions",
                (
                    'EVALUATE\nVAR Cold = DATATABLE ( "DurationMs", INTEGER, { '
                    "{ 100 }, { 120 }, { 110 } } )\nVAR Warm = DATATABLE ( "
                    '"DurationMs", INTEGER, { { 20 }, { 25 }, { 21 } } '
                    ')\nRETURN ROW ( "SyntheticColdMeanMs", AVERAGEX ( Cold, '
                    '[DurationMs] ), "SyntheticWarmMeanMs", AVERAGEX ( Warm, '
                    "[DurationMs] ) )"
                ),
                [("SyntheticColdMeanMs", "number"), ("SyntheticWarmMeanMs", "number")],
                [[110, 22]],
                (
                    "Original synthetic trial scenario, not measured engine "
                    "output; three supplied values per cache-state label."
                ),
                [
                    "The synthetic cold values sum to 330 and average 110.",
                    "The synthetic warm values sum to 66 and average 22.",
                    (
                        "The different conditions must not be presented as proof "
                        "that one formula is five times faster."
                    ),
                ],
                (
                    "Cache-state labels are part of a benchmark's design. "
                    "These invented values teach the comparison issue but "
                    "establish no performance property of this course or a DAX "
                    "engine."
                ),
                note=(
                    "Arithmetic over explicitly synthetic timing data. No "
                    "timing measurement or engine execution occurred."
                ),
            ),
            r(
                "Best trial and average can disagree",
                (
                    'EVALUATE\nVAR A = DATATABLE ( "DurationMs", INTEGER, { { '
                    "20 }, { 21 }, { 19 } } )\nVAR B = DATATABLE ( "
                    '"DurationMs", INTEGER, { { 18 }, { 60 }, { 18 } } '
                    ')\nRETURN ROW ( "MeanA", AVERAGEX ( A, [DurationMs] ), '
                    '"MedianA", MEDIANX ( A, [DurationMs] ), "BestA", MINX ( '
                    'A, [DurationMs] ), "MeanB", AVERAGEX ( B, [DurationMs] ), '
                    '"MedianB", MEDIANX ( B, [DurationMs] ), "BestB", MINX ( '
                    "B, [DurationMs] ) )"
                ),
                [
                    ("MeanA", "number"),
                    ("MedianA", "number"),
                    ("BestA", "number"),
                    ("MeanB", "number"),
                    ("MedianB", "number"),
                    ("BestB", "number"),
                ],
                [[20, 20, 19, 32, 18, 18]],
                (
                    "Two synthetic three-trial candidates under a hypothetical "
                    "comparable condition; no real benchmark claim."
                ),
                [
                    "CandidateA has mean 20, median 20 and best 19.",
                    (
                        "CandidateB has mean 32, median 18 and best 18 because one "
                        "supplied trial is 60."
                    ),
                    (
                        "Selecting only the best trial hides the variability shown "
                        "by the complete record."
                    ),
                ],
                (
                    "Three invented trials cannot estimate production tail "
                    "latency. The point is to inspect the full evidence and "
                    "design an adequate real measurement procedure."
                ),
                note=(
                    "Synthetic scenario summary only; these values are not "
                    "DS60 runtime performance receipts."
                ),
            ),
        ],
        defines="",
        sources=[
            (
                "https://learn.microsoft.com/en-us/power-bi/create-reports/"
                "desktop-performance-analyzer"
            ),
            "https://daxstudio.org/docs/features/traces/server-timings-options/",
        ],
        practice=[
            t(
                "Predict the mean if the warm 25 ms value is replaced by 40 ms.",
                "Recompute the same statistic rather than selecting a favorable trial.",
                "The mean becomes (20 + 40 + 21)/3 = 27 ms for that revised synthetic scenario.",
            ),
            t(
                ("Compare A's cold trial with B's warm trial conceptually."),
                "The cache condition is confounded with the candidate.",
                (
                    "That comparison cannot isolate a formula effect; measure "
                    "both under a controlled, recorded condition."
                ),
            ),
            t(
                "Write a real benchmark protocol without running it here.",
                "Include semantic parity and workload identity before time.",
                (
                    "Pin source/model/engine, specify filters and cache "
                    "preparation, collect repeated results and diagnostics, "
                    "validate outputs, and report variability and limitations."
                ),
            ),
            t(
                ("Diagnose quoting 18 ms as B's stable production latency."),
                "One synthetic best value has neither real provenance nor tail coverage.",
                (
                    "It is not a measurement at all in this lesson, and a best "
                    "trial would not establish production latency even if "
                    "observed."
                ),
            ),
            t(
                (
                    "Explain why a smaller toy model cannot establish behavior "
                    "at production cardinality."
                ),
                "Physical plans, memory and contention can change with scale.",
                (
                    "Treat toy semantic checks and representative-scale "
                    "performance evidence as separate gates."
                ),
            ),
            t(
                "Transfer the review to a machine-learning inference benchmark.",
                "Separate model loading, compilation, warmup, batch size and synchronization.",
                (
                    "Record comparable conditions and actual output "
                    "correctness before interpreting throughput or latency, "
                    "especially with accelerators."
                ),
            ),
        ],
    ),
    lesson(
        54,
        "Optimization capstone: prove the grouping assumption first",
        ["semantic parity", "grouped rewrite", "constant rate", "cost model", "qualification"],
        (
            "Review a grouped cost rewrite under explicit assumptions "
            "before proposing a performance measurement."
        ),
        (
            "A cost calculation can multiply each sales line's "
            "quantity by its product's constant unit cost, or "
            "aggregate quantities by product first and multiply once "
            "per product. These forms agree only when the grouping "
            "preserves every variable on which the rate depends. In "
            "our fixture UnitCost is explicitly constant per product "
            "across the modeled period.\n\nThe grouped expression still "
            "needs correct context transition for each product's "
            "quantity and cost. A filter on region or date must remain "
            "active while the product key changes. Unsold products "
            "yield blank quantities and should not create invented "
            "costs. Compare several contexts and edge cases rather "
            "than checking only the grand total.\n\nThis is a "
            "semantic-refactoring capstone, not a speed claim. The "
            "grouped iterator can have fewer logical rows but "
            "introduce other evaluation work; an engine may optimize "
            "either expression. If real costs vary by transaction "
            "date, supplier or currency, grouping only by ProductKey "
            "would be invalid. Preserve the required rate grain first, "
            "then design a qualified external measurement."
        ),
        (
            "The line form uses RELATED inside SUMX(Sales,...). The "
            "grouped form iterates ProductKey, transitions the key for "
            "the fact quantity, retrieves the unique product cost and "
            "multiplies. The two result columns are independent "
            "expression shapes over the same fixed assumptions."
        ),
        [
            r(
                "Whole-model parity under a constant product cost",
                (
                    'EVALUATE ROW ( "LineCost", SUMX ( Sales, Sales[Quantity] '
                    '* RELATED ( Product[UnitCost] ) ), "GroupedCost", SUMX ( '
                    "VALUES ( Product[ProductKey] ), CALCULATE ( SUM ( "
                    "Sales[Quantity] ) ) * CALCULATE ( MAX ( Product[UnitCost] "
                    ") ) ) )"
                ),
                [("LineCost", "number"), ("GroupedCost", "number")],
                [[44, 44]],
                ("Clean retail model; UnitCost is constant per product and unique on ProductKey."),
                [
                    "Notebook has 7 units at 2, Pen 5 units at 1 and Mug 5 units at 5.",
                    "Grouped costs are 14, 5 and 25, totaling 44.",
                    "The eight line-level costs independently sum to the same 44.",
                ],
                (
                    "The data model supplies the rate constancy that permits "
                    "this grouping. The formula alone does not prove that "
                    "assumption in another dataset."
                ),
            ),
            r(
                "Parity under a region and year selection",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "LineCost", SUMX ( Sales, '
                    "Sales[Quantity] * RELATED ( Product[UnitCost] ) ), "
                    '"GroupedCost", SUMX ( VALUES ( Product[ProductKey] ), '
                    "CALCULATE ( SUM ( Sales[Quantity] ) ) * CALCULATE ( MAX ( "
                    'Product[UnitCost] ) ) ) ), Customer[Region] = "North", '
                    "'Date'[Year] = 2025 )"
                ),
                [("LineCost", "number"), ("GroupedCost", "number")],
                [[20, 20]],
                (
                    "North and order year 2025 remain active while the grouped "
                    "expression iterates product keys."
                ),
                [
                    "S4, S5, S8 are the eligible lines.",
                    "Their costs are 6, 4 and 10.",
                    "The grouped quantities 3, 4, 2 at rates 2, 1, 5 also yield 20.",
                ],
                (
                    "This filtered case checks that a rewrite does not "
                    "accidentally remove region or period constraints. Add "
                    "missing-key and changing-rate cases before generalizing."
                ),
            ),
        ],
        [
            t(
                "Predict the parity result for Paper.",
                "Notebook and Pen costs are 14 and 5.",
                "Both expressions give 19 under the stated constant-rate assumptions.",
            ),
            t(
                "Introduce a transaction-specific historical cost.",
                "Grouping only by ProductKey would combine different rates.",
                (
                    "The rewrite is no longer justified; preserve the "
                    "effective-rate grain or use a trusted stored line cost."
                ),
            ),
            t(
                "Write a release decision for this proposed rewrite.",
                "Separate proven fixture semantics from unmeasured speed.",
                (
                    "Accept it only as a semantics candidate under documented "
                    "assumptions, retain the context test grid, and require "
                    "real comparable performance evidence before claiming "
                    "improvement."
                ),
            ),
            t(
                (
                    "Diagnose replacing a product's unique cost with MAX "
                    "across conflicting rate rows."
                ),
                "An aggregate can hide a violated uniqueness contract.",
                (
                    "MAX chooses a value rather than repairing ambiguous rate "
                    "data. Validate rate keys and effective dates first."
                ),
            ),
            t(
                "Explain a product with no matching dimension cost.",
                "Missing rates must not silently remove cost from a total.",
                (
                    "Expose a missing-cost quality failure and block or label "
                    "incomplete profit; do not claim the surviving sum is "
                    "complete."
                ),
            ),
            t(
                "Transfer the capstone to currency conversion.",
                "The exchange rate depends on date and currency, not product alone.",
                (
                    "Group only by keys that preserve the full rate domain, "
                    "then compare row-level and grouped results across "
                    "temporal and missing-rate boundaries."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/sumx-function-dax",
            "https://learn.microsoft.com/en-us/dax/related-function-dax",
            (
                "https://learn.microsoft.com/en-us/power-bi/create-reports/"
                "desktop-performance-analyzer"
            ),
        ],
    ),
]

LESSONS[3]["feature"] = (
    "Reviewed 2026-10-25: Microsoft's value-filter-behavior "
    "page labels this setting as preview. Record the actual "
    "model property and engine version when comparing "
    "Coalesced, Independent or Automatic behavior. The offline "
    "cases enumerate explicit domains and do not claim to "
    "execute or configure this engine setting."
)


REASONING = {
    49: [
        (
            (
                "SaleID is the line key. A valid new line, S9, adds one row and one distinct "
                "SaleID, so both counts go from 8 to 9."
            ),
            (
                'Reusing an existing key such as "S8" for the new line gives 9 rows but still 8 '
                "distinct SaleIDs. The key no longer identifies one line."
            ),
            (
                "After adding S9, COUNTROWS(Sales) and DISTINCTCOUNT(Sales[SaleID]) both return 9; "
                "ProductKeys stays 3 unless S9 sells Bag."
            ),
        ),
        (
            (
                "The fact table already stores ProductKey (3 distinct values over 8 rows) and gets "
                "names and categories from the 4-row Product dimension."
            ),
            (
                "Promising that replacing a label column with a key saves a fixed percentage of "
                "storage. Compression depends on the data and the engine, and nothing here was "
                "measured."
            ),
            (
                "The logical check is that every Sales[ProductKey] matches one Product row and "
                "that revenue by ProductName is still Notebook 67, Pen 24 and Mug 96."
            ),
        ),
        (
            (
                "A performance claim needs evidence of the same answer, the same workload and a "
                "measurement, in that order."
            ),
            (
                "Timing a rewrite on this 8-row fixture and treating the result as evidence. At "
                "this size there is nothing to separate from noise."
            ),
            (
                "The checklist starts with result parity (for example NetRevenue 187 and "
                "GrossRevenue 195), then records model, storage mode, filters, engine version, "
                "hardware, cache state and repeated timings."
            ),
        ),
        (
            (
                "Function names do not decide speed. SUM(Sales[NetAmount]) and SUMX(Sales, "
                "Sales[NetAmount]) express the same calculation, 187. GrossRevenue needs the "
                "row-level product."
            ),
            (
                "Replacing SUMX(Sales, Quantity x UnitPrice) with SUM(Quantity) x SUM(UnitPrice) "
                "to avoid an iterator gives 17 x 100 = 1700 instead of 195."
            ),
            (
                "Keep the correct expression (195), and compare engine timings only between "
                "expressions that return the same value."
            ),
        ),
        (
            (
                "SaleID is the only column here that is unique per line. OrderID has 7 distinct "
                "values for 8 rows because order 101 has S1 and S2."
            ),
            (
                "Dropping SaleID because its cardinality equals the row count. Without it, two "
                "identical lines could not be told apart or checked for duplicates."
            ),
            (
                "DISTINCTCOUNT(Sales[SaleID]) = COUNTROWS(Sales) = 8 is the duplicate check, and "
                "it only works while the key exists."
            ),
        ),
        (
            (
                "OrderDate has 7 distinct days. Truncating dates to months leaves 3 values "
                "(January 2024, January 2025 and February 2025)."
            ),
            (
                "Truncating to month to save space breaks the daily windows from earlier lessons, "
                "such as the three days ending February 3, 2025 (56 USD)."
            ),
            (
                "Choose the grain from the questions to be answered: day-level windows need dates. "
                "Then measure the storage of that choice."
            ),
        ),
    ],
    50: [
        (
            (
                "The candidate grid multiplies the dimension sizes. With 5 products and 4 "
                "customers it has 20 cells, but no new sale means no new observed pair."
            ),
            (
                "Expecting ObservedPairs to rise to 7 with the new product. SUMMARIZE over Sales "
                "only sees combinations that sold."
            ),
            "CandidatePairs returns 20 and ObservedPairs stays 6.",
        ),
        (
            (
                "Filtering the calendar to January 2025 leaves 31 dates in VALUES('Date'[Date]), "
                "so the grid is 4 x 4 x 31. Observed cells come from S4, S5 and S6."
            ),
            (
                "Filtering only Sales to January and expecting the grid to shrink. CROSSJOIN of "
                "VALUES still reads all 731 dates unless the Date table is filtered."
            ),
            "Under Year 2025 and MonthNumber 1, CandidateCells is 496 and ObservedCells is 3.",
        ),
        (
            (
                "A coverage matrix needs every requested cell: 4 products by 4 customers, 16 "
                "cells, of which 6 have sales. Bag's row and Di's column are empty."
            ),
            (
                'Using SUMMARIZECOLUMNS(Product[ProductName], Customer[CustomerName], "Revenue", '
                "[NetRevenue]) drops cells with blank revenue and returns 6 rows."
            ),
            (
                "ADDCOLUMNS over CROSSJOIN(VALUES(Product[ProductName]), "
                "VALUES(Customer[CustomerName])) with a missing marker returns 16 rows, 10 of them "
                "without sales."
            ),
        ),
        (
            (
                "11696 is 4 x 4 x 731, the size of a logical expression. The engine may never "
                "build that table."
            ),
            (
                "Reporting that the query scanned 11696 rows. No query plan or server timing was "
                "captured, so that is a guess presented as a measurement."
            ),
            (
                "Describe 11696 as the logical size of the CROSSJOIN, and back any claim about "
                "physical work with a captured plan."
            ),
        ),
        (
            (
                "Eligibility comes from the dimension. Di (customer 40) has no sales, so she "
                "appears in Customer but not in any Sales grouping."
            ),
            (
                "Taking the denominator from SUMMARIZE(Sales, Sales[CustomerKey]) gives 3 active "
                "out of 3 customers, a 100 percent rate."
            ),
            "Over the Customer dimension, 3 of 4 customers have sales, a rate of 0.75.",
        ),
        (
            (
                "A product-by-store-by-day model multiplies the same way. 1,000 products, 50 "
                "stores and 365 days give 18,250,000 candidate cells."
            ),
            (
                "Building that full scaffold in an iterator when only store-days with sales "
                "matter, or using only observed cells when zero-sale days count."
            ),
            (
                "Estimate the grid size first, decide which empty cells the question needs, and "
                "measure the cost of the chosen scaffold."
            ),
        ),
    ],
    51: [
        (
            (
                "Every row under an incoming Quantity >= 2 filter already meets the predicate. "
                "Replacing, intersecting or filtering the visible rows keeps the same 6 lines."
            ),
            (
                "Treating this second agreement as proof that the rewrites are equivalent. Case "
                "B's Quantity = 1 input still separates them."
            ),
            "Under Sales[Quantity] >= 2, all three columns return 163.",
        ),
        (
            (
                "Quantity >= 3 keeps S4 (3 units, 27) and S5 (4 units, 20). Without other filters, "
                "all three forms keep the same two lines."
            ),
            (
                "Expecting the case B pattern to change with the new threshold. Under Quantity = "
                "1, the table and KEEPFILTERS forms still return BLANK and only the column filter "
                "returns 47."
            ),
            (
                "Unfiltered, each form returns 47; under Quantity = 1 the results are BLANK, 47 "
                "and BLANK."
            ),
        ),
        (
            (
                "The grid needs inputs that agree, overlap and conflict. An overlapping Quantity "
                "IN {1, 2} filter and an unrelated Blue filter separate cases A and B."
            ),
            (
                "Testing only the unfiltered case, where all three return 163 and no rewrite can "
                "be wrong."
            ),
            (
                "Under Quantity IN {1, 2}: TableFilter 116, ColumnFilter 163, KEEPFILTERS 116. "
                "Under Blue: all three 143."
            ),
        ),
        (
            (
                "Under Quantity = 1, the column filter replaces the selection and returns 163, "
                "while the others return BLANK. A bigger number is not a better one."
            ),
            (
                "Choosing the column filter because it fills cells the original left blank. It "
                "changes the metric for any visual filtered on Quantity."
            ),
            (
                "Decide whether the business rule should respect the incoming Quantity selection; "
                "if so, keep case B's BLANK as the expected regression value."
            ),
        ),
        (
            (
                "The KEEPFILTERS column form matches the FILTER(Sales, ...) form here because only "
                "one column is involved and FILTER iterates the visible rows."
            ),
            (
                "Generalizing to a table filter built on ALL(Sales). That table carries every "
                "Sales column, and through the expanded table its reach extends to Product, "
                "Customer and Date, so its interaction with incoming dimension filters is "
                "different and must be tested."
            ),
            (
                'Under Product[Color] = "Red", KEEPFILTERS(Sales[Quantity] >= 2) returns 20 '
                "(S5 only). Run any whole-table form under the same Red filter and compare "
                "before calling it equivalent."
            ),
        ),
        (
            (
                "A SQL rewrite needs the same parity checks: duplicate rows, NULL handling and "
                "boundaries, before timings matter."
            ),
            (
                "Summing over SELECT DISTINCT NetAmount to cut rows. S1, S5, S6 and S7 all have "
                "20, so the total falls from 187 to 127."
            ),
            (
                "Compare row counts and totals between original and rewritten queries (8 lines and "
                "187) before reading any timing."
            ),
        ),
    ],
    52: [
        (
            (
                "ALL(Product) removes Product filters only, and none are active. North (Ada and "
                "Cy) and 2025 still select S4, S5 and S8."
            ),
            (
                "Expecting 187 as with ALL(Sales). ALL(Sales) clears the expanded fact table, "
                "including Customer and Date, but ALL(Product) cannot reach them."
            ),
            ("Under Region North and Year 2025, CALCULATE([NetRevenue], ALL(Product)) returns 83."),
        ),
        (
            (
                "Notebook is Paper and Blue, and Mug is Home and Blue, so both requested pairs "
                "exist in Product."
            ),
            (
                "Concluding from this case that a cross product of valid values always exists. "
                "Case B's Home and Red has no product."
            ),
            "RequestedPairs 2 and ExistingPairs 2 for Blue, against 2 and 1 for Red.",
        ),
        (
            (
                "The ledger lists the incoming filters (North, 2025), the modifier and the tables "
                "it covers, the relationship type, the requested and existing pairs, and the value "
                "at each step."
            ),
            (
                'Writing only "used ALL" in the ledger, which does not say whether 187 or 83 is '
                "expected."
            ),
            (
                "For case A the ledger reads Original 83, ALL(Sales) 187 and "
                "REMOVEFILTERS(Sales[NetAmount]) 83, each with its reason."
            ),
        ),
        (
            (
                "To remove only the color filter, name that column. Under Blue, North and 2025, "
                "the lines are S4 and S8."
            ),
            (
                "Using ALL(Sales) also clears North and 2025, so the measure jumps to the "
                "whole-model 187."
            ),
            (
                "Blue, North and 2025 give 63. REMOVEFILTERS(Product[Color]) gives 83, while "
                "ALL(Sales) gives 187."
            ),
        ),
        (
            (
                "Independent and Coalesced settings control how filters on columns of the same "
                "table combine. Formulas do not show the setting."
            ),
            (
                "Predicting a result from the setting's name, such as assuming Independent means "
                "filters never interact, without testing."
            ),
            (
                "Record the setting and engine version, then test case B's Paper or Home with Red "
                "selection and the totals in the target model."
            ),
        ),
        (
            (
                "Size and color selections work like Category and Color here. Each label exists, "
                "but the pair may not: Home and Red has no product."
            ),
            (
                "Computing a share where the denominator counts requested pairs. For Paper or Home "
                "with Red, only Pen exists, so the share must be based on 1 pair, not 2."
            ),
            (
                "Count existing combinations with SUMMARIZE over the dimension before computing "
                "shares; Pen's 24 USD is the only Red revenue."
            ),
        ),
    ],
    53: [
        (
            (
                "Replacing 25 with 40 gives 20, 40 and 21. Recompute the same mean over all three "
                "trials."
            ),
            (
                "Dropping 40 as an outlier and reporting 20.5 ms. That changes the statistic after "
                "seeing the data."
            ),
            "The mean is 81 / 3 = 27 ms; the median is 21 ms.",
        ),
        (
            (
                "Cold trials average 110 ms and warm trials 22 ms, so comparing across cache "
                "states mixes two causes."
            ),
            (
                "Timing A cold, near case A's 110 ms, and B warm, near 22 ms, then crediting "
                "B's formula with an 88 ms gain. Cache state alone explains a gap that size."
            ),
            (
                "Compare A and B only under the same cache condition, as case B does: means 20 and "
                "32, medians 20 and 18."
            ),
        ),
        (
            (
                "A protocol fixes what is being compared before timing: the same model and engine, "
                "the same filters, results that match, and a stated cache preparation."
            ),
            (
                "Running each candidate once after editing it, so the first run is cold for one "
                "and warm for the other."
            ),
            (
                "Each candidate must return the same result before timing; report repeated trials "
                "with mean, median and spread, as case B's three trials show."
            ),
        ),
        (
            (
                "B's trials are 18, 60 and 18. The best is 18, the mean 32, and the 60 ms trial "
                "shows variability."
            ),
            (
                "Quoting 18 ms as production latency. These numbers are synthetic, and a best "
                "trial hides the slow one."
            ),
            "Report 18, 60 and 18 with mean 32 and median 18, and label them synthetic.",
        ),
        (
            (
                "The 8-row Sales table proves results, such as 187, not speed. Plans, memory and "
                "contention change at millions of rows."
            ),
            (
                "Timing two expressions on this fixture and expecting the faster one to stay "
                "faster in production."
            ),
            "Use toy models for correctness and a representative-scale model for speed.",
        ),
        (
            (
                "Inference benchmarks have the same cold path: model loading, compilation and "
                "warmup. A first trial like B's 60 ms can be setup cost."
            ),
            (
                "Averaging the first call with steady-state calls, or reporting only warm calls "
                "without saying so."
            ),
            (
                "Report setup and steady-state timings separately, with batch size and "
                "synchronization stated, and check the outputs match before comparing speed."
            ),
        ),
    ],
    54: [
        (
            (
                "With one cost per product, multiplying each product's quantity by its cost equals "
                "the line sum. Paper's products are Notebook (7 x 2 = 14) and Pen (5 x 1 = 5)."
            ),
            (
                "Multiplying Paper's total quantity, 12, by MAX(UnitCost) over Paper, 2, gives 24. "
                "The grouping has to be by product."
            ),
            'Under Category = "Paper", LineCost and GroupedCost both return 19.',
        ),
        (
            (
                "If Notebook's 2024 line S1 had cost 1.5 instead of 2, the line form gives 3 + 6 + "
                "4 = 13 for Notebook, while grouping by product applies one rate to all 7 units."
            ),
            (
                "Keeping the grouped rewrite. MAX picks 2 and returns 14, so it overstates cost by "
                "1."
            ),
            (
                "Line cost 13 versus grouped 14 for Notebook; group by the key that defines the "
                "rate, or store the line cost."
            ),
        ),
        (
            (
                "The rewrite matches here only because each product has one cost. Case A gives 44 "
                "and 44, and case B gives 20 and 20."
            ),
            (
                "Releasing it as faster without timings, or as correct without the context grid "
                "from cases A and B."
            ),
            (
                "Accept it as correct under the one-cost-per-product rule, keep both cases as "
                "regressions, and require a real benchmark before claiming speed."
            ),
        ),
        (
            (
                "Two cost rows for one product break the one-cost rule. MAX hides that by choosing "
                "one value."
            ),
            (
                "If Notebook had rows at 2 and 3, MAX returns 3 and cost becomes 21, with no "
                "warning that the input was ambiguous."
            ),
            (
                "Check that each ProductKey has one cost; COUNTROWS of cost rows per ProductKey "
                "should be 1 before either formula runs."
            ),
        ),
        (
            (
                "In the unknown-member model, S9 has ProductKey 999 and Net 7, with no matching "
                "Product row, so RELATED(Product[UnitCost]) is BLANK."
            ),
            (
                "Reporting cost 44 against revenue 194. S9's cost is missing, not zero, so profit "
                "is overstated."
            ),
            (
                "Count sales lines whose cost is BLANK (1 here), and label profit incomplete until "
                "it is fixed."
            ),
        ),
        (
            (
                "Rates depend on date and currency. Grouping by (SaleDate, Currency) matches the "
                "row-level sum: 100 x 1 + 100 x 1.1 + 50 x 1.2 = 270."
            ),
            (
                "Grouping by currency only and taking MAX of EUR rates converts 150 EUR at 1.2 for "
                "180 USD instead of 170."
            ),
            (
                "Row-level and (SaleDate, Currency)-grouped conversions both return 270; the "
                "currency-only grouping does not."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

"Stage nine: interpret work and measurements without inventing engine receipts."

from .common import lesson
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
                    "Categories are Paper,Home,Travel and colors are Blue,Red,Green.",
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
                    "The full dimension product is 4 times 4 =16 pairs.",
                    "Observed pairs are(1,10),(2,10),(3,20),(2,30),(1,20),(3,30).",
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
                    "The possible-cell count is 4 *4 *731 =11696.",
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
                "The full candidate grid becomes 5 *4 =20; observed pairs can remain six.",
            ),
            t(
                "Restrict the calendar to January 2025.",
                "The selected Date dimension has 31 days.",
                (
                    "The candidate grid becomes 4 *4 *31 =496; the observed "
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
                    "S2 and S 6 have quantity 1 and contribute 4 +20 =24.",
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
                    "The incoming visible fact rows are S2 and S 6, both quantity 1.",
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
                "Identify S4 and S 5.",
                "Without other filters the retained revenue is 27 +20 =47.",
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
                "The mean becomes(20+40+21)/3 =27 ms for that revised synthetic scenario.",
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
                    "Grouped costs are 14,5 and 25, totaling 44.",
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
                    "S4,S5,S8 are the eligible lines.",
                    "Their costs are 6,4 and 10.",
                    "The grouped quantities 3,4,2 at rates 2,1,5 also yield 20.",
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
                "The exchange rate depends ondate andcurrency, not product alone.",
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

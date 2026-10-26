"""Stage three: the two contexts and explicit evaluation order."""

from .common import lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        13,
        "Row context is not a filter on related facts",
        ["row context", "filter context", "iterator", "context transition"],
        ("Explain why iterating Product does not by itself filter a raw Sales aggregation."),
        (
            "Row context provides access to the current row's column "
            "values. A calculated column or iterator can create it. "
            "Filter context specifies which model rows are eligible "
            "for aggregations. They are different mechanisms: being "
            "positioned on a Product row does not automatically filter "
            "a raw SUM over Sales.\n\nSELECTCOLUMNS iterates its input "
            "table to construct output rows. Product[Product] can read "
            "the current row's name. SUM(Sales[NetAmount]) still sees "
            "the outer filter context unless an operation transitions "
            "the current row into filters. This is why a raw "
            "aggregation can repeat the whole-model total beside every "
            "product, even with a perfectly valid "
            "relationship.\n\nCALCULATE can perform context transition. "
            "Once the current Product row becomes filter context, its "
            "key travels through the active relationship to Sales. A "
            "model measure invoked in row context performs this "
            "transition implicitly. Understanding that implicit "
            "behavior explains why changing a raw SUM to a measure "
            "reference can change results even when the measure "
            "definition contains the same SUM."
        ),
        (
            "The first projection contains a column lookup and an "
            "untransitioned aggregation. The second surrounds the "
            "aggregation with CALCULATE. Both return all four products "
            "because SELECTCOLUMNS retains its input rows even if a "
            "projected value is BLANK. The explicit ORDER BY makes "
            "their display comparable."
        ),
        [
            r(
                "A row label beside an unfiltered sum",
                (
                    'EVALUATE SELECTCOLUMNS ( Product, "Product", '
                    'Product[Product], "RawSum", SUM ( Sales[NetAmount] ) '
                    ")\nORDER BY [Product]"
                ),
                [("Product", "text"), ("RawSum", "number")],
                [["Bag", 187], ["Mug", 187], ["Notebook", 187], ["Pen", 187]],
                "No outer filters; SELECTCOLUMNS supplies a Product row context only.",
                [
                    "The Product label changes on each iteration.",
                    "The raw SUM has no transitioned Product filter.",
                    "Every iteration therefore adds the same eight sales lines and returns 187.",
                ],
                (
                    "The repeated total is not evidence of a broken "
                    "relationship. It is evidence that the formula never "
                    "supplied that relationship with a Product filter."
                ),
            ),
            r(
                "Transition the current product into a filter",
                (
                    'EVALUATE SELECTCOLUMNS ( Product, "Product", '
                    'Product[Product], "Revenue", CALCULATE ( SUM ( '
                    "Sales[NetAmount] ) ) )\nORDER BY [Product]"
                ),
                [("Product", "text"), ("Revenue", "number")],
                [["Bag", None], ["Mug", 96], ["Notebook", 67], ["Pen", 24]],
                "The same Product rows, now with explicit context transition for the raw SUM.",
                [
                    "CALCULATE turns each current Product row into filters.",
                    "The active key relationship restricts Sales for that product.",
                    "Bag has no matching fact rows; the other products contribute 96, 67 and 24.",
                ],
                (
                    "The sum of the three nonblank product results reconciles "
                    "to 187 because these product populations partition the "
                    "fact rows in the clean model."
                ),
            ),
        ],
        [
            t(
                (
                    "Predict the second projection if it uses [NetRevenue] "
                    "instead of CALCULATE(SUM(...))."
                ),
                "A model measure invoked in row context has an implicit transition.",
                "It returns the same per-product values for this model.",
            ),
            t(
                "Add an outer North filter to the raw-SUM case.",
                "Row context still does not become a Product filter.",
                "RawSum repeats the North total 107 for every visible product.",
            ),
            t(
                "Write a projection that shows both raw and transitioned sums.",
                "Keep separate output labels in the same SELECTCOLUMNS call.",
                (
                    "Each row can show RawSum 187 beside its own Revenue; this "
                    "makes the missing transition directly observable."
                ),
            ),
            t(
                "Diagnose replacing the relationship because every row shows 187.",
                "Inspect evaluation context before changing model structure.",
                (
                    "The relationship can be correct; the raw aggregation has "
                    "no Product filter to propagate."
                ),
            ),
            t(
                "Explain why Bag remains a returned row in case B.",
                "SELECTCOLUMNS projects its input rows, including blank expressions.",
                (
                    "Blank output is not a row-removal rule for this function. "
                    "Other table functions may have different blank-row "
                    "behavior."
                ),
            ),
            t(
                (
                    "Transfer the distinction to a Customer calculated column "
                    "containing total sales."
                ),
                "A current customer row is initially row context.",
                (
                    "A raw Sales SUM repeats the outer total; CALCULATE or a "
                    "model measure transitions the customer row so the "
                    "relationship can filter its sales."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
            "https://learn.microsoft.com/en-us/dax/selectcolumns-function-dax",
        ],
    ),
    lesson(
        14,
        "Filter context is the full question, not just one slicer",
        ["filter context", "intersection", "selection", "report cell"],
        (
            "Record a complete context ledger and explain two cells "
            "with the same measure definition."
        ),
        (
            "Filter context can come from a query, a visual's rows and "
            "columns, a slicer, a page filter or an expression that "
            "modifies it. A measure does not know that one selected "
            "value was visually prominent and another was hidden in a "
            "report pane. All effective filters belong to the "
            "question. Record them by table and column before "
            "diagnosing a surprising number.\n\nFilters on different "
            "dimensions intersect through the fact table. Multiple "
            "selected values on one column form an allowed set rather "
            "than several independent calculations added together. "
            "Selecting North and South admits customers from either "
            "region; adding Year 2025 still restricts the eligible "
            "sales dates. In contrast, two separate dimensions such as "
            "region and product category impose simultaneous "
            "conditions.\n\nA result also depends on relationship status "
            "and model scope. A Date selection reaches OrderDate "
            "through the active relationship in our model. It does not "
            "mean ShipDate merely because a page title says "
            "'shipping'. Context traces should name date role, "
            "selected keys and remaining facts, not just state that a "
            "measure is 'filtered'."
        ),
        (
            "The IN operator expresses membership in a literal value "
            "set. CALCULATETABLE provides the two stated filters "
            "around a ROW. The measure is identical across cases, so "
            "the row-eligibility ledger explains the changed answer. "
            "Neither calculation contains row context."
        ),
        [
            r(
                "One region in one year",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue] '
                    "), Customer[Region] = \"North\", 'Date'[Year] = 2025 )"
                ),
                [("Revenue", "number")],
                [[83]],
                "Customer.Region = North and Date.Year = 2025, using active OrderDate.",
                [
                    "North supplies customer keys 10 and 30.",
                    "Year 2025 removes S1, S2 and S3.",
                    "S4, S5 and S8 remain: 27 + 20 + 36 = 83.",
                ],
                (
                    "The same regional total across all years would be 107. "
                    "Omitting the year from an explanation would conceal why "
                    "those two correct values differ."
                ),
            ),
            r(
                "A multi-selection retains the year",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue] '
                    '), Customer[Region] IN { "North", "South" }, \'Date\'[Year] '
                    "= 2025 )"
                ),
                [("Revenue", "number")],
                [[123]],
                "Region is the allowed set {North, South}; order year remains 2025.",
                [
                    "The region set admits all three customers with sales.",
                    "The year filter still excludes the three 2024 lines.",
                    "S4 through S8 total 123.",
                ],
                (
                    "Broadening one filter does not remove the others. The "
                    "answer does not return to the all-year total 187."
                ),
            ),
        ],
        [
            t(
                "Predict 2025 South revenue.",
                "Find customer 20's lines in 2025.",
                "S6 and S7 contribute 20 each, totaling 40.",
            ),
            t(
                "Add Product.Category = Paper to case B.",
                "Keep the year and region set while restricting product keys.",
                "S4, S5 and S7 remain, totaling 67.",
            ),
            t(
                "Write a context ledger for North, Home and 2025.",
                "State each filter's dimension and key effect.",
                (
                    "North admits customers 10/30, Home admits product 3, and "
                    "2025 keeps S8; revenue is 36."
                ),
            ),
            t(
                "Diagnose a report comparing North 2025 with South across all years.",
                "Check whether both sides use the same temporal population.",
                (
                    "The comparison mixes 83 with 80 rather than "
                    "comparable-year 83 with 40. Define the intended period "
                    "consistently."
                ),
            ),
            t(
                "Predict a West-plus-2025 selection.",
                "A valid dimension selection can have no facts.",
                "The result is BLANK because customer 40 has no Sales rows.",
            ),
            t(
                "Transfer the ledger to a dashboard with several pages.",
                "Hidden filters can still change the query.",
                (
                    "Capture effective filters, date role and relationship "
                    "assumptions for each reported number, not only the "
                    "visible slicer caption."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/dax-overview",
            "https://learn.microsoft.com/en-us/dax/calculatetable-function-dax",
        ],
    ),
    lesson(
        15,
        "CALCULATE replaces a filter on the same column",
        ["CALCULATE", "Boolean filter", "replacement", "added filter"],
        "Predict replacement on one column while retaining unrelated filters.",
        (
            "CALCULATE evaluates a scalar expression in a modified "
            "filter context. A simple Boolean filter on a column "
            "normally replaces an existing filter on that same column. "
            "If the column was not filtered, the new filter is added. "
            "Other filters are not erased merely because CALCULATE "
            "appears in the expression.\n\nThis is a precise rule, not a "
            "slogan that CALCULATE 'ignores slicers'. An outer Blue "
            "filter on Product[Color] can be replaced by an inner Red "
            "filter on that column. An outer Paper filter on "
            "Product[Category] remains when Blue is added to Color, so "
            "the result is the blue Paper product rather than every "
            "blue product.\n\nWhen the business rule requires "
            "intersection with an existing selection on the same "
            "column, KEEPFILTERS can express it; the next stage "
            "examines that alternative. First become comfortable "
            "naming the exact modified column. Whole-table filters and "
            "expanded-table behavior require additional care, which is "
            "why the reference begins with narrow column predicates."
        ),
        (
            "Read the outer CALCULATETABLE as the starting question "
            "and the inner CALCULATE as a measure-specific change. A "
            "Boolean filter must obey DAX's restrictions, including "
            "referencing columns from one table and not referring "
            "directly to a measure. The output names distinguish the "
            "original and modified contexts."
        ),
        [
            r(
                "Replace Blue with Red",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Original", [NetRevenue], '
                    '"RedRevenue", CALCULATE ( [NetRevenue], Product[Color] = '
                    '"Red" ) ), Product[Color] = "Blue" )'
                ),
                [("Original", "number"), ("RedRevenue", "number")],
                [[163, 24]],
                "Start with Product.Color = Blue; the inner calculation sets Color = Red.",
                [
                    "The original measure includes Notebook and Mug, totaling 163.",
                    "The inner predicate replaces the filter on the same Color column.",
                    "Red admits Pen and produces 24.",
                ],
                (
                    "The second result is not a Blue-and-Red intersection. "
                    "That would have no product rows in this fixture."
                ),
            ),
            r(
                "Add Color while retaining Category",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "PaperRevenue", '
                    '[NetRevenue], "BluePaperRevenue", CALCULATE ( '
                    '[NetRevenue], Product[Color] = "Blue" ) ), '
                    'Product[Category] = "Paper" )'
                ),
                [("PaperRevenue", "number"), ("BluePaperRevenue", "number")],
                [[91, 67]],
                "Start with Category = Paper; add Color = Blue on a different column.",
                [
                    "Paper supplies Notebook and Pen: 91.",
                    "Blue is added while Paper remains active.",
                    "Only Notebook satisfies both; revenue is 67.",
                ],
                (
                    "Replacing one column's selection and retaining a "
                    "different column's selection are compatible behaviors. "
                    "Always specify which column the expression modifies."
                ),
            ),
        ],
        [
            t(
                "Predict setting Color = Green inside the Blue context.",
                "The existing Color filter is replaced.",
                "Green selects Bag, whose revenue is BLANK because it has no facts.",
            ),
            t(
                "Change case B's Color to Red.",
                "Paper remains and Red selects Pen.",
                "The modified revenue is 24.",
            ),
            t(
                "Write a measure that forces year 2025 but retains region.",
                "Modify only Date.Year.",
                (
                    "CALCULATE([NetRevenue],'Date'[Year]=2025) retains an "
                    "independent Customer.Region filter; under North the "
                    "result is 83."
                ),
            ),
            t(
                "Diagnose saying CALCULATE removed every report filter.",
                "Identify filters on columns not mentioned by the modifier.",
                (
                    "They can remain active. Case B retains Category and "
                    "therefore does not return all-Blue revenue 163."
                ),
            ),
            t(
                "Explain when a constant filter is inappropriate for an interactive metric.",
                "Forcing a value can contradict the user's intended selection.",
                (
                    "A fixed-year or fixed-color measure should be clearly "
                    "named; use an intersection policy when the metric should "
                    "respect the selection."
                ),
            ),
            t(
                "Transfer the distinction to a share denominator.",
                "Choose exactly which selection should be removed or replaced.",
                (
                    "Preserve filters defining the comparable population while "
                    "changing only the category or time dimension required by "
                    "the denominator's definition."
                ),
            ),
        ],
        sources=["https://learn.microsoft.com/en-us/dax/calculate-function-dax"],
    ),
    lesson(
        16,
        "Filter arguments are not an imperative sequence",
        ["evaluation order", "nested CALCULATE", "filter argument", "captured scalar"],
        ("Explain why sibling filter arguments differ from deliberately nested evaluation."),
        (
            "DAX filter arguments are expressions evaluated in the "
            "incoming context; they are not a series of imperative "
            "assignments executed left to right. If one filter "
            "expression uses MAX(Product[ProductKey]), that scalar is "
            "determined from its evaluation context, not automatically "
            "from the effect of a neighboring Color filter.\n\nStart "
            "with Paper. Its visible keys are 1 and 2, so MAX is 2. A "
            "single CALCULATE that adds Blue and also restricts "
            "ProductKey to that incoming maximum requests a blue "
            "product with key 2. None exists. A learner imagining that "
            "Blue runs first will incorrectly predict key 1 and "
            "revenue 67.\n\nNesting can intentionally establish a new "
            "context before another expression is evaluated. An outer "
            "Blue calculation changes the context received by the "
            "inner calculation; MAX then sees only the blue Paper "
            "product. Make the nesting express a business question "
            "rather than using it as a trial-and-error fix. Write the "
            "contexts as successive ledgers before trusting a "
            "complicated expression."
        ),
        (
            "Both cases begin in Paper. Case A puts Color and the "
            "MAX-derived key in sibling filter arguments. Case B puts "
            "the Blue modifier in an outer CALCULATE so the inner key "
            "expression sees the changed context. MAX is a scalar "
            "aggregation allowed in this column-filter construction; "
            "its value must still be traced at the correct time."
        ),
        [
            r(
                "Sibling filters use the incoming key maximum",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "IncomingMaxKey", MAX ( '
                    'Product[ProductKey] ), "Revenue", CALCULATE ( '
                    '[NetRevenue], Product[Color] = "Blue", '
                    "Product[ProductKey] = MAX ( Product[ProductKey] ) ) ), "
                    'Product[Category] = "Paper" )'
                ),
                [("IncomingMaxKey", "integer"), ("Revenue", "number")],
                [[2, None]],
                "Incoming Product.Category = Paper; sibling Color and ProductKey filters.",
                [
                    "Paper's incoming keys are 1 and 2; MAX is 2.",
                    "Blue and ProductKey 2 are then applied together with the retained category.",
                    "Pen is key 2 but Red, so the resulting product set is empty.",
                ],
                (
                    "BLANK is the coherent answer to those combined "
                    "constraints. It is not evidence that MAX or the "
                    "relationship failed."
                ),
            ),
            r(
                "Nested context before computing the key",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", CALCULATE ( '
                    "CALCULATE ( [NetRevenue], Product[ProductKey] = MAX ( "
                    'Product[ProductKey] ) ), Product[Color] = "Blue" ) ), '
                    'Product[Category] = "Paper" )'
                ),
                [("Revenue", "number")],
                [[67]],
                (
                    "Paper first; outer CALCULATE applies Blue before the "
                    "inner key expression is evaluated."
                ),
                [
                    "Paper plus Blue leaves ProductKey 1.",
                    "The inner MAX therefore evaluates to 1.",
                    "Notebook revenue is 67.",
                ],
                (
                    "The formulas answer differently sequenced questions. Do "
                    "not call them interchangeable rewrites merely because "
                    "they mention the same functions and columns."
                ),
            ),
        ],
        [
            t(
                "Predict case A with Color = Red.",
                "Incoming MAX is still key 2.",
                "Red and key 2 agree, so revenue is 24.",
            ),
            t(
                "Predict case B with Color = Red.",
                "The outer context leaves only Pen.",
                (
                    "The inner maximum is 2 and revenue is 24; this fixture "
                    "would hide the sequencing difference if only Red were "
                    "tested."
                ),
            ),
            t(
                "Write a context ledger for each sibling expression.",
                "Record where MAX is evaluated before recording final eligibility.",
                (
                    "Start Paper {1,2}; bind maximum 2; form Blue; combine key "
                    "2 with Blue; identify the empty intersection."
                ),
            ),
            t(
                "Diagnose testing only the Red variant and declaring equivalence.",
                "A passing ordinary case can miss a counterexample.",
                "Blue distinguishes the two evaluation orders, returning BLANK versus 67.",
            ),
            t(
                ("Explain why a variable bound before the outer modifier can reintroduce the bug."),
                "Stage two established that scalar variables are not reevaluated macros.",
                ("Capturing max key 2 before Blue preserves 2 even inside the nested calculation."),
            ),
            t(
                "Transfer the principle to selecting the last eligible period.",
                "Ask whether 'last' is computed before or after a population filter.",
                (
                    "Define the population whose maximum period is needed, "
                    "then evaluate the maximum in that context. Do not assume "
                    "sibling arguments form a procedural pipeline."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
            "https://learn.microsoft.com/en-us/dax/best-practices/dax-variables",
        ],
    ),
    lesson(
        17,
        "Explicit and implicit context transition",
        ["context transition", "model measure", "SUMX", "row identity", "duplicate rows"],
        (
            "Trace a raw aggregation and a measure reference inside an "
            "iterator without treating context transition as a row "
            "pointer."
        ),
        (
            "Context transition converts the values of the current row "
            "context into filters. It is not a hidden instruction to "
            "remember one physical row object. On a table with "
            "duplicated rows, those value filters can match several "
            "rows. A unique fact key helps ensure that transitioning a "
            "Sales row selects the intended one-line population.\n\nIn "
            "SUMX(Sales, SUM(Sales[NetAmount])), the inner raw SUM "
            "sees no filter generated from the iterator's current row. "
            "With no outer filters it returns 187 on every one of "
            "eight iterations, producing 1496. CALCULATE around that "
            "inner SUM performs the transition, so each unique SaleID "
            "admits its own amount and the total is 187.\n\nCalling "
            "[NetRevenue] inside row context performs an implicit "
            "transition because it is a model measure. This "
            "convenience does not remove the need to understand the "
            "mechanism. A variable holding a precomputed scalar is "
            "different, and a duplicate-key model still needs "
            "diagnosis. Prefer simple direct sums when their semantics "
            "already fit; use an iterator only for a real row-by-row "
            "calculation."
        ),
        (
            "SUMX takes a table and a scalar expression to evaluate "
            "for each row. Case A deliberately contrasts raw and "
            "transitioned aggregations over unique Sales rows. Case B "
            "iterates Customer and invokes a measure. Customer 40's "
            "blank result contributes no amount, while the three "
            "purchasing customers partition the clean fact data."
        ),
        [
            r(
                "Eight repetitions versus eight individual amounts",
                (
                    'EVALUATE ROW ( "RawRepeated", SUMX ( Sales, SUM ( '
                    'Sales[NetAmount] ) ), "Transitioned", SUMX ( Sales, '
                    "CALCULATE ( SUM ( Sales[NetAmount] ) ) ) )"
                ),
                [("RawRepeated", "number"), ("Transitioned", "number")],
                [[1496, 187]],
                "No outer filters; SUMX creates one Sales row context per unique SaleID.",
                [
                    "Without transition, the inner SUM is 187 for every row.",
                    "Eight iterations give 8 * 187 = 1496.",
                    "With transition, the eight selected line amounts sum once each to 187.",
                ],
                (
                    "The two formulas differ in context semantics, not numeric "
                    "precision. Dividing the wrong result by eight would hide "
                    "the mistake and fail under another population."
                ),
            ),
            r(
                "Measure invocation transitions each customer",
                (
                    'EVALUATE ROW ( "CustomerRows", COUNTROWS ( Customer ), '
                    '"SumOfCustomerRevenue", SUMX ( Customer, [NetRevenue] ) )'
                ),
                [("CustomerRows", "integer"), ("SumOfCustomerRevenue", "number")],
                [[4, 187]],
                ("No outer filters; a model measure is invoked within each Customer row context."),
                [
                    "Ada contributes 51, Bo 80 and Cy 56.",
                    "Di has no matching sales and contributes BLANK.",
                    "51 + 80 + 56 = 187.",
                ],
                (
                    "This additive reconciliation works because each sale has "
                    "exactly one valid customer in this fixture. It is not a "
                    "general theorem that summing any measure over any "
                    "dimension equals its total."
                ),
            ),
        ],
        [
            t(
                "Predict the raw repeated formula for Paper's five lines.",
                "The inner raw SUM sees the outer Paper context.",
                "It repeats 91 five times, producing 455; the transitioned sum is 91.",
            ),
            t(
                "Replace the transitioned inner SUM with [NetRevenue].",
                "A measure supplies the implicit transition.",
                "The result stays 187 for unique Sales rows in this context.",
            ),
            t(
                "Write the simplest formula for this additive revenue total.",
                "An iterator is unnecessary for a stored additive column.",
                (
                    "SUM(Sales[NetAmount]) directly expresses the total "
                    "without a per-row context transition."
                ),
            ),
            t(
                "Diagnose fixing RawRepeated by dividing by COUNTROWS(Sales).",
                "The patch relies on a particular repeated-total mistake.",
                (
                    "It does not express the intended measure and can hide "
                    "other context or blank issues. Correct the expression "
                    "instead."
                ),
            ),
            t(
                "Explain the risk of two completely identical fact rows without a unique key.",
                "Transition filters by values rather than physical row identity.",
                (
                    "Both rows can match the transition on each iteration, so "
                    "an inner aggregation can count both repeatedly."
                ),
            ),
            t(
                "Transfer the reasoning to a per-customer cost allocation.",
                "Separate customer-level values from fact-line allocation weights.",
                (
                    "Define the allocation grain and denominator, then "
                    "transition only where the measure should be evaluated for "
                    "each customer or line."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
            "https://learn.microsoft.com/en-us/dax/sumx-function-dax",
        ],
    ),
    lesson(
        18,
        "Measure predicates need an explicit candidate table",
        ["FILTER", "measure predicate", "candidate set", "table filter", "lineage"],
        (
            "Build a measure-dependent selection by evaluating the "
            "measure for each candidate member."
        ),
        (
            "A simple Boolean filter argument to CALCULATE cannot "
            "directly refer to a measure. The expression 'keep "
            "products whose revenue exceeds 50' needs a candidate set "
            "and a measure evaluation for each candidate. FILTER can "
            "express that work: iterate a table of product keys, "
            "evaluate the measure in each row's transitioned context, "
            "and retain the keys meeting the condition.\n\nThe candidate "
            "table is part of the question. "
            "VALUES(Product[ProductKey]) uses visible product keys. "
            "ALL(Product[ProductKey]) would deliberately consider a "
            "different domain if a key selection is active. Neither "
            "version means 'all possible products in the business' "
            "unless the model and filter policy establish that "
            "population.\n\nThe retained key table can filter a later "
            "CALCULATE because it preserves its model-column identity. "
            "At threshold 50, Notebook and Mug qualify, so their "
            "revenues sum to 163. At threshold 90, only Mug qualifies, "
            "giving 96. This is not the same as testing whether the "
            "overall model revenue exceeds the threshold once and then "
            "keeping every product."
        ),
        (
            "FILTER supplies row context over "
            "VALUES(Product[ProductKey]). The measure [NetRevenue] "
            "performs context transition for that candidate key. The "
            "variable Qualifying holds the resulting table; using it "
            "as a CALCULATE filter applies those product keys to the "
            "measure evaluation. The source uses a table filter rather "
            "than an invalid direct measure predicate."
        ),
        [
            r(
                "Products above fifty",
                (
                    "EVALUATE\nVAR Qualifying = FILTER ( VALUES ( "
                    "Product[ProductKey] ), [NetRevenue] > 50 )\nRETURN ROW ( "
                    '"Products", COUNTROWS ( Qualifying ), "Revenue", '
                    "CALCULATE ( [NetRevenue], Qualifying ) )"
                ),
                [("Products", "integer"), ("Revenue", "number")],
                [[2, 163]],
                "No incoming filters; consider each visible ProductKey independently.",
                [
                    "Candidate revenues are Notebook 67, Pen 24, Mug 96 and Bag BLANK.",
                    "Keys 1 and 3 exceed 50.",
                    "Applying those retained keys yields 67 + 96 = 163.",
                ],
                (
                    "The threshold is applied to each product's measure "
                    "result. A single comparison of the grand total would not "
                    "perform this segmentation."
                ),
            ),
            r(
                "A stricter threshold",
                (
                    "EVALUATE\nVAR Qualifying = FILTER ( VALUES ( "
                    "Product[ProductKey] ), [NetRevenue] > 90 )\nRETURN ROW ( "
                    '"Products", COUNTROWS ( Qualifying ), "Revenue", '
                    "CALCULATE ( [NetRevenue], Qualifying ) )"
                ),
                [("Products", "integer"), ("Revenue", "number")],
                [[1, 96]],
                "Same candidate population, threshold changed from 50 to 90.",
                [
                    "Notebook no longer qualifies because 67 is not greater than 90.",
                    "Mug's 96 still qualifies.",
                    "The retained one-key table filters the final measure to 96.",
                ],
                (
                    "Changing the threshold changes membership, not the "
                    "source's definition of revenue. Keep both decisions "
                    "visible in a segmentation specification."
                ),
            ),
        ],
        [
            t(
                "Predict the retained products at threshold 24 using >.",
                "Equality at the boundary is excluded.",
                "Notebook and Mug qualify; Pen at exactly 24 does not.",
            ),
            t(
                "Change > 24 to >= 24.",
                "Check the boundary product explicitly.",
                "Pen is added, so three products qualify and their revenue is 187.",
            ),
            t(
                "Write a selection for customers with revenue above 55.",
                "Iterate CustomerKey and invoke the revenue measure.",
                (
                    "Bo at 80 and Cy at 56 qualify; Ada at 51 and Di at BLANK "
                    "do not. Their total is 136."
                ),
            ),
            t(
                "Diagnose CALCULATE([NetRevenue], [NetRevenue] > 50).",
                "A measure is not allowed in that simple Boolean filter slot.",
                (
                    "Use FILTER over a deliberate candidate table so the "
                    "measure has a per-candidate evaluation context."
                ),
            ),
            t(
                "Predict a threshold above every product's revenue.",
                "An empty qualifying table stays distinct from a one-row blank table.",
                (
                    "No product qualifies. COUNTROWS(Qualifying) and the final "
                    "SUM result are BLANK in this case."
                ),
            ),
            t(
                "Transfer the pattern to dynamic customer segments.",
                "Define the time window and candidate population before the threshold.",
                (
                    "A segment based on current-period revenue must state its "
                    "period and whether unsold or previously filtered "
                    "customers are eligible candidates."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/filter-function-dax",
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
            "https://learn.microsoft.com/en-us/dax/values-function-dax",
        ],
    ),
]

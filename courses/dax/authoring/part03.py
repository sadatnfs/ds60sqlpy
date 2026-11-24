"""Stage three: the two contexts and explicit evaluation order."""

from .common import explain, lesson
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


REASONING = {
    13: [
        (
            (
                "A model measure reference carries an implicit CALCULATE, so each Product row "
                "becomes a ProductKey filter that the relationship passes to Sales. The values "
                "match case B."
            ),
            (
                "Pasting the measure's body, SUM(Sales[NetAmount]), in place of the reference "
                "drops that implicit transition and brings back 187 on every row, as in case A."
            ),
            "Expect Bag BLANK, Mug 96, Notebook 67 and Pen 24, which add to 187.",
        ),
        (
            (
                "The outer North filter does reach Sales through Customer, so the raw SUM sees "
                "Ada's and Cy's five lines. The Product row context still adds no filter, so each "
                "row repeats 107."
            ),
            (
                "Expecting North's per-product split from RawSum is the error. That split "
                "(Notebook 47, Pen 24, Mug 36) needs a transition, not just an outer filter."
            ),
            (
                'Under `Customer[Region] = "North"` RawSum reads 107 on all four rows, while a '
                "transitioned column reads 47, 24, 36 and BLANK."
            ),
        ),
        (
            (
                "Two labeled columns in one SELECTCOLUMNS share each Product row, so RawSum (no "
                "transition) and Revenue (with CALCULATE) differ only by the transition."
            ),
            (
                "Iterating with SUMX(Product, SUM(Sales[NetAmount])) to get a total adds 187 four "
                "times and returns 748, the same missing transition hidden in one number."
            ),
            ("Expect rows Bag 187 and BLANK, Mug 187 and 96, Notebook 187 and 67, Pen 187 and 24."),
        ),
        (
            (
                "The ProductKey relationship is active and one to many, and it works whenever a "
                "Product filter exists. Case A simply creates no filter, so nothing travels to "
                "Sales."
            ),
            (
                "Making the relationship bidirectional or rebuilding it changes nothing here, "
                "because a row context is still not a filter, and every row still shows 187."
            ),
            (
                "`CALCULATE ( SUM ( Sales[NetAmount] ), Product[ProductKey] = 3 )` returns 96, "
                "which shows the relationship already filters correctly."
            ),
        ),
        (
            (
                "SELECTCOLUMNS keeps one output row per input row, so all four Product rows "
                "appear. Bag's Revenue is BLANK because no Sales line carries key 4."
            ),
            (
                "Expecting SELECTCOLUMNS to drop Bag mixes it up with SUMMARIZECOLUMNS, which "
                "removes rows whose measures are all blank and would return three rows."
            ),
            (
                "COUNTROWS of case B returns 4, while `SUMMARIZECOLUMNS ( Product[Product], "
                '"Revenue", SUM ( Sales[NetAmount] ) )` returns 3 rows without Bag.'
            ),
        ),
        (
            (
                "In a Customer calculated column, CALCULATE or [NetRevenue] turns the row into a "
                "CustomerKey filter, which gives Ada 51, Bo 80, Cy 56 and Di BLANK."
            ),
            (
                "A raw SUM(Sales[NetAmount]) column stores 187 for every customer. Summing that "
                "column over four customers reports 748."
            ),
            "The transitioned column sums to 187, and Di's BLANK stays BLANK rather than 0.",
        ),
    ],
    14: [
        (
            (
                "Customer 20 (Bo) is the only South customer. Under 2025 his lines are S6 and S7 "
                "at 20 each, so South revenue is 40."
            ),
            (
                "Leaving out the year returns 80, because Bo's 2024 Mug line S3 (40) joins the "
                "result."
            ),
            (
                "`CALCULATE ( [NetRevenue], Customer[Region] = \"South\", 'Date'[Year] = 2025 )` "
                "returns 40, and 83 + 40 equals case B's 123."
            ),
        ),
        (
            (
                "The region set, the year and the category all apply together. Among 2025 lines, "
                "Paper keeps S4 (27), S5 (20) and S7 (20), so revenue is 67."
            ),
            (
                "Letting the category filter replace the earlier filters returns all-years Paper "
                "revenue of 91, which adds the 2024 lines S1 and S2."
            ),
            (
                'Case B with `Product[Category] = "Paper"` added returns 67, and dropping Paper '
                "returns 123 again."
            ),
        ),
        (
            (
                "North admits customers 10 and 30, Home admits product 3 and 2025 admits S4 to S8. "
                "Only S8 (Cy's Mug, 36) passes all three."
            ),
            (
                "A ledger that writes down only the visible Home slicer predicts 96, because it "
                "forgets the region and year filters on other tables."
            ),
            "The three filters together return 36, the NetAmount of S8.",
        ),
        (
            (
                "A fair comparison uses the same period on both sides: North 83 against South 40 "
                "in 2025, or North 107 against South 80 for all years."
            ),
            (
                "Comparing North 2025 (83) with South all years (80) suggests the regions are "
                "nearly equal, when in the same year North sold about twice as much."
            ),
            (
                "Query both regions under one year filter and expect 83 and 40, then without it "
                "and expect 107 and 80."
            ),
        ),
        (
            (
                "West is a valid Customer member (Di, key 40) with no Sales rows, so the year "
                "makes no difference and revenue is BLANK."
            ),
            (
                "Taking BLANK as a broken relationship or an invalid selection leads to model "
                "changes, when it is simply a population with no facts."
            ),
            (
                "Under West and 2025, COUNTROWS(Customer) returns 1 while `ISEMPTY ( Sales )` "
                "returns TRUE and revenue is BLANK."
            ),
        ),
        (
            (
                "Each number needs its full context written down. A card showing 83 may have a "
                "visible North slicer and a hidden 2025 page filter, and it uses the active "
                "OrderDate relationship."
            ),
            (
                "Documenting only the visible North caption leads a reader to expect 107. "
                "Switching the date role also matters: January 2025 is 67 by order date and 47 by "
                "ship date."
            ),
            (
                "Replaying CALCULATE with every captured filter should reproduce 83; S6, ordered "
                "January 5 and shipped February 1, explains the date-role difference."
            ),
        ),
    ],
    15: [
        (
            (
                'Product[Color] = "Red" replaces the incoming Blue filter on that same column. '
                "Green replaces it the same way, leaving Bag, which has no sales."
            ),
            (
                "Reading BLANK as proof that Blue and Green were intersected is the mistake. The "
                "intersection is also empty, so revenue cannot tell the two rules apart."
            ),
            (
                'Under Blue, `CALCULATE ( COUNTROWS ( Product ), Product[Color] = "Green" )` '
                "returns 1 (Bag), while the KEEPFILTERS version returns BLANK."
            ),
        ),
        (
            (
                "Color and Category are different columns, so the Red filter is added beside "
                "Paper. Only Pen is both, and its lines S2 and S5 give 24."
            ),
            (
                "Offering Red as proof that Paper survived proves nothing, because all-Red revenue "
                "is also 24. Blue is the case that tells them apart: 67 against 163."
            ),
            "Under Paper, CALCULATE with Red returns 24 and COUNTROWS(Product) returns 1.",
        ),
        (
            (
                "CALCULATE([NetRevenue], 'Date'[Year] = 2025) replaces only the year. A "
                "Customer[Region] filter stays, so under North it returns 83."
            ),
            (
                "`CALCULATE ( [NetRevenue], FILTER ( ALL ( Sales ), RELATED ( 'Date'[Year] ) = "
                "2025 ) )` also removes the region filter through ALL(Sales) and returns 123 under "
                "North."
            ),
            "Expect 83 under North, 40 under South and 123 with no region selected.",
        ),
        (
            (
                "CALCULATE replaces filters only on the columns its arguments name. In case B the "
                "Color filter is new, so the incoming Category filter stays."
            ),
            (
                "If CALCULATE cleared every filter, BluePaperRevenue would be all-Blue revenue, "
                "163, and would include the Mug lines."
            ),
            "BluePaperRevenue is 67, the Notebook lines S1 (20), S4 (27) and S7 (20).",
        ),
        (
            (
                "A fixed-color measure answers a fixed question. Named Blue Revenue, it returns "
                "163 under any color slicer, which is right only if readers know it ignores that "
                "selection."
            ),
            (
                "Naming it Revenue and showing 163 under a Red slicer contradicts the user's "
                "choice; an intersection with KEEPFILTERS would return BLANK there."
            ),
            (
                "Under Red, the base measure returns 24, the fixed measure 163 and the KEEPFILTERS "
                "version BLANK."
            ),
        ),
        (
            (
                "For a category share within the current region and year, remove only the category "
                "filter. North 2025 Paper is 47 (S4 and S5) out of 83, about 0.566."
            ),
            (
                "Using ALL or REMOVEFILTERS on everything makes the denominator 187, and Paper's "
                "share drops to about 0.251 of a total outside the selection."
            ),
            (
                "Under North and 2025, Paper is 47 / 83 and Home is 36 / 83, and the two shares "
                "add to 1."
            ),
        ),
    ],
    16: [
        (
            (
                "MAX(Product[ProductKey]) is evaluated in the incoming Paper context, so it "
                "returns 2. Red with key 2 leaves Pen, whose revenue is 24."
            ),
            (
                "Taking 24 as proof that the filters ran from left to right overlooks that Pen is "
                "both the incoming maximum and the only Red Paper product."
            ),
            "The row reads IncomingMaxKey 2 and Revenue 24, from S2 (4) and S5 (20).",
        ),
        (
            (
                "The outer Red filter is applied first, so the inner MAX sees only Pen and returns "
                "2. Revenue is 24, the same as case A with Red."
            ),
            (
                "Assuming the outer Red replaces Paper confuses the columns. Color and Category "
                "differ, so Paper stays, though here both readings happen to give Pen."
            ),
            (
                "Inside the outer Red context COUNTROWS(Product) is 1 and MAX(Product[ProductKey]) "
                "is 2, so revenue is 24."
            ),
        ),
        (
            (
                "Ledger: Paper gives keys {1, 2}; MAX bound there is 2; Blue gives {1, 3}; key 2 "
                "gives {2}. Their intersection with Paper is empty."
            ),
            (
                "A ledger written in argument order, applying Blue before computing MAX, binds key "
                "1 and predicts Notebook's 67, which is case B's answer, not case A's."
            ),
            (
                "Case A returns IncomingMaxKey 2 and Revenue BLANK, which matches the empty "
                "intersection."
            ),
        ),
        (
            (
                "Red returns 24 under both forms, so it cannot show which order is used. Blue can: "
                "the incoming maximum stays 2 in case A, while the nested inner MAX sees {1} in "
                "case B."
            ),
            (
                "Declaring the forms equivalent after one passing Red test treats agreement on one "
                "input as proof for all inputs."
            ),
            "Run both forms with Blue and expect BLANK for case A and 67 for case B.",
        ),
        (
            (
                "A variable is evaluated where it is defined. `VAR K = MAX ( Product[ProductKey] "
                ")` under Paper binds 2 before the outer Blue filter exists."
            ),
            (
                "Moving the MAX into a variable to tidy case B brings back the bug, because the "
                "inner filter then uses the stored 2 rather than the key under Blue."
            ),
            (
                "The variable version returns BLANK under Paper, while the nested form with MAX "
                "inline returns 67."
            ),
        ),
        (
            (
                "Find the last Paper sale date inside the Paper filter. Paper's last order is S7 "
                "on 2025-02-02, worth 20."
            ),
            (
                "Computing MAX(Sales[OrderDate]) as a sibling of the Paper filter evaluates it "
                "over all sales, which gives 2025-02-03, the date of the Mug line S8, so the "
                "result is BLANK."
            ),
            (
                "Nested as `CALCULATE ( CALCULATE ( [NetRevenue], 'Date'[Date] = MAX ( "
                'Sales[OrderDate] ) ), Product[Category] = "Paper" )`, expect 20.'
            ),
        ),
    ],
    17: [
        (
            (
                "Under Paper, SUMX visits five lines. A raw SUM inside sees the whole Paper "
                "context each time and returns 91, so the result is 5 x 91 = 455."
            ),
            (
                "Thinking the raw SUM sees only the current line, as a SQL row expression would, "
                "predicts 91. The transition is what makes that true."
            ),
            "Under Paper, RawRepeated returns 455 and Transitioned returns 91.",
        ),
        (
            (
                "[NetRevenue] includes an implicit CALCULATE, so each line becomes a filter on its "
                "own unique SaleID and contributes only its NetAmount. The total stays 187."
            ),
            (
                "Expecting the measure to act like the raw SUM and return 1,496 forgets that "
                "measure references always transition."
            ),
            (
                "`SUMX ( Sales, [NetRevenue] )` returns 187, while the raw version returns 1,496, "
                "which is 8 x 187."
            ),
        ),
        (
            (
                "NetAmount is stored per line and adds up across lines, so SUM(Sales[NetAmount]) "
                "gives 187 with no iterator and no transitions."
            ),
            (
                "Keeping SUMX(Sales, [NetRevenue]) runs eight transitions to get the same 187, and "
                "it would overcount if two rows were identical (see the fifth exercise)."
            ),
            "SUM(Sales[NetAmount]) and SUMX(Sales, Sales[NetAmount]) both return 187.",
        ),
        (
            (
                "Dividing by the row count happens to work here, because the raw SUMX adds the "
                "total once per row. It does not give per-row values."
            ),
            (
                "Applied to a Customer iteration, the patch still shows 187 for each customer, and "
                "SUMX(Customer, SUM(Sales[NetAmount])) / COUNTROWS(Sales) returns 748 / 8 = 93.5."
            ),
            (
                "Per customer, [NetRevenue] returns Ada 51, Bo 80, Cy 56 and Di BLANK; the patched "
                "expression cannot produce those."
            ),
        ),
        (
            (
                "A transition filters on every column's value, not on a physical row. SaleID is "
                "unique today, so each line matches only itself."
            ),
            (
                "If S5 were loaded twice with identical values, SUM would give 207, but "
                "SUMX(Sales, [NetRevenue]) would give 247, because each copy matches both copies "
                "(40 twice)."
            ),
            (
                "Before relying on transitions, check that COUNTROWS(Sales) equals "
                "DISTINCTCOUNT(Sales[SaleID]); both are 8 here."
            ),
        ),
        (
            (
                "To split a 100 USD charge by revenue, transition each customer with [NetRevenue] "
                "and divide by 187 bound outside the iterator: Ada gets about 27.27, Bo 42.78 and "
                "Cy 29.95."
            ),
            (
                "A raw SUM inside SUMX(Customer, ...) gives every customer a share of 187 / 187 = "
                "1, which allocates the full 100 to each of four customers."
            ),
            "The allocations should add to 100, and Di, with no sales, should receive BLANK.",
        ),
    ],
    18: [
        (
            (
                "FILTER evaluates [NetRevenue] once per ProductKey. Notebook (67) and Mug (96) "
                "exceed 24, while Pen equals 24 and Bag is BLANK, so revenue is 163."
            ),
            (
                "Filtering lines with Sales[NetAmount] > 24 answers a different question. It keeps "
                "S3, S4 and S8 for 103, because it tests lines, not product totals."
            ),
            "The candidate table has 2 rows and CALCULATE over it returns 163.",
        ),
        (
            (
                "With >= 24, Pen's 24 also qualifies. Bag's BLANK compares as 0, which is below "
                "24, so three products qualify and revenue is 187."
            ),
            (
                "Lowering the threshold to >= 0 would also admit Bag, because BLANK >= 0 is TRUE, "
                "so a product with no sales would join the list."
            ),
            "Expect Products 3 and Revenue 187, and check that Bag is not in the list.",
        ),
        (
            (
                "Iterate VALUES(Customer[CustomerKey]) and invoke [NetRevenue] per key. Bo (80) "
                "and Cy (56) exceed 55, Ada (51) does not and Di is BLANK."
            ),
            (
                "`FILTER ( Sales, Sales[NetAmount] > 55 )` checks single lines, and the largest "
                "line is 40, so the result is BLANK."
            ),
            "Expect 2 customers with revenue 80 + 56 = 136.",
        ),
        (
            (
                "A simple Boolean filter in CALCULATE must test a column. FILTER over "
                "VALUES(Product[ProductKey]) gives the measure one product context per candidate."
            ),
            (
                "`FILTER ( Sales, [NetRevenue] > 50 )` runs but transitions to single lines, and "
                "since no line exceeds 50 it returns an empty table and BLANK."
            ),
            "The ProductKey candidate version returns 2 products and 163, as in case A.",
        ),
        (
            (
                "Mug's 96 is the largest product total, so a threshold of 100 leaves the candidate "
                "table empty. CALCULATE with an empty filter table sees no rows."
            ),
            (
                "Assuming an empty filter means no filter predicts 187. It actually admits no "
                "products, so revenue is BLANK."
            ),
            "At > 100 the row should read Products BLANK and Revenue BLANK.",
        ),
        (
            (
                "State the period and the candidates. Under 2025, Ada has 27, Bo 40 and Cy 56, so "
                "only Cy exceeds 50. Over all years, Ada (51), Bo (80) and Cy (56) all do."
            ),
            (
                "Building the segment over all years but reporting it in a 2025 view labels Ada "
                "high value, though her 2025 revenue is 27."
            ),
            (
                "Under 2025 the FILTER returns Cy alone with 56; with no year filter it returns "
                "three customers and 187."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

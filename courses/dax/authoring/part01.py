"""Stage one: explain the model and the question before manipulating context."""

from .common import lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        1,
        "A semantic model, a question and a worked result",
        ["semantic model", "fact", "dimension", "measure", "query"],
        ("Explain what a revenue number means by identifying the model, grain and eligible rows."),
        (
            "A semantic model is a set of typed tables, relationships "
            "and calculation definitions. It is not the report "
            "picture. A visual asks the model a question; a measure "
            "gives a scalar answer for the question's current context. "
            "A query can ask for a table of such answers. Keeping "
            "these objects separate prevents a common beginner "
            "mistake: treating a number on a page as if it were stored "
            "in the formula itself.\n\nOur synthetic retailer records "
            "one order line per Sales row. NetAmount is Quantity times "
            "UnitPrice minus a discount for the entire line. Every "
            "ordinary retail amount is USD. Product and Customer "
            "describe the keys on those lines. The complete Date table "
            "describes calendar days. The eight lines total 187, but "
            "that number alone does not tell us whether returns, tax "
            "or an unobserved month belong in the question. Here tax "
            "and refunds are excluded by the fixture contract.\n\nThis "
            "classroom provides source editing, saved notes and fixed "
            "worked references. It does not host a semantic-model "
            "engine. The two result tables below explain this exact "
            "reference and fixture. Change your draft to explore an "
            "idea, then compare your reasoning with the explanation; "
            "the displayed numbers do not change into results of your "
            "edit. This distinction is part of learning reproducible "
            "analysis, not a temporary missing compiler."
        ),
        (
            "Read the reference from its declarations to its query. "
            "DEFINE MEASURE introduces a query-local measure named "
            "NetRevenue on Sales. SUM accepts one numeric column and "
            "adds its eligible values. EVALUATE expects a table, so "
            "ROW wraps a scalar in a one-row table with a named output "
            "column. Case B uses CALCULATETABLE to give that same "
            "question an explicit ProductKey filter. Its detailed "
            "context rules arrive in stage three; here trace the "
            "selected rows first."
        ),
        [
            r(
                "All eight lines",
                'EVALUATE ROW ( "NetRevenue", [NetRevenue] )',
                [("NetRevenue", "number")],
                [[187]],
                "No filters; regular active relationships; USD sales-line grain.",
                [
                    "Eligible lines are S1 through S8.",
                    "Add 20 + 4 + 40 + 27 + 20 + 20 + 20 + 36.",
                    "The total is 187 USD before returns and tax.",
                ],
                (
                    "The answer is attached to a defined population of lines. "
                    "It is not proof that every business revenue policy has "
                    "been represented. Changing the question to refunded "
                    "revenue would require another fact or calculation."
                ),
            ),
            r(
                "Notebook product only",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "NetRevenue", '
                    "[NetRevenue] ), Product[ProductKey] = 1 )"
                ),
                [("NetRevenue", "number")],
                [[67]],
                ("ProductKey 1; the Product-to-Sales relationship is active and single-direction."),
                [
                    "ProductKey 1 identifies Notebook, not all products in the Paper category.",
                    "The key filter admits Sales S1, S4 and S7.",
                    "20 + 27 + 20 = 67 USD.",
                ],
                (
                    "The measure text did not change. Its eligible rows did. A "
                    "report selection must be part of the explanation whenever "
                    "someone compares this 67 with the overall 187."
                ),
            ),
        ],
        [
            t(
                "Predict the all-line quantity alongside revenue.",
                "Add the Quantity column, not the distinct products.",
                "Quantity is 17; revenue is 187 USD. Their units differ.",
            ),
            t(
                (
                    "Change the product question from Notebook to Mug and list "
                    "the contributing lines."
                ),
                "Find ProductKey 3 before adding amounts.",
                "S3, S6 and S8 contribute 40 + 20 + 36 = 96.",
            ),
            t(
                "Write a one-row query that names the output QuantitySold.",
                "ROW supplies the table; SUM supplies a scalar.",
                'EVALUATE ROW ( "QuantitySold", SUM ( Sales[Quantity] ) ) gives 17.',
            ),
            t(
                "Diagnose a report labeled net profit that displays 187.",
                "Identify the deductions actually represented.",
                (
                    "The fixture total is sales after line discounts, before "
                    "cost, returns and tax. Profit is a different measure."
                ),
            ),
            t(
                ("Explain what happens in this classroom after editing 187 into a draft comment."),
                "Separate a saved source file from a derived result.",
                (
                    "Only the draft changes. The hand-derived reference table "
                    "remains bound to the reference file and model."
                ),
            ),
            t(
                "Describe the evidence needed to call an exported formula engine-tested.",
                "A source file and a calculation result are different artifacts.",
                (
                    "Record the actual engine/version, model, filter context, "
                    "exact submitted source and observed output. Offline "
                    "comparison supplies none of those execution observations."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/dax-overview",
            "https://learn.microsoft.com/en-us/dax/dax-queries",
        ],
    ),
    lesson(
        2,
        "Grain, keys and why rows are not orders",
        ["grain", "key", "order line", "distinct count", "unit"],
        ("Distinguish sales lines, orders and customers before selecting an aggregation."),
        (
            "Grain is the claim made by one row. Sales has a unique "
            "SaleID, while OrderID can occur on several lines. Order "
            "101 contains a notebook and a pen, so counting rows "
            "answers how many lines were recorded, not how many orders "
            "were placed. A correct arithmetic operation on the wrong "
            "unit still produces the wrong metric.\n\nA key identifies "
            "the row at its declared grain. The fact's foreign keys "
            "identify dimensions that describe it; they are not "
            "alternate unique keys for the fact. ProductKey repeats "
            "because the same product can be sold again. CustomerKey "
            "repeats because one customer can place several orders. A "
            "transaction table that accidentally repeats the same "
            "SaleID violates the model even if the repeated quantities "
            "look plausible.\n\nBefore writing a measure, finish the "
            "sentence 'one observation represents ...'. Then state "
            "whether the metric is additive across the intended "
            "groups. Line quantity is additive across disjoint line "
            "sets. Distinct orders can span product groups, so summing "
            "per-product order counts can double-count a multi-product "
            "order. Later totals lessons build on this grain "
            "distinction."
        ),
        (
            "COUNTROWS receives a table and counts eligible rows. "
            "DISTINCTCOUNT receives one column and counts distinct "
            "values in that column, including BLANK if present. Our "
            "OrderID values are complete. NetRevenue remains an "
            "amount, so a row count, an order count and revenue should "
            "use different names rather than one ambiguous 'total'."
        ),
        [
            r(
                "Whole model counts",
                (
                    'EVALUATE ROW ( "Lines", COUNTROWS ( Sales ), "Orders", '
                    'DISTINCTCOUNT ( Sales[OrderID] ), "Revenue", [NetRevenue] '
                    ")"
                ),
                [("Lines", "integer"), ("Orders", "integer"), ("Revenue", "number")],
                [[8, 7, 187]],
                "All Sales rows; one row per SaleID.",
                [
                    "S1 and S2 share OrderID 101.",
                    "Seven distinct order identifiers remain after counting 101 once.",
                    "Revenue still includes both legitimate lines of that order.",
                ],
                (
                    "Deduplicating entire orders before summing their lines "
                    "would lose a product, while counting every line as an "
                    "order overstates order count. The aggregation must match "
                    "the question rather than flatten every metric to one "
                    "grain."
                ),
            ),
            r(
                "One multi-line order",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Lines", COUNTROWS ( '
                    'Sales ), "Orders", DISTINCTCOUNT ( Sales[OrderID] ), '
                    '"Revenue", [NetRevenue] ), Sales[OrderID] = 101 )'
                ),
                [("Lines", "integer"), ("Orders", "integer"), ("Revenue", "number")],
                [[2, 1, 24]],
                "OrderID 101 only; both matching fact rows retained.",
                [
                    "S1 contributes Notebook quantity 2 and amount 20.",
                    "S2 contributes Pen quantity 1 and amount 4.",
                    "The order has two lines, one identity and revenue 24.",
                ],
                (
                    "This small order is a counterexample to the claim that "
                    "line count equals order count. Keep it as a fixture when "
                    "a later model refactor changes joins or grouping."
                ),
            ),
        ],
        [
            t(
                "Predict distinct customers with sales.",
                "Read CustomerKey from Sales rather than counting the dimension.",
                (
                    "The keys are 10, 20 and 30: three customers with sales, "
                    "although the Customer table has four rows."
                ),
            ),
            t(
                "Explain the result if S2 is duplicated with the same SaleID.",
                "Check both row identity and additive amounts.",
                (
                    "The row count and revenue rise incorrectly; the unique "
                    "SaleID contract fails. DISTINCTCOUNT(OrderID) alone would "
                    "conceal the duplicate."
                ),
            ),
            t(
                "Write the average revenue per order measure.",
                "Use a ratio of totals and a safe denominator.",
                (
                    "DIVIDE ( [NetRevenue], [OrderCount] ) is 187 / 7 for the "
                    "whole model and 24 for order 101."
                ),
            ),
            t(
                "Diagnose summing per-product order counts.",
                "Order 101 belongs to two products.",
                (
                    "The per-product counts are 3, 2 and 3, summing to 8, "
                    "while overall distinct orders are 7."
                ),
            ),
            t(
                "State a policy for a missing order identifier.",
                "DISTINCTCOUNT does not silently discard BLANK.",
                (
                    "Decide whether to reject the row, show an unknown-order "
                    "bucket or use DISTINCTCOUNTNOBLANK with an explicit "
                    "exclusion. Do not call a blank identifier a known order."
                ),
            ),
            t(
                (
                    "Transfer the grain question to a hospital visit table "
                    "with several charge lines."
                ),
                "Separate visit identity from charge-line identity.",
                (
                    "Count distinct visit IDs for visits, sum charge amounts "
                    "for billed charges and preserve a separate unique line "
                    "key."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/countrows-function-dax",
            "https://learn.microsoft.com/en-us/dax/distinctcount-function-dax",
        ],
    ),
    lesson(
        3,
        "A star schema and the path of a filter",
        ["star schema", "dimension", "foreign key", "filter propagation"],
        (
            "Trace a dimension selection through an active "
            "relationship to the exact contributing fact rows."
        ),
        (
            "A star schema separates descriptive dimensions from event "
            "facts. A product category is described once per product; "
            "transaction rows keep the corresponding product key. A "
            "filter on the dimension first restricts its visible keys, "
            "then an active relationship propagates those keys to the "
            "fact. It does not physically create a permanent joined "
            "copy of both tables.\n\nOur model uses regular one-to-many "
            "relationships with filters flowing from Product and "
            "Customer into Sales. Paper admits ProductKey 1 and 2. "
            "North admits CustomerKey 10 and 30. Applying both "
            "selections means a sales line must satisfy both sets. The "
            "filters intersect at the fact; two slicers do not mean "
            "'Paper OR North' unless an expression explicitly defines "
            "that different question.\n\nModel design is already part of "
            "calculation design. If a category is copied "
            "inconsistently into different sales rows, a filter on "
            "that fact attribute can answer a different question than "
            "the dimension's current category. Historical "
            "classification may be a legitimate requirement, but it "
            "needs a declared versioned dimension or event-time "
            "attribute. Do not hide that decision in an unexplained "
            "formula."
        ),
        (
            "CALCULATETABLE supplies the stated filters around a "
            "one-row result table. Product[Category] and "
            "Customer[Region] are column references with table "
            "qualification. Two filter arguments are applied together. "
            "The relationship metadata, not a textual resemblance "
            "between column names, determines which Sales rows they "
            "reach."
        ),
        [
            r(
                "Paper products",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue] '
                    '), Product[Category] = "Paper" )'
                ),
                [("Revenue", "number")],
                [[91]],
                "Product.Category = Paper; other dimensions unrestricted.",
                [
                    "Paper maps to product keys 1 and 2.",
                    "Eligible lines are S1, S2, S4, S5 and S7.",
                    "20 + 4 + 27 + 20 + 20 = 91.",
                ],
                (
                    "The result includes several customers and years. A "
                    "category selection does not implicitly select the latest "
                    "year or a region."
                ),
            ),
            r(
                "Paper in the North",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue] '
                    '), Product[Category] = "Paper", Customer[Region] = '
                    '"North" )'
                ),
                [("Revenue", "number")],
                [[71]],
                "Product.Category = Paper AND Customer.Region = North.",
                [
                    "North admits customer keys 10 and 30.",
                    "Intersect those customers with Paper's product keys.",
                    "S7 is excluded because customer 20 is South; 91 - 20 = 71.",
                ],
                (
                    "A relationship graph plus eligible-row list explains the "
                    "reduction without guessing which visual control caused "
                    "it. Both filters remain part of the measure's question."
                ),
            ),
        ],
        [
            t(
                "Predict Home revenue in North.",
                "Intersect ProductKey 3 with customers 10 and 30.",
                "Only S8 remains, so revenue is 36.",
            ),
            t(
                "Change Paper to Home while leaving North selected.",
                "Only the product filter changes.",
                ("The customer filter remains; the result is 36 rather than all-Home revenue 96."),
            ),
            t(
                "Draw the two paths that meet at Sales.",
                "Use arrows for filter direction, not SQL join syntax.",
                (
                    "Product.ProductKey -> Sales.ProductKey and "
                    "Customer.CustomerKey -> Sales.CustomerKey, each "
                    "one-to-many and active."
                ),
            ),
            t(
                "Diagnose a report that adds 91 and 107 to represent Paper-and-North revenue.",
                "Those populations overlap.",
                (
                    "91 + 107 counts the overlap twice and includes other "
                    "rows. The intersection revenue is 71."
                ),
            ),
            t(
                "Predict a selection of West customers.",
                "Customer 40 has no Sales rows.",
                (
                    "SUM over the empty eligible set is BLANK, not evidence of "
                    "a missing West dimension row."
                ),
            ),
            t(
                "Explain how an event-time customer region requirement changes the model.",
                "Current customer attributes are not automatically historical attributes.",
                (
                    "Use a documented historical key or event-time "
                    "classification. Repeatedly changing a current Region "
                    "label can rewrite historical report membership."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema",
            (
                "https://learn.microsoft.com/en-us/power-bi/transform-model"
                "/desktop-relationships-understand"
            ),
        ],
    ),
    lesson(
        4,
        "Relationships are filter rules, not materialized joins",
        ["relationship direction", "one side", "many side", "relationship versus join"],
        ("Predict asymmetric filter propagation and identify when a SQL join analogy breaks."),
        (
            "A relationship connects typed columns and declares "
            "cardinality, active status and filter direction. The "
            "engine uses it when determining eligible rows. It does "
            "not promise that selecting any fact row will also shrink "
            "every connected dimension. In our single-direction star, "
            "a Product selection filters Sales, but a direct Sales "
            "filter does not flow backward to Product.\n\nThat asymmetry "
            "is useful: dimensions remain stable descriptive "
            "populations while facts record activity. Counting "
            "products in the Product table answers how many dimension "
            "products remain visible; it does not necessarily count "
            "products sold in the currently filtered fact rows. For "
            "products actually sold, count Sales[ProductKey] or "
            "deliberately construct the matching set.\n\nA materialized "
            "SQL join has different mechanics. A duplicate dimension "
            "key can multiply joined fact rows, while a regular "
            "one-to-many model relationship requires uniqueness on its "
            "one side. Missing foreign keys can create an engine blank "
            "member rather than the same rows returned by a naive "
            "inner join. Use SQL as an independent arithmetic check "
            "only after aligning the population and missing-key policy."
        ),
        (
            "The paired queries count Product and Sales in the same "
            "outer context. COUNTROWS(Product) is not a measure of "
            "sales activity. Filtering Sales[SaleID] leaves Product's "
            "single-direction incoming eligibility unchanged. "
            "Bidirectional filtering would change this behavior and "
            "can introduce ambiguous paths, so do not enable it merely "
            "to make one number look convenient."
        ),
        [
            r(
                "Dimension-to-fact propagation",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "VisibleProducts", '
                    'COUNTROWS ( Product ), "Lines", COUNTROWS ( Sales ), '
                    '"Revenue", [NetRevenue] ), Product[Color] = "Blue" )'
                ),
                [("VisibleProducts", "integer"), ("Lines", "integer"), ("Revenue", "number")],
                [[2, 6, 163]],
                "Blue Product rows; active Product -> Sales direction.",
                [
                    "Notebook and Mug are Blue.",
                    "Their keys admit six sales lines.",
                    "Product count is 2; their revenues 67 and 96 sum to 163.",
                ],
                (
                    "The selected dimension supplies a key set that travels to "
                    "the fact. It is not inferred from which products happen "
                    "to have sales in another visual."
                ),
            ),
            r(
                "Fact filter does not flow backward",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "VisibleProducts", '
                    'COUNTROWS ( Product ), "Lines", COUNTROWS ( Sales ), '
                    '"Revenue", [NetRevenue] ), Sales[SaleID] = "S4" )'
                ),
                [("VisibleProducts", "integer"), ("Lines", "integer"), ("Revenue", "number")],
                [[4, 1, 27]],
                (
                    "Direct filter Sales.SaleID = S4; no Product filter; "
                    "single-direction relationships."
                ),
                [
                    "Sales is reduced to S4.",
                    "The relationship does not propagate from its many side to Product.",
                    "All four Product rows remain visible, even though S4 uses only product 1.",
                ],
                (
                    "A product-count card showing four is consistent with the "
                    "declared model. The mistake would be naming that count "
                    "'products sold in this line'."
                ),
            ),
        ],
        [
            t(
                "Predict DISTINCTCOUNT(Sales[ProductKey]) in the S4 context.",
                "Count keys in the filtered fact.",
                "It is 1, unlike COUNTROWS(Product), which is 4.",
            ),
            t(
                "Predict the all-model product count and products-with-sales count.",
                "Bag has no sales.",
                "The dimension has four products, while Sales contains three product keys.",
            ),
            t(
                "Write a query returning both populations with unambiguous labels.",
                "Place both scalar counts in ROW.",
                (
                    'Use ROW("CatalogProducts",COUNTROWS(Product),"SoldProducts'
                    '",DISTINCTCOUNT(Sales[ProductKey])).'
                ),
            ),
            t(
                "Diagnose a proposed bidirectional fix for every empty report cell.",
                "A change in model semantics affects more than that cell.",
                (
                    "Review path ambiguity and intended populations first. An "
                    "explicit measure can be preferable to changing every "
                    "filter path."
                ),
            ),
            t(
                "Explain why a duplicate ProductKey is not solved by sorting the dimension.",
                "The one-side uniqueness requirement concerns identity.",
                (
                    "Sorting changes display order, not duplicate keys. Repair "
                    "the key or model the legitimate lower grain."
                ),
            ),
            t(
                "Compare an inner SQL join with this model when a sales key has no product.",
                "An inner join removes the unmatched event.",
                (
                    "Regular-model blank-member behavior can retain its "
                    "amount. Match missing-key policy before using the join as "
                    "an oracle."
                ),
            ),
        ],
        sources=[
            (
                "https://learn.microsoft.com/en-us/power-bi/transform-model"
                "/desktop-relationships-understand"
            )
        ],
    ),
    lesson(
        5,
        "DAX query shape, names and deterministic result tables",
        ["EVALUATE", "ROW", "SELECTCOLUMNS", "TOPN", "ORDER BY"],
        (
            "Distinguish scalar expressions, table expressions and "
            "named model measures in a readable query."
        ),
        (
            "A DAX query returns tables. EVALUATE introduces a table "
            "expression; a scalar such as SUM(Sales[NetAmount]) is not "
            "itself a result table. ROW creates one named row from "
            "scalar expressions, while SELECTCOLUMNS projects names "
            "and expressions over rows of an input table. This shape "
            "distinction explains many apparent syntax problems before "
            "a learner memorizes more functions.\n\nA column reference "
            "such as Sales[NetAmount] identifies a column. A measure "
            "reference such as [NetRevenue] requests a scalar "
            "evaluation in the current context. Double quotes delimit "
            "text such as output labels. Single quotes delimit table "
            "names when needed, as in 'Date'[Date]. Square brackets "
            "delimit identifiers; they are not Python list "
            "indexing.\n\nDo not infer ordering from a table "
            "expression's internal implementation. TOPN chooses a set "
            "according to ordering criteria, while an outer ORDER BY "
            "specifies the presentation of the returned query table. "
            "Use a unique tie-breaker when a stable top set matters. "
            "Choosing a table and presenting its rows are separate "
            "obligations."
        ),
        (
            "The first query uses a label/value pair in ROW. The "
            "second takes the first two unique SaleID values, projects "
            "them as Line and Amount, and orders the final table by "
            "Line. These are small inspectable query objects; they do "
            "not persist calculated tables in the semantic model."
        ),
        [
            r(
                "A scalar wrapped as a table",
                'EVALUATE ROW ( "RevenueUSD", [NetRevenue] )',
                [("RevenueUSD", "number")],
                [[187]],
                "No filters; one named scalar in a one-row query result.",
                [
                    "SUM produces one scalar in the current context.",
                    "ROW assigns that scalar the output name RevenueUSD.",
                    "EVALUATE returns the one-row table, not a stored model column.",
                ],
                (
                    "Output aliases belong to this query. Renaming RevenueUSD "
                    "does not rename the NetRevenue measure or change its "
                    "arithmetic."
                ),
            ),
            r(
                "A projected two-row result",
                (
                    "EVALUATE\nSELECTCOLUMNS ( TOPN ( 2, Sales, Sales[SaleID], "
                    'ASC ), "Line", Sales[SaleID], "Amount", Sales[NetAmount] '
                    ")\nORDER BY [Line] ASC"
                ),
                [("Line", "text"), ("Amount", "number")],
                [["S1", 20], ["S2", 4]],
                ("No filters; smallest two unique SaleID values, then explicit output ordering."),
                [
                    "SaleID is unique, so the two smallest keys select exactly S1 and S2.",
                    "SELECTCOLUMNS evaluates each projected expression for its input row.",
                    "The outer ORDER BY makes the displayed sequence S1 then S2.",
                ],
                (
                    "The result is two rows because the input selection has "
                    "two rows. It is not a sum and not a measure definition. "
                    "The amount column retains each line's value."
                ),
            ),
        ],
        [
            t(
                "Repair EVALUATE SUM(Sales[NetAmount]).",
                "Identify which argument needs table shape.",
                'Wrap the scalar: EVALUATE ROW("Revenue",SUM(Sales[NetAmount])).',
            ),
            t(
                "Change the projection to include Quantity.",
                "Add a new output-name/expression pair.",
                (
                    "The first two rows have quantities 2 and 1; keep Amount "
                    "rather than replacing it silently."
                ),
            ),
            t(
                "Write a query returning three rows in descending SaleID order.",
                "Selection and final ordering both need a direction.",
                (
                    "TOPN(3,Sales,Sales[SaleID],DESC) chooses S8,S7,S6; an "
                    "outer ORDER BY makes that display order explicit."
                ),
            ),
            t(
                ("Diagnose the name RevenueUSD being used as a measure in a later separate query."),
                "A result alias is not a persisted measure.",
                (
                    "Define a measure or reconstruct the query. An alias in "
                    "one returned table does not install model metadata."
                ),
            ),
            t(
                "Predict what changes if TOPN orders only by a tied amount.",
                "Rows at the cutoff can share the ordering value.",
                (
                    "More than N rows can be returned at a tie; add a unique "
                    "key if an exact-sized selection is the intended contract."
                ),
            ),
            t(
                "Explain how a query differs from a calculated table.",
                "Ask when the rows are produced and retained.",
                (
                    "A query returns a requested table now; a calculated table "
                    "is model content computed during processing and used "
                    "later."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/dax-queries",
            "https://learn.microsoft.com/en-us/dax/selectcolumns-function-dax",
            "https://learn.microsoft.com/en-us/dax/topn-function-dax",
        ],
    ),
    lesson(
        6,
        "Model quality capstone: duplicates, missing keys and unknown members",
        ["referential integrity", "duplicate key", "unknown member", "model validation"],
        (
            "Produce a model-quality ledger that separates an invalid "
            "dimension key from an unmatched fact key."
        ),
        (
            "A model-quality review starts with grain and identity, "
            "not a large measure catalog. A duplicate key on the one "
            "side prevents the intended regular one-to-many "
            "relationship. It is not a reason to arbitrarily choose "
            "one descriptive row. An unmatched foreign key is a "
            "different defect: a regular relationship can represent "
            "unmatched facts through a synthetic blank member on the "
            "dimension side.\n\nThis lesson uses the named "
            "unknown-member fixture, which adds S9 with ProductKey 999 "
            "and amount 7. Product still contains keys 1 through 4. "
            "The unmatched amount must remain visible in a "
            "reconciliation: known products contribute 187 and the "
            "unmatched line contributes 7, so total sales are 194. "
            "Hiding the unknown bucket would make a catalog report "
            "disagree with the fact total.\n\nThe first worked case "
            "builds a deliberately duplicated diagnostic table inside "
            "the query. It does not claim that an invalid one-side "
            "relationship was loaded successfully. The second case "
            "inspects the actual missing key. Record a disposition for "
            "each issue: repair upstream identity, establish a "
            "legitimate composite grain, or explicitly expose unknown "
            "facts. Do not confuse a model-design decision with an "
            "engine execution receipt."
        ),
        (
            "DATATABLE introduces a literal typed table for the "
            "duplicate diagnostic. SELECTCOLUMNS projects just the key "
            "before DISTINCT counts it. EXCEPT returns values in its "
            "first table that are absent from the second. The "
            "comparison uses raw fact ProductKey values and DISTINCT "
            "over stored dimension keys, so the missing code 999 is "
            "visible."
        ),
        [
            r(
                "A duplicate-key diagnostic, not a loaded dimension",
                (
                    'EVALUATE\nVAR Candidate = DATATABLE ( "Key", INTEGER, '
                    '"Label", STRING, { { 1, "Notebook" }, { 1, "Other label" '
                    '}, { 2, "Pen" } } )\nRETURN ROW ( "Rows", COUNTROWS ( '
                    'Candidate ), "UniqueKeys", COUNTROWS ( DISTINCT ( '
                    'SELECTCOLUMNS ( Candidate, "Key", [Key] ) ) ) )'
                ),
                [("Rows", "integer"), ("UniqueKeys", "integer")],
                [[3, 2]],
                "A query-local candidate table; it is not related to Sales.",
                [
                    "The candidate contains keys 1, 1 and 2.",
                    "Projecting Key then taking DISTINCT leaves 1 and 2.",
                    "Three rows and two keys prove the one-row-per-key contract fails.",
                ],
                (
                    "This diagnostic explains why the intended dimension "
                    "cannot be accepted as unique. Summing its labels or "
                    "choosing the first row is not a principled repair."
                ),
            ),
            r(
                "An unmatched fact key",
                (
                    "EVALUATE EXCEPT ( VALUES ( Sales[ProductKey] ), DISTINCT "
                    "( Product[ProductKey] ) )"
                ),
                [("ProductKey", "integer")],
                [[999]],
                "Unknown-member model; no filters; S9 references absent ProductKey 999.",
                [
                    "Fact keys are 1, 2, 3 and 999.",
                    "Stored Product keys are 1, 2, 3 and 4.",
                    "The fact-minus-dimension set contains only 999.",
                ],
                (
                    "An unmatched key is not the same as an absent fact. S9 "
                    "still represents seven dollars of recorded activity, "
                    "subject to the explicit unknown-member policy."
                ),
            ),
        ],
        [
            t(
                "Reconcile all amounts after adding S9.",
                "Add the unmatched amount without discarding valid lines.",
                (
                    "Known products contribute 187, unknown product 7, and the "
                    "whole fact total is 194."
                ),
            ),
            t(
                "Predict the missing-key result after adding a valid Product row for key 999.",
                "The key would exist on both sides.",
                (
                    "EXCEPT would return an empty table. Descriptive "
                    "attributes and uniqueness still need review."
                ),
            ),
            t(
                "Write an issue ledger with type, evidence and disposition.",
                "Separate duplicate identity from missing membership.",
                (
                    "Record duplicate key 1 in the candidate as a uniqueness "
                    "failure, and key 999 in Sales as unmatched membership; "
                    "each needs a distinct upstream/model decision."
                ),
            ),
            t(
                "Diagnose removing S9 solely to make category totals match.",
                "A matching total can conceal an excluded population.",
                (
                    "That deletes recorded activity from the report rather "
                    "than repairing its classification. Expose exclusions and "
                    "reconcile the retained population."
                ),
            ),
            t(
                "Explain the role of ProductKey 4, which has no sales.",
                "A dimension member can exist without a matching fact.",
                (
                    "It is a valid unsold product, not an unmatched fact key "
                    "or a duplicate dimension row."
                ),
            ),
            t(
                "Transfer the review to assignments and exposure events in an experiment.",
                "Identify the assigned unit separately from repeated events.",
                (
                    "Check assignment uniqueness and exposure foreign keys; "
                    "repeated exposure events do not become extra independent "
                    "randomized units."
                ),
            ),
        ],
        model="unknown-member",
        sources=[
            "https://learn.microsoft.com/en-us/dax/except-function-dax",
            "https://learn.microsoft.com/en-us/dax/values-function-dax",
            (
                "https://learn.microsoft.com/en-us/power-bi/transform-model"
                "/desktop-relationships-understand"
            ),
        ],
    ),
]

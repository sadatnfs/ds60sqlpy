"Lesson-specific study notes that replace the shared routine in each guide and solution."

FOCUS = {
    "dax-001": {
        "draft": (
            "The starter returns a one-row table whose two columns, visible sales lines and "
            "net revenue, are still BLANK. Before opening anything else, predict both numbers"
            " for the whole retail fixture and name the grain each one counts."
        ),
        "model": (
            "Both cases read only Sales, plus the active Product relationship for the "
            "Notebook slice. NetAmount already includes the line discount, so the 187 USD "
            "total is a sum of eight stored line amounts, and selecting ProductKey 1 leaves "
            "S1, S4 and S7."
        ),
        "misconception": (
            "A tempting belief is that the NetRevenue measure stores the value 187, so the "
            "Notebook figure of 67 must come from a different formula. Both cases evaluate "
            "the same definition. What differs is the set of eligible lines: eight in the "
            "first case, three in the second. If you edit the measure text, both numbers can "
            "change; if you change only the selection, the text stays fixed and only the "
            "contributing rows move."
        ),
        "check": (
            "Pick the Mug (ProductKey 3) and list its lines, amounts and total before "
            "checking practice item 2. Then write one sentence explaining why 96 and 67 "
            "cannot be added to recover 187 without the Pen lines S2 and S5."
        ),
        "reference": (
            "The reference defines NetRevenue once and reuses it in both cases, so the only "
            "difference between 187 and 67 is the filter argument. Confirm that your draft "
            "names its outputs and states USD as the unit."
        ),
    },
    "dax-002": {
        "draft": (
            "The starter asks for two numbers that beginners often treat as one: order lines "
            "and distinct orders. Predict both for the full fixture by reading the SaleID and"
            " OrderID columns, and write down which column decides each count."
        ),
        "model": (
            "Only the Sales table matters here. SaleID is unique per row, while OrderID 101 "
            "repeats on S1 and S2. ProductKey and CustomerKey also repeat, which is expected "
            "for foreign keys and says nothing about whether the fact is valid."
        ),
        "misconception": (
            "Many first drafts assume that COUNTROWS(Sales) counts orders because each row "
            "looks like a purchase. The fixture contradicts this directly: eight rows but "
            "only seven distinct OrderID values, because order 101 carries a Notebook line of"
            " 20 USD and a Pen line of 4 USD. Revenue does not have this problem, since "
            "NetAmount is additive across lines, so the same 24 USD appears whether you sum "
            "by line or by order. The repair is to choose the aggregation from the unit named"
            " in the question: lines use COUNTROWS, orders use DISTINCTCOUNT over OrderID, "
            "and customers use DISTINCTCOUNT over CustomerKey."
        ),
        "check": (
            "Compute average revenue per line and per order for the whole model, then explain"
            " in one sentence why they differ. As a counterexample, describe a fixture in "
            "which line count and order count agree, and state why that agreement would be a "
            "coincidence rather than a rule."
        ),
        "reference": (
            "In the reference, confirm that Lines and Orders come from different functions "
            "and that order 101 yields 2, 1 and 24. Also check that the shared OrderCount "
            "measure uses DISTINCTCOUNT rather than COUNTROWS."
        ),
    },
    "dax-003": {
        "draft": (
            "The starter already groups by Product[Category] but returns a BLANK draft "
            "measure. Predict revenue for Paper, Home and Travel, decide whether a category "
            "with no sales appears at all, and then predict how Paper changes when a North "
            "filter joins it."
        ),
        "model": (
            "Two dimensions meet at Sales in this lesson. Paper covers ProductKey 1 "
            "(Notebook) and 2 (Pen); North covers CustomerKey 10 (Ada) and 30 (Cy). Both "
            "relationships are active and one-directional, so each selection narrows Sales "
            "independently and only lines satisfying both survive."
        ),
        "misconception": (
            "A common reading of two slicers is that they add together, as if the report "
            "showed Paper lines plus North lines. Work through the rows instead. Paper keeps "
            "S1, S2, S4, S5 and S7 for 91 USD. North keeps every line from customers 10 and "
            "30: S1, S2, S4, S5 and S8 for 107 USD. The intersection is S1, S2, S4 and S5, "
            "which totals 71 USD, and S8 drops out because the Mug is a Home product. Summing"
            " 91 and 107 counts the four shared lines twice. Filters from different "
            "dimensions combine with AND at the fact table; an OR across dimensions requires "
            "an explicit expression."
        ),
        "check": (
            "Replace North with South and derive Paper revenue by listing customer 20's "
            "lines. Then name the lines that would have to become Paper products for the "
            "answer to equal South's total of 80 USD, and explain why the Customer filter "
            "alone cannot produce that."
        ),
        "reference": (
            "Compare the reference's CALCULATETABLE filters with your draft: each filter "
            "argument names one dimension column, and together they return 91 and then 71. "
            "Check that no filter is placed on a Sales column."
        ),
    },
    "dax-004": {
        "draft": (
            "The starter asks for two product counts that sound alike: products in the "
            "dimension and products that were sold. Predict both with no filter and again "
            "with a filter on the single line S4, and note which table each count reads."
        ),
        "model": (
            "Product to Sales is one-to-many and filters only from Product toward Sales. Blue"
            " covers the Notebook (key 1) and the Mug (key 3), whose six lines total 163 USD."
            " The Bag (key 4) has no sales, so the dimension holds one more product than the "
            "fact references."
        ),
        "misconception": (
            "Learners who know SQL often expect a filter on Sales to shrink Product the way "
            "an inner join would. In this model it does not. Filtering SaleID to S4 leaves "
            "one Sales line worth 27 USD, yet COUNTROWS(Product) still returns 4, because "
            "single-direction relationships carry filters from the one side to the many side "
            "only. The count is correct for the question it answers, which is how many "
            "catalog products are visible. The error lies in labeling it as products sold. "
            "DISTINCTCOUNT over Sales[ProductKey] answers that question and returns 1 for S4."
        ),
        "check": (
            "Under a Color = Green filter, predict COUNTROWS(Product), COUNTROWS(Sales) and "
            "NetRevenue, then explain why the fact results are empty even though the "
            "dimension result is not. Say what a bidirectional relationship would and would "
            "not change in this case."
        ),
        "reference": (
            "In the reference, verify that the same three expressions appear in both cases "
            "and that only the filter argument changes. The pair 2, 6, 163 and 4, 1, 27 "
            "should be explainable from relationship direction alone."
        ),
    },
    "dax-005": {
        "draft": (
            "The starter projects every Sales line with a label and a BLANK amount, ordered "
            "by line. Fill in the amount column mentally for S1 through S3, then predict how "
            "many rows the query returns and whether any arithmetic is performed."
        ),
        "model": (
            "Only Sales columns appear in this lesson, and no relationship is traversed. "
            "SaleID values S1 to S8 are unique text, which makes them a safe ordering and "
            "TOPN key, whereas NetAmount ties at 20 on four lines (S1, S5, S6 and S7)."
        ),
        "misconception": (
            "A frequent first attempt is EVALUATE SUM(Sales[NetAmount]), on the theory that a"
            " query can return any expression. EVALUATE requires a table, so the scalar 187 "
            "must be wrapped, for example by ROW. The opposite slip also appears: treating "
            "SELECTCOLUMNS over two rows as if it summarized them. TOPN over SaleID returns "
            "S1 at 20 USD and S2 at 4 USD as separate rows; no sum of 24 is produced unless "
            "you ask for one. Asking whether an expression yields a scalar or a table, before"
            " choosing a function, resolves both errors."
        ),
        "check": (
            "Write a TOPN call that ranks Sales by NetAmount descending with N equal to 4, "
            "and list every row it can return given the four-way tie at 20 USD. Then add the "
            "second ordering key that limits the result to exactly four rows."
        ),
        "reference": (
            "Check that the reference wraps the scalar case in ROW and orders the projected "
            "case explicitly after TOPN. Confirm your draft uses the output names RevenueUSD,"
            " Line and Amount, which belong to the query rather than the model."
        ),
    },
    "dax-006": {
        "draft": (
            "The starter has two BLANK counters, one for duplicate dimension keys and one for"
            " unmatched foreign keys. Decide which table each counter should read before "
            "writing any expression, because the two defects live on opposite sides of the "
            "relationship."
        ),
        "model": (
            "This lesson switches to the unknown-member model. It keeps Product keys 1 "
            "through 4 and adds S9, a seven-dollar line pointing at ProductKey 999. The "
            "duplicate-key candidate is query-local DATATABLE data and is never related to "
            "Sales."
        ),
        "misconception": (
            "Seeing an unmatched key, some reviewers filter S9 out so that category totals "
            "reconcile with 187 USD. That hides seven dollars of recorded activity and makes "
            "the fact total disagree with the source, which holds 194. The regular "
            "relationship already places S9 under a blank Product member. The defensible "
            "policy keeps it visible, labels it as an unknown product and records the missing"
            " key in an issue ledger."
        ),
        "check": (
            "Classify ProductKey 4, ProductKey 999 and the duplicated candidate key 1 as "
            "unsold, unmatched or non-unique, citing the table that proves each label. Then "
            "state what a blank Product category row would total in a category breakdown."
        ),
        "reference": (
            "The reference pairs a row count against a distinct-key count (3 against 2) with "
            "an EXCEPT that returns 999. Verify that your ledger cites each result as "
            "evidence for a different defect rather than one combined error."
        ),
    },
    "dax-007": {
        "draft": (
            "The starter keeps one numeric column and one text label side by side, with the "
            "label set to the word Draft. Predict the type of each column before filling "
            "them, and decide which one a report should sort and total."
        ),
        "model": (
            "Types matter more than tables in this lesson. Quantity is a whole-number count "
            "of 17 units, NetAmount is a USD amount totaling 187, and the derived ratio of 11"
            " USD per unit carries both units. The literal date 2025-01-02 is a calendar "
            "value inside the complete Date range."
        ),
        "misconception": (
            "Because a formatted measure looks right on a card, learners sometimes wrap every"
            " revenue measure in FORMAT so the dollar sign always appears. The result $187.00"
            " is then text. Text sorts character by character, so $36.00 lands after $187.00 "
            "because 3 follows 1, and text cannot be summed or divided by quantity. Keep "
            "NetRevenue numeric and apply the currency display through a format string on the"
            " measure or the visual, leaving the number available for arithmetic."
        ),
        "check": (
            "Compute revenue per unit for the Notebook (67 USD over 7 units) and for the Mug,"
            " and state each result with its unit. Then explain why formatting both ratios "
            "with a percent sign would mislead even though the digits stay the same."
        ),
        "reference": (
            "Confirm the reference keeps NumericRevenue as the measure itself and builds "
            "DisplayText separately with FORMAT and an explicit en-US locale. Compare the "
            "four literal types in the first case with the types your draft predicted."
        ),
    },
    "dax-008": {
        "draft": (
            "The starter contrasts an empty population, a measured zero and a comparison left"
            " BLANK. Predict what BLANK() = 0 and BLANK() == 0 each return before reading the"
            " first case, and write the reason for any difference."
        ),
        "model": (
            "The second case filters Product to key 4, the Bag. Its Product row exists with "
            "Travel as its category, but Sales contains no line for it, so COUNTROWS(Sales) "
            "and NetRevenue are BLANK while COUNTROWS(Product) is 1. Every other product has "
            "at least two sales lines."
        ),
        "misconception": (
            "A common shortcut treats BLANK and zero as the same thing because BLANK() = 0 "
            "evaluates to TRUE. That loose equality is a coercion rule, not a statement that "
            "missing equals measured zero; strict equality with == returns FALSE. Arithmetic "
            "is inconsistent in an instructive way too: BLANK() + 5 is 5, yet BLANK() * 5 "
            "stays BLANK. If a predicate uses = 0 to find products with zero revenue, the Bag"
            " passes it, even though nothing was sold and no zero was ever recorded. Use "
            "ISBLANK for missing results and reserve zero for observed zeros."
        ),
        "check": (
            "Write a Bag measure that returns 0 only when the product is listed as available "
            "and BLANK otherwise, assuming a hypothetical IsActive column. Explain which "
            "business reader would be misled if COALESCE filled every blank with zero."
        ),
        "reference": (
            "Check that the reference evaluates loose and strict comparisons in the same row,"
            " and that COALESCE appears only in the DisplayRevenue column while Revenue stays"
            " BLANK. Your draft should keep those two columns distinct."
        ),
    },
    "dax-009": {
        "draft": (
            "The starter defines a draft revenue measure as BLANK and reuses it in one row. "
            "Decide whether your replacement should be a measure or a calculated column, then"
            " predict its value for the whole model and for North in 2025."
        ),
        "model": (
            "The first case reads S1 and S2 row by row, recomputing Quantity times UnitPrice "
            "minus Discount. The second applies Customer[Region] and 'Date'[Year] filters, "
            "which reach Sales through the active OrderDate relationship and leave S4, S5 and"
            " S8."
        ),
        "misconception": (
            "Some learners believe a measure computes its value once and stores it, like a "
            "column. If that were true, the North 2025 case would show 187, the stored-"
            "looking total. It shows 83 because the measure is evaluated afresh for that "
            "context, summing S4 (27), S5 (20) and S8 (36). The opposite error is also "
            "common: expecting S4's stored NetAmount of 27 to become a regional figure under "
            "a filter. Row values persist through refresh; measure results exist only for the"
            " context that asked for them."
        ),
        "check": (
            "Predict Revenue and Quantity for South in 2025 by listing the eligible lines. "
            "Then explain what would go wrong if the 83 USD North total were copied into a "
            "calculated column on each of its three lines and later summed."
        ),
        "reference": (
            "In the reference, verify that the Reconstructed column repeats the arithmetic "
            "per row and matches Stored for S1 and S2, while the North 2025 case uses model "
            "measures. That split mirrors the column versus measure decision you drafted."
        ),
    },
    "dax-010": {
        "draft": (
            "The starter wants three counts from one row: rows, orders and customers. Predict"
            " all three for the whole model and then for Paper only, and mark which of your "
            "answers you expect to fall when the filter is applied."
        ),
        "model": (
            "Paper covers five lines from four orders (101, 201, 202 and 204) placed by all "
            "three purchasing customers. Home covers S3, S6 and S8, three orders from "
            "customers 20 and 30. The Customer table lists four people, but Di (key 40) never"
            " buys."
        ),
        "misconception": (
            "A matrix with category rows invites the belief that its total row should equal "
            "the sum of the rows above it. That holds for revenue: Paper 91 plus Home 96 "
            "gives 187. It fails for customers. Paper has 3 customers and Home has 2, but the"
            " grand total is 3, not 5, because Bo (20) and Cy (30) bought from both "
            "categories. Order counts happen to add here (4 plus 3 is 7) only because no "
            "order mixes categories; order 101 holds two Paper products. A distinct count "
            "must be reevaluated in the total context rather than accumulated from subtotals."
        ),
        "check": (
            "Predict the customer counts for Paper in 2024, Home in 2024 and both together. "
            "Explain why those parts add in 2024 but the same customer metric does not add "
            "across both years."
        ),
        "reference": (
            "Confirm the reference evaluates the same four expressions in both cases, so "
            "customers with sales stays 3 while revenue drops from 187 to 91. Your draft "
            "should use DISTINCTCOUNT over Sales[CustomerKey], not COUNTROWS(Customer)."
        ),
    },
    "dax-011": {
        "draft": (
            "The starter leaves net amount, quantity and amount per unit as BLANK. Predict "
            "the first two for the whole model, derive the third by hand, and write its unit "
            "before deciding which function should perform the division."
        ),
        "model": (
            "The ratio uses two Sales columns at line grain: NetAmount in USD after line "
            "discounts and Quantity in units. Year comes from the Date table through the "
            "active OrderDate relationship, which splits the fixture into 64 USD over 5 units"
            " in 2024 and 123 USD over 12 units in 2025."
        ),
        "misconception": (
            "When a report shows yearly ratios, a natural shortcut is to average them for the"
            " total. The 2024 rate is 12.8 USD per unit and 2025 is 10.25, so the simple mean"
            " is 11.525. The pooled rate is 187 over 17, exactly 11. They differ because 2025"
            " sold more than twice as many units, and a mean of ratios gives each year equal "
            "weight regardless. Recompute ratios from totals in the target context. A related"
            " trap is substituting 0 for every undefined ratio: DIVIDE(0, 0) is BLANK by "
            "default, which differs from DIVIDE(0, 5), a genuine zero."
        ),
        "check": (
            "Compute net revenue per unit for Paper and for Home, then show that averaging "
            "those two category rates does not reproduce 11. Name the weighting that would "
            "make an average of category rates equal the pooled ratio."
        ),
        "reference": (
            "Check that the reference computes NetPerUnit from the two model measures with "
            "DIVIDE and that the literal case returns BLANK, 0 and 0. Your draft should "
            "explain which of those zeroes is a chosen display and which is measured."
        ),
    },
    "dax-012": {
        "draft": (
            "The starter binds a variable to BLANK and returns it beside a second BLANK "
            "column. Before replacing either, predict whether a variable captured outside a "
            "color filter can change when CALCULATE adds that filter later."
        ),
        "model": (
            "Product[Color] is the only filter that moves here. Blue keeps the Notebook and "
            "the Mug for 163 USD; removing the color filter restores all eight lines and 187."
            " The relationship from Product to Sales carries each color selection into the "
            "fact."
        ),
        "misconception": (
            "Variables look like named formulas, so it is natural to expect CALCULATE over "
            "RevenueBeforeColorChange with a Blue filter to recompute revenue under Blue. It "
            "returns 187 instead, because the variable already holds a number, and CALCULATE "
            "cannot modify the context of a value that has been computed. The second case "
            "shows the mirror image: a variable bound inside Blue keeps 163 even after "
            "REMOVEFILTERS. To get a context-sensitive result, pass the measure itself to "
            "CALCULATE or bind the variable inside the intended context."
        ),
        "check": (
            "Predict both columns of the first case when the color is Green, where only the "
            "unsold Bag is selected. Then explain how a frozen variable could hide the fact "
            "that Green has no sales at all."
        ),
        "reference": (
            "In the reference, locate where each variable is bound relative to CALCULATETABLE"
            " and CALCULATE. The 187 and 163 pair should follow directly from those "
            "positions; renaming the variables would not change either value."
        ),
    },
    "dax-013": {
        "draft": (
            "The starter adds a BLANK column to every Sales row. Decide what your calculation"
            " should read from the current row, then predict what an unwrapped "
            "SUM(Sales[NetAmount]) would return on each of the eight rows."
        ),
        "model": (
            "The cases iterate the four Product rows: Bag, Mug, Notebook and Pen. A filter "
            "from a Product row reaches Sales only when filter context carries that product's"
            " key across the active relationship. The Bag has no sales, so its transitioned "
            "revenue is BLANK."
        ),
        "misconception": (
            "Seeing 187 on every product row, learners often decide the Product to Sales "
            "relationship is broken and start rebuilding it. The relationship is fine. "
            "SELECTCOLUMNS provides a row context, which exposes Product[Product] and the "
            "other columns of the current row but creates no filter. SUM over Sales therefore"
            " sees all eight lines each time. Wrapping the sum in CALCULATE performs context "
            "transition, turning the current product row into a filter, so the results become"
            " 96, 67 and 24 with BLANK for the Bag. A model measure reference such as "
            "[NetRevenue] gets the same transition implicitly."
        ),
        "check": (
            "Add an outer South filter and predict both columns for each of the four "
            "products. Then explain why the transitioned column still reconciles to the South"
            " total while the raw column does not."
        ),
        "reference": (
            "Compare the reference's two projections: the only change is CALCULATE around the"
            " same SUM. Verify that the transitioned values 96, 67 and 24 sum to 187 and that"
            " the Bag row is still returned with BLANK revenue."
        ),
    },
    "dax-014": {
        "draft": (
            "The starter asks for three things at once: which products, which customers and "
            "what amount are visible. Fill them for the North 2025 cell by listing keys "
            "rather than names, so your ledger shows every filter that the single revenue "
            "number depends on."
        ),
        "model": (
            "Two filters act here. Customer[Region] picks customer keys (North is 10 and 30; "
            "South is 20), and 'Date'[Year] picks order dates through the active OrderDate "
            "relationship, not ShipDate. In this fixture the two date roles agree on year for"
            " every line, but the ledger should still name OrderDate."
        ),
        "misconception": (
            "When a report shows one prominent slicer, readers often explain a number by that"
            " slicer alone: North revenue is 83. That sentence is wrong as stated, because "
            "North across both years is 107. The 83 belongs to North and 2025 together, and "
            "the 2025 filter may sit on a page pane the reader never looks at. The same trap "
            "appears when broadening a selection. Adding South to the region filter raises "
            "revenue to 123, not to 187, because the year constraint stays. A ledger that "
            "lists every effective filter, including hidden ones, is the only reliable "
            "explanation of a cell."
        ),
        "check": (
            "Write a full ledger for South, Paper and 2025: list the admitted customer keys, "
            "product keys, eligible lines and revenue. Then name the one filter whose removal"
            " would change the result most, and verify the claim against the fixture."
        ),
        "reference": (
            "The reference changes only the Region filter between its two cases, from one "
            "value to an IN list, while the 2025 year filter stays fixed. Check that your "
            "ledger explains 83 and 123 without appealing to 187."
        ),
    },
    "dax-015": {
        "draft": (
            "The starter wraps a BLANK draft measure in a Blue context. Predict what the "
            "selected amount should be for Blue, then predict what happens to it when an "
            "inner CALCULATE sets the same Color column to Red."
        ),
        "model": (
            "Every filter in this lesson sits on Product columns, and all reach Sales through"
            " one active relationship. Blue holds the Notebook and the Mug (163 USD), Red "
            "holds only the Pen (24 USD), Green holds only the unsold Bag, and Paper holds "
            "the Notebook and the Pen (91 USD)."
        ),
        "misconception": (
            "There are two opposite misreadings of CALCULATE. The first says that adding a "
            "Red filter inside a Blue context should intersect the two, leaving no product "
            "and a BLANK result. The fixture returns 24 instead: a Boolean filter on "
            "Product[Color] replaces the existing Color selection rather than joining it. The"
            " second misreading overcorrects and says CALCULATE wipes every incoming filter. "
            "Case B refutes that: with Paper selected, adding Blue gives 67, the Notebook "
            "alone, not the all-Blue 163, because Category is a different column and survives"
            " untouched. Replacement is column by column. To keep an earlier selection on the"
            " same column, wrap the new filter in KEEPFILTERS, which a later lesson covers."
        ),
        "check": (
            "Start from a Home context and add an inner filter Color = Blue, then Color = "
            "Red. Predict both results and say which incoming filter survived each time. Then"
            " explain why the Red result being BLANK is a correct answer rather than a broken"
            " relationship."
        ),
        "reference": (
            "Compare the reference's two cases: the inner filter names Product[Color] both "
            "times, but only the first starts from an existing Color selection. Verify that "
            "163 to 24 is a replacement and 91 to 67 is an addition."
        ),
    },
    "dax-016": {
        "draft": (
            "The starter asks for two interpretations of one request: Paper products, colored"
            " Blue, at the highest product key. Predict both answers before reading the "
            "cases, writing down which product key you think MAX returns in each."
        ),
        "model": (
            "Only Product filters matter here. Paper admits ProductKey 1 (Notebook, Blue) and"
            " 2 (Pen, Red), so the incoming maximum key is 2. Within Paper and Blue together,"
            " the only key is 1, whose three sales lines total 67 USD."
        ),
        "misconception": (
            "Reading left to right, it seems natural that CALCULATE first applies Blue and "
            "then evaluates MAX inside the Blue result, returning the Notebook. Filter "
            "arguments do not work that way. Each one is evaluated in the incoming context, "
            "which here is Paper alone, so MAX(Product[ProductKey]) yields 2 before Blue is "
            "applied. The final context then asks for Blue and key 2 together, which matches "
            "no product, giving BLANK. Only nesting, where the outer CALCULATE sets Blue and "
            "the inner one computes the maximum, produces 67. Testing only Red would have "
            "hidden this, since Red and key 2 both point at the Pen."
        ),
        "check": (
            "Change the incoming category from Paper to all products and predict both cases "
            "with Blue. Then find a color that would make the two formulas agree and explain "
            "why agreement on that color proves nothing about their equivalence."
        ),
        "reference": (
            "In the reference, trace where MAX is evaluated: as a sibling argument in case A "
            "and inside the inner CALCULATE in case B. Your draft should reproduce BLANK and "
            "67 and explain both through that position."
        ),
    },
    "dax-017": {
        "draft": (
            "The starter adds a BLANK per-product amount beside each product key. Predict the"
            " correct value for each key, then predict what a raw SUM placed inside an "
            "iterator would return on each row without context transition."
        ),
        "model": (
            "Sales has a unique SaleID on every line, which is what makes transitioning a "
            "Sales row select exactly one line. Customer has four rows, including Di (key 40)"
            " with no purchases, so a measure invoked per customer returns BLANK for her and "
            "187 across the other three."
        ),
        "misconception": (
            "Because SUMX iterates eight rows, it is easy to assume that SUM inside it "
            "automatically sums one row at a time. Without context transition, the inner SUM "
            "sees the whole Sales table on every iteration and returns 187 eight times, which"
            " totals 1,496. Some learners notice the inflated number and divide by eight, "
            "which happens to give 187 here but would break as soon as a filter changed the "
            "row count. The actual fix is CALCULATE around the inner SUM, or a measure "
            "reference, which turns each row's values into filters so only the current line "
            "contributes."
        ),
        "check": (
            "Predict RawRepeated and Transitioned under a Home filter, where three lines "
            "remain. Then describe a fixture with two identical rows and no unique key, and "
            "explain what Transitioned would return for those rows."
        ),
        "reference": (
            "Check that the reference's two SUMX expressions differ only by CALCULATE, and "
            "that the customer case invokes the model measure directly. Your draft should "
            "reconcile 187 from both routes and explain why 1,496 is not a rounding issue."
        ),
    },
    "dax-018": {
        "draft": (
            "The starter filters product keys with FALSE(), so it returns an empty table. "
            "Replace FALSE() mentally with a revenue condition and predict which keys survive"
            " at a threshold of 50, writing each product's revenue beside its key."
        ),
        "model": (
            "The candidate table is VALUES(Product[ProductKey]), four keys from the "
            "dimension. Each key's revenue comes from Sales through the active relationship: "
            "67 for key 1, 24 for key 2, 96 for key 3 and BLANK for key 4, the unsold Bag."
        ),
        "misconception": (
            "A natural first draft is CALCULATE([NetRevenue], [NetRevenue] > 50), as if the "
            "measure could filter itself. A Boolean filter argument must refer to columns, so"
            " that form is rejected; and even the idea behind it is muddled, because there is"
            " no candidate whose revenue is being tested. FILTER supplies the missing piece: "
            "it walks a deliberate table of product keys and evaluates the measure once per "
            "key, which is how 67 and 96 pass at 50 while 24 and BLANK do not. The surviving "
            "keys then become a table filter for the final revenue of 163."
        ),
        "check": (
            "Apply the threshold 50 to customers instead of products and list each customer's"
            " revenue and whether it qualifies. Then explain why the Bag and Di both fail "
            "their thresholds for the same reason even though neither has any recorded "
            "revenue."
        ),
        "reference": (
            "Confirm that the reference builds Qualifying with FILTER over "
            "VALUES(Product[ProductKey]) and uses it twice: counted with COUNTROWS and "
            "applied as a CALCULATE filter. Only the threshold differs between the two cases."
        ),
    },
    "dax-019": {
        "draft": (
            "The starter contrasts a replacement result with an intersection result. Predict "
            "both for a Blue selection when the measure asks for Red, and say in a sentence "
            "what a report user who selected Blue would expect to see."
        ),
        "model": (
            "Colors map to products as follows: Blue is the Notebook and the Mug (163 USD), "
            "Red is the Pen (24 USD) and Green is the unsold Bag. Selecting Blue and Red "
            "together therefore covers every sold line and totals 187."
        ),
        "misconception": (
            "Once learners see that a plain CALCULATE filter replaces the incoming selection,"
            " some conclude that KEEPFILTERS restores everything the report had selected, as "
            "if it froze the original total. It does neither. KEEPFILTERS changes the policy "
            "for the filter it wraps from replacement to intersection on that column. With "
            "Blue selected, intersecting with Red leaves no product, so the honest answer is "
            "BLANK rather than the 24 that replacement produces. With Blue and Red selected, "
            "intersecting with Blue keeps the Mug and Notebook for 163, which is less than "
            "the original 187. The wrapper narrows within the selection; it never widens "
            "beyond it and never brings back filters removed elsewhere."
        ),
        "check": (
            "With Paper and Home both selected in Category, predict a measure that applies "
            "KEEPFILTERS on Category equal to Home, and another that applies the plain "
            "filter. Then change the selection to Paper only and explain which measure "
            "follows the user's choice."
        ),
        "reference": (
            "In the reference, compare the plain Color filter in ForcedRed with the "
            "KEEPFILTERS wrapper beside it. Verify that the outer selection is the only thing"
            " that changes between cases and that 24, BLANK, 187 and 163 follow from it."
        ),
    },
    "dax-020": {
        "draft": (
            "The starter leaves numerator, declared denominator and share BLANK. Before "
            "writing any formula, describe the denominator's population in words, for example"
            " Paper products of any color, and only then predict the three numbers for Paper "
            "and Blue."
        ),
        "model": (
            "Category and Color are separate columns on the same Product table, so removing "
            "one leaves the other in place. Customer[Region] lives on a different table "
            "entirely. With Paper, Blue and North selected, the eligible lines are S1 and S4,"
            " the Notebook purchases of Ada."
        ),
        "misconception": (
            "Because the result is called a share, learners often assume its denominator is "
            "the grand total of 187. Neither case uses that population. Removing only Color "
            "keeps Paper, so the first denominator is 91 and the share is about 73.6 percent."
            " Removing the whole Product table clears Category and Color but leaves North, so"
            " the second denominator is 107 and the share is about 43.9 percent. The word all"
            " in a measure name never removes filters by itself; only the arguments to "
            "REMOVEFILTERS decide which ones leave."
        ),
        "check": (
            "Write a third denominator that removes both Product and Customer filters for the"
            " Paper, Blue and North selection, and compute its share. Then name a report "
            "question for which each of the three denominators would be the right one."
        ),
        "reference": (
            "The reference repeats one numerator in both cases and changes only the "
            "REMOVEFILTERS argument, from a column to a table. Check that your shares come "
            "from DIVIDE over the stated populations: 67 of 91 and 47 of 107."
        ),
    },
    "dax-021": {
        "draft": (
            "The starter asks for a sum of line expressions and a mean of admitted lines. "
            "Predict gross and net amounts by computing Quantity times UnitPrice on each of "
            "the eight lines, then decide which rows a mean over products should admit."
        ),
        "model": (
            "Discount in this fixture is a currency amount per line, not a percentage, "
            "totaling 8 USD across S2 (1), S4 (3) and S8 (4). Product has four rows, and the "
            "Bag has no Sales lines, so its revenue measure is BLANK when an iterator visits "
            "it."
        ),
        "misconception": (
            "Asked for average product revenue, many learners divide 187 by 4 because the "
            "catalog lists four products, then are surprised when AVERAGEX returns 62.33. "
            "AVERAGEX skips the Bag because its measure result is BLANK, so the population is"
            " the three sold products and the divisor is 3. Neither number is wrong; they "
            "answer different questions. Coalescing BLANK to zero deliberately admits the "
            "Bag, which gives 46.75 over the full catalog. The mistake is reporting either "
            "figure without naming its population, or assuming the iterated table alone fixes"
            " the divisor when blanks can drop out silently."
        ),
        "check": (
            "Compute AVERAGEX over Customer with and without COALESCE, and say which customer"
            " changes the divisor. Then explain why the two customer averages match the two "
            "product averages here and why that coincidence teaches nothing general."
        ),
        "reference": (
            "Confirm that the reference's gross and net expressions differ only by "
            "subtracting Sales[Discount], and that the catalog average wraps the measure in "
            "COALESCE. Your draft should state the divisor behind 62.33 and 46.75."
        ),
    },
    "dax-022": {
        "draft": (
            "The starter binds one value outside an iterator and leaves a second column for a"
            " value evaluated inside it. Predict both for the four Product rows with no "
            "filter, and write which products the outside value was actually computed for."
        ),
        "model": (
            "Product has four rows, including the Bag with no sales, and the cases iterate "
            "all of them. Under a Paper filter only the Notebook and the Pen remain, worth 67"
            " and 24 USD, so the incoming total is 91."
        ),
        "misconception": (
            "Because both variables are called something like revenue, it is easy to believe "
            "that moving the VAR above SUMX is only a readability refactor. The fixture shows"
            " otherwise. Bound outside, the variable holds 187 once, and SUMX adds that same "
            "number for each of four products, giving 748. Even the Bag contributes 187, "
            "although it sold nothing, because its own revenue was never evaluated. Bound "
            "inside the iterator body, the variable receives each product's value in turn, "
            "67, 24, 96 and BLANK, which sum to 187. Move a variable out only when its value "
            "is meant to be invariant across rows."
        ),
        "check": (
            "Predict both sums under a Home filter, then under a filter on Paper and Travel "
            "together. Explain why one of those tests exposes the bug and the other hides it."
        ),
        "reference": (
            "In the reference, the only difference between the two SUMX expressions is where "
            "VAR sits. Verify that 748 equals four copies of 187 and 182 equals two copies of"
            " 91, and that the per-product sums match the incoming totals."
        ),
    },
    "dax-023": {
        "draft": (
            "The starter contrasts a recomputed total with the sum of visible ratios. Before "
            "filling either, compute net revenue per unit for Home and Paper by hand and "
            "decide which of your two numbers a matrix total row ought to show."
        ),
        "model": (
            "Grouping uses Product[Category]. Home is the Mug alone (96 USD over 5 units) and"
            " Paper is the Notebook and the Pen (91 USD over 12 units). Travel contains only "
            "the unsold Bag, so its group is all BLANK and the grouped summary omits it."
        ),
        "misconception": (
            "Report reviewers sometimes flag a total row as broken when it does not equal the"
            " sum of the cells above it. Here Home shows 19.2 and Paper about 7.58, which add"
            " to about 26.78, yet the total is 11. The total is correct: it reevaluates the "
            "same ratio over all 17 units, so Paper's larger volume pulls it down. Forcing "
            "the total to 26.78 with SUMX over categories produces a number with no "
            "meaningful unit, since dollars per unit cannot be added across groups. Check the"
            " measure's definition at the total context, not the visual's arithmetic layout."
        ),
        "check": (
            "Add a hypothetical Travel sale of 10 USD for one Bag unit and recompute the "
            "pooled ratio and the sum of category ratios. Explain which number moved more and"
            " why."
        ),
        "reference": (
            "Compare the reference's grouped NetPerUnit column with its pooled total. Verify "
            "that 19.2 and 91/12, weighted by 5 and 12 units, reproduce 11, and that the SUMX"
            " column is labeled as a different metric."
        ),
    },
    "dax-024": {
        "draft": (
            "The starter groups by Category with a BLANK amount and a BLANK selected total. "
            "Rewrite the grouping mentally to Product, then predict the selected total for a "
            "report where only the Notebook and the Pen are chosen."
        ),
        "model": (
            "The outer selection keeps the Notebook (67 USD) and the Pen (24 USD), both "
            "Paper. The model's full product total is 187, which includes the Mug and nothing"
            " for the unsold Bag."
        ),
        "misconception": (
            "ALLSELECTED is often explained as returning whatever the user sees on screen, so"
            " readers expect it to behave identically in every query. Its result depends on "
            "the query's grouping and evaluation context. In this query the selected total is"
            " 91 and the shares sum to one, but placing ALLSELECTED inside another iterator "
            "could change the shadow context, and the 91 derivation would no longer apply."
        ),
        "check": (
            "Select the Pen and the Mug and compute both share columns. Then explain to a "
            "reader why the all-product shares add to less than one without anything being "
            "wrong."
        ),
        "reference": (
            "Check that the reference keeps the same outer selection and grouping in both "
            "cases and changes only the denominator, ALLSELECTED versus REMOVEFILTERS on "
            "Product[Product]. Shares of 91 and of 187 should both be explainable."
        ),
    },
    "dax-025": {
        "draft": (
            "The starter asks for stored product keys, relationship values and the unknown "
            "amount. Predict all three for the unknown-member model before reading the cases,"
            " and note which of your counts includes something that is not a stored row."
        ),
        "model": (
            "This lesson uses the unknown-member model: Product keys 1 to 4 are stored, and "
            "Sales line S9 carries ProductKey 999 for 7 USD. Because the relationship is "
            "regular, the engine adds a blank Product member that collects S9."
        ),
        "misconception": (
            "In a clean model VALUES and DISTINCT return the same rows, so learners often "
            "treat them as synonyms. With an unmatched key they diverge: VALUES over "
            "ProductKey returns five members because it includes the relationship's blank "
            "member, while DISTINCT over the stored column returns four. Another mistake is "
            "reading the five as five valid products, or reading the blank member as a count "
            "of bad codes. It is one bucket no matter how many unmatched keys exist, so a "
            "separate fact-minus-dimension query must count those."
        ),
        "check": (
            "Suppose S10 arrives with ProductKey 998 and 5 USD. Predict both member counts "
            "and the unknown revenue, then write the query that would reveal the two distinct"
            " bad keys."
        ),
        "reference": (
            "In the reference, verify that the 5 and 4 counts come from VALUES and DISTINCT "
            "over the same column, and that ISBLANK selects the blank member for the 7 USD. "
            "Your reconciliation should read 187 plus 7 equals 194."
        ),
    },
    "dax-026": {
        "draft": (
            "The starter extends each category with a BLANK amount. Predict how many rows it "
            "returns and which category would show an empty amount once filled, then compare "
            "that with a grouped summary of the same measure."
        ),
        "model": (
            "VALUES(Product[ProductKey]) supplies four keys in the clean retail model. Keys "
            "1, 2 and 3 have sales worth 67, 24 and 96 USD; key 4, the Bag, has none. "
            "Categories follow the same pattern, with Travel holding only the Bag."
        ),
        "misconception": (
            "Learners often assume that any function returning a table keeps every input row,"
            " so they expect SUMMARIZECOLUMNS over ProductKey to list four keys just as "
            "ADDCOLUMNS does. It lists three. SUMMARIZECOLUMNS drops a group when every "
            "measure expression is BLANK, which is exactly the Bag's situation, while "
            "ADDCOLUMNS keeps each input row and attaches BLANK. Neither behavior is a bug. A"
            " coverage report that must show the unsold product needs a function that retains"
            " it, or a deliberate COALESCE that keeps the row on purpose."
        ),
        "check": (
            "Rewrite the grouped summary to include a second expression, the count of Product"
            " rows, and predict whether key 4 returns. Then name the report reader who would "
            "be misled if the Bag silently disappeared."
        ),
        "reference": (
            "Confirm that the reference returns four rows from the ADDCOLUMNS projection and "
            "three from SUMMARIZECOLUMNS, with only the row-retention policy changing. Your "
            "draft should explain the missing key 4 without calling it an error."
        ),
    },
    "dax-027": {
        "draft": (
            "The starter holds a literal key list of 1 and 3 and a BLANK transferred "
            "selection. Predict the revenue those keys should select, then decide whether a "
            "table of plain numbers can filter Product at all without help."
        ),
        "model": (
            "ProductKey is the Product to Sales relationship column. Paper covers keys 1 and "
            "2 (91 USD), and keys 1 and 3 select the Notebook and the Mug (163 USD). A key "
            "table filters the model only when it carries lineage to Product[ProductKey] or "
            "is mapped there by TREATAS."
        ),
        "misconception": (
            "Two tables that print the same values look interchangeable, so learners expect "
            "the detached key list to filter exactly like the direct projection. It does not."
            " Adding zero to ProductKey creates a computed column with the same digits but no"
            " lineage, so CALCULATE has no model column to apply it to and returns 187, the "
            "unfiltered total. TREATAS fixes this by declaring the target column explicitly, "
            "which restores 91. The output alias, Key in both cases, is irrelevant; lineage "
            "follows the expression, not the name."
        ),
        "check": (
            "Predict CALCULATE([NetRevenue], TREATAS({1, 3}, Product[ProductKey])) and the "
            "same call mapped to Customer[CustomerKey]. Explain why the second is wrong even "
            "when it runs without error."
        ),
        "reference": (
            "In the reference, compare the direct projection of Product[ProductKey] with the "
            "+ 0 variant. Verify that 91, 187 and 91 follow from lineage alone, and that "
            "TREATAS names its target column explicitly."
        ),
    },
    "dax-028": {
        "draft": (
            "The starter builds two literal sets, 10 and 20 against 20 and 30. Predict the "
            "union row count and the intersection row count, then repeat the prediction for "
            "the Paper keys and the Blue keys before opening the cases."
        ),
        "model": (
            "Paper selects ProductKey 1 and 2, the Notebook and the Pen. Blue selects 1 and "
            "3, the Notebook and the Mug. Only the Notebook belongs to both sets, so the key "
            "populations overlap by exactly one product out of three distinct ones."
        ),
        "misconception": (
            "SQL users often bring the habit that UNION removes duplicates and UNION ALL "
            "keeps them, then read DAX UNION as the deduplicating form. In DAX, UNION keeps "
            "every row, so combining the Paper and Blue keys returns four rows with key 1 "
            "twice, and only DISTINCT reduces that to three. The second trap is argument "
            "order. EXCEPT(PaperKeys, BlueKeys) returns key 2, while EXCEPT(BlueKeys, "
            "PaperKeys) returns key 3; both have one row, so a count-only test cannot tell a "
            "swapped call from a correct one. An iterator over the raw union would add the "
            "Notebook's 67 USD twice, reporting 254 instead of 187."
        ),
        "check": (
            "Compute SUMX over the raw union and over its DISTINCT version, using each key's "
            "revenue. Then name which set operation a list of products sold in both Paper and"
            " Blue should use."
        ),
        "reference": (
            "Check that the reference counts INTERSECT and EXCEPT from the same two "
            "variables, and that the UNION case reports both the raw row count of 4 and the "
            "distinct key count of 3. Your draft should list which key each difference "
            "returns."
        ),
    },
    "dax-029": {
        "draft": (
            "The starter wants one amount by order date and one by ship date. Before filling "
            "them, list the 2025 lines whose OrderDate and ShipDate fall in different months,"
            " since only those lines can make the two January figures disagree."
        ),
        "model": (
            "Sales carries OrderDate and ShipDate, both related to the Date table, but only "
            "the OrderDate relationship is active. S6 is the cross-month line: ordered "
            "2025-01-05, shipped 2025-02-01, for 20 USD. S5 also ships later (January 8) but "
            "stays inside January."
        ),
        "misconception": (
            "A shipped-revenue figure that differs from the ordered figure for the same month"
            " is often reported as a data quality defect, and someone proposes deleting or "
            "reassigning the late row. Nothing is missing. In January 2025 the order role "
            "collects S4, S5 and S6 for 67 USD, while the ship role collects only S4 and S5 "
            "for 47 USD, because S6 shipped on February 1. February mirrors this: 56 by order"
            " date, 76 by ship date, since S6 moves in. Over all of 2025 both roles give 123."
            " USERELATIONSHIP changes which date column filters Sales for that one CALCULATE;"
            " it does not modify facts or the model's default."
        ),
        "check": (
            "Predict both role totals for the single date 2025-01-04, then for the whole of "
            "2024. Explain why the 2024 test cannot reveal a wrong relationship choice in "
            "this fixture."
        ),
        "reference": (
            "Verify that the reference evaluates both role columns under the same Date filter"
            " and that the only change is USERELATIONSHIP on Sales[ShipDate]. January 67 and "
            "47, February 56 and 76, should reconcile to 123 per role."
        ),
    },
    "dax-030": {
        "draft": (
            "The starter asks for Newsletter revenue, Prospects revenue and a distinct union."
            " Using the membership keys, predict all three before reading the cases, and "
            "decide whether the two audience amounts should add to the union."
        ),
        "model": (
            "This lesson uses the analytics model. GroupMembership is a bridge with one row "
            "per audience and customer pair. Newsletter holds customers 10 and 20 (Ada and "
            "Bo), Prospects holds 20 and 30 (Bo and Cy), and both relationships point into "
            "the bridge in one direction."
        ),
        "misconception": (
            "Selecting an audience and seeing 187 USD, the full total, leads many learners to"
            " conclude that the bridge is broken and that bidirectional filtering is the fix."
            " The 187 is expected: Audience filters GroupMembership, but nothing propagates "
            "from the bridge back to Customer and then to Sales. TREATAS on the membership "
            "keys is the explicit route, giving Newsletter 131 (Ada 51 plus Bo 80) and "
            "Prospects 136 (Bo 80 plus Cy 56). A second mistake follows: adding 131 and 136 "
            "to report 267 for both audiences. Bo is in each, so the unique population is "
            "187, and the 80 overlap must be subtracted once."
        ),
        "check": (
            "Predict TREATAS revenue for an audience containing Ada and Di only, then for all"
            " three audience customers. Explain which overlap figure a marketing reader needs"
            " alongside the two audience totals."
        ),
        "reference": (
            "Compare the reference's RawRevenue and AudienceRevenue columns under each "
            "audience. Verify 131 and 136 from customer totals, and the reconciliation 131 "
            "plus 136 minus 80 equal to the 187 union."
        ),
    },
    "dax-031": {
        "draft": (
            "The starter asks for calendar days, observed sales dates and missing dates. "
            "Count all three for January 2025 by hand, and decide whether the missing figure "
            "measures absent dates or simply dates without transactions."
        ),
        "model": (
            "The Date table holds one row per calendar day through the classic Gregorian "
            "calendar. In January 2025, Sales lines S4, S5 and S6 were ordered on January 2, "
            "3 and 5, so three of the 31 calendar dates have sales and 2025-01-04 has none."
        ),
        "misconception": (
            "Some authors build a Date table with DISTINCT(Sales[OrderDate]) because it seems"
            " to contain all the dates that matter. For January 2025 that table has three "
            "rows instead of 31. Any calculation that walks dates then breaks quietly: a per-"
            "day average divides by 3 instead of 31, and a time-intelligence function "
            "receives a calendar with holes. The opposite error also appears. A blank on "
            "2025-01-04 is a real no-sale day inside observed coverage, but a blank after the"
            " data watermark would mean the outcome is not yet known. The calendar alone "
            "cannot tell these apart; availability metadata must."
        ),
        "check": (
            "Compute January 2025 revenue per calendar day and per sale day. Then say which "
            "one a staffing planner should use and which one a sales-day performance review "
            "should use."
        ),
        "reference": (
            "Confirm that the reference counts 'Date' rows and DISTINCTCOUNT of "
            "Sales[OrderDate] under the same month filter, giving 31 and 3. For 2025-01-04, "
            "both Sales rows and revenue should be BLANK while the calendar count is 1."
        ),
    },
    "dax-032": {
        "draft": (
            "The starter shows a current period and a year-to-date column. For the January 3 "
            "anchor and the February 3 anchor, list which Sales lines DATESYTD should admit "
            "and their sum before you run anything."
        ),
        "model": (
            "The Date table follows the Gregorian year and the active OrderDate relationship."
            " 2025 lines in order: S4 on January 2 (27 USD), S5 on January 3 (20), S6 on "
            "January 5 (20), S7 on February 2 (20) and S8 on February 3 (36)."
        ),
        "misconception": (
            "A tempting shortcut treats year to date as the current value scaled by elapsed "
            "time, or as the whole year's total. Neither matches DATESYTD. For the January 3 "
            "anchor, the current day holds 20 USD from S5, and the YTD filter expands the "
            "date set to January 1 through January 3, admitting S4 and S5 for 47. January 1 "
            "has no sales but stays in the set. For February 3 the set runs from January 1, "
            "and the result is 123, which equals the full 2025 total only because the fixture"
            " ends there. Moving the anchor to February 2 drops S8 and gives 87. Write the "
            "boundary, not just the label, beside any YTD figure."
        ),
        "check": (
            "Predict YTD for anchors 2025-01-05 and 2024-01-03. Then explain why a February 3"
            " YTD equal to the full year total is a fixture coincidence rather than a rule."
        ),
        "reference": (
            "Check that the reference applies DATESYTD to 'Date'[Date] inside CALCULATE under"
            " each single-date anchor. Your draft should enumerate the admitted lines: S4 and"
            " S5 for 47, then S4 through S8 for 123."
        ),
    },
    "dax-033": {
        "draft": (
            "Predict current, prior and growth for full January 2025 against January 2024, "
            "then for January 1 to 3 in both years. Mark which comparison you would publish "
            "and the reason."
        ),
        "model": (
            "January 2024 holds S1 and S2 on January 2 (24 USD) and S3 on January 3 (40), so "
            "64. January 2025 holds 67 in total, of which 47 falls on January 1 to 3."
        ),
        "misconception": (
            "The partial window turns plus 4.69 percent into minus 26.56 percent without any "
            "change in trading, because the shifted prior period is compared on matching "
            "dates but the current figure omits S6 on January 5. Neither result is invalid; "
            "the comparison window decides the sign."
        ),
        "check": (
            "Compute growth for January 1 to 5 in both years and state whether the sign "
            "matches the full-month result."
        ),
        "reference": (
            "Verify that both reference cases use SAMEPERIODLASTYEAR under different Date "
            "filters, giving 67 over 64 and 47 over 64."
        ),
    },
    "dax-034": {
        "draft": (
            "The starter fixes the anchor at February 3, 2025. List the three calendar dates "
            "in the window and the revenue on each, then predict a calendar-day rate and a "
            "sale-day mean before reading either case."
        ),
        "model": (
            "The window covers February 1, 2 and 3 under the OrderDate role. February 1 has "
            "no order (S6 merely ships that day), February 2 has S7 for 20 USD and February 3"
            " has S8 for 36, so the window total is 56."
        ),
        "misconception": (
            "Learners often expect AVERAGEX over the window dates to divide by three because "
            "the window has three days. It divides by two. AVERAGEX skips February 1, where "
            "NetRevenue is BLANK, so the mean is 56/2, or 28, an average over sale days. "
            "Wrapping the measure in COALESCE admits the empty date as zero and returns 56/3,"
            " about 18.67, which matches dividing the window revenue by COUNTROWS of the "
            "dates. Both are correct for different denominators. The risk comes later: past "
            "the data watermark a BLANK means unknown, and coalescing it would assert a zero "
            "sale that nobody observed."
        ),
        "check": (
            "Move the anchor to February 2 and predict both averages. Then name the condition"
            " under which the two averages agree for any window."
        ),
        "reference": (
            "Confirm that the reference builds WindowDates once with DATESINPERIOD and a "
            "minus 3 DAY interval, and that the two averages differ only by COALESCE. Your "
            "draft should explain 28 and 18.67 from the same 56."
        ),
    },
    "dax-035": {
        "draft": (
            "The starter names a June 30 boundary and leaves the fiscal amount BLANK. Write "
            "the fiscal year label for June 30, 2024 and for July 1, 2024 first, then decide "
            "which Sales lines belong to FY 2025 under that rule."
        ),
        "model": (
            "FiscalYear starts on July 1 and is named by the year in which it ends. Every "
            "2024 sale in the fixture (S1 to S3, 64 USD) falls in January 2024 and so belongs"
            " to FY 2024. The 2025 lines S4 to S8 (123 USD) fall in FY 2025."
        ),
        "misconception": (
            "Because FY 2025 to date and calendar 2025 to date both return 123 here, it is "
            "easy to conclude that the fiscal column is decoration. The match is an accident "
            "of the fixture: no sales fall between July and December 2024. Add a single "
            "hypothetical sale on 2024-09-10 and the fiscal figure rises while the calendar "
            "figure does not, since September 2024 is in FY 2025 but outside calendar 2025. A"
            " second confusion is the label convention itself. Naming by ending year puts "
            "July 2024 into FY 2025; naming by starting year would call the same months FY "
            "2024. The rows stay the same; only the caption changes, so the convention must "
            "be written beside the number. Finally, 123 covers July through February only, so"
            " comparing it with all twelve months of FY 2024 mixes coverage with performance."
        ),
        "check": (
            "Predict FY 2024 revenue and FY 2025 revenue through February 28 if a 30 USD sale"
            " is added on 2024-11-15. Then say which of the two totals a calendar-year report"
            " would move."
        ),
        "reference": (
            "Check that the reference reads 'Date'[FiscalYear] rather than deriving the label"
            " from Year, and that the to-date case caps dates at February 28, 2025. Your "
            "draft should explain why 123 matches the calendar total here only by "
            "coincidence."
        ),
    },
    "dax-036": {
        "draft": (
            "The starter asks for a Gregorian YTD and a declared retail YTD at the same "
            "anchor. Before reading the cases, write the date range each year definition "
            "admits for 2025-02-03 and the lines inside each range."
        ),
        "model": (
            "The classic Date table uses the Gregorian year. The optional RetailCalendar "
            "metadata declares a retail year starting February 1, so the anchor sits on day "
            "three of RetailYear 2026. The February 2025 lines are S7 (20 USD) and S8 (36)."
        ),
        "misconception": (
            "Learners who see TOTALYTD in both queries expect the same number and suspect the"
            " retail result of 56 is a bug. The function is the same, but the calendar "
            "argument differs. With 'Date'[Date] the year starts on January 1 and admits S4 "
            "through S8 for 123. With RetailCalendar the year begins on February 1 and admits"
            " only S7 and S8. The other trap is treating the second number as observed "
            "output. It is a derivation under a declared metadata assumption about a preview "
            "feature, and pasting the query into a model without that calendar object will "
            "not run."
        ),
        "check": (
            "Predict both YTD values at anchor 2025-01-31. Then list the metadata you would "
            "need to confirm before trusting any retail-calendar figure in a real model."
        ),
        "reference": (
            "Confirm that the reference keeps the anchor and measure identical and changes "
            "only the TOTALYTD calendar argument. Your draft should derive 123 and 56 from "
            "the lines each year definition admits."
        ),
    },
    "dax-037": {
        "draft": (
            "The starter attaches an amount and a dense rank to each ProductKey. Rank the Mug"
            " (96), the Notebook (67), the Pen (24) and the unsold Bag by hand, then do the "
            "same for the candidate scores 100, 80, 80 and 50."
        ),
        "model": (
            "The cases use a query-local Candidates table: Alpha 100, Beta 80, Gamma 80 and "
            "Delta 50. Beta and Gamma tie, which is the only condition under which DENSE and "
            "SKIP disagree and TOPN can return more rows than requested."
        ),
        "misconception": (
            "Asking TOPN for two rows and receiving three looks like a defect, and many "
            "learners respond by switching to a different function. TOPN is honoring the tie:"
            " Beta and Gamma share the second score, so both qualify, and 2 is a minimum when"
            " the cutoff lands on a tie. Adding Name as a secondary sort key returns exactly "
            "Alpha and Beta, but that choice is arbitrary alphabetical ordering, not a real "
            "difference between candidates. Similarly, Delta's rank is 3 under DENSE and 4 "
            "under SKIP; neither is wrong, and the specification must name the policy."
        ),
        "check": (
            "Change Delta's score to 80 and predict both rank columns and both TOPN row "
            "counts for a cutoff of 2. Explain which display a reader of a prize shortlist "
            "should see."
        ),
        "reference": (
            "Verify that the reference ranks over Candidates with the same score expression "
            "in both RANKX calls and changes only DENSE versus SKIP. The second case should "
            "return 3 and 2 rows, explained by the tie and the Name tie-breaker."
        ),
    },
    "dax-038": {
        "draft": (
            "Predict the SaleIDs at positions 1 and 2 and at the last two positions, and the "
            "line before S4, ordering by SaleID."
        ),
        "model": (
            "S1 and S2 share order date 2024-01-02, so two positions here are two lines, not "
            "two days."
        ),
        "misconception": (
            "WINDOW counts rows in a declared order, not dates, so the first two positions "
            "hold 24 USD from one day."
        ),
        "check": ("Predict OFFSET(-1) from S1 and say what an empty result means."),
        "reference": (
            "Check that every reference case orders by the unique Sales[SaleID] and returns "
            "S1 and S2, S7 and S8, S1, then S3."
        ),
    },
    "dax-039": {
        "draft": (
            "The starter fixes an as-of date of February 15, 2025. Write the closing units on"
            " January 31 and February 28 from the snapshot rows, then decide what number "
            "should appear for February 15 when no snapshot exists that day."
        ),
        "model": (
            "This lesson uses the analytics model. Inventory holds two end-of-day snapshots: "
            "January 31 with the Notebook 10, the Pen 20 and the Mug 5 (35 units), and "
            "February 28 with 8, 15 and 7 (30 units)."
        ),
        "misconception": (
            "A matrix that adds Inventory[Units] across January and February shows 65 units, "
            "and nothing in the visual warns that this figure is meaningless as stock on "
            "hand. Nobody ever held 65 units; the same shelves were counted twice. Units add "
            "across products at one date, but over time a balance needs a rule such as the "
            "closing snapshot, which gives 30 for the two months. The Notebook and Mug subset"
            " at February 15 shows the opposite risk: carrying forward January 31 gives 15 "
            "(10 plus 5), which is an estimate from a two-week-old count, not a measurement. "
            "It also equals the February 28 subset total, 8 plus 7, for unrelated reasons."
        ),
        "check": (
            "Compute the closing balance for the Pen alone over the two months and its "
            "carried value at February 15. Then state a staleness limit that would make you "
            "return BLANK instead."
        ),
        "reference": (
            "Confirm that the reference's ClosingUnits uses LASTDATE over the two-month date "
            "set and returns 30, and that the carried case finds the last snapshot on or "
            "before February 15. Your draft should separate 65, 30 and 15."
        ),
    },
    "dax-040": {
        "draft": (
            "The starter wants eligible members, observed active members and retention. Using"
            " CohortMember and Activity, compute those for the January cohort at age one "
            "before reading the cases, and decide what the February cohort can report."
        ),
        "model": (
            "This lesson uses the analytics model. Members 100 and 200 joined in January 2025"
            " and members 300 and 400 in February. Activity rows: 100 in January and "
            "February, 200 in January only, and 300 in February. Observation ends with "
            "February 2025."
        ),
        "misconception": (
            "Two cells showing 50 percent invite a direct comparison, but they measure "
            "different things. January's 1 of 2 is retention at age one: member 100 returned "
            "in February while 200 did not. February's 1 of 2 is entry-month activity, since "
            "member 300 was active on joining and 400 was not. February's age-one retention "
            "is BLANK, because March lies beyond observed data. Coalescing it to zero would "
            "claim both February members churned when nobody has looked yet."
        ),
        "check": (
            "Add a March 2025 activity row for member 300 and extend observation through "
            "March. Predict the February cohort's retention at age one and which January "
            "figure stays unchanged."
        ),
        "reference": (
            "Check that the reference counts eligibility from CohortMember and activity with "
            "DISTINCTCOUNT of MemberKey, and that February's age-one result is BLANK. Your "
            "draft should name which member makes each half."
        ),
    },
    "dax-041": {
        "draft": (
            "Predict Paper's January 2025 actual, budget and variance, then the same for the "
            "single day January 2, and say what the budget should be there."
        ),
        "model": (
            "Budget rows are monthly by category, with January Paper at 60 USD. Paper sold S4"
            " (27) and S5 (20) in January 2025, so the actual is 47."
        ),
        "misconception": (
            "Showing 60 against January 2 alone would report a 33 USD shortfall for one day; "
            "the guard returns BLANK until an allocation policy exists."
        ),
        "check": (
            "Compute January Home actual, budget and variance, then the uniform daily target "
            "for January Home."
        ),
        "reference": (
            "Verify that the reference returns 47, 60 and minus 13 for the full month, and 27"
            " with a BLANK budget for the day."
        ),
    },
    "dax-042": {
        "draft": (
            "The starter asks for local transactions, converted USD and missing rates. Before"
            " reading the cases, multiply each ForeignSales row by the rate for its own date "
            "and currency, and note what a plain sum of LocalAmount would be."
        ),
        "model": (
            "This lesson uses the analytics model. ForeignSales has F1 (100 USD on "
            "2025-01-02), F2 (100 EUR the same day) and F3 (50 EUR on 2025-02-03). "
            "ExchangeRate holds one row per date and currency: USD at 1, EUR at 1.1 in "
            "January and 1.2 in February."
        ),
        "misconception": (
            "Summing LocalAmount first and converting afterward feels efficient, but the 250 "
            "it produces adds dollars to euros and has no unit. Conversion has to happen per "
            "row, at the grain of the rate key: 100 plus 110 plus 60 gives 270 USD. The EUR "
            "case shows a subtler version of the same error. Taking the highest rate and "
            "applying it to all 150 EUR gives 180, while the transaction-date rates give 170,"
            " because F2 was booked when the euro was worth 1.1. The shortcut only looks like"
            " a latest-rate policy because rates happen to rise in this fixture; a falling "
            "rate would make MAX pick January."
        ),
        "check": (
            "Add a row F4 for 20 EUR on 2025-02-04 with no matching rate. Predict what "
            "LOOKUPVALUE returns for it and what a responsible total and missing-rate count "
            "would show."
        ),
        "reference": (
            "Confirm that the reference multiplies inside SUMX with LOOKUPVALUE matching both"
            " RateDate and Currency. The 270, 170 and 180 figures should each be traced to "
            "specific rows and rates."
        ),
    },
    "dax-043": {
        "draft": (
            "The starter defines DraftCost and DraftProfit as BLANK. Using UnitCost from "
            "Product, compute cost for each product line by hand, then total cost, profit and"
            " margin for the whole model and for Blue products."
        ),
        "model": (
            "Product UnitCost is 2 for the Notebook, 1 for the Pen, 5 for the Mug and 10 for "
            "the Bag, held constant per product. Units sold are 7, 5, 5 and 0, so cost is 14,"
            " 5 and 25, totaling 44 USD against 187 of revenue."
        ),
        "misconception": (
            "When a report needs margin as a percentage, a common shortcut is "
            'FORMAT([NetMargin], "0.0%") inside the measure itself. The measure then returns '
            "text such as 76.5%, and anything that builds on it, a variance against target or"
            " an average across categories, either fails or compares strings. The numeric "
            "margin, 143 over 187, is about 0.7647, and formatting belongs to the display "
            "layer. A related slip is recomputing cost with a different filter than revenue; "
            "under Blue the family must give 163, 39 and 124 together, or the margin of about"
            " 0.761 mixes two populations."
        ),
        "check": (
            "Compute cost, profit and margin for the Paper category. Then explain what "
            "happens to the Paper margin if a report overrides only the revenue measure's "
            "filter."
        ),
        "reference": (
            "Verify that the reference builds Profit from NetRevenue and Cost and NetMargin "
            "from Profit with DIVIDE. The whole-model row should read 187, 44, 143 and about "
            "0.765; the Blue row 163, 39, 124 and about 0.761."
        ),
    },
    "dax-044": {
        "draft": (
            "The starter asks for transformed revenue and unaffected quantity. Decide which "
            "measure the fee item should touch, then predict both values for the whole model "
            "and for Blue products before you read the expanded query."
        ),
        "model": (
            "The retail model exposes NetRevenue (187 USD overall, 163 for Blue) and "
            "QuantitySold (17 units overall, 12 for Blue). The lesson's calculation item "
            "applies a 10 percent fee to revenue only, and its expansion is algebra, not live"
            " group execution."
        ),
        "misconception": (
            "Because a calculation item applies to whatever measure is in the visual, authors"
            " sometimes write SELECTEDMEASURE() * 0.9 and assume nobody will pair it with a "
            "unit count. Then a matrix with both revenue and units turns 17 sold units into "
            "15.3, a fractional quantity that never happened. ISSELECTEDMEASURE guards "
            "against this by naming the measures the transformation is meant for and passing "
            "every other measure through unchanged. The guard is part of the business rule, "
            "not an optimization. Remember too that the expanded query, 168.3 and 17, is a "
            "reference derivation; real models also need compatibility level 1500 and correct"
            " group configuration."
        ),
        "check": (
            "Predict the guarded item's result for Paper revenue and Paper units. Then name "
            "one more measure in this course that should be excluded and say why."
        ),
        "reference": (
            "Check that the reference's expanded query multiplies only NetRevenue by 0.9 and "
            "leaves QuantitySold untouched. Results of 168.3 and 17 follow from the guarded "
            "definition shown in the lesson's extra block."
        ),
    },
    "dax-045": {
        "draft": (
            "The starter compares scale outside addition with addition outside scale. Write "
            "both expressions around NetRevenue of 187 and compute them by hand before "
            "reading the cases, then explain the size of the gap."
        ),
        "model": (
            "Two calculation items act on the same measure: AddTen adds 10 and Scale "
            "multiplies by 0.9. Precedence decides which item wraps the other, so the outer "
            "item receives the inner item's result rather than the raw measure."
        ),
        "misconception": (
            "Learners often assume that applying two transformations is like applying two "
            "filters, so order cannot matter. Here it does: (187 + 10) times 0.9 is 177.3, "
            "while 187 times 0.9 plus 10 is 178.3. The gap is always 1, the 10 scaled by 0.1,"
            " regardless of revenue. Testing each item alone would pass in both "
            "configurations, which is why combined cases belong in a regression grid. A "
            "second error is fixing a wrong number with a dynamic format string; that changes"
            " the display, never the value."
        ),
        "check": (
            "Compute both expansions when the base measure is BLANK. Then say whether any "
            "revenue value can make the two orders agree and why."
        ),
        "reference": (
            "Verify that the reference's two cases differ only in which item expression is "
            "outermost, returning 177.3 and 178.3. Your notes should name the precedence "
            "assumption behind each number."
        ),
    },
    "dax-046": {
        "draft": (
            "The starter asks for a default fee and a boundary fee. Before reading the cases,"
            " write the function signature you expect, with a parameter domain and default, "
            "and compute the result for 187 at rates 0.1, 0.2, 1 and 1.2."
        ),
        "model": (
            "Course.NetAfterFee takes an amount and an optional fee rate defaulting to 0.1, "
            "valid from 0 to 1. Applied to the model's 187 USD it returns 168.3 by default "
            "and 149.6 at 0.2. Real UDF use needs compatibility level 1702."
        ),
        "misconception": (
            "A default argument looks like a convenience, so changing it seems harmless. It "
            "is part of the contract: every call that omits the rate silently changes. Moving"
            " the default to 0.15 turns 168.3 into 158.95 across reports nobody edited, while"
            " explicit 0.2 calls stay at 149.6. The domain matters too. A rate of 1 is valid "
            "and yields 0, a full fee. A rate of 1.2 is invalid and returns BLANK, which a "
            "caller can misread as no revenue unless the function's documentation and a "
            "validation signal say otherwise."
        ),
        "check": (
            "Predict Course.NetAfterFee(0, 0.5) and Course.NetAfterFee(100, -0.1). State "
            "which result a caller could confuse with missing activity."
        ),
        "reference": (
            "Check that the reference function validates the rate before computing and "
            "returns 168.3, 149.6, 0 and BLANK in the cases. Your draft should spell out the "
            "domain and the default as stated parts of the contract."
        ),
    },
    "dax-047": {
        "draft": (
            "The starter passes the same amount as a value and as an expression. Predict both"
            " functions' results with no filter and under a Red caller filter, deciding for "
            "each when NetRevenue is actually evaluated."
        ),
        "model": (
            "Both functions apply a Blue color filter in their bodies. Course.BlueValue "
            "receives a VAL parameter, already computed in the caller's context, while "
            "Course.BlueExpression receives EXPR and evaluates it after the filter. Red "
            "covers only the Pen (24 USD)."
        ),
        "misconception": (
            "Switching a parameter from VAL to EXPR is sometimes treated as a performance "
            "tweak. It changes results. With no caller filter, the value version returns 187 "
            "and the expression version 163, since only the deferred argument sees Blue. "
            "Under Red the gap widens: 24 against 163, because the plain Blue filter replaces"
            " the caller's color."
        ),
        "check": (
            "Predict both functions for a Paper caller, then for a Blue caller. Explain which"
            " call is the safer default for a reusable library."
        ),
        "reference": (
            "Verify that the two reference functions share a body and differ only in VAL "
            "versus EXPR, giving 187 and 163, then 24 and 163."
        ),
    },
    "dax-048": {
        "draft": (
            "Predict running revenue for the January and February 2025 snapshot rows in "
            "ascending order, then in descending order."
        ),
        "model": (
            "The snapshot holds two monthly aggregates, January 67 and February 56, already "
            "summed from Sales."
        ),
        "misconception": (
            "RUNNINGSUM follows the visual's sort, so reversing months gives 56 then 123; the"
            " last value matches but the first row's meaning changes."
        ),
        "check": ("Add a March row with 10 USD at position 3 and predict all running values."),
        "reference": (
            "Confirm that both reference expansions sum by Position and end at 123 from 67 and 56."
        ),
    },
    "dax-049": {
        "draft": (
            "The starter asks for fact rows, product groups and the arithmetic you would need"
            " to explain. Count Sales rows, distinct ProductKey, OrderDate and SaleID values "
            "by hand, then list Product's distinct categories and colors, before running "
            "anything."
        ),
        "model": (
            "Sales has eight lines with eight SaleIDs. Only three ProductKeys appear, because"
            " the Bag never sold, and seven OrderDates, because S1 and S2 share 2024-01-02. "
            "Product has four rows across three categories and three colors."
        ),
        "misconception": (
            "A familiar claim says that high-cardinality columns are always waste and should "
            "be dropped to make a model fast. SaleID is the counterexample in this fixture. "
            "It has the highest cardinality of any Sales column, one value per line, yet it "
            "is the only single column that names a line. S1 and S2 share an order, a "
            "customer and a date; two future lines for the same product on that order would "
            "be indistinguishable without it. Removing it would save encoded space in a large"
            " model but would also remove the ability to trace a refund, a duplicate or a "
            "disputed line. The opposite claim is just as unsafe: a low distinct count, such "
            "as three ProductKeys in Sales, does not prove the Product dimension has three "
            "members. It has four, and the unsold Bag must remain if reports list the "
            "catalog. Cardinality is a property of the data, not a verdict about cost; only "
            "measurement on a real engine can say what a column costs."
        ),
        "check": (
            "Add a hypothetical S9 for the Bag sold to Di on 2025-02-04. Predict all four "
            "fact counts and the three dimension counts afterward, and say which numbers "
            "change only because the Bag sold."
        ),
        "reference": (
            "Confirm that the reference counts Sales and Product cardinalities in separate "
            "rows, returning 8, 3, 7, 8 and 4, 3, 3. Your draft should explain why "
            "ProductKeys is 3 in Sales but Product has 4 rows."
        ),
    },
    "dax-050": {
        "draft": (
            "The starter asks for candidate combinations and observed combinations. Multiply "
            "the four products by the four customers, then list the product and customer "
            "pairs that actually appear in Sales, before reading either case."
        ),
        "model": (
            "Sales covers six distinct product and customer pairs: Notebook with Ada and Bo, "
            "Pen with Ada and Cy, Mug with Bo and Cy. S1 and S2 share a date but not a "
            "product, so product, customer and date together give eight observed cells. The "
            "Date table spans 731 days across 2024 and 2025."
        ),
        "misconception": (
            "A query that returns one number is easy to imagine as cheap. Yet a CROSSJOIN of "
            "products, customers and dates describes 11,696 candidate cells (4 by 4 by 731) "
            "to reach an answer drawn from 8 observed ones. Two opposite errors follow. One "
            "is concluding that the engine must physically scan 11,696 rows, which the source"
            " cannot show; real engines prune and fuse work, and only a measured plan can say"
            " what happened. The other is replacing every full grid with SUMMARIZE over Sales"
            " to be safe. That drops the ten pairs that never sold, which is exactly the "
            "population a coverage report on unsold product and customer pairs needs. Choose "
            "the grid for its meaning first, then measure its cost."
        ),
        "check": (
            "Restrict both queries to February 2025 and predict candidate cells and observed "
            "cells. Then name a report for which the ten unobserved pairs are the main "
            "finding."
        ),
        "reference": (
            "Verify that the reference compares CROSSJOIN over dimension VALUES with "
            "SUMMARIZE over Sales in both cases. The figures 16 and 6, then 11,696 and 8, "
            "should each be explained as logical table sizes rather than scan counts."
        ),
    },
    "dax-051": {
        "draft": (
            "The starter asks for a replacement population and a preserved intersection. List"
            " the Sales lines with Quantity of at least 2 and their revenue, then predict all"
            " three forms when the report already filters Quantity to 1."
        ),
        "model": (
            "Six lines have Quantity of 2 or more: S1, S3, S4, S5, S7 and S8, together 163 "
            "USD. The other two, S2 and S6, have Quantity 1 and total 24. Sales[Quantity] is "
            "the column both the incoming filter and the predicate touch."
        ),
        "misconception": (
            "Rewriting FILTER(Sales, ...) as a plain column predicate is often recommended as"
            " a performance win, and on the unfiltered case all three forms agree at 163. "
            "That agreement is the trap. When the report already filters Quantity to 1, the "
            "table filter iterates only the visible lines, finds none with Quantity of at "
            "least 2, and returns BLANK. The column predicate replaces the incoming Quantity "
            "filter instead and returns 163, as if the report filter did not exist. "
            "KEEPFILTERS restores intersection and matches the table filter. A rewrite that "
            "turns BLANK into 163 is answering a different question."
        ),
        "check": (
            "Predict all three forms when the incoming filter is Quantity of 3 or more. Then "
            "add a product filter for Paper and repeat, explaining which form would mislead a"
            " user who selected both."
        ),
        "reference": (
            "Check that the reference evaluates the same three expressions in both cases and "
            "changes only the outer Quantity filter. The second row should read BLANK, 163 "
            "and BLANK, with the middle value explained by filter replacement."
        ),
    },
    "dax-052": {
        "draft": (
            "Predict North 2025 revenue, then the effect of ALL(Sales) and of removing the "
            "NetAmount filter alone."
        ),
        "model": (
            "North holds Ada and Cy. Their 2025 lines are S4 (27), S5 (20) and S8 (36), which"
            " total 83 USD."
        ),
        "misconception": (
            "ALL(Sales) looks like it clears only Sales, but its expanded table includes "
            "Customer and Date, so it returns 187 and loses the North and 2025 filters."
        ),
        "check": (
            "Predict REMOVEFILTERS(Customer) under the same filters and name which filter survives."
        ),
        "reference": (
            "Verify the reference's 83, 187 and 83, and its requested versus existing pairs "
            "of 2 and 1."
        ),
    },
    "dax-053": {
        "draft": (
            "The starter shows three supplied trial timings, 20, 21 and 19 ms. Compute their "
            "mean and median, then compute the same for the cold and warm sets in the first "
            "case, and label each as synthetic."
        ),
        "model": (
            "All timings in this lesson are invented scenario values. Cold trials are 100, "
            "120 and 110 ms; warm trials are 20, 25 and 21. Candidate A runs 20, 21 and 19; "
            "candidate B runs 18, 60 and 18."
        ),
        "misconception": (
            "Shown that B's best trial is 18 ms against A's 19, a reader may declare B "
            "faster. B's three trials include a 60 ms outlier, so its mean is 32 against A's "
            "20, even though its median of 18 beats A's 20. Best, median and mean answer "
            "different questions, and three trials support none of them for production. "
            "Comparing a cold run of one candidate with a warm run of another is worse still:"
            " the 110 versus 22 gap in the first case is cache state, not formula quality."
        ),
        "check": (
            "Replace B's 60 ms trial with 19 ms and recompute mean, median and best for B. "
            "Then state what evidence you would need before calling either candidate faster."
        ),
        "reference": (
            "Confirm that the reference computes mean, median and best for A and B from "
            "DATATABLE values and labels every column as synthetic. Your notes should explain"
            " why B wins on best and median yet loses on mean."
        ),
    },
    "dax-054": {
        "draft": (
            "The starter compares line-grain cost with a grouped rewrite. Compute line cost "
            "by multiplying each line's quantity by its product's UnitCost, then the grouped "
            "version per product, for the whole model and for North in 2025."
        ),
        "model": (
            "UnitCost is constant per product: 2 for the Notebook, 1 for the Pen and 5 for "
            "the Mug. Total units sold are 7, 5 and 5, so line-grain cost is 44 USD. North "
            "2025 holds S4 (3 Notebooks), S5 (4 Pens) and S8 (2 Mugs), for 6 plus 4 plus 10."
        ),
        "misconception": (
            "Matching results at 44 and again at 20 can feel like proof that the grouped "
            "rewrite is equivalent and should ship. It is evidence under one assumption: each"
            " product has exactly one UnitCost. The grouped form multiplies the summed "
            "quantity by MAX of the cost, which is exact only when the cost cannot vary "
            "within a product. If the model later stored a cost per transaction date, or two "
            "conflicting cost rows for the Mug, MAX would silently choose one and the totals "
            "would diverge with no error. A second mistake is treating parity as a "
            "performance result. The lesson shows only that the two expressions mean the same"
            " thing here; whether the rewrite is faster needs a measured comparison on "
            "representative data."
        ),
        "check": (
            "Suppose the Notebook's cost became 3 for 2025 lines only. Compute the true line-"
            "grain cost and the grouped result using MAX, and explain the gap."
        ),
        "reference": (
            "Verify that both reference cases return identical line and grouped costs, 44 and"
            " 20, and that the grouped form uses MAX over Product[UnitCost]. Your draft "
            "should state the constant-cost assumption that makes parity hold."
        ),
    },
    "dax-055": {
        "draft": (
            "The starter contrasts a fixed snapshot with a hypothetical later source. Predict"
            " both values from the checked-in Sales rows and the scenario's extra 10 USD "
            "event, and write which number you could defend as observed."
        ),
        "model": (
            "The fixture's eight Sales lines total 187 USD whether you call NetRevenue or "
            "iterate NetAmount directly. The later event in case B is scenario data only; it "
            "is not in the Sales CSV, and no source is connected."
        ),
        "misconception": (
            "When two reports disagree, storage mode is a frequent scapegoat: the DirectQuery"
            " report shows 197, the Import report shows 187, so Import must be wrong or stale"
            " in some mysterious way. In this lesson the measure is identical in both "
            "columns, and the 10 USD gap is entirely a refresh boundary: the snapshot was "
            "taken before the new event arrived. Calling DirectQuery real time truth makes "
            "the opposite mistake, because the source can itself be late, partially loaded or"
            " corrected. A third confusion is assuming every change adds an amount. If the "
            "later event corrected S8 from 36 to 30, the fresh figure would be 181, lower "
            "than the snapshot. Compare snapshot identity and timestamps before blaming the "
            "mode or the formula."
        ),
        "check": (
            "Rewrite case B so the later source corrects S5 from 20 to 15 instead of adding a"
            " sale. Predict both columns, then list the metadata a report would need to show "
            "the reader why they differ."
        ),
        "reference": (
            "Confirm that the reference returns 187 twice in case A and 187 and 197 in case "
            "B, with the extra 10 added explicitly as scenario arithmetic. Your notes should "
            "name the refresh boundary as the only difference."
        ),
    },
    "dax-056": {
        "draft": (
            "The starter wants visible revenue and revenue after an ordinary filter removal. "
            "For a North report filter, then for an enforced NorthViewer role, predict both "
            "columns and state which assumption each case makes."
        ),
        "model": (
            "This lesson uses the analytics model. North customers are Ada (51 USD) and Cy "
            "(56), so North revenue is 107; South is Bo alone at 80. Di, in the West, has no "
            "sales. Case B assumes an enforced role rather than demonstrating one."
        ),
        "misconception": (
            "Report authors sometimes publish a North page filter and treat it as access "
            "control because North users only ever see 107. Any query that can call "
            "REMOVEFILTERS on Customer gets 187 back, as case A shows, because the filter was"
            " a query choice, not a restriction on rows. Under a real role-restricted Viewer "
            "the same removal leaves 107, since the security context removes South rows "
            "before any measure evaluates. The second error is believing the expected 107 in "
            "case B proves the role works. It is a hand-derived expectation; only a test run "
            "under the actual identity and role in a compatible service can confirm it."
        ),
        "check": (
            "Predict both columns for an enforced SouthViewer role and for a South page "
            "filter without a role. Then describe the one test identity whose result would "
            "expose a filter posing as security."
        ),
        "reference": (
            "Verify that case A returns 107 then 187 and case B returns 107 twice, and that "
            "only case B depends on an assumed role. Your notes should keep the expected "
            "values separate from any claim of enforcement."
        ),
    },
    "dax-057": {
        "draft": (
            "The starter asks for permitted customers and visible revenue. Predict both for "
            "north.learner@example.test, south.learner@example.test and an unmapped "
            "principal, and record the default-deny assumption before reading the cases."
        ),
        "model": (
            "This lesson uses the analytics model. The synthetic Access table maps the north "
            "principal to North (Ada and Cy, 107 USD) and the south principal to South (Bo, "
            "80 USD). No principal maps to West, where Di sits."
        ),
        "misconception": (
            "An empty mapping can look like a bug to be fixed by granting everything, "
            "especially when a new user reports a blank dashboard. Under the declared policy,"
            " an unmapped principal sees no customers and BLANK revenue, and that denial is "
            "the correct outcome. Falling back to all regions would give a stranger 187 USD "
            "of data. Also note that securing Customer does not hide Access itself."
        ),
        "check": (
            "Add a mapping from the south principal to West as well. Predict permitted "
            "customers and revenue, and explain why the customer count changes while revenue "
            "does not."
        ),
        "reference": (
            "Confirm that the reference expects 2 customers and 107 for the north principal, "
            "and BLANK, BLANK and FALSE for the unmapped one."
        ),
    },
    "dax-058": {
        "draft": (
            "Predict core revenue, attributed refunds, adjusted revenue and converted foreign"
            " USD, then the Paper and Home budget variance for January and February 2025."
        ),
        "model": (
            "Returns link R1 (4 USD) to S2 and R2 (9 USD) to S4. Budget for the two months "
            "totals 165."
        ),
        "misconception": (
            "Adding the 270 foreign USD to the 174 adjusted core figure mixes populations; "
            "the budget covers core sales only."
        ),
        "check": (
            "Reconcile 2025 adjusted core revenue of 114 to its lines and refund, then "
            "explain the minus 51 variance."
        ),
        "reference": (
            "Verify 187, 13, 174 and 270, then 123, 9, 114, 165 and minus 51 in the reference."
        ),
    },
    "dax-059": {
        "draft": ("Predict assigned units, converted units and the unit-level rate per arm."),
        "model": ("U3 has two exposure events; U4 has none."),
        "misconception": ("Counting exposure events as units hides U4 from treatment."),
        "check": ("Add a U3 event and predict each column."),
        "reference": ("Confirm rates 0.5 and 1 per arm."),
    },
    "dax-060": {
        "draft": ("Predict revenue and cost for NorthViewer and SouthViewer."),
        "model": ("North costs 25 USD; South costs 19."),
        "misconception": ("Matching text is not deployment evidence."),
        "check": ("Reconcile 25 plus 19 to 44."),
        "reference": ("Confirm 107 and 25, then 80 and 19."),
    },
}

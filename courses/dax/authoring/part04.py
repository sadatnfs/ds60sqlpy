"""Stage four: deliberate filter policies, iterators and totals."""

from .common import lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        19,
        "KEEPFILTERS expresses an intersection policy",
        ["KEEPFILTERS", "intersection", "replacement", "selection policy"],
        ("Choose between forcing a value and respecting an existing selection on the same column."),
        (
            "The ordinary Boolean-filter behavior of CALCULATE "
            "replaces an existing selection on the same column. "
            "KEEPFILTERS changes that policy to intersection. It is "
            "not a universal instruction to preserve every report "
            "feature; it applies to the filter argument it wraps. "
            "Naming the policy makes a measure's interaction with user "
            "selections predictable.\n\nUnder an existing Blue "
            "selection, forcing Red gives Pen revenue 24. Keeping Blue "
            "while additionally requiring Red yields an empty product "
            "set because no product has both values in our fixture. "
            "BLANK is therefore a meaningful result, not a syntax "
            "failure. The measure is expressing 'Red within the "
            "current selection', rather than 'Red regardless of the "
            "selected color'.\n\nA broader current selection can still "
            "overlap the new restriction. If Blue and Red are "
            "selected, KEEPFILTERS(Blue) retains the blue subset and "
            "gives 163. This is useful for measures that quantify an "
            "interesting subgroup without silently expanding the "
            "population chosen by a learner or report user. Explain "
            "that contract in the metric name and tooltip."
        ),
        (
            "KEEPFILTERS wraps the Boolean condition inside CALCULATE. "
            "The outer CALCULATETABLE supplies a simulated selection "
            "for this named reference. In each case, enumerate the "
            "original allowed colors, intersect with the new set, then "
            "propagate the remaining product keys to Sales."
        ),
        [
            r(
                "A disjoint subgroup stays empty",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "ForcedRed", CALCULATE ( '
                    '[NetRevenue], Product[Color] = "Red" ), '
                    '"RedWithinSelection", CALCULATE ( [NetRevenue], '
                    'KEEPFILTERS ( Product[Color] = "Red" ) ) ), '
                    'Product[Color] = "Blue" )'
                ),
                [("ForcedRed", "number"), ("RedWithinSelection", "number")],
                [[24, None]],
                ("Original allowed color {Blue}; compare replacement with intersection by {Red}."),
                [
                    "Replacement changes the allowed set to Red and admits Pen.",
                    "Intersection computes {Blue} intersect {Red}, an empty set.",
                    "ForcedRed is 24; the selected-subgroup result is BLANK.",
                ],
                (
                    "An intersection measure should not escape its selected "
                    "population to manufacture a nonblank result."
                ),
            ),
            r(
                "An overlapping subgroup is retained",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "SelectedRevenue", '
                    '[NetRevenue], "BlueWithinSelection", CALCULATE ( '
                    '[NetRevenue], KEEPFILTERS ( Product[Color] = "Blue" ) ) '
                    '), Product[Color] IN { "Blue", "Red" } )'
                ),
                [("SelectedRevenue", "number"), ("BlueWithinSelection", "number")],
                [[187, 163]],
                (
                    "Original allowed colors {Blue, Red}; restrict to Blue "
                    "without expanding selection."
                ),
                [
                    "All products with recorded sales are Blue or Red, totaling 187.",
                    "Intersecting with Blue removes Pen's 24.",
                    "Notebook and Mug remain and total 163.",
                ],
                (
                    "KEEPFILTERS does not freeze the original total. It can "
                    "narrow a population while preserving the fact that the "
                    "starting selection is an outer constraint."
                ),
            ),
        ],
        [
            t(
                "Predict BlueWithinSelection if only Red is selected.",
                "Intersect the two color sets.",
                "It is BLANK because {Red} and {Blue} do not overlap.",
            ),
            t(
                "Replace the new subgroup by Color IN {Blue, Green}.",
                "Keep only colors also present in the original {Blue, Red} set.",
                "The intersection is Blue; Green does not get added. Revenue remains 163.",
            ),
            t(
                "Write a selected-subgroup measure for Trade customers.",
                "Wrap the condition defining the subgroup.",
                (
                    'CALCULATE([NetRevenue],KEEPFILTERS(Customer[Segment]="Trad'
                    'e")) retains only selected Trade customers.'
                ),
            ),
            t(
                "Diagnose changing KEEPFILTERS to a plain filter because blanks look untidy.",
                "That is a change of population policy.",
                (
                    "A disjoint selection would be replaced rather than "
                    "respected. Decide the intended metric before changing its "
                    "appearance."
                ),
            ),
            t(
                "Explain whether KEEPFILTERS restores a removed earlier filter.",
                "It intersects with the context that exists at its evaluation point.",
                (
                    "It does not remember arbitrary historical selections or "
                    "undo unrelated filter-removal operations."
                ),
            ),
            t(
                "Transfer the policy to a quality metric for failed events.",
                "Ask whether failure counts should remain inside the selected cohort.",
                (
                    "Intersect a failure subgroup with the selected cohort "
                    "when reporting failures among that population; label any "
                    "intentionally global failure metric separately."
                ),
            ),
        ],
        sources=["https://learn.microsoft.com/en-us/dax/keepfilters-function-dax"],
    ),
    lesson(
        20,
        "REMOVEFILTERS and the exact denominator population",
        ["REMOVEFILTERS", "denominator scope", "column versus table", "share"],
        "State which filters a share denominator removes and which it retains.",
        (
            "A share is not defined by the word percent. Its "
            "denominator might be the category, the selected products, "
            "all catalog products, a region or the entire model. "
            "REMOVEFILTERS makes one part of that population change "
            "explicit. Removing Color leaves Category in place; "
            "removing the Product table clears its product attributes "
            "while an independent Customer filter can remain.\n\nThis "
            "difference explains apparently inconsistent percentages. "
            "Notebook's 67 is about 73.6 percent of Paper's 91, but it "
            "is about 35.8 percent of all revenue 187. Neither "
            "percentage is inherently the correct one. The correct "
            "denominator follows the business question, which must be "
            "written before the formula.\n\nA broad table modifier can "
            "have consequences beyond one visible column because model "
            "relationships and expanded-table semantics matter. Begin "
            "with narrow dimension modifiers when that is the intended "
            "scope. Do not remove filters from a large fact table as "
            "an unexplained shortcut to 'all data'. The advanced model "
            "lessons examine cases where that shortcut changes more "
            "than expected."
        ),
        (
            "The numerator uses the current context. The denominator "
            "reevaluates [NetRevenue] after removing only the named "
            "filters. DIVIDE preserves undefined ratios as BLANK. "
            "Customer filters are not removed by the Product-only "
            "modifier in the second case."
        ),
        [
            r(
                "Share within the retained category",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Numerator", '
                    '[NetRevenue], "CategoryDenominator", CALCULATE ( '
                    "[NetRevenue], REMOVEFILTERS ( Product[Color] ) ), "
                    '"Share", DIVIDE ( [NetRevenue], CALCULATE ( [NetRevenue], '
                    "REMOVEFILTERS ( Product[Color] ) ) ) ), Product[Category] "
                    '= "Paper", Product[Color] = "Blue" )'
                ),
                [("Numerator", "number"), ("CategoryDenominator", "number"), ("Share", "number")],
                [[67, 91, 67 / 91]],
                "Paper and Blue selected; remove only Color in the denominator.",
                [
                    "The numerator contains Notebook: 67.",
                    "Removing Color restores Pen within Paper, giving 67 + 24 = 91.",
                    "The share is 67/91; Home remains outside the category population.",
                ],
                (
                    "The denominator does not become 187 because the Category "
                    "filter was deliberately retained."
                ),
            ),
            r(
                "All products within North",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Numerator", '
                    '[NetRevenue], "RegionalDenominator", CALCULATE ( '
                    '[NetRevenue], REMOVEFILTERS ( Product ) ), "Share", '
                    "DIVIDE ( [NetRevenue], CALCULATE ( [NetRevenue], "
                    "REMOVEFILTERS ( Product ) ) ) ), Product[Category] = "
                    '"Paper", Product[Color] = "Blue", Customer[Region] = '
                    '"North" )'
                ),
                [("Numerator", "number"), ("RegionalDenominator", "number"), ("Share", "number")],
                [[47, 107, 47 / 107]],
                ("Paper, Blue and North selected; remove Product filters only in the denominator."),
                [
                    "North Notebook sales are S1 and S4: 47.",
                    (
                        "Removing Product restrictions admits North Pen 24? In "
                        "North Pen contributes S2 4 plus S5 20, totaling 24, and "
                        "Mug contributes 36."
                    ),
                    "The retained North population totals 47 + 24 + 36 = 107; share is 47/107.",
                ],
                (
                    "An 'all products' denominator can still be regional and "
                    "temporal. The model does not interpret the word all as an "
                    "instruction to remove every other dimension."
                ),
            ),
        ],
        [
            t(
                "Predict case A after removing the entire Product table instead of Color.",
                "No other dimension filters exist in that case.",
                "The denominator becomes 187 and the share becomes 67/187.",
            ),
            t(
                "Restrict case B to year 2025.",
                "Keep the year in both numerator and denominator.",
                (
                    "The numerator is 27 and the North-year denominator is 83, "
                    "so the share is 27/83."
                ),
            ),
            t(
                "Write the denominator contract in plain language before coding.",
                "Name both removed and retained filters.",
                (
                    "For case B: all products among North customers, within "
                    "any other unchanged date or report constraints."
                ),
            ),
            t(
                "Diagnose a 100-percent share produced by a frozen denominator variable.",
                "Recall where the scalar was bound.",
                (
                    "Removing filters around a precomputed scalar does not "
                    "reevaluate revenue. Bind "
                    "CALCULATE([NetRevenue],REMOVEFILTERS(...)) instead."
                ),
            ),
            t(
                "Explain the denominator for a selected unsold product.",
                "A blank numerator and a valid broader population are different facts.",
                (
                    "The numerator may remain BLANK even with a positive "
                    "denominator. Decide whether the display should expose "
                    "absence or coalesce it deliberately."
                ),
            ),
            t(
                "Transfer the pattern to a departmental cost share.",
                "Retain the relevant company, currency and period.",
                (
                    "Remove the department selection only if the denominator "
                    "should cover all departments in that same compatible "
                    "population."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/removefilters-function-dax",
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
        ],
    ),
    lesson(
        21,
        "SUMX and AVERAGEX choose both an expression and a population",
        ["SUMX", "AVERAGEX", "row expression", "blank exclusion", "weighting"],
        "Derive an iterator result and explain how blank rows affect its denominator.",
        (
            "An iterator evaluates an expression for each row of a "
            "table. SUMX adds those scalar results; AVERAGEX averages "
            "the numerical results it includes. The input table "
            "therefore determines the weighting unit. Iterating sales "
            "lines, products or customers can give different results "
            "even when the expression's name contains the same "
            "business word.\n\nSUMX is appropriate when the additive "
            "amount must be calculated from several row columns. "
            "Quantity times UnitPrice minus a line discount is such an "
            "expression. A stored NetAmount column can instead be "
            "summed directly when its contract is trusted. Neither "
            "form is automatically faster for every model; establish "
            "semantic equivalence before measuring.\n\nBlank handling "
            "changes averages. Product-level [NetRevenue] is blank for "
            "Bag, so averaging that measure over Product averages the "
            "three nonblank product results. Coalescing Bag's value to "
            "zero includes a fourth number and lowers the average. "
            "Both computations are valid expressions, but they answer "
            "different questions about the catalog population."
        ),
        (
            "Inside SUMX(Sales,...), Sales columns refer to the "
            "current line. Inside AVERAGEX(Product,[NetRevenue]), the "
            "model measure transitions each Product row before "
            "evaluating its sales. COALESCE changes the value supplied "
            "to the averaging operation and therefore the effective "
            "numerical denominator."
        ),
        [
            r(
                "Calculate additive row amounts",
                (
                    'EVALUATE ROW ( "Gross", SUMX ( Sales, Sales[Quantity] * '
                    'Sales[UnitPrice] ), "Net", SUMX ( Sales, Sales[Quantity] '
                    "* Sales[UnitPrice] - Sales[Discount] ) )"
                ),
                [("Gross", "number"), ("Net", "number")],
                [[195, 187]],
                "All eight Sales rows; Discount is a currency amount per line.",
                [
                    "The line gross amounts are 20, 5, 40, 30, 20, 20, 20 and 40.",
                    "Their sum is 195; the line discounts sum to 8.",
                    "Subtracting each line's discount yields net total 187.",
                ],
                (
                    "If Discount represented a percentage or per-unit amount, "
                    "this expression would be wrong even though its arithmetic "
                    "is valid. The data dictionary is part of the formula "
                    "contract."
                ),
            ),
            r(
                "Average sold products or the complete catalog",
                (
                    'EVALUATE ROW ( "NonblankProducts", AVERAGEX ( Product, '
                    '[NetRevenue] ), "AllCatalogProducts", AVERAGEX ( Product, '
                    "COALESCE ( [NetRevenue], 0 ) ) )"
                ),
                [("NonblankProducts", "number"), ("AllCatalogProducts", "number")],
                [[187 / 3, 187 / 4]],
                "All four Product rows; Bag has no sales and a blank revenue measure.",
                [
                    "Per-product results are 67, 24, 96 and BLANK.",
                    "AVERAGEX over the nonblank numerical results divides 187 by 3.",
                    "COALESCE changes Bag to zero, so the average divides 187 by 4.",
                ],
                (
                    "The lower second average reflects a broader denominator, "
                    "not worse arithmetic. Label the population as sold "
                    "products or all catalog products."
                ),
            ),
        ],
        [
            t(
                "Predict the net amount if each line's discount is subtracted twice.",
                "Total discounts are 8.",
                "The incorrect total would be 195 - 16 = 179.",
            ),
            t(
                "Filter to Blue before calculating gross and net.",
                "Exclude the red Pen lines.",
                "Gross is 170 and net is 163; blue-line discounts total 7.",
            ),
            t(
                "Write a customer-level average revenue for customers with sales.",
                "AVERAGEX can iterate Customer while the measure supplies transition.",
                (
                    "AVERAGEX(Customer,[NetRevenue]) averages 51,80,56 and "
                    "excludes Di's BLANK, yielding 187/3."
                ),
            ),
            t(
                "Diagnose calling the mean product revenue an average unit price.",
                "Its denominator is products, not units.",
                (
                    "AVERAGEX(Product,[NetRevenue]) is USD per contributing "
                    "product. Net unit price is 187/17 = 11."
                ),
            ),
            t(
                "Explain what adding another unsold catalog product does to the two averages.",
                "One expression excludes its blank; the other includes zero.",
                (
                    "The nonblank average stays 187/3; the zero-filled catalog "
                    "average becomes 187/5."
                ),
            ),
            t(
                "Transfer the choice to average regional performance.",
                "Decide whether regions or underlying customers receive equal weight.",
                (
                    "An equal-region average and a pooled customer-weighted "
                    "rate answer different questions; state the estimand "
                    "before selecting the iterator."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/sumx-function-dax",
            "https://learn.microsoft.com/en-us/dax/averagex-function-dax",
        ],
    ),
    lesson(
        22,
        "Variables inside and outside an iterator",
        ["variable scope", "iterator body", "implicit transition", "shared scalar"],
        ("Locate a variable's binding context and avoid repeating one total for every member."),
        (
            "A variable outside an iterator can hold one scalar for "
            "the entire iterator. A variable declared in the "
            "iterator's expression can be bound separately for each "
            "row. The difference is easy to miss when both variables "
            "are named Revenue. Use names that expose whether the "
            "value is a global total, an incoming-context total or a "
            "current-member result.\n\nWith no filters, a variable bound "
            "to [NetRevenue] is 187. Summing that value once per "
            "Product row yields 748 because Product has four rows. "
            "Defining the variable inside SUMX(Product,...) instead "
            "invokes the measure for each row, giving 67,24,96 and "
            "BLANK, which sum to 187.\n\nOuter filters still matter "
            "before either binding. In Paper there are two Product "
            "rows and the incoming total is 91. A shared scalar is "
            "repeated twice to give 182, while per-product binding "
            "sums 67 and 24 to 91. A variable can improve readability "
            "without preserving the intended meaning if moved across "
            "an evaluation boundary."
        ),
        (
            "The first named variable is outside SUMX; the second is "
            "declared after the iterator's table argument, inside its "
            "scalar expression. RETURN ends that inner variable block. "
            "This is a scope distinction, not a mutable assignment "
            "updated by each loop iteration."
        ),
        [
            r(
                "One shared total versus one value per product",
                (
                    "EVALUATE\nVAR IncomingRevenue = [NetRevenue]\nRETURN ROW ( "
                    '"SharedScalarSum", SUMX ( Product, IncomingRevenue ), '
                    '"PerProductSum", SUMX ( Product, VAR ProductRevenue = '
                    "[NetRevenue] RETURN ProductRevenue ) )"
                ),
                [("SharedScalarSum", "number"), ("PerProductSum", "number")],
                [[748, 187]],
                "No outer filters; four Product rows, including unsold Bag.",
                [
                    "IncomingRevenue is bound once to 187.",
                    "The shared scalar contributes 187 on four iterations, totaling 748.",
                    (
                        "The inner measure binding transitions each product and "
                        "sums 67 + 24 + 96 = 187."
                    ),
                ],
                (
                    "The shared value is not blank for Bag because it was "
                    "never evaluated for Bag. Variable movement can therefore "
                    "change both population and missing-value behavior."
                ),
            ),
            r(
                "An incoming filtered total is still shared",
                (
                    "EVALUATE CALCULATETABLE ( VAR IncomingRevenue = "
                    '[NetRevenue] RETURN ROW ( "SharedScalarSum", SUMX ( '
                    'Product, IncomingRevenue ), "PerProductSum", SUMX ( '
                    "Product, VAR ProductRevenue = [NetRevenue] RETURN "
                    'ProductRevenue ) ), Product[Category] = "Paper" )'
                ),
                [("SharedScalarSum", "number"), ("PerProductSum", "number")],
                [[182, 91]],
                (
                    "Paper is established before either variable binding; "
                    "Product has two eligible rows."
                ),
                [
                    "The incoming measure total is 91.",
                    "An outer scalar is reused for Notebook and Pen, giving 182.",
                    "Binding inside the iterator evaluates 67 and 24 separately, totaling 91.",
                ],
                (
                    "Context is not simply filtered versus unfiltered. The "
                    "exact point at which a scalar is bound determines which "
                    "filtered total gets repeated."
                ),
            ),
        ],
        [
            t(
                "Predict the shared-scalar sum under Home.",
                "Home has one Product row.",
                (
                    "It is 96, coincidentally equal to the correct result. A "
                    "one-member test hides the bug."
                ),
            ),
            t(
                "Add a second unsold product to the unfiltered model.",
                "The shared scalar contributes on every dimension row.",
                (
                    "The incorrect sum rises to 5 * 187 = 935 while the "
                    "per-product additive total remains 187."
                ),
            ),
            t(
                "Write an iterator whose variable intentionally holds one global denominator.",
                "Only the denominator should be shared; the numerator should vary per member.",
                (
                    "Bind a deliberate total outside, then evaluate each "
                    "member's [NetRevenue] inside and DIVIDE by that total."
                ),
            ),
            t(
                "Diagnose a refactor that moves all variables above SUMX for readability.",
                "Readability does not override evaluation scope.",
                (
                    "Move only expressions intended to be invariant. Keep "
                    "row-dependent measure bindings in the iterator body."
                ),
            ),
            t(
                "Explain why the variables are not updated mutable loop counters.",
                "VAR is a binding within expression scope.",
                (
                    "Each inner evaluation binds its own value; there is no "
                    "assignment that mutates one outer variable across "
                    "iterations."
                ),
            ),
            t(
                "Transfer the lesson to allocating a shared monthly target.",
                "Distinguish an invariant target from per-member weights.",
                (
                    "Keep the target and validated weight denominator shared, "
                    "but compute each member's weight in the appropriate "
                    "row/filter context."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/var-dax",
            "https://learn.microsoft.com/en-us/dax/sumx-function-dax",
        ],
    ),
    lesson(
        23,
        "Grand totals reevaluate the measure",
        ["grand total", "subtotal", "nonadditive measure", "ratio", "reevaluation"],
        (
            "Reconcile row values and a grand-total ratio without "
            "forcing the total to sum visible cells."
        ),
        (
            "A total is another evaluation of the measure in a broader "
            "context. For additive revenue, that reevaluation often "
            "equals the sum of disjoint visible rows. For a ratio, "
            "distinct count, median or closing balance, it need not. A "
            "total that differs from the sum of row values is not "
            "automatically a broken total.\n\nPaper has revenue 91 and "
            "12 units, giving about 7.5833 USD per unit. Home has 96 "
            "and 5 units, giving 19.2. The whole population has "
            "revenue 187 and 17 units, giving 11. Adding the two row "
            "ratios produces about 26.7833, which has no sensible "
            "interpretation as the pooled price per unit.\n\nIf a "
            "business requirement truly asks for a sum or "
            "equal-weighted mean of displayed group results, express "
            "that separate measure with an explicit group iterator and "
            "label it accordingly. Do not overwrite a correct pooled "
            "ratio just to imitate a spreadsheet total. First identify "
            "the unit of each displayed number and the estimand at the "
            "total level."
        ),
        (
            "SUMMARIZECOLUMNS builds category groups and evaluates the "
            "named measures for each. Rows for which every supplied "
            "expression is BLANK are omitted, so unsold Travel does "
            "not appear here. The second query compares the pooled "
            "ratio with an explicitly summed category-ratio "
            "expression. The two outputs intentionally have different "
            "definitions."
        ),
        [
            r(
                "Category-level prices",
                (
                    'EVALUATE SUMMARIZECOLUMNS ( Product[Category], "Revenue", '
                    '[NetRevenue], "Units", [QuantitySold], "NetPerUnit", '
                    "DIVIDE ( [NetRevenue], [QuantitySold] ) )\nORDER BY "
                    "Product[Category]"
                ),
                [
                    ("Category", "text"),
                    ("Revenue", "number"),
                    ("Units", "integer"),
                    ("NetPerUnit", "number"),
                ],
                [["Home", 96, 5, 19.2], ["Paper", 91, 12, 91 / 12]],
                (
                    "One group per Category; no outer filters; all-blank "
                    "Travel group omitted by this summary."
                ),
                [
                    "Home contributes 96 over 5 units.",
                    "Paper contributes 91 over 12 units.",
                    "Each ratio describes its own category population.",
                ],
                (
                    "The two categories have different unit counts. An "
                    "equal-weight operation over the ratios would change the "
                    "weighting unit from sold units to categories."
                ),
            ),
            r(
                "The total and an intentionally different measure",
                (
                    'EVALUATE ROW ( "PooledNetPerUnit", DIVIDE ( [NetRevenue], '
                    '[QuantitySold] ), "SumOfCategoryRatios", SUMX ( VALUES ( '
                    "Product[Category] ), DIVIDE ( [NetRevenue], "
                    "[QuantitySold] ) ) )"
                ),
                [("PooledNetPerUnit", "number"), ("SumOfCategoryRatios", "number")],
                [[11, 19.2 + 91 / 12]],
                (
                    "No category grouping for the pooled total; a separate "
                    "iterator explicitly sums category ratios."
                ),
                [
                    "The pooled measure reevaluates 187/17 and returns 11.",
                    "The iterator evaluates 19.2 and 91/12 for the two nonblank categories.",
                    "Their sum is about 26.7833, a different defined calculation.",
                ],
                (
                    "The contrast is a useful review test: a total-row formula "
                    "should reflect the intended definition, not merely "
                    "resemble the visual's arithmetic layout."
                ),
            ),
        ],
        [
            t(
                "Derive the pooled ratio as a weighted average of the two category ratios.",
                "Use their unit counts as weights.",
                "(19.2 * 5 + (91/12) * 12) / 17 = 11.",
            ),
            t(
                "Filter the model to Paper only.",
                "There is now one contributing category.",
                (
                    "The pooled ratio and sum of category ratios both equal "
                    "91/12. This restricted test does not establish general "
                    "equivalence."
                ),
            ),
            t(
                "Write a separately named equal-category average.",
                "Choose category weighting intentionally.",
                (
                    "AVERAGEX(VALUES(Product[Category]),DIVIDE([NetRevenue],[Qu"
                    "antitySold])) averages the two nonblank ratios equally; "
                    "label it accordingly."
                ),
            ),
            t(
                "Diagnose changing a distinct-customer total to SUMX over categories.",
                "Customers can belong to several category populations.",
                (
                    "That counts customer-category memberships rather than "
                    "unique customers. A matching visual row sum does not "
                    "preserve the metric."
                ),
            ),
            t(
                "Explain why Travel is absent from the first table.",
                "All three expressions are blank for its empty fact population.",
                (
                    "SUMMARIZECOLUMNS omits that all-blank result row. A "
                    "SELECTCOLUMNS projection or zero-filled measure can have "
                    "different row-retention behavior."
                ),
            ),
            t(
                "Transfer total reasoning to inventory at month end.",
                "A balance is additive across products but generally not across dates.",
                (
                    "The total over time should use the intended closing or "
                    "average-balance definition, not sum all snapshots."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/summarizecolumns-function-dax",
            "https://learn.microsoft.com/en-us/dax/divide-function-dax",
        ],
    ),
    lesson(
        24,
        "Selected totals and the limits of ALLSELECTED intuition",
        ["ALLSELECTED", "visual total", "query grouping", "outer selection", "shadow context"],
        (
            "Differentiate share of an explicitly selected population "
            "from share of all model products."
        ),
        (
            "ALLSELECTED is useful for selected or visual totals, but "
            "it is not a command that reads pixels from a report. Its "
            "behavior depends on query and evaluation contexts. In the "
            "named query below, an outer filter selects Notebook and "
            "Pen, while SUMMARIZECOLUMNS creates one result row for "
            "each selected product. Removing the current grouping "
            "effect while retaining the outer selection yields a "
            "selected denominator of "
            "91.\n\nREMOVEFILTERS(Product[Product]) expresses a "
            "different policy: it removes that product-name "
            "restriction, including the outer selection in this "
            "example, giving denominator 187. Shares of 67/91 and "
            "24/91 sum to one across the selected products. Shares of "
            "67/187 and 24/187 describe their contribution to a larger "
            "population and need not sum to one within the visible "
            "subset.\n\nDo not generalize this simple query into a rule "
            "that ALLSELECTED always means the current slicer. "
            "Iterators can introduce shadow filter contexts, and "
            "nested evaluations can change which context is restored. "
            "When designing a visual-total calculation, specify the "
            "exact query shape, selected domain and grouping columns. "
            "Advanced reuse should preserve that contract rather than "
            "inserting ALLSELECTED into an arbitrary iterator."
        ),
        (
            "Both cases use the same outer product-name selection and "
            "grouping. The first denominator uses ALLSELECTED on the "
            "grouping column. The second uses REMOVEFILTERS on that "
            "column. No year or region filters are present; if they "
            "were, their treatment would need to be stated separately."
        ),
        [
            r(
                "Share of the selected product set",
                (
                    "EVALUATE CALCULATETABLE ( SUMMARIZECOLUMNS ( "
                    'Product[Product], "Revenue", [NetRevenue], '
                    '"SelectedTotal", CALCULATE ( [NetRevenue], ALLSELECTED ( '
                    'Product[Product] ) ), "Share", DIVIDE ( [NetRevenue], '
                    "CALCULATE ( [NetRevenue], ALLSELECTED ( Product[Product] "
                    ') ) ) ), Product[Product] IN { "Notebook", "Pen" } '
                    ")\nORDER BY Product[Product]"
                ),
                [
                    ("Product", "text"),
                    ("Revenue", "number"),
                    ("SelectedTotal", "number"),
                    ("Share", "number"),
                ],
                [["Notebook", 67, 91, 67 / 91], ["Pen", 24, 91, 24 / 91]],
                (
                    "Outer selection {Notebook, Pen}; query groups by "
                    "Product.Product; no nested iterator in the measure."
                ),
                [
                    "The outer selected population totals 67 + 24 = 91.",
                    "Each product group supplies its own numerator.",
                    (
                        "ALLSELECTED removes this grouping restriction while "
                        "preserving the named outer selection."
                    ),
                ],
                (
                    "The sum of the two shares is one because the displayed "
                    "groups partition this selected population. That "
                    "conclusion depends on this exact denominator and query "
                    "shape."
                ),
            ),
            r(
                "Share of all products instead",
                (
                    "EVALUATE CALCULATETABLE ( SUMMARIZECOLUMNS ( "
                    'Product[Product], "Revenue", [NetRevenue], '
                    '"AllProductTotal", CALCULATE ( [NetRevenue], '
                    'REMOVEFILTERS ( Product[Product] ) ), "Share", DIVIDE ( '
                    "[NetRevenue], CALCULATE ( [NetRevenue], REMOVEFILTERS ( "
                    "Product[Product] ) ) ) ), Product[Product] IN { "
                    '"Notebook", "Pen" } )\nORDER BY Product[Product]'
                ),
                [
                    ("Product", "text"),
                    ("Revenue", "number"),
                    ("AllProductTotal", "number"),
                    ("Share", "number"),
                ],
                [["Notebook", 67, 187, 67 / 187], ["Pen", 24, 187, 24 / 187]],
                (
                    "Same selected rows; the denominator removes the "
                    "Product.Product restriction entirely."
                ),
                [
                    "The visible numerators remain 67 and 24.",
                    "The denominator includes Mug's 96 as well, totaling 187.",
                    "The selected rows' shares sum to 91/187, not one.",
                ],
                (
                    "This can be exactly the intended comparison to the full "
                    "catalog. A chart should label the denominator so a "
                    "partial sum is not mistaken for an error."
                ),
            ),
        ],
        [
            t(
                "Predict selected shares when only Notebook is selected.",
                "The selected denominator becomes the same product population.",
                (
                    "Notebook's selected share is 1; its all-product share "
                    "remains 67/187 in the stated otherwise-unfiltered context."
                ),
            ),
            t(
                "Select Notebook and Mug instead.",
                "The selected denominator is their sum.",
                "The selected total is 163 and their shares are 67/163 and 96/163.",
            ),
            t(
                "Write a denominator specification for a chart with a year slicer.",
                "Decide whether year remains part of the selected population.",
                (
                    "State that product selection/grouping changes while the "
                    "chosen year remains; then verify the exact query rather "
                    "than inferring from the chart's appearance."
                ),
            ),
            t(
                "Diagnose calling ALLSELECTED inside an arbitrary nested SUMX.",
                "An iterator can change the available shadow context.",
                (
                    "The simple selected-total derivation no longer proves the "
                    "nested expression. Trace that iterator or bind a "
                    "deliberate denominator before it."
                ),
            ),
            t(
                (
                    "Explain whether rows hidden by a visual necessarily "
                    "disappear from the denominator."
                ),
                "Separate display behavior from query/filter context.",
                (
                    "Not necessarily. State and inspect the actual grouping, "
                    "filter and measure context instead of reasoning only from "
                    "visible pixels."
                ),
            ),
            t(
                "Transfer the distinction to a selected cohort versus all assigned units.",
                "A denominator change changes the question.",
                (
                    "Both selected-cohort and all-assignment rates can be "
                    "meaningful, but the population and exclusion policy must "
                    "be explicit and consistent."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/allselected-function-dax",
            "https://learn.microsoft.com/en-us/dax/summarizecolumns-function-dax",
            "https://learn.microsoft.com/en-us/dax/removefilters-function-dax",
        ],
    ),
]

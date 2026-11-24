"""Stage four: deliberate filter policies, iterators and totals."""

from .common import explain, lesson
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
                        "Removing Product restrictions admits the other North products: "
                        "Pen contributes S2 4 plus S5 20, totaling 24, and "
                        "Mug contributes S8 36."
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
                    "AVERAGEX(Customer,[NetRevenue]) averages 51, 80, 56 and "
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
            "invokes the measure for each row, giving 67, 24, 96 and "
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


REASONING = {
    19: [
        (
            (
                "KEEPFILTERS intersects the new Blue condition with the existing Red selection. "
                "The two color sets share nothing, so no product remains and revenue is BLANK."
            ),
            (
                "A plain Blue filter replaces Red and returns 163 inside a Red-only report, "
                "showing a number for products the user never selected."
            ),
            (
                "Under Red, SelectedRevenue is 24, the KEEPFILTERS version is BLANK and the plain "
                "version is 163."
            ),
        ),
        (
            (
                "The intersection of {Blue, Green} with the selected {Blue, Red} is {Blue}, so "
                "Notebook and Mug remain and revenue is 163."
            ),
            (
                "A plain IN filter replaces the selection with Blue and Green and adds Bag. "
                "Revenue still reads 163 because Bag has no sales, so revenue alone cannot show "
                "the error."
            ),
            (
                "Count products instead: COUNTROWS(Product) is 2 with KEEPFILTERS and 3 with the "
                "plain filter."
            ),
        ),
        (
            (
                "Cy (key 30) is the only Trade customer, at 56. KEEPFILTERS keeps Trade only where "
                "the user's segment selection allows it."
            ),
            (
                "A plain Segment filter under a Retail slicer replaces Retail and shows Cy's 56, a "
                "Trade number in a Retail view."
            ),
            (
                "Under Segment = Retail the KEEPFILTERS version is BLANK and the plain one is 56. "
                "With no segment filter both return 56."
            ),
        ),
        (
            (
                "BLANK in RedWithinSelection says that Red lies outside the selected Blue "
                "products. That is the intended population rule, not a display flaw."
            ),
            (
                "Switching to a plain filter fills the cell with ForcedRed's 24, so a Blue-only "
                "report then shows Pen revenue the user excluded."
            ),
            (
                "Case A shows the two policies side by side: 24 for replacement and BLANK for "
                "intersection under the same Blue selection."
            ),
        ),
        (
            (
                "KEEPFILTERS intersects with the context that exists when it is applied. If an "
                "outer REMOVEFILTERS(Product[Color]) has already cleared Red, nothing is left to "
                "intersect."
            ),
            (
                "Expecting the user's earlier Red choice to come back predicts BLANK. The color "
                "filter is gone, so the KEEPFILTERS Blue condition returns 163."
            ),
            (
                "Under Red, `CALCULATE ( CALCULATE ( [NetRevenue], KEEPFILTERS ( Product[Color] = "
                '"Blue" ) ), REMOVEFILTERS ( Product[Color] ) )` returns 163.'
            ),
        ),
        (
            (
                "With a discounted line standing in for a failed event, count flagged lines inside "
                "the selected cohort. North has five lines (S1, S2, S4, S5, S8), and three of them "
                "(S2, S4 and S8) carry a discount, a rate of 0.6."
            ),
            (
                "`FILTER ( ALL ( Sales ), Sales[Discount] > 0 )` ignores the cohort and returns 3 "
                "under every region, so South looks discounted although Bo's lines had none."
            ),
            (
                "The cohort version returns 3 under North and BLANK under South; the global "
                "version, labeled as global, returns 3 everywhere."
            ),
        ),
    ],
    20: [
        (
            (
                "REMOVEFILTERS(Product) clears both Category and Color. With no other filters, the "
                "denominator becomes all sales, 187, and the share is 67 / 187, about 0.358."
            ),
            (
                "Treating table removal as the same as removing Color keeps expecting 91, so the "
                "label would still say share of Paper."
            ),
            (
                "The row reads Numerator 67, denominator 187 and Share about 0.3583, compared with "
                "0.7363 in case A."
            ),
        ),
        (
            (
                "The year filter is not removed, so it applies to both parts. North Blue Paper in "
                "2025 is S4 alone (27), and North 2025 is 83, for about 0.325."
            ),
            (
                "Also removing the Date filter in the denominator uses all-years North, 107, and "
                "gives 27 / 107, about 0.252, a ratio across different periods."
            ),
            "Expect Numerator 27, RegionalDenominator 83 and Share about 0.3253.",
        ),
        (
            (
                "The contract is: all products bought by North customers, with every other filter "
                "unchanged. The numerator is Notebook's North lines S1 and S4 (47) and the "
                "denominator is 107."
            ),
            (
                "Writing the contract as all sales leads to REMOVEFILTERS() or ALL, a denominator "
                "of 187 and a share of about 0.251 that ignores the region."
            ),
            (
                "Case B returns numerator 47, denominator 107 and share about 0.4393, and each "
                "removed and kept filter appears in the written contract."
            ),
        ),
        (
            (
                "The denominator must be CALCULATE([NetRevenue], REMOVEFILTERS(Product[Color])) "
                "evaluated in place, which returns 91 under Paper and Blue."
            ),
            (
                "Binding `VAR D = [NetRevenue]` under Paper and Blue holds 67. Wrapping D in "
                "REMOVEFILTERS keeps 67, and the share reads exactly 1."
            ),
            (
                "Show the denominator as its own column: 91 is correct and 67 means it is frozen. "
                "The share should be about 0.7363."
            ),
        ),
        (
            (
                "Bag (key 4) has no sales, so its numerator is BLANK. With no other filters a "
                "REMOVEFILTERS(Product) denominator is 187, and case A's color-only removal leaves "
                "Travel, also BLANK. DIVIDE returns BLANK, which correctly says nothing was sold."
            ),
            (
                "Treating the BLANK share as a denominator bug sends you to debug a healthy 187. "
                "Coalescing it to 0 without saying so hides the difference between unsold and sold "
                "at zero."
            ),
            (
                "Under ProductKey 4 with the table-level removal, the numerator is BLANK, the "
                "denominator 187 and the share BLANK; a deliberate COALESCE shows 0."
            ),
        ),
        (
            (
                "For a category cost share within a year, remove only Category. In 2025 Paper cost "
                "is Notebook 5 x 2 plus Pen 4 x 1, or 14, out of 29 in total, about 0.483."
            ),
            (
                "Removing all filters in the denominator uses the all-years cost of 44, so Paper's "
                "2025 share drops to 14 / 44, about 0.318."
            ),
            "Under 2025, Paper 14 / 29 and Home (Mug, 3 x 5 = 15) 15 / 29 add to 1.",
        ),
    ],
    21: [
        (
            (
                "Discount is a currency amount per line, so each line is Quantity x UnitPrice "
                "minus Discount, once. The discounts are S2 1, S4 3 and S8 4, which add to 8."
            ),
            (
                "Subtracting SUM(Sales[Discount]) again after a SUMX that already subtracted it "
                "removes 16 and returns 179."
            ),
            "Net is 187, and S8 alone checks as 2 x 20 - 4 = 36.",
        ),
        (
            (
                "Blue keeps Notebook and Mug, lines S1, S3, S4, S6, S7 and S8. Their gross is 170, "
                "their discounts are S4 3 and S8 4, and net is 163."
            ),
            (
                "Treating Discount as a rate, Quantity x UnitPrice x (1 - Discount), turns S4 into "
                "30 x (1 - 3) = -60 and S8 into -120, which are impossible line amounts."
            ),
            (
                "Under Blue expect Gross 170 and Net 163; the difference, 7, equals the Blue "
                "discounts."
            ),
        ),
        (
            (
                "AVERAGEX over Customer transitions each row, so it averages Ada 51, Bo 80 and Cy "
                "56. Di's BLANK is skipped, which gives 187 / 3, about 62.33."
            ),
            (
                "DIVIDE([NetRevenue], COUNTROWS(Customer)) counts Di and returns 46.75. "
                "AVERAGE(Sales[NetAmount]) gives 23.375, which is revenue per line, not per "
                "customer."
            ),
            (
                "Expect about 62.33, and a matching DIVIDE ( [NetRevenue], DISTINCTCOUNT ( "
                "Sales[CustomerKey] ) )."
            ),
        ),
        (
            (
                "AVERAGEX(Product, [NetRevenue]) divides 187 by three selling products, so it is "
                "62.33 USD per product. A unit price divides revenue by units: 187 / 17 = 11."
            ),
            (
                "Labeling 62.33 an average unit price overstates it more than five times, since "
                "its denominator counts products, not the 17 units sold."
            ),
            (
                "`DIVIDE ( [NetRevenue], SUM ( Sales[Quantity] ) )` returns 11, while the product "
                "average stays about 62.33."
            ),
        ),
        (
            (
                "AVERAGEX skips BLANK, so a new unsold product changes nothing in the nonblank "
                "average, 187 / 3. COALESCE turns it into a 0, so the catalog average becomes 187 "
                "/ 5 = 37.4."
            ),
            (
                "Expecting both averages to stay put misses that the zero-filled version counts "
                "every catalog member, as it already does for Bag (187 / 4 = 46.75)."
            ),
            (
                "Today the results are about 62.33 and 46.75. With one more unsold product expect "
                "about 62.33 and 37.4."
            ),
        ),
        (
            (
                "Decide what gets equal weight. Regions give North 107 and South 80 (average "
                "93.5). Customers give 187 / 3, about 62.33."
            ),
            (
                "Averaging per-region customer averages, North (51 + 56) / 2 = 53.5 and South 80, "
                "gives 66.75 and presents it as the average customer, which favors Bo."
            ),
            (
                "AVERAGEX over regions of [NetRevenue] returns 93.5, and AVERAGEX over Customer "
                "returns about 62.33; label each for what it weights."
            ),
        ),
    ],
    22: [
        (
            (
                "Home has one product, Mug, so the shared scalar 96 is added once. That matches "
                "the correct per-product sum by coincidence."
            ),
            (
                "Passing this one-member test and shipping the formula is the mistake. Under "
                "Paper, with two products, the shared version returns 182, not 91."
            ),
            "Test both: Home gives 96 and 96, and Paper gives 182 and 91.",
        ),
        (
            (
                "The variable outside SUMX holds 187 and is added once per Product row. With a "
                "fifth row, an unsold product, the wrong sum becomes 5 x 187 = 935."
            ),
            (
                "Expecting the extra product to do nothing applies the correct sum's behavior to "
                "the shared scalar. Only the per-product version ignores the blank row."
            ),
            (
                "Today the results are 748 (4 x 187) and 187. After adding the product expect 935 "
                "and 187."
            ),
        ),
        (
            (
                "Bind `VAR Total = [NetRevenue]` before SUMX, and evaluate [NetRevenue] inside the "
                "body for each product. The shares are Notebook 0.358, Pen 0.128, Mug 0.513 and "
                "Bag BLANK."
            ),
            (
                "Binding the numerator outside too divides 187 by 187 on every row, and SUMX over "
                "the four products returns 4 rather than 1."
            ),
            "The shares should add to 1, and each share times 187 should give 67, 24 and 96.",
        ),
        (
            (
                "Only values meant to stay constant belong above SUMX. The per-product "
                "[NetRevenue] must be bound inside the body, so that each product's transition "
                "happens there."
            ),
            (
                "Moving ProductRevenue above SUMX makes the per-product column equal "
                "SharedScalarSum, 748 unfiltered and 182 under Paper."
            ),
            "After any refactor, rerun both cases and expect PerProductSum to stay 187 and 91.",
        ),
        (
            (
                "A VAR is a name for one value within its scope. Each iteration that defines "
                "ProductRevenue creates a new binding and changes nothing outside."
            ),
            (
                "Writing `VAR Counter = 0` and expecting `Counter + 1` to number the products "
                "gives 1 on every row, so SUMX returns 4, not 1 + 2 + 3 + 4 = 10."
            ),
            "`SUMX ( Product, Counter + 1 )` returns 4, which shows that nothing accumulated.",
        ),
        (
            (
                "Keep the target shared and compute each weight inside the iterator. In February "
                "2025, Notebook has 20 and Mug 36, so an assumed 200 USD target splits as about "
                "71.43 and 128.57."
            ),
            (
                "Binding the weight [NetRevenue] outside the iterator gives every product a weight "
                "of 1, and the full 200 is allocated to each of four products, 800 in total."
            ),
            (
                "The allocations should add to 200, with Pen and Bag BLANK because they had no "
                "February 2025 sales."
            ),
        ),
    ],
    23: [
        (
            (
                "The pooled ratio weights each category's ratio by its units: Home 19.2 x 5 = 96 "
                "and Paper (91 / 12) x 12 = 91, so 187 / 17 = 11."
            ),
            (
                "A simple mean of 19.2 and about 7.583 is about 13.39. That gives Home's five "
                "units as much weight as Paper's twelve."
            ),
            "The weighted formula returns 11, which matches PooledNetPerUnit in case B.",
        ),
        (
            (
                "Under Paper only one category contributes, so DIVIDE over the total and SUMX over "
                "one category both give 91 / 12, about 7.583."
            ),
            (
                "Concluding from this match that the sum of ratios is a valid total is the error. "
                "With both categories present they differ: 11 against about 26.78."
            ),
            (
                "Under Paper both measures return about 7.5833; with no filter they return 11 and "
                "about 26.7833."
            ),
        ),
        (
            (
                "AVERAGEX over VALUES(Product[Category]) gives each category equal weight. "
                "Travel's ratio is BLANK and skipped, so the result is (19.2 + 7.583) / 2, about "
                "13.39."
            ),
            (
                "Adding a third argument of 0 to DIVIDE turns Travel into a 0 and drags the "
                "average to about 8.93, as if Travel had sold units for free."
            ),
            (
                "Expect about 13.3917 under a name such as Equal Category Net Per Unit, shown "
                "beside the pooled 11."
            ),
        ),
        (
            (
                "DISTINCTCOUNT(Sales[CustomerKey]) evaluated at the total counts Ada, Bo and Cy "
                "once each, 3, even though Bo and Cy appear in both categories."
            ),
            (
                "SUMX over categories adds Paper's 3 and Home's 2 and returns 5. The visual total "
                "may match the sum of rows, but the measure now counts customer-category pairs."
            ),
            "The grand total of the distinct measure is 3, while the SUMX version is 5.",
        ),
        (
            (
                "Travel has only Bag, which has no sales, so Revenue, Units and NetPerUnit are all "
                "BLANK and SUMMARIZECOLUMNS drops the row."
            ),
            (
                "Adding COALESCE(..., 0) to make Travel appear changes the measures, so Travel now "
                "shows 0 revenue and 0 units, which looks like an observed outcome."
            ),
            (
                "The case returns two rows. `ADDCOLUMNS ( VALUES ( Product[Category] ), "
                '"Revenue", [NetRevenue] )` returns three, with Travel BLANK.'
            ),
        ),
        (
            (
                "A stock balance adds across products but not across dates. A closing-balance "
                "total over a quarter should take the last snapshot, not the sum."
            ),
            (
                "If Notebook held 10 units on January 31 and 6 on February 28, summing snapshots "
                "reports 16 units in stock, which never existed on any day."
            ),
            (
                "A closing-balance measure over both months returns 6, and an average balance "
                "returns 8; the sum, 16, matches neither."
            ),
        ),
    ],
    24: [
        (
            (
                "With only Notebook selected, ALLSELECTED(Product[Product]) gives the same single "
                "product, so the denominator is 67 and the share is 1."
            ),
            (
                "Reading 1 as Notebook's share of all sales ignores the denominator; against all "
                "products Notebook is 67 / 187, about 0.358."
            ),
            "Expect a selected share of 1 and an all-product share of about 0.3583.",
        ),
        (
            (
                "ALLSELECTED restores the outer selection {Notebook, Mug}, so the denominator is "
                "67 + 96 = 163. The shares are about 0.411 and 0.589."
            ),
            (
                "Using REMOVEFILTERS here gives 187 and shares of about 0.358 and 0.513, which do "
                "not add to 1 across the visible rows."
            ),
            (
                "Under the Notebook and Mug selection, SelectedTotal reads 163 on both rows and "
                "the shares add to 1."
            ),
        ),
        (
            (
                "Say which filters stay: the year stays, and only the product grouping is widened. "
                "In 2025 Notebook is 47 (S4, S7) and Pen 20 (S5), so the selected total is 67."
            ),
            (
                "Also removing the Date filter in the denominator uses all-years 91 and gives "
                "Notebook 47 / 91, about 0.516, comparing 2025 sales with a multiyear total."
            ),
            (
                "Under 2025 and {Notebook, Pen}, expect a denominator of 67 and shares of about "
                "0.701 and 0.299."
            ),
        ),
        (
            (
                "Case A works because ALLSELECTED runs where the outer selection is the only "
                "shadow context. Inside an iterator that sets its own filters, that simple account "
                "no longer applies."
            ),
            (
                "Assuming a nested SUMX over VALUES(Product[Product]) still sees 91 at every step "
                "skips the trace, and the iterator's own context may change what ALLSELECTED "
                "restores."
            ),
            (
                "Bind `VAR SelectedTotal = CALCULATE ( [NetRevenue], ALLSELECTED ( "
                "Product[Product] ) )` before the iterator, confirm it reads 91, then use it "
                "inside."
            ),
        ),
        (
            (
                "What is visible and what is in the query are different. In case B only Notebook "
                "and Pen are visible, but REMOVEFILTERS widens the denominator to all products, "
                "187."
            ),
            (
                "Assuming the visible shares must add to 1 suggests a bug, but 0.358 + 0.128 is "
                "about 0.487 because Mug's 96 is in the denominator without being shown."
            ),
            (
                "Add the denominator as a column. Case B reads 187 on both rows, which explains "
                "why the visible shares add to about 0.487."
            ),
        ),
        (
            (
                "Within the Treatment arm, 2 of 2 assigned units converted (1.0). Over all four "
                "assigned units, Treatment's conversions are 2 of 4 (0.5). Both are valid when "
                "named."
            ),
            (
                "Labeling 0.5 as Treatment's conversion rate puts Control's units into its "
                "denominator and halves the reported effect."
            ),
            (
                "ExperimentSummary shows Treatment Rate 1 and Control Rate 0.5, and the pooled "
                "rate is (1 + 2) / 4 = 0.75."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

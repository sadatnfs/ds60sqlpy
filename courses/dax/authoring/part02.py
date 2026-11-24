"""Stage two: typed expressions, storage lifetime, aggregation and variables."""

from .common import explain, lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        7,
        "Scalar types, operators and measurement units",
        ["scalar", "number", "text", "Boolean", "date", "format"],
        ("Keep a numeric measure numeric and explain why its display label is a separate concern."),
        (
            "DAX expressions have types, even when a report formats "
            "several types to look similar. A whole number can "
            "represent a count, a decimal can represent an amount or "
            "ratio, a Boolean expresses a logical condition, and a "
            "date identifies a calendar value. Text that looks like a "
            "number is still text until an explicit or implicit "
            "conversion occurs. Do not design a model around hoping "
            "that every consumer makes the conversion you "
            "intended.\n\nOperators also carry meaning. The plus sign "
            "adds numeric values; an ampersand concatenates text. "
            "Parentheses make grouping visible. Multiplication before "
            "subtraction matters in the line formula Quantity * "
            "UnitPrice - Discount, because Discount is defined for the "
            "entire line. If the discount were per unit, the correct "
            "formula and data dictionary would differ.\n\nA unit is not "
            "enforced merely because a column is numeric. Revenue in "
            "USD, units sold and the number of orders are all numbers "
            "with different interpretations. FORMAT produces text for "
            "presentation; it is not a substitute for a numeric "
            "measure with a format property. Preserve the numeric "
            "value when later visuals need sorting, aggregation or "
            "numerical comparison."
        ),
        (
            "ROW can hold differently typed columns in one result. "
            "DATE constructs a date from year, month and day. DIVIDE "
            "returns the ratio of two numeric expressions. FORMAT's "
            "explicit en-US locale makes this example's decimal and "
            "currency characters reproducible; it still returns text. "
            "The classroom records an ISO date string in the worked "
            "table rather than pretending to emulate a report's "
            "regional display settings."
        ),
        [
            r(
                "A row of distinct types",
                (
                    'EVALUATE ROW ( "Count", 3, "Ratio", DIVIDE ( 3, 2 ), '
                    '"Larger", 3 > 2, "Day", DATE ( 2025, 1, 2 ) )'
                ),
                [("Count", "integer"), ("Ratio", "number"), ("Larger", "boolean"), ("Day", "date")],
                [[3, 1.5, True, "2025-01-02"]],
                "Literal expressions; no model filter is needed.",
                [
                    "The whole-number literal is 3.",
                    "Three divided by two is 1.5, while the comparison is TRUE.",
                    (
                        "DATE constructs 2025-01-02; a different display format "
                        "would not change that date."
                    ),
                ],
                (
                    "Putting values in the same row does not make them "
                    "interchangeable. The ratio is not a count of one and a "
                    "half transactions; its unit depends on its numerator and "
                    "denominator."
                ),
            ),
            r(
                "A number and its text label",
                (
                    'EVALUATE ROW ( "NumericRevenue", [NetRevenue], '
                    '"DisplayText", FORMAT ( [NetRevenue], "$0.00", "en-US" ) )'
                ),
                [("NumericRevenue", "number"), ("DisplayText", "text")],
                [[187, "$187.00"]],
                (
                    "All retail sales; a numeric result and an explicitly "
                    "formatted text representation."
                ),
                [
                    "The measure evaluates to numeric 187.",
                    "FORMAT renders the same amount as the text $187.00.",
                    "The original number remains available for later arithmetic.",
                ],
                (
                    "Replacing every revenue measure with FORMAT can break "
                    "numerical behavior even when the report looks correct. "
                    "Numeric measures and display policy should remain "
                    "separate."
                ),
            ),
        ],
        [
            t(
                "Predict 2 + 3 * 4 and (2 + 3) * 4.",
                "Apply the multiplication grouping before addition.",
                "The results are 14 and 20. Parentheses change the expression's structure.",
            ),
            t(
                "Change the displayed currency prefix without changing NumericRevenue.",
                "Change presentation, not the fact table.",
                (
                    "A different label or format string changes text only; it "
                    "does not convert USD into another currency."
                ),
            ),
            t(
                "Write a result row containing quantity, revenue and revenue per unit.",
                "Give each output its own name and unit.",
                (
                    "Use SUM(Sales[Quantity]), [NetRevenue] and "
                    "DIVIDE([NetRevenue],SUM(Sales[Quantity])); quantity is 17, revenue "
                    "is 187 and revenue per unit is 11."
                ),
            ),
            t(
                "Diagnose sorting currency text alphabetically.",
                "Compare text beginning with 9 and text beginning with 1.",
                (
                    "Lexical order need not match numeric order. Sort by the "
                    "numeric measure rather than its formatted string."
                ),
            ),
            t(
                (
                    "Explain whether multiplying a percentage by an amount "
                    "preserves a meaningful unit."
                ),
                ("A fraction is dimensionless; a displayed percent includes a scale convention."),
                (
                    "Multiplying 0.1 by 187 gives 18.7 USD. Multiplying by 10 "
                    "instead would be a hundredfold scaling error."
                ),
            ),
            t(
                "Transfer the distinction to a duration shown as 02:30.",
                "A string's appearance does not declare seconds, minutes or a clock time.",
                (
                    "Define the stored numeric duration and unit separately "
                    "from the formatted label before aggregation."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/dax-operator-reference",
            "https://learn.microsoft.com/en-us/dax/format-function-dax",
        ],
    ),
    lesson(
        8,
        "BLANK, zero and the difference between missing and false",
        ["BLANK", "ISBLANK", "strict equality", "COALESCE", "empty population"],
        "Explain coercion and choose a deliberate missing-value display policy.",
        (
            "BLANK is a semantic value in DAX, not the word blank and "
            "not a universal synonym for zero. It can describe an "
            "absent measure result, an empty aggregation, a missing "
            "value or an unknown relationship member. Those causes "
            "have different business meanings even when a visual hides "
            "them in the same way. Preserve the reason in your model "
            "and notes before deciding how to display the "
            "result.\n\nOrdinary equality can coerce BLANK to a value "
            "such as zero in a numeric comparison. Strict equality "
            "with == distinguishes BLANK from zero. Arithmetic also "
            "depends on the operator: adding five to BLANK yields "
            "five, while multiplying it by five preserves BLANK. "
            "Therefore a single remembered rule such as 'blank always "
            "acts as zero' is unsafe.\n\nThe unsold Bag product gives a "
            "concrete empty-population case. Its Product row exists, "
            "but no Sales row survives its key filter. "
            "SUM(Sales[NetAmount]) is BLANK. Showing zero may be "
            "useful for a complete catalog, but COALESCE is a "
            "presentation or business-policy decision, not evidence "
            "that a transaction of zero occurred. The distinction "
            "becomes essential in retention and incomplete-period "
            "analysis."
        ),
        (
            "ISBLANK directly tests the value. The two equality "
            "operators answer different questions under coercion. "
            "COALESCE chooses the first nonblank argument. COUNTROWS "
            "over an empty table returns BLANK, while COUNTROWS over "
            "the visible Bag dimension returns one. The row and the "
            "absence of matching events are separate facts."
        ),
        [
            r(
                "Blank coercion is operator-specific",
                (
                    'EVALUATE ROW ( "LooseZero", BLANK() = 0, "StrictZero", '
                    'BLANK() == 0, "PlusFive", BLANK() + 5, "TimesFive", '
                    "BLANK() * 5 )"
                ),
                [
                    ("LooseZero", "boolean"),
                    ("StrictZero", "boolean"),
                    ("PlusFive", "number"),
                    ("TimesFive", "number"),
                ],
                [[True, False, 5, None]],
                "Literal BLANK operations; no model context.",
                [
                    "Ordinary numeric equality coerces BLANK for the comparison with zero.",
                    "Strict equality does not identify BLANK with numeric zero.",
                    "Addition and multiplication have different blank behavior: 5 versus BLANK.",
                ],
                (
                    "A predicate written with = 0 may include missing results "
                    "that the author intended to exclude. Test the intended "
                    "missingness condition explicitly."
                ),
            ),
            r(
                "An existing product with no sales",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Products", COUNTROWS ( '
                    'Product ), "SalesRows", COUNTROWS ( Sales ), "Revenue", '
                    '[NetRevenue], "DisplayRevenue", COALESCE ( [NetRevenue], '
                    "0 ) ), Product[ProductKey] = 4 )"
                ),
                [
                    ("Products", "integer"),
                    ("SalesRows", "integer"),
                    ("Revenue", "number"),
                    ("DisplayRevenue", "number"),
                ],
                [[1, None, None, 0]],
                "ProductKey 4, Bag; no matching Sales rows.",
                [
                    "One dimension member remains.",
                    "The related fact table is empty, so COUNTROWS and SUM return BLANK.",
                    (
                        "COALESCE deliberately displays zero while the original "
                        "measure remains blank."
                    ),
                ],
                (
                    "A zero-filled display can be appropriate if unsold "
                    "products are in scope. Retain a separate eligibility or "
                    "availability signal when zero could otherwise mean an "
                    "observed failure."
                ),
            ),
        ],
        [
            t(
                "Predict ISBLANK(0) and ISBLANK(BLANK()).",
                "Test the values, not their formatting.",
                "They are FALSE and TRUE.",
            ),
            t(
                "Replace the Bag filter with Pen.",
                "Pen has two sales lines.",
                "Products is 1, SalesRows is 2 and Revenue/DisplayRevenue are both 24.",
            ),
            t(
                "Write a label distinguishing no sales from positive revenue.",
                "Test ISBLANK before numeric comparisons.",
                (
                    'IF(ISBLANK([NetRevenue]),"No matching sales","Revenue '
                    'observed") avoids treating an empty result as an observed '
                    "zero."
                ),
            ),
            t(
                "Diagnose a report claiming every blank retention cell is a lost customer.",
                "A future month may not have been observed yet.",
                (
                    "Missing observation time is different from observed "
                    "inactivity. Do not coalesce the future into failures."
                ),
            ),
            t(
                "Explain why an empty table differs from one row containing BLANK.",
                "Count the objects at the table level.",
                (
                    "An empty table has no row; a one-row table can carry a "
                    "blank cell. Their membership and joins can differ."
                ),
            ),
            t(
                "Transfer the policy to missing cost data.",
                "Zero cost would inflate profit if the cost was merely absent.",
                (
                    "Preserve missing cost as a quality issue or "
                    "exclude/report it explicitly before calculating margins."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/blank-function-dax",
            "https://learn.microsoft.com/en-us/dax/dax-operator-reference",
            "https://learn.microsoft.com/en-us/dax/coalesce-function-dax",
        ],
    ),
    lesson(
        9,
        "Calculated columns, measures and evaluation lifetime",
        ["calculated column", "measure", "refresh", "query context", "stored value"],
        ("Separate a row's stored calculation from a scalar reevaluated for a query context."),
        (
            "A calculated column produces a value for each row when "
            "the model processes that calculation. A measure is "
            "evaluated for a query context. The same arithmetic may "
            "appear in both, but its lifetime and shape differ. A "
            "column's values can be used as model attributes; a "
            "measure answers a context-dependent question without "
            "storing one answer for every future report "
            "selection.\n\nOur CSV contains NetAmount as an explicit "
            "input column. It was authored from a documented line "
            "formula. If you implemented that formula as a calculated "
            "column in an external model, each line would use its "
            "row's quantity, unit price and line discount during "
            "processing. A report selection would choose which stored "
            "line amounts contribute, not retroactively rewrite their "
            "values.\n\nCalculated tables are another model object, "
            "computed during processing and then available as tables. "
            "A table expression inside a query is temporary to that "
            "expression. Decide between these choices based on "
            "semantic lifetime, cardinality and intended reuse rather "
            "than naming every intermediate object a measure. The "
            "offline classroom shows their definitions and "
            "consequences; it does not create these objects in a live "
            "engine."
        ),
        (
            "Case A reconstructs two row amounts with SELECTCOLUMNS so "
            "the stored and derived numbers can be compared. Case B "
            "asks for a measure under customer and date filters. The "
            "Date relationship uses OrderDate. The filter changes "
            "eligible lines; the definition of the line amount remains "
            "fixed."
        ),
        [
            r(
                "Stored row amounts and their formula",
                (
                    "EVALUATE SELECTCOLUMNS ( TOPN ( 2, Sales, Sales[SaleID], "
                    'ASC ), "Line", Sales[SaleID], "Stored", Sales[NetAmount], '
                    '"Reconstructed", Sales[Quantity] * Sales[UnitPrice] - '
                    "Sales[Discount] )\nORDER BY [Line]"
                ),
                [("Line", "text"), ("Stored", "number"), ("Reconstructed", "number")],
                [["S1", 20, 20], ["S2", 4, 4]],
                "Two first SaleID values; each projection evaluates its own Sales row.",
                [
                    "S1: 2 times 10 minus 0 equals 20.",
                    "S2: 1 times 5 minus 1 equals 4.",
                    "The supplied NetAmount column agrees with the documented row formula.",
                ],
                (
                    "Agreement verifies this tiny fixture's arithmetic. It "
                    "does not prove that a source system applies every "
                    "discount or tax policy correctly."
                ),
            ),
            r(
                "A measure over a selected population",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue], '
                    '"Quantity", [QuantitySold] ), Customer[Region] = "North", '
                    "'Date'[Year] = 2025 )"
                ),
                [("Revenue", "number"), ("Quantity", "integer")],
                [[83, 9]],
                "North customers and order year 2025.",
                [
                    "Eligible lines are S4, S5 and S8.",
                    "Their stored amounts are 27, 20 and 36, totaling 83.",
                    "Their quantities are 3, 4 and 2, totaling 9.",
                ],
                (
                    "The context changes the measure result from 187 to 83. It "
                    "does not change S4's line value from 27 into a regional "
                    "total."
                ),
            ),
        ],
        [
            t(
                "Predict S4's stored NetAmount after selecting South.",
                "Filtering visibility does not rewrite an excluded row.",
                ("It remains 27 in the data, but S4 is not eligible for the South measure result."),
            ),
            t(
                "Change the case B year to 2024.",
                "Only Ada's two early lines are North in that year.",
                "Revenue is 24 and quantity is 3.",
            ),
            t(
                "Write a calculated-column expression for a line's gross amount.",
                "Use columns from the current Sales row.",
                (
                    "Sales[Quantity] * Sales[UnitPrice] is the expression; its "
                    "values would be stored per row if added as a calculated "
                    "column externally."
                ),
            ),
            t(
                ("Diagnose storing a region-wide total on every sales line and summing it later."),
                "Repeated group aggregates change the grain.",
                (
                    "The total would be counted once per line. Use a "
                    "context-dependent measure or model a separate aggregate "
                    "fact with its own grain."
                ),
            ),
            t(
                "Explain why a measure cannot serve as a stable product-category key.",
                "A key identifies stored members; a measure changes with context.",
                (
                    "Use a column with a declared domain and grain for "
                    "relationships or category membership."
                ),
            ),
            t(
                (
                    "Choose a lifetime for a sales-band label that must "
                    "reflect refreshed row values."
                ),
                "Distinguish a persisted classification from a selected-context ratio.",
                (
                    "A processed row classification may be a calculated column "
                    "or upstream attribute; a dynamic threshold over selected "
                    "totals requires a measure/table expression."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/dax-overview",
            (
                "https://learn.microsoft.com/en-us/power-bi/transform-model"
                "/desktop-calculations-options"
            ),
        ],
    ),
    lesson(
        10,
        "Additive sums and distinct populations",
        ["SUM", "COUNTROWS", "DISTINCTCOUNT", "additivity", "population"],
        ("Choose an aggregation whose input grain and total behavior match the metric definition."),
        (
            "A sum over disjoint sets is additive when each event "
            "contributes once in a common unit. Distinct counts are "
            "not generally additive because the same identity can "
            "appear in more than one group. The difference is "
            "semantic, not a limitation of a visual. A grand total of "
            "distinct orders should ask for distinct orders in the "
            "entire context, not blindly add the row-level "
            "counts.\n\nOur retail fact has eight lines, seven orders "
            "and three customers with sales. The Product dimension has "
            "four catalog members, including an unsold bag. These "
            "populations can all be useful, but they answer different "
            "questions. Name the denominator or counted entity "
            "explicitly so downstream ratios do not switch populations "
            "unnoticed.\n\nA measure is reusable only when its "
            "definition is stable. If 'active customer' means at least "
            "one eligible sale, define that eligibility before "
            "counting. If it means enrolled customers regardless of "
            "sales, the dimension or an enrollment fact is the correct "
            "starting point. A formula that happens to match the "
            "expected total on this fixture may still fail when a "
            "multi-product order or unsold customer appears."
        ),
        (
            "The same four aggregate expressions are evaluated under "
            "all rows and under Paper. The Product filter travels to "
            "Sales, so fact-based distinct counts change with that "
            "selection. Customers can buy products from several "
            "categories, which is why category-level customer counts "
            "cannot be added to produce a unique customer total."
        ),
        [
            r(
                "Whole-model populations",
                (
                    'EVALUATE ROW ( "Revenue", [NetRevenue], "Lines", '
                    'COUNTROWS ( Sales ), "Orders", [OrderCount], '
                    '"CustomersWithSales", DISTINCTCOUNT ( Sales[CustomerKey] '
                    ") )"
                ),
                [
                    ("Revenue", "number"),
                    ("Lines", "integer"),
                    ("Orders", "integer"),
                    ("CustomersWithSales", "integer"),
                ],
                [[187, 8, 7, 3]],
                "All rows; complete nonblank order/customer fact keys.",
                [
                    "Eight SaleID values represent eight lines.",
                    "Order 101 repeats across two lines, leaving seven orders.",
                    "The fact includes customer keys 10, 20 and 30.",
                ],
                (
                    "Counting Customer rows would produce four, which is a "
                    "valid catalog population but a different metric."
                ),
            ),
            r(
                "Paper's overlapping order population",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue], '
                    '"Lines", COUNTROWS ( Sales ), "Orders", [OrderCount], '
                    '"CustomersWithSales", DISTINCTCOUNT ( Sales[CustomerKey] '
                    ') ), Product[Category] = "Paper" )'
                ),
                [
                    ("Revenue", "number"),
                    ("Lines", "integer"),
                    ("Orders", "integer"),
                    ("CustomersWithSales", "integer"),
                ],
                [[91, 5, 4, 3]],
                "Paper products 1 and 2; all years and customers otherwise allowed.",
                [
                    "Five eligible lines total 91.",
                    "Their order keys are 101, 101, 201, 202 and 204.",
                    (
                        "All three purchasing customers still appear, but only "
                        "four distinct orders remain."
                    ),
                ],
                (
                    "A lower revenue total does not imply fewer distinct "
                    "customers. One population can remain unchanged while "
                    "another metric changes substantially."
                ),
            ),
        ],
        [
            t(
                "Predict customer counts for Paper and Home separately.",
                "Customer 20 and 30 can appear in both groups.",
                (
                    "Paper has 3 customers and Home has 2; their sum 5 exceeds "
                    "the whole-model distinct count 3."
                ),
            ),
            t(
                "Restrict Paper to 2025 and predict order count.",
                "Remove both lines from order 101.",
                "Orders 201, 202 and 204 remain: three orders.",
            ),
            t(
                "Write two separate measures for catalog customers and customers with sales.",
                "Choose the table before choosing the count function.",
                (
                    "COUNTROWS(Customer) counts catalog members; "
                    "DISTINCTCOUNT(Sales[CustomerKey]) counts purchasing "
                    "identities in eligible facts."
                ),
            ),
            t(
                "Diagnose a grand total built by adding per-category distinct customers.",
                "Look for customers crossing category boundaries.",
                (
                    "The same customer can be counted repeatedly. Reevaluate "
                    "the distinct-count measure in total context."
                ),
            ),
            t(
                "Explain how blank keys change DISTINCTCOUNT.",
                "BLANK is included in its distinct domain.",
                (
                    "A blank can count as one distinct value. Decide whether "
                    "it is an unknown bucket or excluded quality failure."
                ),
            ),
            t(
                "Transfer the reasoning to daily active users.",
                "A user can be active on several days.",
                (
                    "The sum of daily distinct users measures user-days, not "
                    "monthly unique users; both can be useful if named "
                    "correctly."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/sum-function-dax",
            "https://learn.microsoft.com/en-us/dax/distinctcount-function-dax",
        ],
    ),
    lesson(
        11,
        "DIVIDE, weighted averages and zero denominators",
        ["ratio of totals", "DIVIDE", "weighted average", "denominator", "zero"],
        ("Derive a ratio at its declared population and distinguish an undefined ratio from zero."),
        (
            "A ratio inherits the populations and units of both its "
            "numerator and denominator. NetRevenue divided by "
            "QuantitySold is net revenue per unit, not the mean of "
            "order prices or the mean of product-level ratios. Unequal "
            "quantities make those averages different. Start with the "
            "business definition, then identify the sufficient totals "
            "needed for the ratio.\n\nDIVIDE handles zero or blank "
            "denominators according to an explicit fallback. Without "
            "an alternate result it returns BLANK for an invalid "
            "denominator. An alternate zero can be a useful display "
            "choice, but it does not make an undefined conversion rate "
            "or unit price mathematically zero. The alternate result "
            "must be a constant, so a more elaborate policy belongs "
            "outside that argument.\n\nFor this fixture, 187 divided by "
            "17 is exactly 11 USD per unit. The value is a weighted "
            "aggregate: products with more eligible units contribute "
            "more weight. A grand total should normally reevaluate the "
            "numerator and denominator for the total population. "
            "Averaging displayed percentages can be legitimate only "
            "when equal group weighting is itself the intended "
            "estimand."
        ),
        (
            "The first case calls DIVIDE on two measures. The second "
            "uses literal zero denominators so the missing-ratio "
            "policy is visible without a hidden data condition. "
            "Ordinary division and DIVIDE should not be treated as "
            "interchangeable merely because both work for a positive "
            "denominator."
        ),
        [
            r(
                "A ratio of sufficient totals",
                (
                    'EVALUATE ROW ( "Revenue", [NetRevenue], "Units", '
                    '[QuantitySold], "NetPerUnit", DIVIDE ( [NetRevenue], '
                    "[QuantitySold] ) )"
                ),
                [("Revenue", "number"), ("Units", "integer"), ("NetPerUnit", "number")],
                [[187, 17, 11]],
                "All sales; numerator USD and denominator sold units.",
                [
                    "Sum net revenue to 187 and quantities to 17.",
                    "187 / 17 = 11.",
                    "The resulting unit is USD per sold unit, not USD per order.",
                ],
                (
                    "Changing the denominator to OrderCount would produce an "
                    "average order value, a different metric even though its "
                    "source data are identical."
                ),
            ),
            r(
                "Explicit undefined-ratio policy",
                (
                    'EVALUATE ROW ( "DefaultResult", DIVIDE ( 0, 0 ), '
                    '"ChosenDisplay", DIVIDE ( 0, 0, 0 ), "ZeroNumerator", '
                    "DIVIDE ( 0, 5 ) )"
                ),
                [
                    ("DefaultResult", "number"),
                    ("ChosenDisplay", "number"),
                    ("ZeroNumerator", "number"),
                ],
                [[None, 0, 0]],
                (
                    "Literal values distinguish no denominator from a positive "
                    "denominator with zero outcome."
                ),
                [
                    "Zero divided by zero is not a defined observed rate.",
                    (
                        "DIVIDE's default is BLANK; the third argument "
                        "deliberately replaces it with zero."
                    ),
                    "Zero divided by five is a defined zero rate.",
                ],
                (
                    "A table showing two zeroes can therefore combine two "
                    "different situations. Retain an eligibility count or "
                    "availability marker to preserve that distinction."
                ),
            ),
        ],
        [
            t(
                "Predict net revenue per unit in 2025.",
                "Use that year's totals, not the mean of yearly ratios.",
                "2025 revenue is 123 and units are 12, so the ratio is 10.25.",
            ),
            t(
                "Change the denominator to distinct orders.",
                "The whole-model order count is 7.",
                "The result is 187/7, approximately 26.7143 USD per order.",
            ),
            t(
                "Write a measure that leaves undefined rates blank.",
                "Use DIVIDE without a third argument.",
                (
                    "DIVIDE([NetRevenue],[QuantitySold]) leaves an empty or "
                    "zero-denominator population blank."
                ),
            ),
            t(
                "Diagnose averaging the 2024 and 2025 unit-price ratios.",
                "The years have 5 and 12 units.",
                (
                    "An equal-year mean of 12.8 and 10.25 is 11.525, while the "
                    "pooled unit-weighted ratio is 11."
                ),
            ),
            t(
                "Explain when zero is a legitimate numerator result.",
                "A positive denominator establishes observed opportunity.",
                (
                    "Zero conversions among five eligible units is a valid "
                    "zero; no eligible units gives an undefined conversion "
                    "rate."
                ),
            ),
            t(
                "Transfer the rule to experiment conversion rates.",
                (
                    "Count assigned or eligible units according to the design, "
                    "not exposure rows by accident."
                ),
                (
                    "Choose the unit and eligibility policy first, then divide "
                    "conversions by that population. Repeated events must not "
                    "silently inflate the denominator."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/divide-function-dax",
            ("https://learn.microsoft.com/en-us/dax/best-practices/dax-divide-function-operator"),
        ],
    ),
    lesson(
        12,
        "VAR and RETURN: values are not context-sensitive macros",
        ["VAR", "RETURN", "evaluation context", "binding", "readability"],
        (
            "Predict when a variable freezes a value and when a "
            "measure is reevaluated in modified context."
        ),
        (
            "A variable binds the result of its expression in the "
            "context where the variable is evaluated. Reusing the "
            "variable uses that value. It is not textual substitution "
            "that reevaluates its defining formula wherever its name "
            "appears. This makes variables useful for clarity and "
            "avoiding repeated work, but it also explains a frequent "
            "context bug.\n\nSuppose Revenue is evaluated before a Blue "
            "product filter is introduced. The scalar stored in that "
            "variable is 187. Passing the variable to CALCULATE after "
            "adding Blue does not turn it back into a measure; its "
            "value remains 187. Passing the measure reference itself "
            "allows evaluation in the changed context and yields "
            "163.\n\nThe location of a variable is therefore a semantic "
            "choice. A variable defined inside an iterator can be "
            "evaluated separately for each iteration; one outside can "
            "hold one shared scalar. Prefer names that describe the "
            "bound value, such as RevenueBeforeColorChange, rather "
            "than suggesting an automatic live link to every later "
            "context. Return intermediate values while debugging and "
            "trace where they were bound."
        ),
        (
            "VAR introduces a local name and RETURN supplies the "
            "expression using it. Case A binds the scalar before "
            "CALCULATE adds Blue. Case B establishes Blue outside, "
            "then compares a frozen scalar with a measure after "
            "removing that color filter. The changed order of binding "
            "and filtering produces different answers without changing "
            "the underlying data."
        ),
        [
            r(
                "Binding before a new filter",
                (
                    "EVALUATE\nVAR RevenueBeforeColorChange = "
                    '[NetRevenue]\nRETURN ROW ( "FrozenInBlue", CALCULATE ( '
                    'RevenueBeforeColorChange, Product[Color] = "Blue" ), '
                    '"RecomputedInBlue", CALCULATE ( [NetRevenue], '
                    'Product[Color] = "Blue" ) )'
                ),
                [("FrozenInBlue", "number"), ("RecomputedInBlue", "number")],
                [[187, 163]],
                "Start unfiltered; bind the variable before introducing Blue.",
                [
                    "The variable binds NetRevenue in the original all-row context: 187.",
                    "CALCULATE around that scalar cannot recreate its earlier measure expression.",
                    "The direct measure reference is evaluated with Blue and returns 163.",
                ],
                (
                    "The wrong result is not repaired by renaming the "
                    "variable. Its defining location or the expression passed "
                    "to CALCULATE must change."
                ),
            ),
            r(
                "Binding inside Blue before removing it",
                (
                    "EVALUATE CALCULATETABLE (\n    VAR RevenueBeforeRemoval = "
                    '[NetRevenue]\n    RETURN ROW ( "FrozenWithoutColor", '
                    "CALCULATE ( RevenueBeforeRemoval, REMOVEFILTERS ( "
                    'Product[Color] ) ), "RecomputedWithoutColor", CALCULATE ( '
                    "[NetRevenue], REMOVEFILTERS ( Product[Color] ) ) ),\n    "
                    'Product[Color] = "Blue"\n)'
                ),
                [("FrozenWithoutColor", "number"), ("RecomputedWithoutColor", "number")],
                [[163, 187]],
                "The outer CALCULATETABLE supplies Blue before the variable is bound.",
                [
                    "Blue makes NetRevenue 163 at variable binding time.",
                    "Removing the color filter around the scalar still returns 163.",
                    "Removing color before evaluating the measure restores the full revenue 187.",
                ],
                (
                    "Variables and filter modifiers are both predictable when "
                    "the sequence is explicit. Do not infer that a variable "
                    "called Total always means an unfiltered grand total."
                ),
            ),
        ],
        [
            t(
                "Predict the first case when the added color is Red.",
                "The pre-filter variable is unchanged.",
                "FrozenInRed remains 187; the direct measure under Red returns 24.",
            ),
            t(
                "Move the variable binding inside the Blue calculation.",
                "Establish context before evaluating its defining expression.",
                (
                    "Binding [NetRevenue] inside Blue produces 163. Later uses "
                    "still reuse that scalar."
                ),
            ),
            t(
                "Rewrite a filtered share with separately named numerator and denominator.",
                "Bind each measure in the context it is meant to represent.",
                (
                    "Bind numerator=[NetRevenue] and "
                    "denominator=CALCULATE([NetRevenue],REMOVEFILTERS(Product[C"
                    "olor])), then DIVIDE(numerator, denominator)."
                ),
            ),
            t(
                ("Diagnose a denominator that remains equal to the numerator after REMOVEFILTERS."),
                "Check whether the denominator uses a precomputed scalar variable.",
                (
                    "CALCULATE(FrozenRevenue,REMOVEFILTERS(...)) preserves the "
                    "frozen value. Reevaluate the measure in the intended "
                    "denominator context."
                ),
            ),
            t(
                "Explain whether a variable defined before SUMX changes per row.",
                "Ask where its expression is evaluated.",
                (
                    "An outer scalar is shared. A variable declared in the "
                    "iterator body can bind a different result for each row's "
                    "context."
                ),
            ),
            t(
                "Describe a debugging trace that exposes the bug without engine access.",
                "Record binding context and value before each modifier.",
                (
                    "Write a ledger with original filters, variable binding, "
                    "later filters and reused versus reevaluated values; "
                    "reconcile 187 and 163 from their fact rows."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/best-practices/dax-variables",
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
        ],
    ),
]


REASONING = {
    7: [
        (
            (
                "DAX binds multiplication tighter than addition, so 2 + 3 * 4 first forms 12 and "
                "then adds 2. The parentheses build a different tree whose sum 5 is multiplied by "
                "4."
            ),
            (
                "Reading the expression strictly left to right gives 20 for both forms, which "
                "hides the fact that the parentheses changed the structure rather than the style."
            ),
            ('`EVALUATE ROW ( "Plain", 2 + 3 * 4, "Grouped", ( 2 + 3 ) * 4 )` returns 14 and 20.'),
        ),
        (
            (
                "NumericRevenue is SUM(Sales[NetAmount]), a USD number of 187. FORMAT only "
                "produces DisplayText, so a euro sign in place of the dollar sign changes a string "
                "and leaves the number alone."
            ),
            (
                "Showing 187.00 with a euro sign claims a conversion that never happened. At an "
                "assumed 1.10 USD per EUR the same sales would be about 170 EUR, so the label "
                "would overstate them."
            ),
            (
                "Both rows keep NumericRevenue at 187; only the DisplayText column differs, and no "
                "rate table appears anywhere in the query."
            ),
        ),
        (
            (
                "Each output keeps its own unit: 17 units, 187 USD and their ratio of totals, 11 "
                "USD per unit. The ratio pools all eight lines, so heavy lines such as S5's four "
                "Pens weigh more."
            ),
            (
                "AVERAGE(Sales[UnitPrice]) returns 100 / 8 = 12.5. It averages list prices per "
                "line and ignores both quantities and the 8 USD of discounts."
            ),
            "The row reads quantity 17, revenue 187 and per unit 11, and 11 x 17 reproduces 187.",
        ),
        (
            (
                "FORMAT returns text, and text compares character by character. The line amounts "
                "4, 20, 27, 36 and 40 become strings whose order follows their first digits, not "
                "their size."
            ),
            (
                'Sorting the DisplayText column puts S2\'s "$4.00" after "$36.00" and before '
                '"$40.00", because "." sorts before "0". The smallest line then looks '
                "mid-sized."
            ),
            (
                "Order the rows by Sales[NetAmount] and expect 4, 20, 20, 20, 20, 27, 36, 40; the "
                "text labels can then follow that numeric order."
            ),
        ),
        (
            (
                "A rate of 0.1 is dimensionless, so 0.1 x 187 USD stays in USD and gives 18.7. The "
                "percent sign in a label is only a display convention for that fraction."
            ),
            (
                'Typing the displayed "10" into the formula multiplies 187 by 10 and reports '
                "1,870 USD, a hundredfold error that still looks like a plausible dollar figure."
            ),
            (
                '`ROW ( "Fee", 0.1 * [NetRevenue] )` returns 18.7, and 18.7 / 187 returns the '
                "0.1 rate back."
            ),
        ),
        (
            (
                "The label 02:30 could mean 150 minutes, 150 seconds or half past two at night. "
                "Storing a number with a declared unit, such as 150 minutes, lets SUM and AVERAGE "
                "mean something."
            ),
            (
                "Parsing the string as minutes and seconds gives 150 seconds while hours and "
                "minutes gives 150 minutes, a sixtyfold disagreement that no formatting choice "
                "reveals."
            ),
            (
                "Two stored durations of 150 minutes sum to 300 minutes, which you may then format "
                "as 05:00 after an explicit conversion from minutes to hours."
            ),
        ),
    ],
    8: [
        (
            (
                "ISBLANK asks whether the value itself is BLANK. Zero is a real number, so it "
                "fails the test, while BLANK() passes. Case A shows why a separate test is needed: "
                "BLANK() = 0 is TRUE."
            ),
            (
                "Testing a result with = 0 returns TRUE for both values, because loose equality "
                "coerces BLANK to zero. A missing value and an observed zero become identical."
            ),
            (
                '`ROW ( "Zero", ISBLANK ( 0 ), "Blank", ISBLANK ( BLANK () ), "Loose", BLANK '
                "() = 0 )` returns FALSE, TRUE and TRUE."
            ),
        ),
        (
            (
                "Pen is ProductKey 2, and the relationship keeps S2 (4) and S5 (20). Revenue is "
                "therefore 24 and nonblank, so COALESCE leaves it unchanged at 24."
            ),
            (
                "Putting COALESCE([NetRevenue], 0) in the Revenue column instead of a separate "
                "display column agrees for Pen but shows 0 for Bag, which then reads as an "
                "observed zero sale."
            ),
            (
                "Under ProductKey 2 the row is Products 1, SalesRows 2, Revenue 24 and "
                "DisplayRevenue 24."
            ),
        ),
        (
            (
                'Checking ISBLANK first sends Bag, whose filter reaches no Sales rows, to "No '
                'matching sales". Notebook (67), Pen (24) and Mug (96) all reach "Revenue '
                'observed".'
            ),
            (
                "`IF ( [NetRevenue] <= 0, ... )` also catches Bag, because BLANK coerces to 0, but "
                "it would mislabel a real zero, such as a product whose lines were fully "
                "discounted to 0, as having no sales."
            ),
            (
                '`ADDCOLUMNS ( VALUES ( Product[Product] ), "Label", ... )` should label Bag '
                "alone as no sales and the other three as observed."
            ),
        ),
        (
            (
                "The retail facts end on 2025-02-03. February is observed: Bo and Cy bought and "
                "Ada did not, so Ada's February blank is real inactivity. March has no observation "
                "for anyone."
            ),
            (
                'Coalescing every blank cell to "lost" marks all three buyers lost in March. '
                "That is a 100% churn claim for a month the data never covered."
            ),
            (
                "`MAX ( Sales[OrderDate] )` returns 2025-02-03. Classify only months up to that "
                "date, and leave March marked as unobserved."
            ),
        ),
        (
            (
                "Under the Bag filter Sales has no rows, so COUNTROWS(Sales) is BLANK. ROW always "
                "builds one row, so a table wrapping the blank revenue still has one member."
            ),
            (
                "Testing ISEMPTY on the ROW result to detect missing sales returns FALSE for Bag, "
                "because the row exists even though its revenue cell is BLANK."
            ),
            (
                'Under ProductKey 4, `ISEMPTY ( Sales )` is TRUE while `COUNTROWS ( ROW ( "R", '
                "[NetRevenue] ) )` is 1."
            ),
        ),
        (
            (
                "Cost lives on Product. Today the cost is Notebook 7 x 2, Pen 5 x 1 and Mug 5 x 5, "
                "or 44, giving a margin of 143. A missing Mug cost should surface as three unknown "
                "lines, not as cheap lines."
            ),
            (
                "COALESCE ( RELATED ( Product[UnitCost] ), 0 ) would drop cost to 19 if Mug's cost "
                "were missing, inflating margin to 168 and making Mug look like pure profit."
            ),
            (
                "Count Sales lines where RELATED(Product[UnitCost]) is BLANK. On the current data "
                "expect 0 such lines and a margin of 143."
            ),
        ),
    ],
    9: [
        (
            (
                "A filter only decides which rows a measure can see. Selecting South keeps S3 "
                "(40), S6 (20) and S7 (20) for 80, and S4 still stores 27 because Ada is in North."
            ),
            (
                "A calculated column that rewrites S4 to 0 whenever the region is not South would "
                "make stored data depend on one slicer, and North would lose 27 of its 107."
            ),
            (
                '`CALCULATE ( [NetRevenue], Customer[Region] = "South" )` returns 80, while '
                '`CALCULATE ( SUM ( Sales[NetAmount] ), Sales[SaleID] = "S4" )` with no region '
                "filter still returns 27."
            ),
        ),
        (
            (
                "In 2024 the only North lines are Ada's S1 (20) and S2 (4), so revenue is 24 and "
                "quantity is 3. Both filters must hold at once, so Bo's S3 is excluded."
            ),
            (
                "Changing the year but also dropping the region filter returns 64 and 5, because "
                "Bo's 40 USD Mug line from order 102 joins the result."
            ),
            (
                "The 2024 row reads 24 and 3. Adding the 2025 row (83 and 9) gives the North "
                "totals of 107 and 12."
            ),
        ),
        (
            (
                "A calculated column evaluates per Sales row, so S1 gets 2 x 10 = 20 and S2 gets 1 "
                "x 5 = 5. S2's stored NetAmount is 4 because its 1 USD discount is already "
                "removed."
            ),
            (
                "A measure written as SUM(Sales[Quantity]) * SUM(Sales[UnitPrice]) multiplies "
                "totals, 17 x 100 = 1,700, instead of summing row products."
            ),
            (
                "Summing the gross column, or running `SUMX ( Sales, Sales[Quantity] * "
                "Sales[UnitPrice] )`, returns 195, and 195 minus 8 of discounts equals 187."
            ),
        ),
        (
            (
                "North has five lines: Ada's S1, S2 and S4 and Cy's S5 and S8. A measure filtered "
                "to North returns 107 once, whatever grain the visual uses."
            ),
            (
                "Writing 107 onto each North line and summing it gives 5 x 107 = 535, five times "
                "the real revenue, and the multiple would change as lines are added."
            ),
            (
                "Under North, SUM of the stored column returns 535 while `CALCULATE ( "
                '[NetRevenue], Customer[Region] = "North" )` returns 107.'
            ),
        ),
        (
            (
                "Product[Category] is a stored column with the members Paper, Home and Travel. Bag "
                "stays in Travel even with no sales, so relationships and slicers have a fixed "
                "domain."
            ),
            (
                "Deriving a category from a measure such as revenue over 50 makes membership move "
                "with filters: Mug is 96 overall but 36 under North, so its category would flip "
                "with the region slicer."
            ),
            (
                "`VALUES ( Product[Category] )` returns three rows under any Customer filter, "
                "while the Mug revenue changes from 96 to 36."
            ),
        ),
        (
            (
                "A band from the row itself, such as NetAmount of at least 30 for S3 and S8, may "
                "be stored and recomputed at refresh. A share of the selected total depends on the "
                "filter, so it must be a measure."
            ),
            (
                "A column storing NetAmount divided by the refresh total gives S8 36 / 187, about "
                "0.193, and keeps it under North, where S8's real share is 36 / 107, about 0.336."
            ),
            (
                "Under North the measure returns about 0.336 for S8 and about 0.193 with no "
                "filter; the column shows 0.193 in both views."
            ),
        ),
    ],
    10: [
        (
            (
                "DISTINCTCOUNT(Sales[CustomerKey]) is evaluated in each category. Paper reaches "
                "Ada, Bo and Cy (3); Home reaches Bo and Cy (2). Bo and Cy bought in both."
            ),
            (
                "Adding the category counts gives 5 customers, but the whole model has only three "
                "customers with sales. Overlapping populations are not additive."
            ),
            (
                '`SUMMARIZECOLUMNS ( ROLLUPADDISSUBTOTAL ( Product[Category], "IsTotal" ), '
                '"Customers", DISTINCTCOUNT ( Sales[CustomerKey] ) )` shows 3, 2 and a total of '
                "3."
            ),
        ),
        (
            (
                "Removing 2024 drops order 101, which held two Paper lines (S1 and S2). Paper "
                "keeps S4, S5 and S7 in orders 201, 202 and 204, for 3 orders and 67 USD."
            ),
            (
                "Subtracting the two removed lines from Paper's four orders gives 2. That treats "
                "lines as orders, though both removed lines came from one order."
            ),
            (
                "`CALCULATE ( [OrderCount], Product[Category] = \"Paper\", 'Date'[Year] = 2025 )` "
                "returns 3, and NetRevenue under the same filters returns 67."
            ),
        ),
        (
            (
                "COUNTROWS(Customer) counts catalog members (4, including Di), while "
                "DISTINCTCOUNT(Sales[CustomerKey]) counts buyers in eligible facts (3). Under West "
                "these are 1 and BLANK."
            ),
            (
                'Using COUNTROWS(Customer) as "customers who bought Paper" returns 4, because '
                "the single-direction relationship does not filter Customer from Product through "
                "Sales."
            ),
            (
                "Under Paper expect a catalog count of 4 and a buyer count of 3; under West expect "
                "1 and BLANK."
            ),
        ),
        (
            (
                "Each product has two buyers: Notebook (Ada, Bo), Pen (Ada, Cy) and Mug (Bo, Cy). "
                "The total row must reevaluate DISTINCTCOUNT over all eight lines, which gives 3."
            ),
            (
                "`SUMX ( VALUES ( Product[Product] ), [Customers] )` adds 2 + 2 + 2 and reports 6 "
                "customers, double counting every buyer."
            ),
            (
                "The per-product rows show 2, 2 and 2 while the total row shows 3, the same as the "
                "whole-model case."
            ),
        ),
        (
            (
                "DISTINCTCOUNT treats BLANK as one more distinct value. If one sales line lacked a "
                "CustomerKey, the count would rise from 3 to 4 without any new person."
            ),
            (
                "Reporting 4 as customers counts an unknown bucket as a buyer; quietly dropping "
                "the line instead hides a data-quality failure."
            ),
            (
                "With such a row, DISTINCTCOUNT returns 4, DISTINCTCOUNTNOBLANK returns 3 and "
                "COUNTBLANK(Sales[CustomerKey]) returns 1, so all three can be reported."
            ),
        ),
        (
            (
                "In 2025 each sales date has one buyer: Ada on January 2, Cy on January 3, Bo on "
                "January 5, Bo on February 2 and Cy on February 3. Their sum, 5, is a count of "
                "customer-days."
            ),
            (
                "Calling that 5 the unique 2025 customers overstates the population, because only "
                "Ada, Bo and Cy bought that year; Bo and Cy are counted twice."
            ),
            (
                "Under 2025, `SUMX ( VALUES ( 'Date'[Date] ), DISTINCTCOUNT ( Sales[CustomerKey] ) "
                ")` returns 5 and DISTINCTCOUNT alone returns 3."
            ),
        ),
    ],
    11: [
        (
            (
                "The 2025 lines are S4 to S8, with 123 USD over 12 units. Dividing the two totals "
                "weights each line by its units, so 10.25 USD per unit is the pooled rate."
            ),
            (
                "Averaging the line ratios (9, 5, 20, 10 and 18) gives 62 / 5 = 12.4. S6's single "
                "20 USD Mug then counts as much as S5's four Pens."
            ),
            (
                "`CALCULATE ( DIVIDE ( [NetRevenue], [QuantitySold] ), 'Date'[Year] = 2025 )` "
                "returns 10.25, and 10.25 x 12 = 123."
            ),
        ),
        (
            (
                "OrderCount uses DISTINCTCOUNT on OrderID because order 101 has two lines. Seven "
                "orders share 187 USD, about 26.7143 USD per order."
            ),
            (
                "Dividing by COUNTROWS(Sales) uses 8 lines and returns 23.375. That is revenue per "
                "line, not per order, because S1 and S2 belong to one order."
            ),
            (
                "`DIVIDE ( [NetRevenue], DISTINCTCOUNT ( Sales[OrderID] ) )` returns about "
                "26.7143, and 26.7143 x 7 reproduces 187."
            ),
        ),
        (
            (
                "DIVIDE with two arguments returns BLANK for an empty or zero denominator. Bag has "
                "no units, so its rate stays blank, while Notebook returns 67 / 7, about 9.571."
            ),
            (
                "Supplying 0 as the third argument shows Bag at 0 USD per unit, as if it sold "
                "units for free. Using `/` after coalescing units to 0 would produce infinity or "
                "NaN."
            ),
            (
                "By product expect Notebook about 9.571, Pen 24 / 5 = 4.8, Mug 96 / 5 = 19.2 and "
                "Bag BLANK."
            ),
        ),
        (
            (
                "Units are the denominator, so the pooled ratio weights each year by its units: "
                "12.8 x 5 + 10.25 x 12 = 64 + 123 = 187, and 187 / 17 = 11."
            ),
            (
                "`AVERAGEX ( VALUES ( 'Date'[Year] ), [NetPerUnit] )` gives each year equal weight "
                "and returns 11.525, as if 2024's five units mattered as much as 2025's twelve."
            ),
            (
                "The pooled measure returns 11 at the total, while the yearly rows show 12.8 and "
                "10.25."
            ),
        ),
        (
            (
                "A zero is observed when the denominator shows real opportunity. Bo's lines S3, S6 "
                "and S7 have 80 USD gross and no discount, so his discount rate is a true 0 / 80 = "
                "0."
            ),
            (
                "Using DIVIDE ( 0, 0, 0 ) for Di, who has no lines, shows his undefined rate as 0, "
                "so he looks exactly like Bo in the report."
            ),
            (
                "The case row shows DefaultResult BLANK but ZeroNumerator 0. By customer, Bo's "
                "discount rate is 0 and Di's is BLANK."
            ),
        ),
        (
            (
                "The design assigns two units per arm, so the denominator is assigned units. "
                "Control converts 1 of 2 (0.5) and Treatment converts 2 of 2 (1.0)."
            ),
            (
                "Building the denominator from exposure rows counts U3 twice, because it was "
                "exposed twice, and drops U4, which was assigned but never exposed."
            ),
            (
                "The rates should match ExperimentSummary: Assigned 2 and Rate 0.5 for Control, "
                "and Assigned 2 and Rate 1 for Treatment."
            ),
        ),
    ],
    12: [
        (
            (
                "The variable is bound once, with no filter, as 187. CALCULATE can change the "
                "filter around a scalar but cannot reevaluate it. Pen is the only Red product, so "
                "the direct measure returns 24."
            ),
            (
                "Expecting FrozenInRed to show 24 treats the variable as a formula that "
                "reevaluates in its new context. VAR stores a value, not the expression."
            ),
            (
                "The row should read FrozenInRed 187 and RecomputedInRed 24, the value of Pen's "
                "lines S2 and S5."
            ),
        ),
        (
            (
                "Binding inside the Blue CALCULATETABLE evaluates [NetRevenue] under Blue, so the "
                "variable holds 163. Every later use reuses 163, even under another filter."
            ),
            (
                "Binding the variable before CALCULATETABLE and expecting the outer Blue filter to "
                "reach it still returns 187, because the binding happened first."
            ),
            (
                "Inside Blue the variable returns 163, the same as `CALCULATE ( [NetRevenue], "
                'Product[Color] = "Blue" )`.'
            ),
        ),
        (
            (
                "Each variable is bound in its own context: the numerator under the current color, "
                "and the denominator after REMOVEFILTERS on Color. Under Blue that gives 163 / "
                "187, about 0.872."
            ),
            (
                "Binding the denominator to [NetRevenue] under Blue and wrapping it in CALCULATE "
                "with REMOVEFILTERS keeps 163, so the share becomes 1.0 for every color."
            ),
            (
                "Under Blue the share returns about 0.872, under Red 24 / 187, about 0.128, and "
                "the two shares add to 1."
            ),
        ),
        (
            (
                "The denominator must reevaluate the measure, so it is CALCULATE([NetRevenue], "
                "REMOVEFILTERS(Product[Color])). That returns 187 under Blue and under Red alike."
            ),
            (
                "Adding ALL or more CALCULATE layers around the frozen variable keeps 163 under "
                "Blue, because no wrapper can recompute a value that is already bound."
            ),
            (
                "Show the denominator as its own column. It should read 187 on every color row; if "
                "it equals the numerator, it is still frozen."
            ),
        ),
        (
            (
                "A variable defined before SUMX is one shared scalar, so `VAR Total = "
                "[NetRevenue]` holds 187 on every row. Each line divided by it gives a share, and "
                "the shares add to 1."
            ),
            (
                "Calling [NetRevenue] inside the iterator causes context transition to each line. "
                "Each share then divides the line by itself, and the eight results add to 8."
            ),
            (
                "`SUMX ( Sales, DIVIDE ( Sales[NetAmount], Total ) )` returns 1, while the in-row "
                "version returns 8."
            ),
        ),
        (
            (
                "A ledger records each step: the starting filter, the binding context, the value "
                "bound, the later filters and whether each use reuses or reevaluates. It can be "
                "checked against the fact rows."
            ),
            (
                "Debugging from the final number alone cannot tell whether 187 came from a frozen "
                "variable or a missing filter, because both give the same output."
            ),
            (
                "Blue is S1, S3, S4, S6, S7 and S8, which sum to 163; Red is S2 and S5, for 24; "
                "together they reconcile to 187."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

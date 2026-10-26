"""Stage two: typed expressions, storage lifetime, aggregation and variables."""

from .common import lesson
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
                    "DIVIDE([NetRevenue],SUM(Sales[Quantity])); the values are "
                    "17, 187 and 11."
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
                    "olor])), then DIVIDE(numerator,denominator)."
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

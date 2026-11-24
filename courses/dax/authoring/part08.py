"""Stage eight: composition, calculation groups, UDFs and visual scope."""

from .common import BASE, explain, lesson
from .common import result as r
from .common import task as t

PROFIT = BASE + (
    "    MEASURE Sales[Cost] = SUMX ( Sales, Sales[Quantity] * "
    "RELATED ( Product[UnitCost] ) )\n    MEASURE Sales[Profit] "
    "= [NetRevenue] - [Cost]\n    MEASURE Sales[NetMargin] = "
    "DIVIDE ( [Profit], [NetRevenue] )\n"
)
UDF_NOTE = (
    "Microsoft's DAX UDF documentation, reviewed on "
    "2026-10-25, states general availability in Power BI "
    "Desktop and Service from June 2026 and database "
    "compatibility level 1702 or higher. These offline "
    "definitions are not engine-tested here. UDF availability "
    "is distinct from calendar-based time intelligence's "
    "preview status."
)
GROUP_NOTE = (
    "Calculation groups require a supported semantic model and "
    "compatibility level 1500 or higher according to the "
    "reviewed Microsoft documentation. This lesson teaches "
    "definitions and explicitly expanded calculations offline; "
    "it does not create a calculation group in an engine."
)

LESSONS = [
    lesson(
        43,
        "Measure composition, dependency graphs and numeric formatting",
        ["measure dependency", "RELATED", "cost grain", "numeric measure", "format property"],
        ("Build a small reusable measure family with explicit units and dependency boundaries."),
        (
            "A measure family should reuse stable definitions rather "
            "than copy a long formula into every report. NetRevenue, "
            "Cost, Profit and NetMargin form a small dependency graph: "
            "profit subtracts compatible currency amounts, and margin "
            "divides profit by revenue. A change to the cost policy "
            "then has a visible dependency path instead of several "
            "subtly different pasted implementations.\n\nOur synthetic "
            "Product.UnitCost is constant per product for the modeled "
            "period. Within a Sales row, RELATED retrieves that "
            "product's cost through the many-to-one relationship. "
            "Multiplying by quantity gives a line cost. This "
            "assumption is deliberately simple: a real historical-cost "
            "requirement would need the effective cost at the "
            "transaction date, not an overwritten current product "
            "attribute.\n\nKeep the resulting margin numeric. Its "
            "display can be a percentage through a format property or "
            "a supported dynamic format string. FORMAT would instead "
            "return text. Formatting is not the source of the metric's "
            "meaning: NetMargin is profit per unit of revenue, and "
            "every term in its dependency graph must use the same "
            "population and compatible currency policy."
        ),
        (
            "The reference defines each dependency once. RELATED uses "
            "the row context created by SUMX to locate the product's "
            "UnitCost. The measure graph is acyclic: NetRevenue and "
            "Cost feed Profit, then Profit and NetRevenue feed "
            "NetMargin. A dynamic format expression belongs to "
            "formatting metadata, not inside the numeric margin "
            "formula."
        ),
        [
            r(
                "Whole-model profit graph",
                (
                    'EVALUATE ROW ( "Revenue", [NetRevenue], "Cost", [Cost], '
                    '"Profit", [Profit], "Margin", [NetMargin] )'
                ),
                [
                    ("Revenue", "number"),
                    ("Cost", "number"),
                    ("Profit", "number"),
                    ("Margin", "number"),
                ],
                [[187, 44, 143, 143 / 187]],
                (
                    "Clean retail model; current UnitCost is explicitly "
                    "constant per product; all amounts USD."
                ),
                [
                    "Line costs are 4, 1, 10, 6, 4, 5, 4, 10, totaling 44.",
                    "Profit is 187 - 44 = 143.",
                    "Margin is 143/187, evaluated from the same all-row population.",
                ],
                (
                    "The margin is a numeric ratio, not the text produced by a "
                    "percent formatter. Its meaning would change if costs and "
                    "revenues used different filters."
                ),
            ),
            r(
                "The same family under Blue",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "Revenue", [NetRevenue], '
                    '"Cost", [Cost], "Profit", [Profit], "Margin", [NetMargin] '
                    '), Product[Color] = "Blue" )'
                ),
                [
                    ("Revenue", "number"),
                    ("Cost", "number"),
                    ("Profit", "number"),
                    ("Margin", "number"),
                ],
                [[163, 39, 124, 124 / 163]],
                "Blue products only; the same measure definitions and cost assumptions.",
                [
                    "Notebook cost is 14 and Mug cost is 25, totaling 39.",
                    "Blue revenue 163 minus 39 gives profit 124.",
                    "The filtered margin is 124/163, not the unfiltered 143/187.",
                ],
                (
                    "A reusable definition remains context-dependent. Reuse "
                    "should preserve a formula's policy while allowing the "
                    "question's population to change."
                ),
            ),
        ],
        [
            t(
                "Predict Pen profit.",
                "Its revenue 24 and cost 5 belong to the same product population.",
                "Profit is 19 and margin is 19/24.",
            ),
            t(
                "Change UnitCost for Notebook to 3 in a hypothetical refreshed model.",
                "There are seven Notebook units in this fixture.",
                (
                    "Notebook cost rises from 14 to 21 and total profit falls "
                    "by 7. This illustrates why overwriting a current cost can "
                    "change historical reports."
                ),
            ),
            t(
                "Draw the dependency graph and annotate units.",
                "Separate base currency measures from a dimensionless ratio.",
                (
                    "NetRevenue USD and Cost USD feed Profit USD; "
                    "Profit/NetRevenue gives a dimensionless margin."
                ),
            ),
            t(
                'Diagnose FORMAT([NetMargin],"0.0%") being reused in arithmetic.',
                "FORMAT returns text.",
                (
                    "Keep NetMargin numeric and apply display formatting "
                    "separately; arithmetic should depend on the numeric "
                    "measure."
                ),
            ),
            t(
                "Explain a zero or missing revenue denominator.",
                "Profit can exist without a defined margin ratio.",
                (
                    "DIVIDE returns BLANK for an invalid denominator unless a "
                    "separate explicit policy is chosen."
                ),
            ),
            t(
                "Transfer the graph to an adjusted revenue family.",
                "Returns, discounts and taxes need compatible grain and units.",
                (
                    "Define each adjustment once, document its sign and "
                    "population, then compose the final metric with an "
                    "auditable dependency graph."
                ),
            ),
        ],
        defines=PROFIT,
        sources=[
            "https://learn.microsoft.com/en-us/dax/related-function-dax",
            (
                "https://learn.microsoft.com/en-us/power-bi/create-reports/"
                "desktop-dynamic-format-strings"
            ),
        ],
    ),
    lesson(
        44,
        "Calculation items transform selected measures",
        ["calculation group", "SELECTEDMEASURE", "ISSELECTEDMEASURE", "applicability", "reuse"],
        (
            "Describe a reusable transformation while preventing it "
            "from changing incompatible measures."
        ),
        (
            "A calculation group contains calculation items that "
            "transform a selected measure. SELECTEDMEASURE stands for "
            "that underlying measure expression within the "
            "calculation-item context. It is not an ordinary variable "
            "that can be pasted into any standalone scalar query. The "
            "group and item are model metadata in a real "
            "engine.\n\nReusing a transformation requires an "
            "applicability policy. A hypothetical ten-percent revenue "
            "fee can apply to NetRevenue, but multiplying QuantitySold "
            "by 0.9 would turn 17 recorded units into 15.3 without any "
            "corresponding change in transactions. ISSELECTEDMEASURE "
            "can guard the transformation so unrelated measures retain "
            "their definitions.\n\nThe worked references show the "
            "current values and the algebraically expanded guarded "
            "item. This is deliberate offline reasoning, not an "
            "execution of model calculation-group machinery. The item "
            "definition below states the reusable model expression; "
            "the query expansions make the expected arithmetic "
            "independently inspectable."
        ),
        (
            "The illustrative calculation item is "
            "IF(ISSELECTEDMEASURE([NetRevenue]),SELECTEDMEASURE()*0.9,S"
            "ELECTEDMEASURE()). Its two branches define revenue and "
            "non-revenue behavior. The reference queries expand those "
            "branches for named measures, so their expected results do "
            "not depend on a hidden configured group."
        ),
        [
            r(
                "Current measures before an item",
                'EVALUATE ROW ( "Revenue", [NetRevenue], "Units", [QuantitySold] )',
                [("Revenue", "number"), ("Units", "integer")],
                [[187, 17]],
                "No calculation item applied; baseline measure definitions.",
                [
                    "The eligible Sales rows total 187 USD.",
                    "Their quantities total 17 units.",
                    "These quantities have different units and transformation policies.",
                ],
                (
                    "A shared visual can contain both measures without "
                    "implying that every calculation item should transform "
                    "them identically."
                ),
            ),
            r(
                "Expanded guarded fee item",
                (
                    'EVALUATE ROW ( "RevenueAfterFee", [NetRevenue] * 0.9, '
                    '"UnitsUnchanged", [QuantitySold] )'
                ),
                [("RevenueAfterFee", "number"), ("UnitsUnchanged", "integer")],
                [[168.3, 17]],
                (
                    "Algebraic expansion of the named revenue-only item; no "
                    "live calculation-group execution."
                ),
                [
                    "The revenue branch multiplies 187 by 0.9, giving 168.3.",
                    "The guard leaves the quantity measure at 17.",
                    (
                        "The transformation changes a defined revenue policy, not "
                        "the observed transaction counts."
                    ),
                ],
                (
                    "An expanded query is a useful semantic reference. It does "
                    "not establish that a particular external model's group "
                    "selection, precedence or formatting is configured "
                    "correctly."
                ),
                note=(
                    "Hand-derived algebraic expansion of a specified "
                    "calculation item. No calculation group was created or "
                    "executed in this classroom."
                ),
            ),
        ],
        [
            t(
                "Predict the guarded item for Blue revenue.",
                "Apply the same policy to the filtered revenue 163.",
                "The transformed revenue is 146.7; Blue units remain 12.",
            ),
            t(
                "Remove the applicability guard conceptually.",
                "The transformation would also apply to quantities.",
                (
                    "Quantity 17 would become 15.3, which is inappropriate for "
                    "this observed-unit measure."
                ),
            ),
            t(
                "Write the calculation-item expression and its applicability contract.",
                "Use SELECTEDMEASURE only in the correct model scope.",
                (
                    "IF(ISSELECTEDMEASURE([NetRevenue]),SELECTEDMEASURE()*0.9,S"
                    "ELECTEDMEASURE()); document that only NetRevenue receives "
                    "the fee."
                ),
            ),
            t(
                "Diagnose pasting SELECTEDMEASURE into an ordinary query-local measure.",
                "The placeholder requires a calculation-item context.",
                (
                    "It does not name a normal measure argument there. Expand "
                    "a named measure for offline arithmetic or create the "
                    "appropriate model object externally."
                ),
            ),
            t(
                ("Explain whether selecting two calculation items has a universal default result."),
                "Selection behavior is model- and feature-dependent.",
                (
                    "Record the group's selection-expression policy and test "
                    "no-selection/multiple-selection cases in a real supported "
                    "model before deployment."
                ),
            ),
            t(
                "Transfer the guard to a prior-period calculation group.",
                "Not every measure should necessarily receive a date shift.",
                (
                    "Define which measures represent period flows, balances or "
                    "labels, then test each intended transformation and "
                    "excluded measure."
                ),
            ),
        ],
        feature=GROUP_NOTE,
        extra=(
            "A calculation-item definition is a different artifact "
            "from a full query:\n\n```dax\nIF ( ISSELECTEDMEASURE ( "
            "[NetRevenue] ), SELECTEDMEASURE() * 0.9, "
            "SELECTEDMEASURE() )\n```\n\nThis expression belongs in a "
            "named calculation item in a separately prepared model. "
            "The offline reference expands it for two known measures; "
            "it does not install metadata or imply an external account "
            "is required for study."
        ),
        sources=[
            (
                "https://learn.microsoft.com/en-us/analysis-services/tabula"
                "r-models/calculation-groups"
            ),
            "https://learn.microsoft.com/en-us/dax/selectedmeasure-function-dax",
            "https://learn.microsoft.com/en-us/dax/isselectedmeasure-function-dax",
        ],
    ),
    lesson(
        45,
        "Precedence and dynamic format strings",
        ["precedence", "expression expansion", "noncommutativity", "dynamic format string"],
        (
            "Expand interacting calculation items and distinguish "
            "numeric transformation from display selection."
        ),
        (
            "Two reusable transformations can produce different "
            "results when their order changes. Adding 10 then "
            "multiplying by 0.9 differs from multiplying first then "
            "adding 10. Calculation-group precedence defines how item "
            "expressions are composed around the selected measure; it "
            "is not a suggestion to ignore parentheses and rely on "
            "ordinary operator precedence.\n\nFor the simple arithmetic "
            "groups specified here, the higher-precedence item's "
            "expression forms the outer structure, and the "
            "lower-precedence expression replaces its SELECTEDMEASURE "
            "placeholder. A higher-precedence scale item therefore "
            "produces (Revenue + 10)*0.9. Reversing the groups' "
            "precedence produces Revenue*0.9 + 10. Write the expanded "
            "tree before calculating.\n\nDynamic format strings have "
            "their own precedence interaction. The highest-precedence "
            "applicable calculation-group format string determines "
            "presentation in the documented model behavior. A format "
            "expression returns a format pattern while leaving the "
            "measure numeric. It cannot repair an incorrectly composed "
            "numerical expression, and a currency pattern applied to a "
            "dimensionless ratio would mislabel the result."
        ),
        (
            "The reference queries are explicit expansions of the two "
            "declared precedence orders. They are intentionally "
            "ordinary arithmetic so the difference is visible without "
            "an engine. Real group creation, selected-item "
            "combinations and format-string precedence need separate "
            "external model tests."
        ),
        [
            r(
                "Scale has higher precedence",
                'EVALUATE ROW ( "ExpandedValue", ( [NetRevenue] + 10 ) * 0.9 )',
                [("ExpandedValue", "number")],
                [[177.3]],
                (
                    "Specified items: AddTen = SELECTEDMEASURE()+10 at lower "
                    "precedence; Scale = SELECTEDMEASURE()*0.9 at higher "
                    "precedence."
                ),
                [
                    "The outer Scale expression receives the lower-precedence AddTen expression.",
                    "The expansion is (187 + 10)*0.9.",
                    "197 multiplied by 0.9 is 177.3.",
                ],
                (
                    "The literal 10 represents an illustrative compatible "
                    "amount for this algebra example. A real fee policy would "
                    "also define which population and measures receive it."
                ),
            ),
            r(
                "Addition has higher precedence",
                'EVALUATE ROW ( "ExpandedValue", [NetRevenue] * 0.9 + 10 )',
                [("ExpandedValue", "number")],
                [[178.3]],
                (
                    "The same two item definitions with AddTen as the "
                    "higher-precedence outer expression."
                ),
                [
                    "The expansion is (187*0.9)+10.",
                    "The scale first yields 168.3.",
                    "Adding 10 gives 178.3, one more than the other order.",
                ],
                (
                    "Passing tests for each group alone does not prove their "
                    "combined behavior. Include interacting groups in a "
                    "measure/context regression matrix."
                ),
            ),
        ],
        [
            t(
                "Predict both expansions for a base value 100.",
                "Keep the parentheses from the expression tree.",
                "Scale-after-add gives 99; add-after-scale gives 100.",
            ),
            t(
                "Replace the additive 10 by zero.",
                "Some fixtures can hide noncommutativity.",
                (
                    "Both expressions become 0.9 times the base, so that case "
                    "cannot validate the intended order."
                ),
            ),
            t(
                "Write a regression grid for two interacting groups.",
                "Include groups alone, together and an unaffected measure.",
                (
                    "Record each group's selection, precedence, underlying "
                    "measure, filters, expanded numeric expression and "
                    "expected format pattern."
                ),
            ),
            t(
                "Diagnose fixing a wrong number by changing its format string.",
                "Presentation does not change the numeric expression's semantics.",
                (
                    "Repair composition or the business policy first. "
                    "Formatting can only change how the numeric result is "
                    "displayed."
                ),
            ),
            t(
                "Explain a percentage format on the value 177.3.",
                "A percent format scales display of a dimensionless fraction.",
                (
                    "It would imply a different unit and misleading scale; "
                    "keep currency and ratio measures' format policies "
                    "distinct."
                ),
            ),
            t(
                "Transfer precedence reasoning to currency conversion and time intelligence.",
                "Conversion and aggregation may occur at different grains.",
                (
                    "Expand the combined expressions and verify "
                    "transaction/rate grain and date-role behavior; arithmetic "
                    "examples alone do not qualify a real currency/time group "
                    "combination."
                ),
            ),
        ],
        feature=GROUP_NOTE,
        extra=(
            "For a separately configured dynamic format string, a "
            "model can choose a pattern while retaining a numeric "
            "measure. A conceptual example for a known margin measure "
            "is:\n\n```dax\nIF ( ISSELECTEDMEASURE ( [NetMargin] ), "
            '"0.0%", SELECTEDMEASUREFORMATSTRING() )\n```\n\nThe '
            "NetMargin definition appears in the measure-composition "
            "lesson. This is a format-expression example in the "
            "appropriate model scope, not a query or a conversion of "
            "units. Actual locale, group selection and format "
            "precedence remain part of external model acceptance."
        ),
        sources=[
            (
                "https://learn.microsoft.com/en-us/analysis-services/tabula"
                "r-models/calculation-groups"
            ),
            (
                "https://learn.microsoft.com/en-us/power-bi/create-reports/"
                "desktop-dynamic-format-strings"
            ),
        ],
    ),
    lesson(
        46,
        "DAX UDFs: explicit parameters and a reusable scalar rule",
        ["FUNCTION", "UDF", "numeric parameter", "default argument", "compatibility"],
        ("Define a small reusable function with a clear parameter domain and default behavior."),
        (
            "A user-defined function packages an expression behind "
            "named parameters. This differs from a measure, which "
            "obtains its evaluation context from the model/query "
            "rather than accepting an ordinary explicit argument "
            "list. A UDF can help centralize a stable calculation "
            "rule, but it still needs a documented domain, units "
            "and error policy.\n\nThe original example "
            "Course.NetAfterFee accepts a numeric amount and an "
            "optional numeric fee rate. The default rate is 0.1; "
            "values outside 0..1 deliberately return BLANK. This "
            "rule is a teaching policy, not a universal financial "
            "convention. Returning BLANK is distinguishable from a "
            "valid zero at a 100-percent fee.\n\nThe function "
            "definition and two calls can live in query scope using "
            "DEFINE FUNCTION on a compatible engine. Persisting a "
            "function in a semantic model is a separate authoring "
            "action. The classroom saves the source text and "
            "explains its result; it neither compiles the "
            "definition nor proves compatibility with a particular "
            "external model."
        ),
        (
            "FUNCTION introduces the name and parameter list, the "
            "arrow separates the signature from its body, and the "
            "default expression follows the optional parameter's "
            "equals sign. NUMERIC is a scalar subtype annotation. The "
            "query supplies explicit output names so default, explicit "
            "and invalid-domain cases cannot be confused."
        ),
        [
            r(
                "Default and explicit rates",
                (
                    'EVALUATE ROW ( "DefaultFee", Course.NetAfterFee ( '
                    '[NetRevenue] ), "ExplicitTwentyPercent", '
                    "Course.NetAfterFee ( [NetRevenue], 0.2 ) )"
                ),
                [("DefaultFee", "number"), ("ExplicitTwentyPercent", "number")],
                [[168.3, 149.6]],
                "All-row revenue 187; fee-rate domain 0..1; default rate 0.1.",
                [
                    "The omitted rate uses 0.1, giving 187*(1-0.1)=168.3.",
                    "An explicit 0.2 overrides that default.",
                    "187*(1-0.2)=149.6.",
                ],
                (
                    "A default argument is part of the function contract. "
                    "Changing it can alter every call that omits the "
                    "parameter, even if the call source itself stays unchanged."
                ),
            ),
            r(
                "A valid zero and an invalid rate",
                (
                    'EVALUATE ROW ( "FullFee", Course.NetAfterFee ( 100, 1 ), '
                    '"InvalidRate", Course.NetAfterFee ( 100, 1.2 ) )'
                ),
                [("FullFee", "number"), ("InvalidRate", "number")],
                [[0, None]],
                "Same function; compare boundary rate 1 with out-of-domain rate 1.2.",
                [
                    "Rate 1 is inside the declared domain and leaves zero amount.",
                    "Rate 1.2 violates the rule.",
                    (
                        "The invalid-domain branch returns BLANK, not a fabricated "
                        "negative net amount."
                    ),
                ],
                (
                    "A caller should retain a validation signal if BLANK could "
                    "be mistaken for no activity. A more elaborate error "
                    "policy belongs in the function's documented contract."
                ),
            ),
        ],
        [
            t(
                "Predict Course.NetAfterFee(50,0).",
                "Zero fee is a valid boundary.",
                "The result is 50.",
            ),
            t(
                "Change the default rate to 0.15 in a hypothetical version.",
                "Only calls omitting the argument use the changed default.",
                (
                    "The 187 default call would become 158.95; the explicit "
                    "0.2 call would remain 149.6."
                ),
            ),
            t(
                "Write a function contract with units and domain.",
                "Types do not fully describe business meaning.",
                (
                    "Amount is a numeric value in one declared currency; "
                    "feeRate is a dimensionless fraction in 0..1; output uses "
                    "the same currency and invalid rates return BLANK."
                ),
            ),
            t(
                (
                    "Diagnose treating a measure reference as a function that "
                    "accepts a rate argument."
                ),
                "Measures and UDFs have different invocation contracts.",
                (
                    "Use a defined UDF for explicit parameters, or model a "
                    "disconnected parameter selection for a measure; do not "
                    "invent measure-call syntax."
                ),
            ),
            t(
                ("Explain why function text alone does not prove an external model supports UDFs."),
                "Availability and compatibility are separate inputs.",
                (
                    "Verify the documented product release and database "
                    "compatibility level before external use; this offline "
                    "file is not a compiler receipt."
                ),
            ),
            t(
                "Transfer the rule to reusable metric normalization.",
                "Avoid hiding population choices inside a deceptively generic function.",
                (
                    "Document units, accepted domains, missingness and "
                    "evaluation-mode assumptions, then test boundary calls and "
                    "the caller's context separately."
                ),
            ),
        ],
        defines=BASE
        + (
            "    FUNCTION Course.NetAfterFee = ( amount : NUMERIC, "
            "feeRate : NUMERIC = 0.1 ) =>\n        IF ( feeRate >= 0 && "
            "feeRate <= 1, amount * ( 1 - feeRate ), BLANK() )\n"
        ),
        feature=UDF_NOTE,
        sources=[
            ("https://learn.microsoft.com/en-us/dax/best-practices/dax-user-defined-functions")
        ],
    ),
    lesson(
        47,
        "UDF value versus expression parameters",
        ["VAL", "EXPR", "eager evaluation", "deferred evaluation", "filter context"],
        (
            "Predict whether a UDF receives a precomputed value or an "
            "expression evaluated under its own modifier."
        ),
        (
            "A value parameter is evaluated before the function body "
            "uses it. An expression parameter can defer evaluation "
            "into the function body, where a changed filter context "
            "can matter. This resembles the variable-versus-measure "
            "distinction, but it is now an explicit part of the "
            "function's parameter contract.\n\nCourse.BlueValue receives "
            "a numeric scalar by VAL and then places that scalar "
            "inside a Blue CALCULATE. With no incoming filters, the "
            "scalar is already 187, so it remains 187. "
            "Course.BlueExpression receives the expression by EXPR and "
            "evaluates it under the Blue modifier, producing 163. The "
            "function body looks similar, but the parameter mode "
            "changes its semantics.\n\nUnder an incoming Red selection, "
            "the eager value is 24 while the deferred expression still "
            "becomes 163 because the function's Blue filter replaces "
            "the same Color column. This is a context-transforming "
            "API, so its name and documentation should disclose that "
            "behavior. Reference parameters have their own required "
            "expression-mode rules; do not assume every type can use "
            "every passing mode."
        ),
        (
            "The signatures explicitly say SCALAR NUMERIC VAL or "
            "SCALAR NUMERIC EXPR. The source passes [NetRevenue] in "
            "both calls. The body uses "
            'CALCULATE(amount,Product[Color]="Blue"). Microsoft\'s '
            "current documentation distinguishes the "
            "row/filter-context inheritance of eager and deferred "
            "arguments; these cases use filter context only and do not "
            "generalize to an arbitrary caller's row context."
        ),
        [
            r(
                "Unfiltered caller",
                (
                    'EVALUATE ROW ( "EagerValue", Course.BlueValue ( '
                    '[NetRevenue] ), "DeferredExpression", '
                    "Course.BlueExpression ( [NetRevenue] ) )"
                ),
                [("EagerValue", "number"), ("DeferredExpression", "number")],
                [[187, 163]],
                (
                    "No incoming filter; both calls receive the same written "
                    "measure argument with different parameter modes."
                ),
                [
                    "VAL evaluates [NetRevenue] before the body and passes 187.",
                    "Changing color around that scalar cannot recreate its original expression.",
                    "EXPR evaluates the measure under Blue and returns 163.",
                ],
                (
                    "Parameter annotations change observable behavior. They "
                    "are not merely documentation for an otherwise identical "
                    "function."
                ),
            ),
            r(
                "Red caller and a Blue-transforming function",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "EagerValue", '
                    'Course.BlueValue ( [NetRevenue] ), "DeferredExpression", '
                    "Course.BlueExpression ( [NetRevenue] ) ), Product[Color] "
                    '= "Red" )'
                ),
                [("EagerValue", "number"), ("DeferredExpression", "number")],
                [[24, 163]],
                "Incoming Color=Red; the function body requests Color=Blue.",
                [
                    "The eager argument is evaluated in Red and becomes 24.",
                    "The deferred argument is evaluated after the body's Color replacement.",
                    "Its Blue result is 163, not a Red-and-Blue intersection.",
                ],
                (
                    "A function intended to stay inside the caller's "
                    "population would need a different filter policy, such as "
                    "an appropriate intersection, plus its own tests."
                ),
            ),
        ],
        [
            t(
                "Predict the eager call when the caller selects Paper.",
                "The value is computed before entering the function.",
                "It receives 91. The deferred Blue expression retains Paper and returns 67.",
            ),
            t(
                "Replace the body's plain Blue filter by KEEPFILTERS(Blue).",
                "Apply the selection policy after distinguishing parameter modes.",
                (
                    "For a Red caller the deferred expression would be BLANK; "
                    "the eager scalar would remain 24 because it was already "
                    "computed."
                ),
            ),
            t(
                "Write documentation warning callers about context changes.",
                "Name the column modified and the argument mode.",
                (
                    "State that the EXPR function reevaluates its numeric "
                    "argument under a Blue Color replacement while preserving "
                    "unrelated filters."
                ),
            ),
            t(
                "Diagnose changing a VAL parameter to EXPR as a purely performance refactor.",
                "The same written call can now evaluate in a different context.",
                (
                    "It is a semantic change and requires result comparison "
                    "across caller filters and row contexts."
                ),
            ),
            t(
                "Explain why this lesson does not validate an arbitrary row-context caller.",
                "The current cases intentionally use filter context only.",
                (
                    "Deferred arguments have documented context-inheritance "
                    "rules; add explicit iterator and reference-parameter "
                    "cases before relying on another calling pattern."
                ),
            ),
            t(
                "Transfer the distinction to a reusable period-selection UDF.",
                "A precomputed value cannot be shifted to another period after the fact.",
                (
                    "Use an appropriately declared deferred "
                    "expression/reference when period context must change, and "
                    "document compatibility and evaluation scope."
                ),
            ),
        ],
        defines=BASE
        + (
            "    FUNCTION Course.BlueValue = ( amount : SCALAR NUMERIC "
            "VAL ) =>\n        CALCULATE ( amount, Product[Color] = "
            '"Blue" )\n    FUNCTION Course.BlueExpression = ( amount : '
            "SCALAR NUMERIC EXPR ) =>\n        CALCULATE ( amount, "
            'Product[Color] = "Blue" )\n'
        ),
        feature=UDF_NOTE,
        sources=[
            ("https://learn.microsoft.com/en-us/dax/best-practices/dax-user-defined-functions"),
            "https://learn.microsoft.com/en-us/dax/calculate-function-dax",
        ],
    ),
    lesson(
        48,
        "Visual calculations operate on a visual's aggregated shape",
        ["visual calculation", "RUNNINGSUM", "visual order", "aggregation grain", "scope"],
        "Distinguish a visual running total from a reusable semantic-model measure.",
        (
            "A visual calculation belongs to a visual and operates "
            "over the data and structure supplied to that visual. It "
            "does not receive the complete transaction model merely "
            "because its expression uses DAX. The fields must be "
            "available in that visual's shape, and "
            "relationship-dependent functions such as RELATED or "
            "USERELATIONSHIP are not available in that scope according "
            "to the reviewed documentation.\n\nThe synthetic visual "
            "snapshot has January 2025 revenue 67 and February 2025 "
            "revenue 56. A running sum in ascending month order gives "
            "67 then 123. Reversing the displayed order gives 56 then "
            "123. The same two aggregated values produce different "
            "intermediate results because position in the visual is "
            "part of the calculation's input.\n\nThe reference queries "
            "below reproduce the running-sum arithmetic over explicit "
            "literal snapshots. They are not executions of Power BI "
            "visual calculations. The actual visual expression "
            "RUNNINGSUM([Revenue]) belongs to a separately prepared "
            "visual with its axis, order and reset behavior defined. "
            "Keep model measures for reusable semantic logic and use "
            "visual calculations only when their visual-scoped "
            "definition fits the question."
        ),
        (
            "The literal Position column makes the visual order "
            "explicit. ADDCOLUMNS evaluates a current position, and "
            "SUMX sums snapshot values at positions up to it. This "
            "expansion explains the arithmetic of the named flat "
            "visual. A hierarchical visual can additionally require "
            "partition/reset rules that this example does not emulate."
        ),
        [
            r(
                "Ascending month snapshot",
                (
                    'EVALUATE\nVAR VisualRows = DATATABLE ( "Position", '
                    'INTEGER, "Month", STRING, "Revenue", INTEGER, { { 1, '
                    '"January2025", 67 }, { 2, "February2025", 56 } } )\nRETURN '
                    'ADDCOLUMNS ( VisualRows, "RunningRevenue", VAR '
                    "CurrentPosition = [Position] RETURN SUMX ( FILTER ( "
                    "VisualRows, [Position] <= CurrentPosition ), [Revenue] ) "
                    ")\nORDER BY [Position]"
                ),
                [
                    ("Position", "integer"),
                    ("Month", "text"),
                    ("Revenue", "number"),
                    ("RunningRevenue", "number"),
                ],
                [[1, "January2025", 67, 67], [2, "February2025", 56, 123]],
                (
                    "A supplied flat visual snapshot in ascending month order; "
                    "arithmetic expansion only."
                ),
                [
                    "The first position contains January revenue 67.",
                    "The second position includes 67 plus February 56.",
                    "Running values are 67 and 123.",
                ],
                (
                    "The snapshot values are already monthly aggregates. "
                    "Reaching back to individual Sales rows would change the "
                    "scope and require model-level logic."
                ),
                note=(
                    "Hand-derived expansion over a named visual snapshot. No "
                    "Power BI visual was created or executed."
                ),
            ),
            r(
                "Reversed visual order",
                (
                    'EVALUATE\nVAR VisualRows = DATATABLE ( "Position", '
                    'INTEGER, "Month", STRING, "Revenue", INTEGER, { { 1, '
                    '"February2025", 56 }, { 2, "January2025", 67 } } )\nRETURN '
                    'ADDCOLUMNS ( VisualRows, "RunningRevenue", VAR '
                    "CurrentPosition = [Position] RETURN SUMX ( FILTER ( "
                    "VisualRows, [Position] <= CurrentPosition ), [Revenue] ) "
                    ")\nORDER BY [Position]"
                ),
                [
                    ("Position", "integer"),
                    ("Month", "text"),
                    ("Revenue", "number"),
                    ("RunningRevenue", "number"),
                ],
                [[1, "February2025", 56, 56], [2, "January2025", 67, 123]],
                (
                    "The same monthly values in descending month order; no "
                    "change to their underlying amounts."
                ),
                [
                    "February 56 is now the first visible position.",
                    "January 67 is added at the second position.",
                    (
                        "The intermediate running value changes from 67 to 56 "
                        "while the final sum remains 123."
                    ),
                ],
                (
                    "A cumulative-looking line can therefore change meaning "
                    "when sort order changes. State its axis and ordering "
                    "contract in the report."
                ),
                note=(
                    "Hand-derived expansion of a second visual snapshot, not "
                    "execution of edited source or visual-calculation APIs."
                ),
            ),
        ],
        [
            t(
                "Predict the running result if the visual includes only February.",
                "The visual-scoped population has one row.",
                (
                    "The running value is 56, not all-year 123, unless another "
                    "explicit semantic-model measure supplies a different "
                    "value."
                ),
            ),
            t(
                "Add a third observed month with revenue 10 at the end.",
                "Use the declared ascending positions.",
                "The running values become 67, 123, 133 for that expanded snapshot.",
            ),
            t(
                "Write the intended visual expression and its scope contract.",
                "The formula alone does not specify axis and ordering.",
                (
                    "RUNNINGSUM([Revenue]) on a flat monthly visual, ascending "
                    "calendar order, with a stated reset policy and the "
                    "required Revenue field present."
                ),
            ),
            t(
                "Diagnose using USERELATIONSHIP inside this visual calculation.",
                "Relationship functions require a different evaluation scope.",
                (
                    "Move the date-role calculation into a semantic-model "
                    "measure, then place that measure's results in the visual."
                ),
            ),
            t(
                "Explain why a hierarchical subtotal requires additional review.",
                "Running accumulation can reset or continue across hierarchy boundaries.",
                (
                    "Specify axis, partition and reset semantics; the flat "
                    "two-row expansion does not prove hierarchical behavior."
                ),
            ),
            t(
                "Transfer the distinction to a report-specific moving average.",
                "The input is displayed aggregate cells, not necessarily raw observations.",
                (
                    "Use it only when the visual grain and order match the "
                    "intended metric; retain reusable model measures for "
                    "cross-report semantics."
                ),
            ),
        ],
        defines="",
        feature=(
            "Reviewed 2026-10-25: Microsoft's visual-calculation "
            "documentation describes a separate visual-scoped facility "
            "available in Desktop and Service. This offline course "
            "does not provide that facility, a visual editor or "
            "external execution; it supplies explicit snapshots and "
            "arithmetic explanations."
        ),
        extra=(
            "A separately prepared flat visual can use this expression "
            "when Revenue is present in its visual "
            "shape:\n\n```dax\nRunningRevenue = RUNNINGSUM ( [Revenue] "
            ")\n```\n\nIt is a visual-calculation definition, not a "
            "persisted semantic-model measure or a complete DAX query. "
            "The two query expansions above explain the named "
            "snapshots without claiming to reproduce every visual-axis "
            "feature."
        ),
        sources=[
            (
                "https://learn.microsoft.com/en-us/power-bi/transform-model"
                "/desktop-visual-calculations-overview"
            ),
            "https://learn.microsoft.com/en-us/dax/runningsum-function-dax",
        ],
    ),
]


REASONING = {
    43: [
        (
            (
                "Revenue and cost are filtered by the same Product row. Pen sold S2 (1 unit, 4 "
                "USD) and S5 (4 units, 20 USD): revenue 24, and cost 5 units x 1 = 5."
            ),
            (
                "Using Pen's revenue with the whole-model cost, 44, gives a profit of -20. The two "
                "inputs must cover the same products."
            ),
            (
                'Under Product[ProductName] = "Pen", expect Revenue 24, Cost 5, Profit 19 and '
                "Margin 19 / 24, about 0.792."
            ),
        ),
        (
            (
                "Cost reads RELATED(Product[UnitCost]) on every line. Notebook sold 2 + 3 + 2 = 7 "
                "units, so its cost moves from 7 x 2 = 14 to 7 x 3 = 21."
            ),
            (
                "Assuming only future sales change. With current-cost lookups, the 2024 Notebook "
                "line S1 is restated too, so last year's reported profit moves."
            ),
            "Total Cost becomes 51, Profit 136 and NetMargin 136 / 187, about 0.727.",
        ),
        (
            (
                "NetRevenue (USD, SUM of NetAmount) and Cost (USD, SUMX of quantity times unit "
                "cost) feed Profit (USD). NetMargin divides Profit by NetRevenue and has no unit."
            ),
            (
                "Drawing NetMargin as depending on Cost directly, or annotating it as USD, hides "
                "that it changes when either Profit or NetRevenue changes."
            ),
            (
                "Each node's value checks against case A: 187 and 44 give 143, and 143 / 187 is "
                "about 0.765."
            ),
        ),
        (
            (
                'FORMAT returns text such as "76.5%". Arithmetic and comparison on that text no '
                "longer follow the numeric value."
            ),
            (
                'Comparing formatted margins as text: "9.0%" is greater than "76.5%" because '
                '"9" sorts after "7", so a threshold test on text gives the wrong answer.'
            ),
            (
                "Keep NetMargin numeric (about 0.765) and set the display format on the measure; "
                "ISNUMBER([NetMargin]) should be TRUE."
            ),
        ),
        (
            (
                "Margin is undefined when revenue is zero or BLANK. Bag has no sales, so its "
                "revenue, cost and profit are BLANK, and DIVIDE returns BLANK for its margin."
            ),
            (
                "Wrapping the ratio as IFERROR(..., 0) shows Bag at a 0 percent margin, which "
                "reads like break-even sales."
            ),
            (
                'Under ProductName = "Bag", NetMargin is BLANK; a hypothetical 0 USD line with 5 '
                "USD cost gives Profit -5 and a BLANK margin."
            ),
        ),
        (
            (
                "Define each adjustment once with its sign: GrossRevenue 195, minus discounts 8 "
                "(S2 1, S4 3, S8 4), is NetRevenue 187. Analytics Returns refunds 4 on S2 and 9 on "
                "S4."
            ),
            (
                "Subtracting the refunds from GrossRevenue as well as from NetRevenue, or applying "
                "the discount twice, makes the family stop reconciling."
            ),
            (
                "195 - 8 = 187, and 187 - 13 = 174 for a return-adjusted revenue; each step "
                "reconciles with the previous measure."
            ),
        ),
    ],
    44: [
        (
            (
                "The guarded item multiplies only NetRevenue. Under Blue, revenue is 163, so the "
                "item returns 163 x 0.9, and Blue units (Notebook 7 + Mug 5) stay 12."
            ),
            (
                "Computing the fee once on the 187 total and subtracting 18.7 from Blue revenue "
                "gives 144.3, which charges Blue for every product's fee."
            ),
            'Under Product[Color] = "Blue", expect 146.7 and 12.',
        ),
        (
            (
                "Without ISSELECTEDMEASURE the item touches every measure in the group's scope, "
                "including counts measured in units."
            ),
            (
                "The unguarded item returns 17 x 0.9 = 15.3 units and turns the 7 distinct orders "
                "into 6.3, values that cannot be observed."
            ),
            (
                "QuantitySold should stay 17 and OrderCount 7 when the item is applied; only "
                "NetRevenue changes to 168.3."
            ),
        ),
        (
            (
                "`IF ( ISSELECTEDMEASURE ( [NetRevenue] ), SELECTEDMEASURE () * 0.9, "
                "SELECTEDMEASURE () )` applies the fee to one named measure and passes the rest "
                "through."
            ),
            (
                'Writing the guard as IF(SELECTEDMEASURENAME() = "Revenue", ...) depends on a '
                "display name, so renaming the measure silently turns the fee off."
            ),
            (
                "The contract lists NetRevenue as the only affected measure and expects 187 to "
                "become 168.3 and QuantitySold to stay 17."
            ),
        ),
        (
            (
                "SELECTEDMEASURE is a placeholder inside calculation items. A query-local measure "
                "has no selected measure to stand for."
            ),
            (
                "Defining MEASURE Sales[Fee] = SELECTEDMEASURE() * 0.9 in a query and expecting "
                "168.3. The reference has nothing to resolve to."
            ),
            "The offline expansion `[NetRevenue] * 0.9` returns 168.3, as in case B.",
        ),
        (
            (
                "When a slicer selects two items, or none, the result depends on the group's "
                "selection-expression settings and the product's rules, not on DAX in general."
            ),
            (
                "Assuming two selected items stack into 187 x 0.9 x 0.9, or that the first one "
                "wins. Neither follows from this file."
            ),
            (
                "Record the expected no-selection result (187 here) and the multiple-selection "
                "result for the configured group, then test both in a supported model."
            ),
        ),
        (
            (
                "A prior-period item should shift flows such as NetRevenue: under January 2025, "
                "the prior year's January is 64. A label such as a data-through date should not "
                "shift."
            ),
            (
                "Applying the shift to every measure makes a freshness label read a year earlier "
                "and makes an inventory balance from another lesson behave like a flow."
            ),
            (
                "Under January 2025, the prior-period item gives NetRevenue 64 and OrderCount 2 "
                "(orders 101 and 102); excluded measures return their current values."
            ),
        ),
    ],
    45: [
        (
            (
                "Precedence sets nesting. In case A, Scale (higher) is applied outside AddTen, "
                "giving (100 + 10) x 0.9. In case B, AddTen is outside, giving 100 x 0.9 + 10."
            ),
            (
                "Treating the two items as commutative because both are simple arithmetic. They "
                "differ by 1 at base 100, as at 187."
            ),
            "(100 + 10) x 0.9 = 99 and 100 x 0.9 + 10 = 100.",
        ),
        (
            (
                "With an additive 0, both orders reduce to 0.9 times the base: 187 x 0.9 = 168.3 "
                "in either order."
            ),
            (
                "Using this zero case as the regression test and concluding precedence is correct, "
                "when it cannot tell the orders apart."
            ),
            (
                "Both expansions return 168.3. Keep a nonzero offset, as in case A's 177.3 and "
                "case B's 178.3, in the test grid."
            ),
        ),
        (
            (
                "The grid covers each item alone, both items, and an unaffected measure: base 187, "
                "AddTen alone 197, Scale alone 168.3, both 177.3 with Scale higher, and "
                "QuantitySold 17 if guarded."
            ),
            (
                "Testing only the combined row. A wrong expression in one item can be hidden by "
                "the other."
            ),
            (
                "Each grid row lists its selection, precedence, measure, filter context, expanded "
                "expression, expected value and expected format string."
            ),
        ),
        (
            (
                "A format string changes only how a number is shown. If 178.3 is expected and "
                "177.3 appears, the items are nested in the wrong order."
            ),
            (
                "Changing the format to zero decimals and calling it fixed: 177.3 shows as 177, "
                "still not 178, and the nesting is unchanged."
            ),
            (
                "Fix the precedence or item expression first, then confirm the raw value, 178.3 or "
                "177.3 as specified, before applying a format."
            ),
        ),
        (
            "177.3 is a USD amount. A percentage format multiplies the display by 100.",
            (
                'Applying "0.0%" to this measure shows 17730.0%, a unit change that makes a '
                "revenue figure look like a ratio."
            ),
            (
                "Keep currency formats on currency measures, and use percentage formats only on "
                "fractions such as NetMargin (about 0.765)."
            ),
        ),
        (
            (
                "Combining a currency item with a time item works like the AddTen and Scale "
                "nesting, except that conversion depends on transaction-date rates."
            ),
            (
                "Converting a shifted total with one rate. Lesson dax-042 shows 150 EUR at "
                "transaction rates is 170 USD, but at the highest rate it is 180."
            ),
            (
                "Expand both orders for a known case and compare with row-level conversion; the "
                "date-role and rate-grain cases need their own tests."
            ),
        ),
    ],
    46: [
        (
            ("A rate of 0 is inside the 0 to 1 domain, so the function returns amount x (1 - 0)."),
            (
                "Expecting 0 to count as omitted and trigger the 0.1 default, which gives 45. The "
                "default applies only when the argument is missing."
            ),
            "Course.NetAfterFee(50, 0) returns 50.",
        ),
        (
            (
                "Calls that omit the rate use the default, so only the first column moves: 187 x "
                "0.85. The explicit 0.2 call still computes 187 x 0.8."
            ),
            (
                "Expecting both columns to change because both call the same function. An explicit "
                "argument always overrides the default."
            ),
            "DefaultFee becomes 158.95 and ExplicitTwentyPercent stays 149.6.",
        ),
        (
            (
                "The contract names the amount's currency (USD for NetRevenue), the rate as a "
                "fraction from 0 to 1, the output in the same currency, and BLANK for invalid "
                "rates."
            ),
            (
                "A caller passing 10 for 10 percent gets BLANK, because 10 is outside the domain. "
                "Without the contract, that looks like a bug."
            ),
            (
                "Course.NetAfterFee(187, 0.1) returns 168.3 and Course.NetAfterFee(187, 10) "
                "returns BLANK, both as documented."
            ),
        ),
        (
            (
                "Measures take no arguments. A rate that varies by caller is either a UDF "
                "parameter or a selection from a disconnected parameter table read with "
                "SELECTEDVALUE."
            ),
            "Writing `[NetRevenue](0.2)` as if a measure accepted a rate. It is not valid DAX.",
            (
                "Course.NetAfterFee([NetRevenue], 0.2) returns 149.6; a parameter table with 0.2 "
                "selected should give the same."
            ),
        ),
        (
            (
                "Whether UDFs are available depends on the product release, the feature's status "
                "and the model's compatibility level. Valid function text does not show that "
                "support."
            ),
            (
                "Copying the FUNCTION definition into an older model and assuming that, since it "
                "ran in this course, it will deploy."
            ),
            (
                "Check the target release and compatibility level in the documentation, then run "
                "case A in that model and expect 168.3 and 149.6."
            ),
        ),
        (
            (
                "A normalization function, such as revenue per unit, should take both values as "
                "parameters: 187 / 17 = 11 USD per unit overall."
            ),
            (
                "A function that applies ALL(Product) inside its body. Every caller then gets the "
                "overall figure, 11, even under Blue, where 163 / 12 is about 13.58."
            ),
            (
                "Call it under Blue and expect about 13.58; any population change belongs in the "
                "caller's filters, where it is visible."
            ),
        ),
    ],
    47: [
        (
            (
                "A VAL parameter is computed in the caller's context before the body runs. Under "
                "Paper that value is 91. The EXPR version is evaluated inside CALCULATE, which "
                "replaces the Color filter with Blue and keeps Category Paper."
            ),
            (
                "Expecting the deferred call to return 163 as in case A. The Paper filter is still "
                "there, so only Notebook is Blue and Paper."
            ),
            'Under Product[Category] = "Paper", EagerValue is 91 and DeferredExpression 67.',
        ),
        (
            (
                "KEEPFILTERS intersects Blue with the caller's filters instead of replacing them. "
                "For a Red caller, Red and Blue have nothing in common."
            ),
            (
                "Assuming KEEPFILTERS also affects the VAL function. Its argument, 24, was already "
                "computed before the body ran."
            ),
            (
                'Under Color = "Red", the KEEPFILTERS EXPR version returns BLANK and the VAL '
                "version still returns 24."
            ),
        ),
        (
            (
                "The documentation should say that BlueExpression re-evaluates its argument with "
                "Product[Color] replaced by Blue and other Product filters kept."
            ),
            (
                'Documenting it as "returns Blue revenue". A Paper caller gets 67, not 163, '
                "which surprises anyone who read the short label."
            ),
            "Run the documented examples: no filter 163, Red caller 163, Paper caller 67.",
        ),
        (
            (
                "Changing VAL to EXPR changes meaning. The same written call is evaluated in the "
                "function's context instead of the caller's."
            ),
            (
                "Treating the change as a performance refactor. For a Red caller the result moves "
                "from 24 to 163."
            ),
            (
                "Compare both modes across callers before shipping: unfiltered 187 versus 163, Red "
                "24 versus 163, Paper 91 versus 67."
            ),
        ),
        (
            (
                "Both cases use filter context only. With a row context, for example inside "
                "ADDCOLUMNS over Product names, the argument picks up each row through context "
                "transition, which these cases do not cover."
            ),
            (
                "Concluding from cases A and B that BlueExpression behaves the same inside any "
                "iterator."
            ),
            (
                "Add an iterator case, such as ADDCOLUMNS(VALUES(Product[ProductName]), ...), with "
                "expected values for each product before relying on it."
            ),
        ),
        (
            (
                "Shifting periods needs the deferred form, because a VAL argument arrives as one "
                "number. Under January 2025 that number is 67 and cannot be moved to January 2024."
            ),
            (
                "Declaring the measure parameter as VAL in a prior-period UDF. `CALCULATE ( "
                "amount, SAMEPERIODLASTYEAR ( 'Date'[Date] ) )` in the body still returns 67."
            ),
            (
                "With an EXPR argument, the function returns 64 under January 2025, the January "
                "2024 value."
            ),
        ),
    ],
    48: [
        (
            (
                "A visual calculation sees only the visual's rows. With February alone, the "
                "running sum has one row to add."
            ),
            (
                "Expecting 123 because February 3 YTD was 123 in an earlier lesson. That total "
                "came from a model measure using the Date table, not from visual rows."
            ),
            "A one-row snapshot of February 2025 at 56 returns RunningRevenue 56.",
        ),
        (
            (
                "With a third row at position 3, each running value adds every row at or before "
                "its position: 67, 67 + 56 and 123 + 10."
            ),
            (
                "Appending the new row at position 1 changes every running value, as reversing the "
                "order did in case B."
            ),
            "The three-row DATATABLE returns 67, 123 and 133.",
        ),
        (
            (
                "`RUNNINGSUM ( [Revenue] )` on a flat visual with Month on the axis, sorted by "
                "month key ascending, with no reset and Revenue in the visual."
            ),
            (
                'Sorting by the Month text. "February2025" sorts before "January2025", which '
                "produces case B's 56 then 123."
            ),
            (
                "With the axis sorted by MonthKey, January 2025 shows 67 and February 2025 shows "
                "123."
            ),
        ),
        (
            (
                "Visual calculations work on the visual's grid and cannot activate relationships. "
                "Date roles belong in model measures."
            ),
            (
                "Writing USERELATIONSHIP inside the visual calculation for a shipped running "
                "total. It is not allowed in that scope."
            ),
            (
                "A model measure for shipped revenue gives January 2025 47 and February 2025 76; "
                "RUNNINGSUM over those cells gives 47 and 123."
            ),
        ),
        (
            (
                "With Year and Month on the axis, January 2024 at 64 and January and February 2025 "
                "at 67 and 56, a running sum can reset at each year or carry on."
            ),
            (
                "Assuming the flat result carries over. Resetting gives 64, then 67 and 123; "
                "continuing gives 64, 131 and 187."
            ),
            (
                "Specify the reset policy, then check both year subtotals (64 and 123) and the "
                "final 187 or 123."
            ),
        ),
        (
            (
                "A two-month moving average on visual rows averages displayed cells: (67 + 56) / 2 "
                "= 61.5 for February 2025."
            ),
            (
                "Hiding empty months makes the window jump. If only months with sales appear, "
                "January 2025's window pairs it with January 2024 and gives (64 + 67) / 2 = 65.5."
            ),
            (
                "Confirm that the visual shows every month in order. For averages reused across "
                "reports, build a model measure over the Date table."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

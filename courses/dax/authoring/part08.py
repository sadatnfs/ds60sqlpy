"""Stage eight: composition, calculation groups, UDFs and visual scope."""

from .common import BASE, lesson
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
                    "Line costs are 4,1,10,6,4,5,4,10, totaling 44.",
                    "Profit is 187 -44 =143.",
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
            "produces (Revenue +10)*0.9. Reversing the groups' "
            "precedence produces Revenue*0.9 +10. Write the expanded "
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
                    "The expansion is(187 +10)*0.9.",
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
                    "The expansion is(187*0.9)+10.",
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
                "The running values become 67,123,133 for that expanded snapshot.",
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

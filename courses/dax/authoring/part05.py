"""Stage five: table shape, lineage and relationship design."""

from .common import explain, lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        25,
        "VALUES, DISTINCT and the model's unknown member",
        ["VALUES", "DISTINCT", "blank member", "referential integrity", "reconciliation"],
        (
            "Reconcile unmatched facts without confusing the stored "
            "dimension with its semantic blank member."
        ),
        (
            "VALUES and DISTINCT can look identical on clean data, "
            "which makes a missing-key fixture essential. On a column, "
            "VALUES can include the blank member introduced by a "
            "regular relationship when fact keys do not match its "
            "dimension. DISTINCT over the stored dimension column does "
            "not add that relationship-generated member. The "
            "difference concerns the model, not merely duplicated text "
            "values.\n\nThe named unknown-member model adds S9 with "
            "product key 999 and net amount 7. Product still stores "
            "four keys, 1 through 4. The semantic blank member groups "
            "the unmatched fact rather than silently discarding it. It "
            "is not an actual product with key zero, and it is "
            "different from the valid unsold Bag product.\n\nA complete "
            "reconciliation should include known-product revenue 187 "
            "and unknown-product revenue 7, totaling 194. An inner "
            "join that drops S9 can make a seemingly tidy product "
            "report understate recorded activity. Conversely, counting "
            "the synthetic blank member as an ordinary catalog SKU can "
            "misstate the inventory of real products. State which "
            "population each metric represents."
        ),
        (
            "COUNTROWS exposes the size of the two returned value "
            "tables. The second query filters the semantic ProductKey "
            "to BLANK and separately returns the unfiltered fact "
            "amount. The source assumes the regular relationship and "
            "deliberately unmatched key declared in this model, not a "
            "limited relationship or a repaired source."
        ),
        [
            r(
                "Stored keys versus semantic members",
                (
                    'EVALUATE ROW ( "ValuesMembers", COUNTROWS ( VALUES ( '
                    'Product[ProductKey] ) ), "StoredDistinctKeys", COUNTROWS '
                    "( DISTINCT ( Product[ProductKey] ) ) )"
                ),
                [("ValuesMembers", "integer"), ("StoredDistinctKeys", "integer")],
                [[5, 4]],
                "Unknown-member model; stored Product keys 1..4; Sales also has key 999.",
                [
                    "DISTINCT sees the four stored Product keys.",
                    (
                        "The unmatched regular relationship introduces one "
                        "semantic blank member for VALUES."
                    ),
                    "VALUES therefore has five members, not a new stored row with key 999.",
                ],
                (
                    "The unknown member can represent multiple unmatched keys. "
                    "It does not tell you how many distinct bad source codes "
                    "exist; inspect fact-minus-dimension keys for that "
                    "diagnostic."
                ),
            ),
            r(
                "Reconcile the unknown amount",
                (
                    'EVALUATE ROW ( "UnknownRevenue", CALCULATE ( '
                    "[NetRevenue], ISBLANK ( Product[ProductKey] ) ), "
                    '"AllRevenue", [NetRevenue] )'
                ),
                [("UnknownRevenue", "number"), ("AllRevenue", "number")],
                [[7, 194]],
                (
                    "Unknown-member model; the first expression selects its "
                    "semantic blank Product member."
                ),
                [
                    "S9 is the only unmatched product fact and contributes 7.",
                    "Known-product facts still contribute 187.",
                    "The full fact total is 194, including the unknown bucket.",
                ],
                (
                    "An explicit unknown bucket preserves a useful "
                    "data-quality signal. Replacing it with an invented valid "
                    "product would conceal a modeling issue."
                ),
            ),
        ],
        [
            t(
                "Predict these two counts in the clean retail model.",
                "No unmatched Product key is present there.",
                (
                    "Both counts are four; that clean fixture alone cannot "
                    "reveal the function difference."
                ),
            ),
            t(
                "Add a second unmatched source key with another fact.",
                "Several unmatched codes can map to one semantic blank member.",
                (
                    "VALUES still adds one blank member, while the unknown "
                    "revenue grows by the new amount. A separate key-quality "
                    "query must count the distinct unmatched codes."
                ),
            ),
            t(
                "Write the reconciliation equation for product reporting.",
                "Keep the unknown bucket separate from known members.",
                "Known revenue 187 + unknown revenue 7 = all revenue 194.",
            ),
            t(
                "Diagnose labeling VALUES(ProductKey) count as the number of sellable SKUs.",
                "One member is generated by relationship semantics.",
                (
                    "The count five includes the unknown bucket. Stored "
                    "sellable-product policy needs its own catalog definition."
                ),
            ),
            t(
                "Explain why Bag is not the unknown member.",
                "Bag has a real dimension key but no facts.",
                (
                    "Key 4 is valid and unsold; the synthetic blank member "
                    "represents facts lacking a valid product mapping."
                ),
            ),
            t(
                "Transfer this reconciliation to late-arriving dimensions.",
                "The fact may arrive before its descriptive record.",
                (
                    "Retain and report the unmatched population, then verify "
                    "how reconciliation changes after the correct dimension "
                    "member arrives."
                ),
            ),
        ],
        model="unknown-member",
        sources=[
            "https://learn.microsoft.com/en-us/dax/values-function-dax",
            "https://learn.microsoft.com/en-us/dax/distinct-function-dax",
        ],
    ),
    lesson(
        26,
        "Virtual tables have row-retention and column contracts",
        ["ADDCOLUMNS", "SELECTCOLUMNS", "SUMMARIZECOLUMNS", "virtual table", "nonempty"],
        "Predict which rows survive a projection, an extension and a grouped summary.",
        (
            "A virtual table is an intermediate table value, not "
            "automatically a persisted model table. Its rows and "
            "columns matter independently of the scalar values "
            "calculated over it. SELECTCOLUMNS starts a projection "
            "with the named expressions; ADDCOLUMNS retains the input "
            "columns and extends each input row. Neither should be "
            "confused with an operation that groups and removes "
            "all-blank result rows.\n\nSUMMARIZECOLUMNS creates groups "
            "and evaluates expressions for them. In the ordinary form "
            "used here, a group whose supplied expressions are all "
            "BLANK is omitted. Therefore a product with no sales can "
            "remain in an ADDCOLUMNS result yet disappear from a "
            "summary of revenue. That is a table-shape difference, not "
            "proof that the source product was deleted.\n\nWhen "
            "debugging a larger expression, expose the intermediate "
            "table before aggregating it. Record its grain, candidate "
            "keys, row count, column names and whether blanks are "
            "preserved. A final scalar can conceal that the formula "
            "changed its candidate population several steps earlier."
        ),
        (
            "The first case projects the extended product-key table "
            "into explicit output names. [NetRevenue] transitions each "
            "candidate product row. The second groups directly by "
            "ProductKey with a revenue expression. Both use the clean "
            "model and explicit sorting; the only intended difference "
            "is all-blank group retention."
        ),
        [
            r(
                "Extend every candidate key",
                (
                    "EVALUATE SELECTCOLUMNS ( ADDCOLUMNS ( VALUES ( "
                    'Product[ProductKey] ), "RevenueForKey", [NetRevenue] ), '
                    '"ProductKey", Product[ProductKey], "Revenue", '
                    "[RevenueForKey] )\nORDER BY [ProductKey]"
                ),
                [("ProductKey", "integer"), ("Revenue", "number")],
                [[1, 67], [2, 24], [3, 96], [4, None]],
                ("All four clean-model Product keys; retain every input row while adding revenue."),
                [
                    "VALUES supplies keys 1, 2, 3, 4.",
                    "ADDCOLUMNS computes one revenue result per input key.",
                    "Bag's blank measure does not remove key 4 from this projected table.",
                ],
                (
                    "An extension column is addressed by its name in the "
                    "virtual table expression. It is not automatically "
                    "installed as a persistent Product column."
                ),
            ),
            r(
                "A grouped summary omits an all-blank group",
                (
                    "EVALUATE SUMMARIZECOLUMNS ( Product[ProductKey], "
                    '"Revenue", [NetRevenue] )\nORDER BY Product[ProductKey]'
                ),
                [("ProductKey", "integer"), ("Revenue", "number")],
                [[1, 67], [2, 24], [3, 96]],
                "Same clean model; grouped summary with one measure expression.",
                [
                    "The four candidate keys form groups.",
                    "Key 4 has BLANK for every supplied expression.",
                    "That all-blank group is omitted; keys 1, 2, 3 remain.",
                ],
                (
                    "Adding a nonblank expression or deliberately coalescing "
                    "revenue can alter which groups appear. Do not assume that "
                    "all table-producing functions have the same row-retention "
                    "policy."
                ),
            ),
        ],
        [
            t(
                "Predict the summary if Revenue uses COALESCE([NetRevenue],0).",
                "The fourth expression becomes nonblank.",
                "Key 4 appears with zero, creating four result rows.",
            ),
            t(
                "Project only product names from the first result.",
                "A projection can change columns without grouping rows.",
                (
                    "The row count remains four if the input table is "
                    "unchanged; naming only a column does not imply DISTINCT."
                ),
            ),
            t(
                "Write an intermediate-table ledger for a revenue-threshold calculation.",
                "Separate candidates, extended values and retained rows.",
                (
                    "Record keys 1..4, revenues 67/24/96/BLANK, then the "
                    "qualifying key set for the threshold before applying it "
                    "as a filter."
                ),
            ),
            t(
                (
                    "Diagnose treating a virtual RevenueForKey column as a "
                    "persisted model attribute."
                ),
                "Its scope is the current expression.",
                (
                    "It does not become a reusable Product column outside the "
                    "table expression; define an appropriate model object or "
                    "reconstruct it."
                ),
            ),
            t(
                "Explain why adding a constant 1 to a summary can change row presence.",
                "At least one expression would be nonblank even for Bag.",
                "The all-blank suppression condition no longer holds for that group.",
            ),
            t(
                "Transfer the distinction to a customer coverage report.",
                "A complete eligibility list may need rows with no outcome.",
                (
                    "Start from the intended customer population and preserve "
                    "absent outcomes explicitly rather than allowing a "
                    "nonempty rule to redefine the denominator."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/addcolumns-function-dax",
            "https://learn.microsoft.com/en-us/dax/selectcolumns-function-dax",
            "https://learn.microsoft.com/en-us/dax/summarizecolumns-function-dax",
        ],
    ),
    lesson(
        27,
        "Lineage and TREATAS: equal values can filter differently",
        ["data lineage", "direct projection", "computed column", "TREATAS", "virtual relationship"],
        (
            "Explain why a virtual column's model identity matters in "
            "addition to its visible values."
        ),
        (
            "Data lineage associates a virtual column with a model "
            "column. A direct projection of Product[ProductKey] can "
            "preserve that association, so the resulting key table can "
            "filter Product when used in CALCULATE. A computed "
            "expression over those keys can contain the same visible "
            "numbers while losing that direct model-column "
            "lineage.\n\nThis distinction prevents a misleading "
            "values-only review. Two tables displaying 1 and 2 are not "
            "guaranteed to have the same filtering effect. One may "
            "represent Product keys; the other may be an unrelated "
            "calculated value table. Column names alone do not repair "
            "the association.\n\nTREATAS explicitly assigns a table's "
            "values to selected target model columns. It is useful for "
            "disconnected selections and carefully designed virtual "
            "relationships. Match the number and order of columns, "
            "data types and target meaning. Values absent from the "
            "target domain are ignored, so missing mappings still "
            "deserve a data-quality check rather than an assumption "
            "that every input value matched."
        ),
        (
            "The first table projects ProductKey directly from Paper "
            "products. The second adds zero to each key, creating an "
            "expression-derived column with the same numbers but no "
            "retained direct lineage. TREATAS then states that those "
            "values should filter Product[ProductKey]. The result is a "
            "semantic comparison, not a runtime or performance receipt."
        ),
        [
            r(
                "A direct key projection retains its model identity",
                (
                    "EVALUATE\nVAR PaperKeys = SELECTCOLUMNS ( FILTER ( "
                    'Product, Product[Category] = "Paper" ), "Key", '
                    'Product[ProductKey] )\nRETURN ROW ( "CandidateRows", '
                    'COUNTROWS ( PaperKeys ), "Revenue", CALCULATE ( '
                    "[NetRevenue], PaperKeys ) )"
                ),
                [("CandidateRows", "integer"), ("Revenue", "number")],
                [[2, 91]],
                "No outer filters; direct projection of the two Paper ProductKey values.",
                [
                    "The projected values are 1 and 2.",
                    "The direct model-column projection retains ProductKey lineage.",
                    "Using that table as a filter selects Paper sales and revenue 91.",
                ],
                (
                    "The result depends on the association with ProductKey, "
                    "not on the output alias Key."
                ),
            ),
            r(
                "Restore an explicitly detached mapping",
                (
                    "EVALUATE\nVAR DetachedKeys = SELECTCOLUMNS ( FILTER ( "
                    'Product, Product[Category] = "Paper" ), "Key", '
                    'Product[ProductKey] + 0 )\nRETURN ROW ( "WithoutTarget", '
                    'CALCULATE ( [NetRevenue], DetachedKeys ), "WithTarget", '
                    "CALCULATE ( [NetRevenue], TREATAS ( DetachedKeys, "
                    "Product[ProductKey] ) ) )"
                ),
                [("WithoutTarget", "number"), ("WithTarget", "number")],
                [[187, 91]],
                (
                    "Expression-derived values {1,2}; compare a lineage-free "
                    "table filter with an explicit target mapping."
                ),
                [
                    (
                        "Adding zero preserves the numbers but changes the "
                        "projected expression's lineage contract."
                    ),
                    (
                        "Without a model target, that detached column does not "
                        "select the Product rows for revenue."
                    ),
                    "TREATAS maps the values to ProductKey, restoring the intended 91.",
                ],
                (
                    "This is why copying a virtual table's printed rows does "
                    "not fully document a DAX expression. Record its "
                    "originating columns or explicit target mapping."
                ),
            ),
        ],
        [
            t(
                "Predict TREATAS({1,999},Product[ProductKey]) in the clean model.",
                "Only values present in the target domain become effective filters.",
                (
                    "Key 1 selects Notebook revenue 67; unmatched key 999 is "
                    "ignored. This differs from the separate unknown-member "
                    "model."
                ),
            ),
            t(
                "Rename the direct projected column without changing its expression.",
                "The model-column origin is distinct from its display name.",
                (
                    "A direct reference can retain lineage despite renaming; "
                    "renaming alone is not the same as calculating a new "
                    "expression."
                ),
            ),
            t(
                "Write a disconnected selection mapping for product keys 1 and 3.",
                "TREATAS states the intended target explicitly.",
                (
                    "CALCULATE([NetRevenue],TREATAS({1,3},Product[ProductKey]))"
                    " selects Notebook and Mug, totaling 163."
                ),
            ),
            t(
                ("Diagnose mapping a customer-code table to ProductKey because both are integers."),
                "Type compatibility does not establish semantic identity.",
                (
                    "A numeric match would filter the wrong domain. The target "
                    "column must represent the same entity or an explicitly "
                    "defined mapping."
                ),
            ),
            t(
                "Explain a two-column TREATAS mapping.",
                "Column count and position matter.",
                (
                    "Each input column maps to the corresponding target "
                    "column; swapping year and month changes meaning or causes "
                    "invalid matches."
                ),
            ),
            t(
                "Transfer lineage reasoning to an imported segment list.",
                (
                    "A list of identifiers is initially disconnected unless "
                    "the model says otherwise."
                ),
                (
                    "Validate its key domain and duplicates, then define a "
                    "physical relationship or an explicit virtual mapping, "
                    "retaining unmatched-key diagnostics."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/treatas-function-dax",
            "https://learn.microsoft.com/en-us/dax/selectcolumns-function-dax",
            "https://learn.microsoft.com/en-us/dax/union-function-dax",
        ],
    ),
    lesson(
        28,
        "Set operations, duplicates and argument order",
        ["UNION", "INTERSECT", "EXCEPT", "duplicates", "set membership"],
        (
            "Distinguish membership operations from bag concatenation "
            "and preserve a deliberate key population."
        ),
        (
            "Virtual-table operations are not interchangeable with the "
            "similarly named operations in every SQL dialect. DAX "
            "UNION combines rows and retains duplicates. INTERSECT and "
            "EXCEPT have their own duplicate and lineage rules, "
            "including dependence on argument order. On small distinct "
            "key sets, membership is easy to reason about; on "
            "duplicated rows, count semantics need explicit "
            "attention.\n\nPaper products have keys 1 and 2; Blue "
            "products have keys 1 and 3. Their intersection is key 1, "
            "Paper minus Blue is key 2, and their concatenation "
            "contains 1, 2, 1, 3. Taking DISTINCT after UNION gives the "
            "three unique keys 1, 2, 3. That extra DISTINCT is a "
            "semantic operation, not merely presentation "
            "cleanup.\n\nBefore using a table result to filter another "
            "expression, state its grain and originating columns. Set "
            "membership can be appropriate for qualifying identities, "
            "while duplicate-bearing rows can represent repeated "
            "events. Removing duplicates from an event table may erase "
            "legitimate activity; retaining them in a list of eligible "
            "entities can inflate later iteration."
        ),
        (
            "The two variables use CALCULATETABLE and VALUES to "
            "construct distinct model-key tables under named filters. "
            "The first query counts membership results. The second "
            "contrasts the row count of UNION with its distinct form. "
            "All source columns are the same ProductKey domain in this "
            "example."
        ),
        [
            r(
                "Intersection and one-sided difference",
                (
                    "EVALUATE\nVAR PaperKeys = CALCULATETABLE ( VALUES ( "
                    'Product[ProductKey] ), Product[Category] = "Paper" )\nVAR '
                    "BlueKeys = CALCULATETABLE ( VALUES ( Product[ProductKey] "
                    '), Product[Color] = "Blue" )\nRETURN ROW ( '
                    '"IntersectionRows", COUNTROWS ( INTERSECT ( PaperKeys, '
                    'BlueKeys ) ), "PaperOnlyRows", COUNTROWS ( EXCEPT ( '
                    "PaperKeys, BlueKeys ) ) )"
                ),
                [("IntersectionRows", "integer"), ("PaperOnlyRows", "integer")],
                [[1, 1]],
                "Distinct Paper keys {1,2} and Blue keys {1,3} from the clean model.",
                [
                    "The shared key is 1, so the intersection has one row.",
                    "Key 2 belongs to Paper but not Blue.",
                    "Reversing the difference would return key 3 instead, a different population.",
                ],
                (
                    "A count of one in both differences does not mean the "
                    "selected entities are identical. Retain the actual key "
                    "sets in a review trace."
                ),
            ),
            r(
                "UNION keeps repeated membership rows",
                (
                    "EVALUATE\nVAR PaperKeys = CALCULATETABLE ( VALUES ( "
                    'Product[ProductKey] ), Product[Category] = "Paper" )\nVAR '
                    "BlueKeys = CALCULATETABLE ( VALUES ( Product[ProductKey] "
                    '), Product[Color] = "Blue" )\nVAR Combined = UNION ( '
                    'PaperKeys, BlueKeys )\nRETURN ROW ( "CombinedRows", '
                    'COUNTROWS ( Combined ), "DistinctKeys", COUNTROWS ( '
                    "DISTINCT ( Combined ) ) )"
                ),
                [("CombinedRows", "integer"), ("DistinctKeys", "integer")],
                [[4, 3]],
                "Concatenate the two two-row key tables; key 1 occurs in each input.",
                [
                    "UNION produces four rows, including key 1 twice.",
                    "DISTINCT removes repeated key rows, leaving 1, 2, 3.",
                    "The two counts represent memberships versus unique product identities.",
                ],
                (
                    "If the downstream calculation iterates the concatenation, "
                    "key 1 can contribute twice. A filter set and an "
                    "iterator's row population should not be conflated."
                ),
            ),
        ],
        [
            t(
                "List EXCEPT(BlueKeys,PaperKeys), not just its count.",
                "The first argument defines the population from which rows are removed.",
                "It contains key 3, Mug.",
            ),
            t(
                "Add a repeated key 1 to an input before UNION.",
                "UNION does not deduplicate.",
                (
                    "The combined row count increases, while DISTINCT over the "
                    "combined keys remains three."
                ),
            ),
            t(
                "Write an eligible-product union that should contain each key once.",
                "State that uniqueness is part of the entity-list contract.",
                "Use DISTINCT(UNION(PaperKeys,BlueKeys)) for this one-column key example.",
            ),
            t(
                "Diagnose deleting duplicates from Sales to imitate a unique product list.",
                "Fact lines and product identities have different grains.",
                (
                    "Repeated ProductKey values in Sales can be valid "
                    "transactions; deduplicating them would lose revenue."
                ),
            ),
            t(
                "Explain why matching column counts is insufficient for a safe union.",
                "Columns match by position and need compatible meaning.",
                (
                    "Combining product codes with customer codes can be "
                    "semantically wrong even if both are integers in one "
                    "column."
                ),
            ),
            t(
                "Transfer the distinction to campaign audiences.",
                "A person can belong to several audiences.",
                (
                    "Unique reach uses a deduplicated person set, while "
                    "audience memberships can count the same person several "
                    "times; label them separately."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/union-function-dax",
            "https://learn.microsoft.com/en-us/dax/intersect-function-dax",
            "https://learn.microsoft.com/en-us/dax/except-function-dax",
        ],
    ),
    lesson(
        29,
        "Active and inactive date roles with USERELATIONSHIP",
        ["active relationship", "inactive relationship", "USERELATIONSHIP", "role-playing date"],
        "Reconcile order-date and ship-date totals without changing the fact amounts.",
        (
            "A fact can have several date roles. Our Sales rows have "
            "OrderDate and ShipDate, but the shared Date dimension's "
            "ordinary active relationship uses OrderDate. A month "
            "selection therefore means order month unless a measure "
            "deliberately activates the shipment relationship. A "
            "report title does not change that model "
            "behavior.\n\nUSERELATIONSHIP selects an existing "
            "relationship for the calculation. It does not create a "
            "relationship between arbitrary expressions, and it does "
            "not mutate the model's permanent active setting. For this "
            "pair of date roles, activating the shipment relationship "
            "displaces the ordinary order-date path for that "
            "calculation.\n\nS6 is ordered on January 5 and shipped on "
            "February 1. It contributes 20 to January order revenue "
            "but February shipment revenue. The total amount remains "
            "unchanged; attribution across periods changes. This is "
            "the exact kind of case that should appear in a date-role "
            "regression matrix rather than relying only on orders "
            "shipped within the same month."
        ),
        (
            "The reference supplies the two existing relationship "
            "endpoint columns to USERELATIONSHIP. The outer Year and "
            "MonthNumber filters come from Date, then travel along the "
            "selected relationship. Both roles use the same NetRevenue "
            "expression and USD amounts."
        ),
        [
            r(
                "January order versus shipment attribution",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "OrderRevenue", '
                    '[NetRevenue], "ShipRevenue", CALCULATE ( [NetRevenue], '
                    "USERELATIONSHIP ( Sales[ShipDate], 'Date'[Date] ) ) ), "
                    "'Date'[Year] = 2025, 'Date'[MonthNumber] = 1 )"
                ),
                [("OrderRevenue", "number"), ("ShipRevenue", "number")],
                [[67, 47]],
                (
                    "Date year 2025/month 1; compare active OrderDate with the "
                    "explicitly selected ShipDate relationship."
                ),
                [
                    "Orders S4, S5, S6 belong to January and total 67.",
                    "Shipments S4 and S5 occur in January and total 47.",
                    ("S6's 20 moves to shipment month February."),
                ],
                (
                    "The 20 difference is explained by a timing boundary, not "
                    "a lost transaction or a changed revenue formula."
                ),
            ),
            r(
                "February absorbs the delayed shipment",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "OrderRevenue", '
                    '[NetRevenue], "ShipRevenue", CALCULATE ( [NetRevenue], '
                    "USERELATIONSHIP ( Sales[ShipDate], 'Date'[Date] ) ) ), "
                    "'Date'[Year] = 2025, 'Date'[MonthNumber] = 2 )"
                ),
                [("OrderRevenue", "number"), ("ShipRevenue", "number")],
                [[56, 76]],
                "Date year 2025/month 2 with the same role comparison.",
                [
                    "Orders S7, S8 total 56 in February.",
                    "Shipments include S6, S7, S8, totaling 76.",
                    "Across January and February, both date-role totals reconcile to 123.",
                ],
                (
                    "Monthly attribution changes while the combined-period "
                    "amount reconciles. A wider window is useful for checking "
                    "that a role change has not duplicated facts."
                ),
            ),
        ],
        [
            t(
                "Predict all-2025 totals for both roles.",
                "All five 2025 orders also ship within 2025 in this fixture.",
                (
                    "Both totals are 123; an annual-only test would hide the "
                    "monthly role difference."
                ),
            ),
            t(
                "Move S6's shipment back into January conceptually.",
                "Only shipment attribution changes.",
                (
                    "January ShipRevenue would rise from 47 to 67 and February "
                    "ShipRevenue fall from 76 to 56."
                ),
            ),
            t(
                "Write a clearly named shipment-revenue measure.",
                "Keep role selection inside the measure definition.",
                (
                    "ShipRevenue = CALCULATE([NetRevenue],USERELATIONSHIP(Sales"
                    "[ShipDate],'Date'[Date]))."
                ),
            ),
            t(
                "Diagnose using a nonexistent computed date expression in USERELATIONSHIP.",
                "The function activates an existing relationship by its endpoints.",
                (
                    "Model the required relationship or a separate date role "
                    "first; the function does not create an arbitrary join."
                ),
            ),
            t(
                "Explain why active/inactive status is not a security bypass.",
                "Security and relationship capabilities have separate constraints.",
                (
                    "Real RLS behavior and model compatibility require "
                    "explicit external validation; a hand-derived period "
                    "comparison does not prove security propagation."
                ),
            ),
            t(
                (
                    "Choose between one shared Date table and separate "
                    "OrderDate/ShipDate dimensions."
                ),
                "Ask whether independent simultaneous selections are required.",
                (
                    "Separate role-playing dimensions can make independent "
                    "slicers clearer; a shared dimension with explicit role "
                    "measures can suit comparable-period analysis."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/userelationship-function-dax",
            ("https://learn.microsoft.com/en-us/power-bi/guidance/relationships-active-inactive"),
        ],
    ),
    lesson(
        30,
        "Bridge tables and overlapping audiences",
        ["bridge table", "many-to-many", "TREATAS", "filter direction", "overlap"],
        (
            "Model overlapping customer groups and reconcile unique "
            "reach without enabling ambiguous filter paths."
        ),
        (
            "A customer can belong to several audiences, so storing "
            "one audience label on Customer would lose information. "
            "A membership bridge has one row per group/customer "
            "pair. Audience and Customer each have one-to-many "
            "relationships into that bridge in the supplied "
            "analytical model. With those single-direction paths, "
            "an Audience filter reaches membership rows but does "
            "not automatically flow backward into Customer and "
            "onward to Sales.\n\nAn explicit virtual mapping can "
            "carry the selected membership keys to Customer for one "
            "measure. This keeps the measure's intention visible "
            "without globally changing relationship direction. It "
            "is not automatically preferable in every real model; a "
            "deliberate physical many-to-many design can be "
            "appropriate after considering ambiguity, security and "
            "performance.\n\nNewsletter contains Ada and Bo; "
            "Prospects contains Bo and Cy. Bo's 80 belongs to both "
            "audience reports. Adding the two audience revenues "
            "yields 267, larger than the unique-customer total 187. "
            "A combined audience should first form a unique "
            "customer set, then aggregate its facts. The model "
            "should distinguish audience memberships from distinct "
            "customer reach."
        ),
        (
            "Audience filters GroupMembership through GroupKey. VALUES "
            "extracts the selected bridge's CustomerKey values. "
            "TREATAS explicitly targets Customer[CustomerKey], whose "
            "ordinary relationship then filters Sales. The raw measure "
            "is included to show that the model's single-direction "
            "bridge alone does not perform that backward propagation."
        ),
        [
            r(
                "Newsletter's two customers",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "RawRevenue", '
                    '[NetRevenue], "AudienceRevenue", CALCULATE ( '
                    "[NetRevenue], TREATAS ( VALUES ( "
                    "GroupMembership[CustomerKey] ), Customer[CustomerKey] ) ) "
                    '), Audience[Audience] = "Newsletter" )'
                ),
                [("RawRevenue", "number"), ("AudienceRevenue", "number")],
                [[187, 131]],
                (
                    "Analytics model; Audience=Newsletter; single-direction "
                    "relationships into GroupMembership."
                ),
                [
                    "Newsletter leaves membership keys 10 and 20.",
                    (
                        "Without explicit mapping the bridge does not filter "
                        "Customer, so RawRevenue stays 187."
                    ),
                    "TREATAS selects Ada 51 and Bo 80, totaling 131.",
                ],
                (
                    "The explicit result follows a documented mapping. "
                    "Enabling broad bidirectional filtering would affect other "
                    "queries as well, so it is a model decision rather than a "
                    "cosmetic fix."
                ),
            ),
            r(
                "Prospects overlaps the first audience",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "RawRevenue", '
                    '[NetRevenue], "AudienceRevenue", CALCULATE ( '
                    "[NetRevenue], TREATAS ( VALUES ( "
                    "GroupMembership[CustomerKey] ), Customer[CustomerKey] ) ) "
                    '), Audience[Audience] = "Prospects" )'
                ),
                [("RawRevenue", "number"), ("AudienceRevenue", "number")],
                [[187, 136]],
                "Analytics model; Audience=Prospects; selected membership keys 20 and 30.",
                [
                    "Prospects selects Bo and Cy through the explicit mapping.",
                    "Their revenues are 80 and 56, totaling 136.",
                    (
                        "Bo is shared with Newsletter, so summing the two audience "
                        "totals would count 80 twice."
                    ),
                ],
                (
                    "Overlap is legitimate membership information. The error "
                    "is treating overlapping audience results as disjoint "
                    "partitions."
                ),
            ),
        ],
        [
            t(
                "Predict the revenue for both audiences selected together.",
                "VALUES over the bridge deduplicates customer keys.",
                "The keys are 10, 20, 30, and the unique population totals 187 rather than 267.",
            ),
            t(
                "Add Di to Newsletter without adding a sale.",
                "The membership count and sales amount can respond differently.",
                (
                    "The selected customer population increases, but "
                    "Newsletter revenue remains 131 because Di has no sales."
                ),
            ),
            t(
                "Write a reconciliation for the two audience totals.",
                "Subtract the overlapping population once.",
                "131 + 136 - 80 = 187 for the union of these two audiences.",
            ),
            t(
                "Diagnose a membership table with duplicate group/customer pairs.",
                "Its declared grain is one pair, not one loading event.",
                (
                    "Reject or repair duplicate membership rows. VALUES may "
                    "hide them for this measure, but other counts or iterators "
                    "could still overcount."
                ),
            ),
            t(
                "Explain why this mapping is not proof of row-level security.",
                "A query-level filter can be edited or removed.",
                (
                    "A real security rule must be enforced by the engine under "
                    "tested identities and relationship behavior; this is an "
                    "analytical selection only."
                ),
            ),
            t(
                "Transfer the design to patients enrolled in multiple programs.",
                "Programs overlap and patient identity remains distinct.",
                (
                    "Model membership at program/patient grain, report overlap "
                    "explicitly and choose unique-patient versus "
                    "membership-weighted denominators deliberately."
                ),
            ),
        ],
        model="analytics",
        sources=[
            ("https://learn.microsoft.com/en-us/power-bi/guidance/relationships-many-to-many"),
            "https://learn.microsoft.com/en-us/dax/treatas-function-dax",
        ],
    ),
]


REASONING = {
    25: [
        (
            (
                "In the clean retail model every Sales ProductKey (1, 2 or 3) matches a stored "
                "Product row, so the engine adds no blank member. VALUES and DISTINCT both return "
                "the four stored keys."
            ),
            (
                "Using the clean fixture as the only test and concluding that VALUES and DISTINCT "
                "are interchangeable. The unknown-member model, with S9 on key 999, returns 5 and "
                "4."
            ),
            "Run case A on both models: retail gives 4 and 4, unknown-member gives 5 and 4.",
        ),
        (
            (
                "Every unmatched code joins the same blank member. A hypothetical S10 on key 998 "
                "with Net 5 leaves VALUES at 5, raises UnknownRevenue from 7 to 12 and AllRevenue "
                "to 199."
            ),
            (
                "Expecting COUNTROWS(VALUES(Product[ProductKey])) to reach 6, one per bad code, "
                "mistakes the semantic bucket for a list of codes, so a key-quality count built "
                "that way stays at one."
            ),
            (
                "`COUNTROWS ( EXCEPT ( DISTINCT ( Sales[ProductKey] ), DISTINCT ( "
                "Product[ProductKey] ) ) )` returns 2 for {998, 999}, while VALUES still counts 5."
            ),
        ),
        (
            (
                "Known revenue is everything mapped to a stored key: Notebook 67 + Pen 24 + Mug 96 "
                "= 187. Adding the blank bucket's 7 gives AllRevenue 194."
            ),
            (
                "A product visual that hides the blank row lists rows that sum to 187 under a "
                "grand total of 194, and a reader who adds the rows reports a 7 USD gap as a "
                "calculation bug."
            ),
            (
                "Case B returns UnknownRevenue 7 and AllRevenue 194, and `CALCULATE ( "
                "[NetRevenue], NOT ISBLANK ( Product[ProductKey] ) )` returns 187."
            ),
        ),
        (
            (
                "The sellable catalog is the stored Product table, four rows, or the three that "
                "sold if the policy requires sales. The fifth VALUES member exists only because "
                "S9's key 999 has no match."
            ),
            (
                "Publishing 5 as the SKU count adds a product nobody can buy, and the count shifts "
                "as soon as the bad key is repaired, although no catalog change occurred."
            ),
            (
                "Under the unknown-member model, COUNTROWS(Product) is 4, DISTINCT is 4 and VALUES "
                "is 5; only the first two belong in a catalog measure."
            ),
        ),
        (
            (
                "Bag (key 4) is a real Product row with no Sales lines, so its revenue is BLANK. "
                "The blank member holds S9's 7 USD, which has no valid product."
            ),
            (
                "Treating Bag as the unknown bucket because both look empty in a report confuses "
                "no facts with no dimension row, and sends the data-quality fix to the wrong "
                "table."
            ),
            (
                "`CALCULATE ( [NetRevenue], Product[ProductKey] = 4 )` is BLANK, and `CALCULATE ( "
                "[NetRevenue], ISBLANK ( Product[ProductKey] ) )` is 7."
            ),
        ),
        (
            (
                "A late product row is the same pattern over time. Until key 999 arrives, S9's 7 "
                "sits in the blank bucket; afterward it moves to the new product, and the total "
                "stays 194."
            ),
            (
                "Filtering out unmatched facts until the dimension catches up reports 187 today "
                "and 194 later, so the same period's total changes for no business reason."
            ),
            (
                "Before the fix: unknown 7, total 194. After a Product row for 999 is loaded: "
                "unknown BLANK, product 999 at 7, total still 194."
            ),
        ),
    ],
    26: [
        (
            (
                "SUMMARIZECOLUMNS drops a group only when every expression is blank. COALESCE "
                "makes Bag's value 0, a nonblank result, so key 4 returns with 0 and the table has "
                "four rows."
            ),
            (
                "Treating COALESCE as a display tweak hides that it changes row presence. An "
                "AVERAGEX over the new rows drops from 187 / 3, about 62.33, to 187 / 4 = 46.75."
            ),
            "The summary returns keys 1 to 4 with revenues 67, 24, 96 and 0.",
        ),
        (
            (
                "SELECTCOLUMNS projects every input row and never groups. With the four-row first "
                "result, projecting product names gives Notebook, Pen, Mug and Bag."
            ),
            (
                "Assuming a projection deduplicates is the trap. Projecting Category instead "
                "returns Paper, Paper, Home and Travel, four rows, not three."
            ),
            "COUNTROWS of the projection is 4, and DISTINCT over the Category projection is 3.",
        ),
        (
            (
                "Record each stage. Candidates are keys 1 to 4; extended revenues are 67, 24, 96 "
                "and BLANK; a rule of revenue above 50 keeps keys 1 and 3; applying them as a "
                "filter gives 163."
            ),
            (
                "Testing the threshold on Sales lines with `FILTER ( Sales, Sales[NetAmount] > 50 "
                ")` keeps nothing, since the largest line is S3 at 40, so the result is BLANK "
                "instead of 163."
            ),
            (
                "`CALCULATE ( [NetRevenue], FILTER ( VALUES ( Product[ProductKey] ), [NetRevenue] "
                "> 50 ) )` returns 163."
            ),
        ),
        (
            (
                "RevenueForKey is a column of the ADDCOLUMNS result and exists only inside that "
                "query. The outer SELECTCOLUMNS can read it because it is iterating that table."
            ),
            (
                "Writing a later measure that refers to Product[RevenueForKey] fails, because the "
                "Product table has no such column, and copying the virtual name into a visual does "
                "nothing."
            ),
            (
                "Case A returns 67, 24, 96 and BLANK. For reuse, define a model measure such as "
                "[NetRevenue] and evaluate it per product."
            ),
        ),
        (
            (
                'A constant column is never blank. Adding "One", 1 to the SUMMARIZECOLUMNS call '
                "means Bag's group has one nonblank expression, so its row returns with Revenue "
                "BLANK."
            ),
            (
                "Adding a helper constant for convenience and expecting three rows. The table now "
                "lists Bag, and any COUNTROWS of the result reads 4."
            ),
            (
                '`SUMMARIZECOLUMNS ( Product[ProductKey], "Revenue", [NetRevenue], "One", 1 )` '
                "returns four rows, one of them key 4 with a BLANK revenue."
            ),
        ),
        (
            (
                "Coverage needs every eligible customer as the denominator. Starting from all four "
                "customers, three have sales (Ada 51, Bo 80, Cy 56), so coverage is 3 / 4 = 0.75."
            ),
            (
                'Counting the rows of `SUMMARIZECOLUMNS ( Customer[Customer], "Revenue", '
                "[NetRevenue] )` drops Di and reports 3 / 3 = 1.0, full coverage that does not "
                "exist."
            ),
            (
                "ADDCOLUMNS over VALUES(Customer[Customer]) returns four rows with Di BLANK, and "
                "the coverage measure returns 0.75."
            ),
        ),
    ],
    27: [
        (
            (
                "TREATAS applies only values that exist in the target column. Product has no key "
                "999 in the clean model, so the filter keeps key 1 and returns Notebook's 67."
            ),
            (
                "Reading 67 as proof that code 999 has no sales. TREATAS drops unmatched values "
                "silently, so a code with real facts and no Product row would vanish from this "
                "result too."
            ),
            (
                "`CALCULATE ( [NetRevenue], TREATAS ( { 1, 999 }, Product[ProductKey] ) )` equals "
                "`CALCULATE ( [NetRevenue], Product[ProductKey] = 1 )`, 67."
            ),
        ),
        (
            (
                "Lineage follows the expression, not the name. A direct reference to "
                "Product[ProductKey] renamed PaperKey still filters Product, so case A still "
                "returns 2 rows and 91."
            ),
            (
                "Expecting the rename to behave like the `+ 0` projection and return 187. Only the "
                "arithmetic in case B creates new values without model lineage."
            ),
            "Rerun case A with the column renamed; CandidateRows stays 2 and Revenue stays 91.",
        ),
        (
            (
                "A table constructor has no lineage, so TREATAS must name Product[ProductKey] as "
                "the target. Keys 1 and 3 are Notebook and Mug, 67 + 96 = 163."
            ),
            (
                "Passing `{ 1, 3 }` straight to CALCULATE filters a column that is not in the "
                "model, as in case B's WithoutTarget, so the result is 187."
            ),
            (
                "The TREATAS measure returns 163, which matches the Blue revenue because Notebook "
                "and Mug are the Blue products."
            ),
        ),
        (
            (
                "The target must be the same entity. Customer codes 10 and 20 belong on "
                "Customer[CustomerKey], where they select Ada and Bo for 51 + 80 = 131."
            ),
            (
                "Mapping them to Product[ProductKey] because both are integers finds no matching "
                "product and returns BLANK, which reads as no sales rather than a wrong domain. "
                "With overlapping numbers it would filter the wrong products."
            ),
            (
                "TREATAS({10, 20}, Customer[CustomerKey]) gives 131 and TREATAS({10, 20}, "
                "Product[ProductKey]) gives BLANK."
            ),
        ),
        (
            (
                "Columns map by position. `TREATAS ( { ( 2025, 1 ) }, 'Date'[Year], "
                "'Date'[MonthNumber] )` filters January 2025, which is S4, S5 and S6, or 67."
            ),
            (
                "Writing the tuple as (1, 2025) asks for year 1 and month 2025. Nothing matches, "
                "and the result is BLANK with no error."
            ),
            "(2025, 1) returns 67, (2025, 2) returns 56 and the swapped tuple returns BLANK.",
        ),
        (
            (
                "An imported list of keys has no relationship. Check its domain and duplicates, "
                "then map it with TREATAS. A list {20, 30, 50} selects Bo and Cy for 136 and "
                "leaves 50 unmatched."
            ),
            (
                "Using the list directly as a CALCULATE filter has no lineage and returns 187, as "
                "DetachedKeys does in case B, so the segment silently becomes everyone."
            ),
            (
                "The TREATAS measure returns 136, and `EXCEPT ( SegmentList, VALUES ( "
                "Customer[CustomerKey] ) )` returns the orphan 50 for the diagnostics column."
            ),
        ),
    ],
    28: [
        (
            (
                "EXCEPT keeps rows of its first argument that are absent from the second. Blue "
                "keys are {1, 3}, Paper keys {1, 2}, so EXCEPT(BlueKeys, PaperKeys) is {3}, Mug."
            ),
            (
                "Treating EXCEPT as symmetric and reusing case A's PaperOnlyRows, {2} Pen. Pen is "
                "the answer to the opposite question."
            ),
            (
                '`CONCATENATEX ( EXCEPT ( BlueKeys, PaperKeys ), Product[ProductKey], "," )` '
                'returns "3", and using it as a filter returns Mug\'s 96.'
            ),
        ),
        (
            (
                "UNION concatenates every row. With an extra key 1 the inputs contribute 3 + 2 = 5 "
                "rows, while DISTINCT still finds keys 1, 2 and 3."
            ),
            (
                "Expecting UNION to behave like SQL UNION and remove repeats, so CombinedRows "
                "stays 4 or drops to 3."
            ),
            "CombinedRows reads 5 and DistinctKeys reads 3.",
        ),
        (
            (
                "The eligible list is an entity list, so uniqueness is part of its contract. "
                "DISTINCT(UNION(PaperKeys, BlueKeys)) returns Notebook, Pen and Mug once each."
            ),
            (
                "Iterating the raw union with SUMX adds Notebook twice, 67 + 67 + 24 + 96 = 254, "
                "which exceeds total revenue 187."
            ),
            "The distinct list has 3 rows, and SUMX over it of [NetRevenue] returns 187.",
        ),
        (
            (
                "Sales is at line grain, and repeated ProductKey values are separate sales. "
                "Notebook alone has S1, S4 and S7. A unique product list comes from "
                "VALUES(Product[ProductKey]) or DISTINCT(Sales[ProductKey])."
            ),
            (
                "Keeping only one line per key in Sales, say S1, S2 and S3, leaves 64 USD of the "
                "187 and discards five real transactions."
            ),
            (
                "DISTINCT(Sales[ProductKey]) returns 3 rows, while COUNTROWS(Sales) stays 8 and "
                "revenue stays 187."
            ),
        ),
        (
            (
                "UNION pairs columns by position, and both inputs must mean the same entity. Two "
                "Product key lists are compatible; Product keys and Customer keys are not."
            ),
            (
                "Unioning PaperKeys {1, 2} with customer keys {10, 20} gives four integer rows. "
                "Mapped onto Product[ProductKey], only two of them filter anything, so the list "
                "claims 4 eligible items while revenue covers 2."
            ),
            (
                "COUNTROWS of the mixed union is 4, but `CALCULATE ( COUNTROWS ( Product ), "
                "TREATAS ( MixedKeys, Product[ProductKey] ) )` is 2."
            ),
        ),
        (
            (
                "Reach counts each person once, and memberships count each pair. In the analytics "
                "model Newsletter has Ada and Bo and Prospects has Bo and Cy, so reach is 3 and "
                "memberships are 4."
            ),
            (
                "Reporting COUNTROWS(GroupMembership) as campaign reach counts Bo twice and "
                "overstates the unique audience by a third."
            ),
            (
                "COUNTROWS(DISTINCT(GroupMembership[CustomerKey])) returns 3, and "
                "COUNTROWS(GroupMembership) returns 4."
            ),
        ),
    ],
    29: [
        (
            (
                "Every 2025 order also ships in 2025 (the latest is S8, shipped 2025-02-04), so "
                "the year contains the same five lines, S4 to S8, in both roles."
            ),
            (
                "Testing ShipRevenue only at the year level and calling it validated. 123 against "
                "123 passes even if the measure ignored the ship role completely."
            ),
            (
                "For Year 2025 both return 123; January returns 67 against 47 and February 56 "
                "against 76."
            ),
        ),
        (
            (
                "Only the ship role reads ShipDate. Moving S6's 20 USD shipment to January makes "
                "ship revenue 47 + 20 = 67 in January and 76 - 20 = 56 in February."
            ),
            (
                "Editing S6's OrderDate instead moves OrderRevenue as well, so the comparison "
                "loses the very difference it is meant to show."
            ),
            "After the change OrderRevenue stays 67 and 56, and ShipRevenue becomes 67 and 56.",
        ),
        (
            (
                "Put USERELATIONSHIP inside the measure, so every visual that uses ShipRevenue "
                "attributes by ShipDate and the active OrderDate relationship is switched off."
            ),
            (
                "Adding `TREATAS ( VALUES ( 'Date'[Date] ), Sales[ShipDate] )` while the order "
                "relationship stays active requires both dates in the month. January still shows "
                "47, but February drops S6 and shows 56 instead of 76."
            ),
            (
                "Check February, not January: the measure must return 76 under Year 2025 and "
                "MonthNumber 2."
            ),
        ),
        (
            (
                "USERELATIONSHIP switches on a relationship already defined between two columns. "
                "The inactive Sales[ShipDate] to 'Date'[Date] link exists, so case A works."
            ),
            (
                "Passing an expression such as `Sales[OrderDate] + 7` for an expected delivery "
                "date fails, because the arguments must be columns in an existing relationship."
            ),
            (
                "Store an ExpectedDate column with an inactive relationship, then test it. Each "
                "2025 order plus 7 days stays in its order month here (S6 lands on January 12), so "
                "January reads 67 and February 56."
            ),
        ),
        (
            (
                "Choosing a relationship changes which date a fact is filed under. It does not "
                "change which rows a security role exposes, and Microsoft documents limits on "
                "using USERELATIONSHIP where row-level security applies to a related table."
            ),
            (
                "Assuming the ship role could reveal rows a North-only role hides, or that a "
                "correct 67 against 47 proves the measure works under security, when that "
                "comparison ran with no role at all."
            ),
            (
                "Under a tested North-only role, January order and ship revenue should both be 47 "
                "(S4 and S5); verify with the engine's role testing, not by hand."
            ),
        ),
        (
            (
                "Separate OrderDate and ShipDate dimensions allow two independent selections. "
                "Ordered in January 2025 and shipped in February 2025 selects S6 alone, 20."
            ),
            (
                "Expecting one shared Date slicer to express that question. A single selection "
                "applies to whichever role each measure activates, so no visual can show the 20."
            ),
            (
                "With separate dimensions, OrderDate January 2025 and ShipDate February 2025 "
                "return 20; with one Date table, use role measures for side-by-side comparisons "
                "such as 67 against 47."
            ),
        ),
    ],
    30: [
        (
            (
                "VALUES over GroupMembership[CustomerKey] returns each customer once. Selecting "
                "both audiences yields {10, 20, 30}, and TREATAS sends that set to Customer: 51 + "
                "80 + 56 = 187."
            ),
            (
                "Adding the two audience totals, 131 + 136, gives 267 and counts Bo's 80 twice, "
                "even though only 187 USD exists."
            ),
            (
                "With both audiences selected AudienceRevenue is 187, and "
                "COUNTROWS(VALUES(GroupMembership[CustomerKey])) is 3 while the bridge has 4 rows."
            ),
        ),
        (
            (
                "Membership and revenue are separate measures. Adding Di (key 40) gives Newsletter "
                "three members, while revenue stays 131 because Di has no sales."
            ),
            (
                "Treating revenue as a check on membership loads. Unchanged revenue looks like the "
                "load failed, and revenue per member silently falls from 65.5 to about 43.67."
            ),
            "Under Newsletter, distinct members read 3 and AudienceRevenue 131.",
        ),
        (
            (
                "Inclusion and exclusion: Newsletter 131 plus Prospects 136, minus the overlap, "
                "which is Bo alone at 80, equals the union, 187."
            ),
            (
                "Subtracting the overlap count, 1, instead of the overlap revenue leaves 266, "
                "which mixes customers with USD."
            ),
            (
                "`CALCULATE ( [NetRevenue], Customer[CustomerKey] = 20 )` returns 80, and 131 + "
                "136 - 80 equals the both-audience result, 187."
            ),
        ),
        (
            (
                "The bridge's grain is one row per group and customer. A second (1, 10) row breaks "
                "that grain. VALUES hides it here, so Newsletter revenue still reads 131."
            ),
            (
                "Accepting the duplicate because the revenue test passes. "
                "COUNTROWS(GroupMembership) under Newsletter becomes 3 instead of 2, and a SUMX "
                "over bridge rows gives 51 + 51 + 80 = 182."
            ),
            (
                "Compare COUNTROWS(GroupMembership) with `COUNTROWS ( SUMMARIZE ( GroupMembership, "
                "GroupMembership[GroupKey], GroupMembership[CustomerKey] ) )`; any difference is a "
                "load defect."
            ),
        ),
        (
            (
                "The audience mapping is a CALCULATE argument in a query. RawRevenue stays 187 "
                "under each audience because Audience filters only the bridge."
            ),
            (
                "Calling the TREATAS measure a security rule. A user who drops the Audience filter "
                "or writes another measure on Sales sees 187, all customers."
            ),
            (
                "Without the audience filter AudienceRevenue is 187. Real protection needs an "
                "engine role, tested under each identity."
            ),
        ),
        (
            (
                "Programs work like audiences: one row per program and patient, unique counts for "
                "reach and pair counts for workload. Using the audience data as a stand-in, Bo is "
                "in two groups."
            ),
            (
                "Summing per-program patient counts, 2 + 2 = 4, as unique patients double-counts "
                "the overlap; the true count is 3."
            ),
            (
                "Distinct patients across both programs should equal the sum of program counts "
                "minus the overlap: 2 + 2 - 1 = 3."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

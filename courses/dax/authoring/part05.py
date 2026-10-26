"""Stage five: table shape, lineage and relationship design."""

from .common import lesson
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
                    "VALUES supplies keys 1,2,3,4.",
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
                    "That all-blank group is omitted; keys 1,2,3 remain.",
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
            "contains 1,2,1,3. Taking DISTINCT after UNION gives the "
            "three unique keys 1,2,3. That extra DISTINCT is a "
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
                "Distinct Paper keys{1,2} and Blue keys{1,3} from the clean model.",
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
                    "DISTINCT removes repeated key rows, leaving 1,2,3.",
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
                    "Orders S4,S5,S6 belong to January and total 67.",
                    "Shipments S4 and S 5 occur in January and total 47.",
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
                    "Orders S7,S8 total 56 in February.",
                    "Shipments include S6,S7,S8, totaling 76.",
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
                "The keys are 10,20,30, and the unique population totals 187 rather than 267.",
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
                "131 +136 -80 =187 for the union of these two audiences.",
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

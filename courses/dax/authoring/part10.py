"Stage ten: storage/security boundaries and three integrated reference capstones."

from .common import BASE, lesson
from .common import result as r
from .common import task as t

RLS_NOTE = (
    "These are hand-derived expectations under explicitly "
    "specified role policies, not tests of real RLS "
    "enforcement. Microsoft documentation reviewed 2026-10-25 "
    "distinguishes role-restricted Viewers from workspace "
    "Admin/Member/Contributor access. No account, role "
    "assignment, model publication or security engine is used "
    "by this classroom."
)
COST = BASE + (
    "    MEASURE Sales[Cost] = SUMX ( Sales, Sales[Quantity] * RELATED ( Product[UnitCost] ) )\n"
)
COMMERCIAL = BASE + (
    "    MEASURE Sales[RefundsAttributedToSale] = COALESCE ( "
    "SUM ( Returns[Refund] ), 0 )\n    MEASURE "
    "Sales[AdjustedCoreRevenue] = [NetRevenue] - "
    "[RefundsAttributedToSale]\n    MEASURE "
    "ForeignSales[ConvertedUSD] = SUMX ( ForeignSales,\n        "
    "ForeignSales[LocalAmount] * LOOKUPVALUE ( "
    "ExchangeRate[USDPerUnit],\n            "
    "ExchangeRate[RateDate], ForeignSales[SaleDate],\n          "
    "  ExchangeRate[Currency], ForeignSales[Currency] ) )\n"
)

LESSONS = [
    lesson(
        55,
        "Storage modes, freshness and capability boundaries",
        ["Import", "DirectQuery", "composite model", "Direct Lake", "refresh"],
        (
            "Separate a metric's definition from data freshness, "
            "storage mode and external capability."
        ),
        (
            "Import stores a processed copy of data in the semantic "
            "model. DirectQuery leaves data in the source and issues "
            "queries through supported connectors at report time. "
            "Composite models combine storage choices and can "
            "introduce additional relationship and query constraints. "
            "Direct Lake is a Fabric-specific mode over supported lake "
            "data with its own framing, identity and fallback "
            "behavior. None of these modes is provided by the offline "
            "DAX classroom.\n\nThe same revenue definition should return "
            "187 when two models expose the same eight facts and "
            "compatible semantics. That numerical agreement does not "
            "establish identical refresh behavior, function support, "
            "security, latency or transaction consistency. Some DAX "
            "functions have specific DirectQuery restrictions in "
            "calculated columns or RLS rules; check the exact use, not "
            "merely the function's name.\n\nFreshness is an explicit "
            "input. If a hypothetical source gains a valid ten-dollar "
            "sale after an Import refresh, the stored snapshot can "
            "still report 187 while a later source view has 197. "
            "DirectQuery is not a universal guarantee of immediate, "
            "uncached or transactionally consistent observation; its "
            "actual behavior depends on the source, connector, caching "
            "and workload. A mode label does not replace a freshness "
            "contract."
        ),
        (
            "The first query states a parity condition on one fixed "
            "fixture. The second models a clearly hypothetical new "
            "source event with an explicit added amount. It does not "
            "connect to an external source or claim that a particular "
            "storage mode was executed."
        ),
        [
            r(
                "Same data, same defined amount",
                (
                    'EVALUATE ROW ( "FixedFixtureRevenue", [NetRevenue], '
                    '"EquivalentSnapshotRevenue", SUMX ( Sales, '
                    "Sales[NetAmount] ) )"
                ),
                [("FixedFixtureRevenue", "number"), ("EquivalentSnapshotRevenue", "number")],
                [[187, 187]],
                ("The same fixed data and compatible semantics; no actual storage-mode execution."),
                [
                    "Both expressions include the same eight line amounts.",
                    "Each totals 187.",
                    (
                        "This parity condition says nothing about refresh latency "
                        "or external function support."
                    ),
                ],
                (
                    "A release should compare actual model outputs after any "
                    "storage-mode change rather than assuming the mode "
                    "preserves every detail."
                ),
            ),
            r(
                "A refresh boundary can explain a difference",
                (
                    'EVALUATE ROW ( "StoredSnapshot", [NetRevenue], '
                    '"HypotheticalLaterSource", [NetRevenue] + 10 )'
                ),
                [("StoredSnapshot", "number"), ("HypotheticalLaterSource", "number")],
                [[187, 197]],
                (
                    "Illustrative scenario: an additional valid 10 USD event "
                    "arrives after the stored snapshot; it is not added to the "
                    "checked-in Sales fixture."
                ),
                [
                    "The snapshot still contains 187.",
                    "The hypothetical later source adds exactly 10 under the same metric policy.",
                    (
                        "Its intended amount is 197; an observed difference would "
                        "need provenance and freshness checks."
                    ),
                ],
                (
                    "The additional event is scenario data, not evidence of a "
                    "connected source or live DirectQuery result."
                ),
                note=(
                    "Hand-derived freshness scenario only. No source "
                    "connection, refresh, DirectQuery or Direct Lake operation "
                    "occurred."
                ),
            ),
        ],
        [
            t(
                "State the observations needed to compare Import and DirectQuery fairly.",
                "Source identity and observation time matter as well as the formula.",
                (
                    "Record equivalent populations, source/snapshot versions, "
                    "filters, roles, function support and actual query/refresh "
                    "evidence."
                ),
            ),
            t(
                "Change the hypothetical later event to a correction of an existing line.",
                "An update is not necessarily an append.",
                (
                    "Recompute the metric from the corrected source identity; "
                    "do not assume every change adds an amount."
                ),
            ),
            t(
                "Write a storage-mode capability review.",
                "Check the exact formula context and relationship type.",
                (
                    "List measures versus calculated columns/RLS uses, "
                    "supported functions, regular/limited relationships, "
                    "security identity, source constraints and "
                    "refresh/fallback behavior."
                ),
            ),
            t(
                "Diagnose saying DirectQuery guarantees real-time truth.",
                "Caching, source transactions and connector behavior remain relevant.",
                (
                    "Define and measure an actual freshness/consistency "
                    "requirement; the mode name alone does not satisfy it."
                ),
            ),
            t(
                (
                    "Explain why this course does not require a Fabric account "
                    "for Direct Lake study."
                ),
                "Conceptual understanding and operating an external service are separate.",
                (
                    "The lesson provides model and scenario reasoning offline. "
                    "Live Direct Lake configuration would be a separately "
                    "authorized external workflow."
                ),
            ),
            t(
                "Transfer the freshness boundary to a cached feature table.",
                "Stored data and source data can represent different versions.",
                (
                    "Attach observation/version metadata and compare "
                    "like-for-like populations before blaming a transformation "
                    "for a changed total."
                ),
            ),
        ],
        sources=[
            ("https://learn.microsoft.com/en-us/power-bi/connect-data/desktop-directquery-about"),
            "https://learn.microsoft.com/en-us/fabric/fundamentals/direct-lake-overview",
            ("https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-composite-models"),
        ],
    ),
    lesson(
        56,
        "A report filter is not row-level security",
        ["RLS", "Viewer", "security context", "report filter", "REMOVEFILTERS"],
        ("Distinguish a removable analytical filter from an engine-enforced role restriction."),
        (
            "A report filter expresses a query choice. A user who can "
            "issue another query can remove or change that choice. "
            "Row-level security instead restricts rows through the "
            "semantic model's security context for applicable "
            "identities and roles. An expression such as REMOVEFILTERS "
            "cannot be treated as permission to retrieve rows that a "
            "real RLS policy denies.\n\nThe two cases deliberately use "
            "different stated contexts. An unrestricted model with an "
            "ordinary North report filter shows 107, but removing that "
            "report filter returns 187. Under the declared NorthViewer "
            "policy, the permitted Customer population is North, so "
            "both the ordinary revenue measure and a "
            "customer-filter-removal attempt are expected to stay at "
            "107.\n\nThis classroom does not enforce those model roles. "
            "The second result is a policy-based hand derivation, not "
            "a penetration test or an observed security guarantee. In "
            "a real Power BI service, workspace-role distinctions also "
            "matter: an unrestricted owner/administrator result is not "
            "a valid substitute for testing the intended Viewer. Keep "
            "identity, role membership, relationship propagation and "
            "model version in the acceptance record."
        ),
        (
            "Case A encodes its ordinary filter in the query. Case B "
            "assumes the externally enforced NorthViewer policy "
            "defined in the model specification and must be evaluated "
            "under that separate context if used externally. Do not "
            "submit both as if one unchanging unrestricted session "
            "could demonstrate RLS. The static role predicate is "
            'Customer[Region]="North" in its appropriate model role '
            "definition."
        ),
        [
            r(
                "An ordinary filter can be removed",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "SelectedRevenue", '
                    '[NetRevenue], "AfterRemovingCustomerFilters", CALCULATE ( '
                    "[NetRevenue], REMOVEFILTERS ( Customer ) ) ), "
                    'Customer[Region] = "North" )'
                ),
                [("SelectedRevenue", "number"), ("AfterRemovingCustomerFilters", "number")],
                [[107, 187]],
                "Unrestricted model; North is only an ordinary report/query filter.",
                [
                    "The report filter selects Ada and Cy, whose revenue totals 107.",
                    "REMOVEFILTERS(Customer) removes that analytical selection.",
                    ("Bo's 80 becomes eligible, restoring 187."),
                ],
                "The removable filter never constituted an access-control boundary.",
            ),
            r(
                "Expected behavior under an enforced NorthViewer role",
                (
                    'EVALUATE ROW ( "VisibleRevenue", [NetRevenue], '
                    '"AfterRemovingCustomerFilters", CALCULATE ( [NetRevenue], '
                    "REMOVEFILTERS ( Customer ) ) )"
                ),
                [("VisibleRevenue", "number"), ("AfterRemovingCustomerFilters", "number")],
                [[107, 107]],
                (
                    "Assume a role-restricted Viewer with the declared "
                    "NorthViewer RLS policy enforced by a compatible engine; "
                    "no ordinary Customer filter is needed."
                ),
                [
                    "The security policy permits Customer 10 and 30 only.",
                    "The expected fact population totals 51 +56 =107.",
                    "Removing ordinary Customer filters must not remove the security restriction.",
                ],
                (
                    "These expected values belong in a real role-test matrix. "
                    "Their presence in a source file does not prove that the "
                    "external role was configured or applied."
                ),
                note=(
                    "Hand-derived security-policy expectation only. The "
                    "classroom has not executed an RLS engine or authenticated "
                    "this synthetic role."
                ),
            ),
        ],
        model="analytics",
        feature=RLS_NOTE,
        sources=[
            ("https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security"),
            "https://learn.microsoft.com/en-us/dax/removefilters-function-dax",
        ],
        practice=[
            t(
                ("Predict the ordinary unfiltered total in case A."),
                "There is no role restriction there.",
                "It is 187.",
            ),
            t(
                "Change the declared role to SouthViewer.",
                ("Only Bo is permitted by that policy."),
                "Expected revenue is 80, including after an ordinary Customer-filter removal.",
            ),
            t(
                "Write a real RLS acceptance record template.",
                "Include identity and role evidence, not just one result.",
                (
                    "Record test identity/workspace role, model/role version, "
                    "relationships, submitted query, expected allowed rows and "
                    "actual observed result, including denial cases."
                ),
            ),
            t(
                "Diagnose testing only as the workspace administrator.",
                "Administrator access is not restricted like the intended Viewer context.",
                (
                    "Use the documented applicable role and identity; an "
                    "unrestricted result cannot certify Viewer RLS behavior."
                ),
            ),
            t(
                "Explain why hidden report pages or disabled buttons are insufficient.",
                "Presentation is not semantic-model access enforcement.",
                (
                    "A real security boundary must constrain allowed data "
                    "through the supported engine/service controls, not just "
                    "the visible navigation."
                ),
            ),
            t(
                "Transfer the distinction to a SQL dashboard WHERE clause.",
                "A query convention is different from enforced authorization.",
                (
                    "A removable predicate does not protect data from another "
                    "authorized query path; test actual role/permission "
                    "boundaries separately."
                ),
            ),
        ],
    ),
    lesson(
        57,
        "Dynamic RLS needs a complete identity and mapping contract",
        ["USERPRINCIPALNAME", "identity mapping", "default deny", "role predicate", "access table"],
        (
            "Reason about a dynamic region policy, including unmapped "
            "identities and policy-table exposure."
        ),
        (
            "Dynamic RLS can derive permitted rows from an "
            "identity-to-domain mapping. Our synthetic Access table "
            "maps north.learner@example.test to North and "
            "south.learner@example.test to South. The Customer role "
            "predicate tests whether its Region belongs to the allowed "
            "set for USERPRINCIPALNAME. The strings are fictional "
            "teaching principals, not actual accounts.\n\nAn unmapped "
            "identity should have an explicitly defined outcome. The "
            "supplied policy uses an empty allowed-region set, so no "
            "Customer rows are permitted. Do not replace a missing "
            "mapping with unrestricted access or infer permission from "
            "an ordinary slicer. Mapping uniqueness, valid region "
            "names, identity normalization and assignment governance "
            "are part of the design.\n\nRestricting Customer does not "
            "automatically protect the Access table itself or every "
            "other disconnected fact. A real model needs a review of "
            "all exposed tables and supported identity/relationship "
            "behavior. The offline reference makes the intended rule "
            "inspectable, but actual enforcement requires a separately "
            "prepared engine and applicable Viewer-role tests."
        ),
        (
            "The model specification contains the dynamic predicate. "
            "FILTER selects Access rows for the current principal, "
            "SELECTCOLUMNS projects allowed regions and IN tests "
            "membership for the current Customer row. The queries "
            "below are intended under the stated policy contexts; they "
            "do not establish identity or security by themselves."
        ),
        [
            r(
                "A mapped synthetic principal",
                (
                    'EVALUATE ROW ( "VisibleCustomers", COUNTROWS ( Customer '
                    '), "VisibleRevenue", [NetRevenue] )'
                ),
                [("VisibleCustomers", "integer"), ("VisibleRevenue", "number")],
                [[2, 107]],
                (
                    "Assume the declared dynamic Customer policy is enforced "
                    "for north.learner@example.test in a role-restricted "
                    "Viewer context."
                ),
                [
                    "The Access mapping supplies North.",
                    "Customer 10 and 30 are allowed.",
                    "Their revenues 51 and 56 total 107.",
                ],
                (
                    "The identity string selects an expected mapping in this "
                    "teaching specification. No external account was "
                    "authenticated and no role-test result is being claimed."
                ),
                note=(
                    "Hand-derived expectation for a fictional principal and "
                    "declared dynamic policy; not live security evidence."
                ),
            ),
            r(
                "An unmapped principal is denied by the declared policy",
                (
                    'EVALUATE ROW ( "VisibleCustomers", COUNTROWS ( Customer '
                    '), "VisibleRevenue", [NetRevenue], "HasVisibleRows", '
                    "COUNTROWS ( Customer ) > 0 )"
                ),
                [
                    ("VisibleCustomers", "integer"),
                    ("VisibleRevenue", "number"),
                    ("HasVisibleRows", "boolean"),
                ],
                [[None, None, False]],
                (
                    "Assume the same enforced policy for "
                    "unmapped.learner@example.test; its allowed-region set is "
                    "empty."
                ),
                [
                    "No Access row matches that principal.",
                    "The policy's allowed Region set is empty and no Customer row qualifies.",
                    (
                        "COUNTROWS and SUM are BLANK on their empty populations; "
                        "the positive-row comparison is FALSE."
                    ),
                ],
                (
                    "This is an explicit deny expectation, not a fallback to "
                    "all regions. Test it under an actual applicable role "
                    "before relying on a deployed model."
                ),
                note=(
                    "Hand-derived default-deny expectation. No authentication "
                    "or live RLS enforcement occurred."
                ),
            ),
        ],
        model="analytics",
        feature=RLS_NOTE,
        extra=(
            "The following is a role predicate on Customer in the "
            "specified external model scope, not a complete "
            "query:\n\n```dax\nCustomer[Region] IN\n    SELECTCOLUMNS ( "
            "FILTER ( Access, Access[Principal] = USERPRINCIPALNAME() "
            '),\n        "AllowedRegion", Access[Region] )\n```\n\nReview '
            "protection of the Access mapping and all other exposed "
            "tables separately. The local classroom stores this text "
            "for study and never applies it to its own authentication "
            "system."
        ),
        sources=[
            "https://learn.microsoft.com/en-us/dax/userprincipalname-function-dax",
            ("https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security"),
        ],
        practice=[
            t(
                "Predict the permitted population for the synthetic south principal.",
                "Read the exact region mapping.",
                "One customer,Bo, is permitted; expected revenue is 80.",
            ),
            t(
                "AddWest to a principal's allowed-region set conceptually.",
                "Customer 40 exists but has no sales.",
                (
                    "The allowed-customer count can increase while revenue "
                    "stays unchanged; permission population and fact activity "
                    "are different."
                ),
            ),
            t(
                "Write a default-deny mapping test matrix.",
                "Include mapped, unmapped and invalid-domain cases.",
                (
                    "Record each fictional principal, allowed regions, "
                    "expected Customer keys and amounts, plus the required "
                    "real identity/role evidence before deployment."
                ),
            ),
            t(
                "Diagnose granting all regions when no mapping exists.",
                "A missing policy record is not authorization.",
                (
                    "That reverses the supplied default-deny contract and "
                    "risks unintended access. Keep an explicit denial and "
                    "investigate provisioning."
                ),
            ),
            t(
                "Explain why securing Customer does not prove Access itself is protected.",
                "Security rules apply according to the actual model and table exposure.",
                (
                    "Review mapping-table visibility and disconnected data "
                    "independently; do not infer complete protection from one "
                    "correctly filtered sales result."
                ),
            ),
            t(
                "Transfer the policy to tenant identifiers.",
                "Tenant membership and identity provenance require explicit contracts.",
                (
                    "Validate authenticated identity, membership changes, "
                    "allowed tenant keys and every query surface; an editable "
                    "tenant filter is not an access-control system."
                ),
            ),
        ],
    ),
    lesson(
        58,
        "Commercial-model capstone: reconcile adjustments and targets",
        [
            "commercial model",
            "refund attribution",
            "currency conversion",
            "budget grain",
            "reconciliation",
        ],
        (
            "Produce a reviewable commercial metric specification with "
            "explicit populations and adjustment policies."
        ),
        (
            "An integrated commercial model needs more than a large "
            "final revenue formula. Define the grain, currency, date "
            "role and adjustment policy for each input. Our core Sales "
            "are USD amounts after line discounts. Returns records "
            "monetary refunds linked to SaleID; this fixture "
            "attributes those refunds to the original sale's date, not "
            "an unprovided return-event date. ForeignSales is a "
            "separate population requiring explicit conversion.\n\nCore "
            "sales total 187 and refunds total 13, giving adjusted "
            "core revenue 174. The foreign transaction fixture "
            "converts to 270 USD under its transaction-date rate "
            "policy. These are distinct named populations. Do not "
            "combine them with a budget unless the budget's scope "
            "includes both and source identities establish that no "
            "transaction is duplicated.\n\nThe supplied Budget covers "
            "the core Paper/Home categories in January and February "
            "2025. Core actuals in that scope are 123 before refunds "
            "and 114 after the nine-dollar refund attributed to S4. "
            "The compatible budget is 165, giving an adjusted-revenue "
            "variance of-51. This does not establish accounting "
            "profit, inventory restatement or tax treatment, which "
            "require additional data and policy."
        ),
        (
            "The reference composes named measures for refund "
            "attribution, adjusted core revenue and converted foreign "
            "amounts. The relationship Sales->Returns propagates the "
            "original sale's dimension/date context. Budget remains "
            "disconnected and is matched explicitly by month and "
            "category. The two cases expose component totals before "
            "reporting a variance."
        ),
        [
            r(
                "Reconcile named monetary populations",
                (
                    'EVALUATE ROW ( "CoreNetSales", [NetRevenue], '
                    '"RefundsAttributedToSales", [RefundsAttributedToSale], '
                    '"AdjustedCoreRevenue", [AdjustedCoreRevenue], '
                    '"SeparateForeignUSD", [ConvertedUSD] )'
                ),
                [
                    ("CoreNetSales", "number"),
                    ("RefundsAttributedToSales", "number"),
                    ("AdjustedCoreRevenue", "number"),
                    ("SeparateForeignUSD", "number"),
                ],
                [[187, 13, 174, 270]],
                (
                    "Analytics model; complete supplied refund and rate "
                    "fixtures; core and foreign populations are reported "
                    "separately."
                ),
                [
                    "Core line discounts are already included in NetAmount, whose total is 187.",
                    "Refunds 4 and 9 total 13; adjusted core revenue is 174.",
                    (
                        "Foreign amounts convert to 100 +110 +60 =270 USD under "
                        "their separate policy."
                    ),
                ],
                (
                    "Showing components makes double subtraction and "
                    "population mixing visible. The foreign number is not "
                    "silently added to a core-only budget comparison."
                ),
            ),
            r(
                "Compare an aligned two-month core population",
                (
                    "EVALUATE CALCULATETABLE ( VAR Target = CALCULATE ( SUM ( "
                    "Budget[Amount] ), TREATAS ( VALUES ( 'Date'[MonthKey] ), "
                    "Budget[MonthKey] ), TREATAS ( VALUES ( Product[Category] "
                    '), Budget[Category] ) ) RETURN ROW ( "CoreBeforeRefund", '
                    '[NetRevenue], "Refunds", [RefundsAttributedToSale], '
                    '"AdjustedCore", [AdjustedCoreRevenue], "Budget", Target, '
                    '"Variance", [AdjustedCoreRevenue] - Target ), '
                    "'Date'[Year] = 2025, 'Date'[MonthNumber] IN { 1, 2 }, "
                    'Product[Category] IN { "Paper", "Home" } )'
                ),
                [
                    ("CoreBeforeRefund", "number"),
                    ("Refunds", "number"),
                    ("AdjustedCore", "number"),
                    ("Budget", "number"),
                    ("Variance", "number"),
                ],
                [[123, 9, 114, 165, -51]],
                (
                    "FullJanuary/February 2025, Paper/Home core sales, refunds "
                    "attributed to original sale dates; Budget covers exactly "
                    "that month/category scope."
                ),
                [
                    "Core 2025 sales in these months total 123.",
                    (
                        "Only the refund linked to S 4 belongs to that sale-date "
                        "population, subtracting 9."
                    ),
                    "The four compatible budget rows total 165;114 -165 =-51.",
                ],
                (
                    "A return-date report could differ, but this fixture does "
                    "not contain ReturnDate. The correct conclusion is to "
                    "state the limitation, not invent another temporal "
                    "attribution."
                ),
            ),
        ],
        defines=COMMERCIAL,
        model="analytics",
        sources=[
            "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema",
            "https://learn.microsoft.com/en-us/dax/treatas-function-dax",
            "https://learn.microsoft.com/en-us/dax/lookupvalue-function-dax",
        ],
        practice=[
            t(
                "Reconcile adjusted core revenue by year.",
                "Attribute each refund through its original SaleID.",
                (
                    "2024 contributes 64 -4 =60;2025 contributes 123 -9 =114; "
                    "together they total 174."
                ),
            ),
            t(
                "Request a report by actual refund-event month.",
                "Check whether that field exists.",
                (
                    "It cannot be derived from this fixture. Add a properly "
                    "grained return-event date and explicit date role rather "
                    "than reusing OrderDate without disclosure."
                ),
            ),
            t(
                "Write the capstone's metric and model specification.",
                "Include input grain, key, currency, relationship, date role and exclusions.",
                (
                    "Document core sales, linked refunds, separate foreign "
                    "transactions/rates, monthly-category budget, observation "
                    "coverage, unknown-key policy and context-result "
                    "regression cases."
                ),
            ),
            t(
                "Diagnose subtracting the line Discount again from NetAmount.",
                "NetAmount already includes that adjustment.",
                (
                    "It would double-count discounts and understate core "
                    "revenue. Reconcile 195 gross -8 discount =187 net before "
                    "applying refunds."
                ),
            ),
            t(
                "Explain why 174 is not automatically accounting profit.",
                "Refund treatment is only one part of a profit definition.",
                (
                    "Costs, return-related inventory/COGS changes, tax and "
                    "other expenses need explicit data and accounting policy."
                ),
            ),
            t(
                "Design an external acceptance plan for the capstone.",
                "Source review, engine behavior and release are distinct gates.",
                (
                    "Validate model loading, exact measures/context matrix, "
                    "missing keys/rates, role restrictions, refresh behavior "
                    "and qualified performance before any deployment claim."
                ),
            ),
        ],
    ),
    lesson(
        59,
        "Experiment and cohort capstone: preserve the assigned unit",
        [
            "assignment unit",
            "exposure events",
            "intention to treat",
            "Wilson interval",
            "causal boundary",
        ],
        (
            "Build an experiment-quality semantic report without "
            "treating repeated events or displayed estimates as causal "
            "proof."
        ),
        (
            "An experiment report must preserve the randomized or "
            "assigned unit. Assignments has one row per unit, Outcomes "
            "one finalized outcome per assigned unit, and Exposures "
            "one row per event. Repeated exposure events are not extra "
            "independent assignments. Missing exposure records also do "
            "not automatically remove an assigned unit from an "
            "intention-to-treat denominator.\n\nThe synthetic Control "
            "arm has two assigned units and one conversion; Treatment "
            "has two assigned units and two conversions. Treatment's "
            "two exposure events both belong to U3, while U4 has no "
            "recorded exposure event. A naive event-level summary can "
            "hide this coverage defect because its event count still "
            "equals two. Report both distinct exposed units and event "
            "rows.\n\nThe supplied statistical summary contains marginal "
            "95-percent Wilson score intervals for each arm's binomial "
            "rate. They are wide because n=2. These intervals are not "
            "an interval for the treatment difference and do not "
            "validate random assignment, measurement quality, "
            "independence or a causal claim. DAX can aggregate and "
            "display the model's data, but it does not establish those "
            "study-design assumptions."
        ),
        (
            "The first query groups Assignments by Arm, allowing its "
            "relationships to filter Outcomes and Exposures. It keeps "
            "assigned, converted, exposed-unit and event counts "
            "separate. The second reads a supplied, explicitly labeled "
            "analysis table. Its interval numbers are input reference "
            "material, not results of a DAX statistical engine or "
            "learner execution."
        ),
        [
            r(
                "Assignment and exposure integrity",
                (
                    'EVALUATE SUMMARIZECOLUMNS ( Assignments[Arm], "Assigned", '
                    'COUNTROWS ( Assignments ), "Converted", SUM ( '
                    'Outcomes[Converted] ), "ExposedUnits", DISTINCTCOUNT ( '
                    'Exposures[UnitID] ), "ExposureEvents", COUNTROWS ( '
                    'Exposures ), "AssignedUnitRate", DIVIDE ( SUM ( '
                    "Outcomes[Converted] ), COUNTROWS ( Assignments ) ) "
                    ")\nORDER BY Assignments[Arm]"
                ),
                [
                    ("Arm", "text"),
                    ("Assigned", "integer"),
                    ("Converted", "integer"),
                    ("ExposedUnits", "integer"),
                    ("ExposureEvents", "integer"),
                    ("AssignedUnitRate", "number"),
                ],
                [["Control", 2, 1, 2, 2, 0.5], ["Treatment", 2, 2, 1, 2, 1]],
                (
                    "Analytics experiment fixture; all four assigned units "
                    "have one complete outcome; exposure is a separate "
                    "repeated-event stream."
                ),
                [
                    ("Control U1/U2 yield one conversion among two assignments."),
                    (
                        "Treatment U3/U4 yield two conversions, but both "
                        "treatment exposure events belong to U3."
                    ),
                    (
                        "Assigned-unit rates are 0.5 and 1; exposure counts reveal "
                        "a separate coverage/duplication issue."
                    ),
                ],
                (
                    "The observed difference 0.5 is a descriptive contrast in "
                    "this synthetic fixture, not evidence that the assignment "
                    "or measurement process supports causal inference."
                ),
            ),
            r(
                "Display supplied uncertainty without overstating it",
                (
                    'EVALUATE SELECTCOLUMNS ( ExperimentSummary, "Arm", '
                    'ExperimentSummary[Arm], "Rate", ExperimentSummary[Rate], '
                    '"WilsonLower", ExperimentSummary[WilsonLower], '
                    '"WilsonUpper", ExperimentSummary[WilsonUpper] )\nORDER BY '
                    "[Arm]"
                ),
                [
                    ("Arm", "text"),
                    ("Rate", "number"),
                    ("WilsonLower", "number"),
                    ("WilsonUpper", "number"),
                ],
                [
                    ["Control", 0.5, 0.09453120573423074, 0.9054687942657693],
                    ["Treatment", 1, 0.34238022750665303, 1],
                ],
                (
                    "Supplied marginal 95 percent Wilson score intervals for "
                    "each arm's binomial rate; n=2 per arm; not a difference "
                    "interval."
                ),
                [
                    "Control has k=1,n=2 and estimate 0.5.",
                    "Treatment has k=2,n=2 and estimate 1.",
                    (
                        "The marginal intervals remain wide; an all-successes "
                        "sample does not imply a known population rate of 1."
                    ),
                ],
                (
                    "The interval table has its own method and assumptions. "
                    "Displaying it accurately is different from validating the "
                    "scientific design or calculating a treatment-effect "
                    "confidence interval."
                ),
                note=(
                    "Hand-derived/displayed supplied statistical summary. No "
                    "DAX or statistical runtime was executed by this lesson."
                ),
            ),
        ],
        model="analytics",
        extra=(
            "The supplied intervals use the Wilson score construction "
            "with\n\\(z=1.959963984540054\\) and \\(\\widehat "
            "p=k/n\\):\n\n\\[\nc=\\frac{\\widehat "
            "p+z^2/(2n)}{1+z^2/n},\\qquad\nh=\\frac{z\\sqrt{\\widehat "
            "p(1-\\widehat p)/n+z^2/(4n^2)}}{1+z^2/n}.\n\\]\n\nThe marginal "
            "bounds are \\(c-h\\) and \\(c+h\\), limited to the "
            "probability range\nfor numerical reporting. The fixture "
            "supplies the two arm-specific summaries.\nThese are not "
            "confidence limits for the treatment-control difference, "
            "and two\nunits per arm provide extremely weak evidence. A "
            "real experimental analysis\nalso needs random assignment, "
            "exposure and outcome definitions, missingness\nchecks, a "
            "declared estimand and an appropriate uncertainty "
            "procedure. DAX can\nreconcile the unit-level data without "
            "substituting for that statistical design.\n"
        ),
        sources=[
            "https://learn.microsoft.com/en-us/dax/distinctcount-function-dax",
            "https://learn.microsoft.com/en-us/power-bi/guidance/star-schema",
        ],
        practice=[
            t(
                ("Predict the treatment exposure-event count after another U3 event."),
                "The assigned population and distinct exposed identities do not change.",
                (
                    "Events become 3, distinct exposed units stay 1, "
                    "assignments stay 2 and the assigned-unit conversion rate "
                    "stays 1."
                ),
            ),
            t(
                ("Remove U4 merely because no exposure is recorded."),
                "That changes the estimand and conditions on a post-assignment process.",
                (
                    "Do not silently remove it from an intention-to-treat "
                    "denominator. Any alternative exposure-based analysis "
                    "needs its own justified design and labeling."
                ),
            ),
            t(
                "Write the quality matrix needed before interpreting the arm contrast.",
                "Include unit identity, assignment, outcome completeness and event integrity.",
                (
                    "Check one assignment per unit, stable arm membership, "
                    "outcome coverage, duplicate exposures, timing, "
                    "eligibility and the provenance of any supplied "
                    "uncertainty summary."
                ),
            ),
            t(
                ("Diagnose claiming statistical certainty because Treatment's observed rate is 1."),
                "A sample of two successes still has substantial uncertainty.",
                (
                    "The supplied Wilson lower bound is about 0.3424; the "
                    "population rate is not known to equal 1, and study "
                    "validity needs additional evidence."
                ),
            ),
            t(
                (
                    "Explain why comparing arm interval overlap is not a "
                    "complete treatment-effect test."
                ),
                "The target contrast has its own sampling distribution and design.",
                (
                    "Use an appropriate difference/ratio analysis with "
                    "assumptions and multiplicity/sequential considerations; "
                    "marginal intervals are not a substitute."
                ),
            ),
            t(
                "Connect this report to the cohort model.",
                "Follow-up opportunity and population definitions remain explicit.",
                (
                    "Report cohort age/coverage, retain eligible units and "
                    "separate unobserved follow-up from failures before "
                    "comparing groups."
                ),
            ),
        ],
    ),
    lesson(
        60,
        "Delivery capstone: a model specification and an evidence ledger",
        [
            "model contract",
            "semantic regression",
            "role matrix",
            "source control",
            "release evidence",
        ],
        (
            "Assemble a reviewable model change with expected "
            "role/context results and explicit unperformed deployment "
            "checks."
        ),
        (
            "A reliable semantic-model deliverable includes more than "
            "formulas. Retain the data/model specification, "
            "relationship directions, date/calendar policies, measure "
            "dependencies, role definitions, expected context results "
            "and a change rationale. Text-based external formats such "
            "as supported PBIP/TMDL projects can assist source "
            "control, but a directory of text is not proof that a real "
            "engine accepted or securely deployed the model.\n\nThis "
            "capstone combines the constant-product-cost rewrite with "
            "two declared security populations. North's expected "
            "revenue is 107 and cost 25; South's expected revenue is "
            "80 and cost 19. The line and grouped cost formulas should "
            "agree within each permitted population. An ordinary "
            "filter-removal expression must not enlarge a real "
            "RLS-restricted population.\n\nThe offline result matrix is "
            "a specification to be tested, not a release approval. A "
            "real release requires observed model loading, "
            "role/identity tests, refresh/recovery behavior, query "
            "parity and representative performance evidence for the "
            "exact revision. Keep synthetic timing examples, "
            "hand-derived arithmetic and actual external observations "
            "in separate evidence categories. A no-go decision is "
            "appropriate when one required boundary remains unverified."
        ),
        (
            "The queries share the declared cost assumption from the "
            "optimization capstone. Each case names a distinct assumed "
            "Viewer security context. Running them externally requires "
            "the corresponding real role setup; the source alone "
            "cannot establish it. The expected matrix makes population "
            "leakage and an incorrect grouped rewrite observable."
        ),
        [
            r(
                "Expected NorthViewer regression row",
                (
                    'EVALUATE ROW ( "Revenue", [NetRevenue], "LineCost", '
                    '[Cost], "GroupedCost", SUMX ( VALUES ( '
                    "Product[ProductKey] ), CALCULATE ( SUM ( Sales[Quantity] "
                    ") ) * CALCULATE ( MAX ( Product[UnitCost] ) ) ), "
                    '"AfterCustomerFilterRemoval", CALCULATE ( [NetRevenue], '
                    "REMOVEFILTERS ( Customer ) ) )"
                ),
                [
                    ("Revenue", "number"),
                    ("LineCost", "number"),
                    ("GroupedCost", "number"),
                    ("AfterCustomerFilterRemoval", "number"),
                ],
                [[107, 25, 25, 107]],
                (
                    "Assume enforced NorthViewer policy on the analytical "
                    "model; all available dates; constant UnitCost per product."
                ),
                [
                    "North permits Ada and Cy, giving revenue 51 +56 =107.",
                    (
                        "Their product quantities are 5 Notebook,5 Pen and 2 Mug, "
                        "costing 10 +5 +10 =25."
                    ),
                    (
                        "Both cost forms agree; a real security restriction must "
                        "remain after ordinary Customer-filter removal."
                    ),
                ],
                (
                    "This expected row combines numerical parity with a policy "
                    "boundary. It does not certify either on a live model "
                    "until actual evidence is recorded."
                ),
                note=(
                    "Hand-derived acceptance specification under an assumed "
                    "role; not a runtime, security or deployment receipt."
                ),
            ),
            r(
                "Expected SouthViewer regression row",
                (
                    'EVALUATE ROW ( "Revenue", [NetRevenue], "LineCost", '
                    '[Cost], "GroupedCost", SUMX ( VALUES ( '
                    "Product[ProductKey] ), CALCULATE ( SUM ( Sales[Quantity] "
                    ") ) * CALCULATE ( MAX ( Product[UnitCost] ) ) ), "
                    '"AfterCustomerFilterRemoval", CALCULATE ( [NetRevenue], '
                    "REMOVEFILTERS ( Customer ) ) )"
                ),
                [
                    ("Revenue", "number"),
                    ("LineCost", "number"),
                    ("GroupedCost", "number"),
                    ("AfterCustomerFilterRemoval", "number"),
                ],
                [[80, 19, 19, 80]],
                (
                    "Assume enforced SouthViewer policy; the same model and "
                    "measure definitions with a different allowed Customer "
                    "population."
                ),
                [
                    "South permits Bo, whose three lines total 80.",
                    "TwoNotebook units cost 4 and three Mug units cost 15, totaling 19.",
                    (
                        "The grouped result agrees and the restricted revenue "
                        "remains 80 after ordinary filter removal."
                    ),
                ],
                (
                    "North plus South reconciles to the unrestricted 187 "
                    "revenue and 44 cost in this complete fixture. That "
                    "reconciliation does not replace testing each denied or "
                    "unmapped identity separately."
                ),
                note=(
                    "Hand-derived role/context matrix only. No actual model "
                    "publication or security enforcement was performed."
                ),
            ),
        ],
        defines=COST,
        model="analytics",
        feature=RLS_NOTE,
        extra=(
            "A reviewable delivery folder should identify these "
            "independent artifacts:\n\n| Artifact | Question it answers "
            "|\n| --- | --- |\n| CSV fixtures and typed model JSON | "
            "What rows, keys, relationships and policies are assumed? "
            "|\n| DAX measure/reference source | Which expressions are "
            "being reviewed? |\n| Named context/result matrix | What "
            "should those expressions mean under each case? |\n| "
            "Source/model hashes | Which exact bytes does the "
            "reference describe? |\n| Optional external execution "
            "record | What actually happened on a named "
            "engine/model/version? |\n| Role and refresh acceptance "
            "records | Were the intended identity and data-lifecycle "
            "boundaries observed? |\n| Qualified performance record | "
            "Were equivalent results measured under a representative "
            "controlled workload? |\n\nThe classroom supplies the first "
            "four for offline study. Its draft save, source comparison "
            "or completion marker does not manufacture the final "
            "three. An optional PBIP/TMDL project must follow the "
            "current supported external editing contract and exclude "
            "credentials, local caches and personal settings."
        ),
        sources=[
            ("https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview"),
            "https://learn.microsoft.com/en-us/analysis-services/tmdl/tmdl-overview",
            ("https://learn.microsoft.com/en-us/fabric/security/service-admin-row-level-security"),
        ],
        practice=[
            t(
                "Reconcile the two role-specific cost rows.",
                "The allowed populations partition this clean fixture.",
                "25 +19 =44, matching the unrestricted constant-product-cost calculation.",
            ),
            t(
                "Add an unmatched principal to the acceptance matrix.",
                "Use the declared default-deny policy from the preceding security lesson.",
                (
                    "Expected Customer and Sales populations are empty under "
                    "that policy; record the corresponding BLANK measures and "
                    "real role-test requirement."
                ),
            ),
            t(
                "Produce an offline change-review packet for the grouped-cost rewrite.",
                "Bind source, model and expected contexts together.",
                (
                    "Include the exact formulas, constant-rate assumption, "
                    "missing-key/rate policy, North/South and ordinary-filter "
                    "cases, hashes, rollback plan and explicit unperformed "
                    "external checks."
                ),
            ),
            t(
                (
                    "Diagnose approving a release because the exported DAX "
                    "matches the reference text."
                ),
                "Byte equality is not engine acceptance or security validation.",
                (
                    "It proves only source identity. Actual model loading, "
                    "role enforcement, refresh and performance need their own "
                    "observed evidence."
                ),
            ),
            t(
                "Explain the acceptance impact of changing a relationship to bidirectional.",
                "That change can affect many measures and security paths.",
                (
                    "Revisit the full context/role matrix and ambiguity "
                    "analysis; do not assume a previously correct formula "
                    "retains identical behavior."
                ),
            ),
            t(
                "Describe a bounded next extension to this model.",
                "Choose one new requirement and its evidence boundary.",
                (
                    "For example, add return-event dates with an explicit "
                    "role, fixture, reconciliation and expected matrix before "
                    "attempting external model execution. Avoid importing an "
                    "unrelated platform merely to increase scope."
                ),
            ),
        ],
    ),
]

LESSONS[4]["extra"] = (
    "The supplied intervals use the Wilson score construction "
    "with\n\\(z=1.959963984540054\\) and \\(\\widehat "
    "p=k/n\\):\n\n\\[\nc=\\frac{\\widehat "
    "p+z^2/(2n)}{1+z^2/n},\\qquad\nh=\\frac{z\\sqrt{\\widehat "
    "p(1-\\widehat p)/n+z^2/(4n^2)}}{1+z^2/n}.\n\\]\n\nThe marginal "
    "bounds are \\(c-h\\) and \\(c+h\\), limited to the "
    "probability range\nfor numerical reporting. The fixture "
    "supplies the two arm-specific summaries.\nThese are not "
    "confidence limits for the treatment-control difference, "
    "and two\nunits per arm provide extremely weak evidence. A "
    "real experimental analysis\nalso needs random assignment, "
    "exposure and outcome definitions, missingness\nchecks, a "
    "declared estimand and an appropriate uncertainty "
    "procedure. DAX can\nreconcile the unit-level data without "
    "substituting for that statistical design.\n"
)

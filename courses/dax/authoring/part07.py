"Stage seven: business meaning, ties, snapshots, cohorts and compatible grains."

from .common import explain, lesson
from .common import result as r
from .common import task as t

RANKING = (
    'DEFINE\n    VAR Candidates = DATATABLE ( "Name", STRING, '
    '"Score", INTEGER,\n        { { "Alpha", 100 }, { "Beta", '
    '80 }, { "Gamma", 80 }, { "Delta", 50 } } )\n'
)

LESSONS = [
    lesson(
        37,
        "Ranking, ties and an exact-sized Top N",
        ["RANKX", "dense rank", "skip rank", "TOPN", "tie-breaker"],
        ("Specify tie behavior separately from deterministic ordering and selection size."),
        (
            "Ranking answers where a value sits within a declared "
            "comparison population. It does not inherently guarantee a "
            "unique position for every row. Equal scores can share a "
            "rank; dense ranking continues with the next distinct "
            "rank, while skip ranking leaves a gap corresponding to "
            "tied positions. Choose the policy before interpreting a "
            "leaderboard.\n\nOur literal candidate table contains "
            "100, 80, 80 and 50. Dense ranks are 1, 2, 2, 3; skip ranks are "
            "1, 2, 2, 4. A Top 2 selection based only on score can "
            "include all three rows at or above the tied cutoff. That "
            "behavior differs from selecting exactly two rows with an "
            "additional unique ordering key.\n\nA tie-breaker is a "
            "decision rule, not evidence that one tied candidate has a "
            "better score. Alphabetical Name is used only to make the "
            "tiny fixture deterministic. In an actual model, specify a "
            "meaningful, stable unique key and disclose whether a "
            "limited display excludes equally scored members. "
            "Numerical precision also matters: floating-point values "
            "that look equal after formatting may not compare as "
            "exactly equal."
        ),
        (
            "RANKX iterates Candidates and evaluates Score for its "
            "ranking distribution. DESC requests higher scores first; "
            "DENSE and SKIP choose the gap policy. TOPN's second "
            "ordering expression resolves the tie when an exact-sized "
            "set is intended. The outer ORDER BY establishes display "
            "order independently."
        ),
        [
            r(
                "Dense and skip ranks",
                (
                    'EVALUATE ADDCOLUMNS ( Candidates, "DenseRank", RANKX ( '
                    'Candidates, [Score], , DESC, DENSE ), "SkipRank", RANKX ( '
                    "Candidates, [Score], , DESC, SKIP ) )\nORDER BY [Score] "
                    "DESC, [Name] ASC"
                ),
                [
                    ("Name", "text"),
                    ("Score", "integer"),
                    ("DenseRank", "integer"),
                    ("SkipRank", "integer"),
                ],
                [
                    ["Alpha", 100, 1, 1],
                    ["Beta", 80, 2, 2],
                    ["Gamma", 80, 2, 2],
                    ["Delta", 50, 3, 4],
                ],
                (
                    "Query-local candidate fixture; descending score; four "
                    "unique names and one score tie."
                ),
                [
                    "Alpha has the only score 100 and rank 1.",
                    "Beta and Gamma share score 80 and rank 2.",
                    "Delta follows the tie at dense rank 3 or skip rank 4.",
                ],
                (
                    "The shared ranks are intentional. Displaying Beta before "
                    "Gamma does not make its dense rank smaller."
                ),
            ),
            r(
                "Tied cutoff versus a deliberate tie-breaker",
                (
                    'EVALUATE ROW ( "TopTwoByScoreRows", COUNTROWS ( TOPN ( 2, '
                    "Candidates, [Score], DESC ) ), "
                    '"TopTwoWithTieBreakerRows", COUNTROWS ( TOPN ( 2, '
                    "Candidates, [Score], DESC, [Name], ASC ) ) )"
                ),
                [("TopTwoByScoreRows", "integer"), ("TopTwoWithTieBreakerRows", "integer")],
                [[3, 2]],
                (
                    "Same candidate table; compare score-only selection with "
                    "score plus unique Name ordering."
                ),
                [
                    "The second score position is 80 and two candidates share it.",
                    "Score-only TOPN includes Alpha, Beta and Gamma.",
                    "Adding Name as a tie-breaker selects Alpha and Beta exactly.",
                ],
                (
                    "A user-facing Top N specification must say whether ties "
                    "are all included or resolved by a secondary key."
                ),
            ),
        ],
        [
            t(
                "Predict both ranks if Gamma's score becomes 79.",
                "There is no longer a tie at 80.",
                "Alpha, Beta, Gamma, Delta rank 1, 2, 3, 4 under both policies.",
            ),
            t(
                "Change the cutoff from 2 to 1.",
                "Only one candidate has the highest score.",
                "Both selection expressions return Alpha alone.",
            ),
            t(
                "Write a ranking specification including its comparison population.",
                "A region-specific rank and a global rank are different questions.",
                (
                    "State eligible candidates, score definition, "
                    "filter-removal policy, order, tie handling and unique "
                    "display key."
                ),
            ),
            t(
                "Diagnose formatting two unequal decimals to the same displayed score.",
                "Formatting does not necessarily change the stored numeric values.",
                (
                    "Decide whether rounded scores should define ties; if so, "
                    "round the ranking expression deliberately rather than "
                    "relying on display formatting."
                ),
            ),
            t(
                "Explain a blank score's policy.",
                "RANKX has documented blank treatment; business eligibility can still differ.",
                (
                    "Decide whether blank-scored candidates belong in the "
                    "ranking population and filter them explicitly if they do "
                    "not."
                ),
            ),
            t(
                ("Transfer the distinction to selecting customers for a limited-capacity program."),
                "An exact capacity requires a disclosed tie-break rule.",
                (
                    "Do not claim that a deterministic secondary key creates a "
                    "substantive difference between equally scored candidates."
                ),
            ),
        ],
        defines=RANKING,
        sources=[
            "https://learn.microsoft.com/en-us/dax/rankx-function-dax",
            "https://learn.microsoft.com/en-us/dax/topn-function-dax",
        ],
    ),
    lesson(
        38,
        "Window positions, ordering and row identity",
        ["WINDOW", "INDEX", "OFFSET", "ORDERBY", "absolute versus relative"],
        (
            "Distinguish a positional row window from a calendar "
            "interval and identify the ordering contract."
        ),
        (
            "A positional window selects rows according to an ordering "
            "and partition definition. Two rows do not automatically "
            "mean two days: our first two sales lines share the same "
            "order date. A calendar window answers a date-membership "
            "question, while a positional window answers a "
            "row-location question. Choose the mechanism that matches "
            "the requested unit.\n\nWINDOW can describe absolute bounds "
            "from the start or end of a relation, or relative bounds "
            "around a current row. INDEX selects a particular "
            "position; OFFSET selects a position relative to the "
            "current row. Relative forms need an unambiguous "
            "current-row match. ORDERBY, PARTITIONBY and MATCHBY "
            "describe different aspects of that contract and should "
            "not be treated as decorative options.\n\nThe worked queries "
            "use absolute bounds with an explicit relation and unique "
            "SaleID ordering, avoiding hidden visual-axis assumptions. "
            "This keeps the first and last two rows inspectable. A "
            "running comparison over real dates should order by a date "
            "plus a unique tie-breaker, and a customer-specific window "
            "should state its partition. Do not rely on an "
            "engine-selected extra ordering column without reviewing "
            "what it means."
        ),
        (
            "ABS makes the bounds positions within the explicitly "
            "supplied relation. Positive positions count from the "
            "start; negative positions count from the end. ALL "
            "supplies the SaleID/NetAmount relation for the named "
            "whole-model example. ORDERBY defines its order and the "
            "outer ORDER BY defines the returned table's display."
        ),
        [
            r(
                "First two positions",
                (
                    "EVALUATE SELECTCOLUMNS ( WINDOW ( 1, ABS, 2, ABS, ALL ( "
                    "Sales[SaleID], Sales[NetAmount] ), ORDERBY ( "
                    'Sales[SaleID], ASC ) ), "Line", Sales[SaleID], "Amount", '
                    "Sales[NetAmount] )\nORDER BY [Line]"
                ),
                [("Line", "text"), ("Amount", "number")],
                [["S1", 20], ["S2", 4]],
                (
                    "Whole clean-model Sales relation ordered by unique "
                    "SaleID; absolute positions 1 through 2."
                ),
                [
                    "The first two keys are S1 and S2.",
                    "Both rows belong to order 101 and date 2024-01-02.",
                    "The window contains two lines, not two distinct dates; amounts are 20 and 4.",
                ],
                (
                    "A two-row average here would average order lines. It "
                    "would not represent average revenue for two calendar days."
                ),
            ),
            r(
                "Last two positions",
                (
                    "EVALUATE SELECTCOLUMNS ( WINDOW ( -2, ABS, -1, ABS, ALL ( "
                    "Sales[SaleID], Sales[NetAmount] ), ORDERBY ( "
                    'Sales[SaleID], ASC ) ), "Line", Sales[SaleID], "Amount", '
                    "Sales[NetAmount] )\nORDER BY [Line]"
                ),
                [("Line", "text"), ("Amount", "number")],
                [["S7", 20], ["S8", 36]],
                "Same explicit relation and ordering; last two absolute positions.",
                [
                    "Position -1 identifies S8; position -2 identifies S7.",
                    "The inclusive window includes both rows.",
                    "Their amounts total 56, but the relation contract remains line-based.",
                ],
                (
                    "The result happens to align with two successive sale "
                    "dates. That coincidence does not make the operator a "
                    "date-window function."
                ),
            ),
        ],
        [
            t(
                "Identify the first position that INDEX(1,...) would select in this relation.",
                "Reuse exactly the same relation and ordering.",
                "It selects S1; a different order or partition can change the result.",
            ),
            t(
                "Describe OFFSET(-1,...) from a current row matched to S4.",
                "The preceding SaleID in this declared order is S3.",
                (
                    "It would refer to S3 with amount 40, provided the "
                    "current-row matching contract is explicit and valid."
                ),
            ),
            t(
                "Specify a per-customer chronological ordering.",
                "Separate partition membership from within-partition order.",
                (
                    "Partition by CustomerKey and order by OrderDate plus a "
                    "unique SaleID tie-breaker; define how the current row is "
                    "matched."
                ),
            ),
            t(
                "Diagnose ordering only by NetAmount for a relative previous-row comparison.",
                "Several lines share amount 20.",
                (
                    "Without a deliberate identity/tie policy, 'previous' is "
                    "ambiguous for the business question even if an engine can "
                    "extend the order."
                ),
            ),
            t(
                "Explain a boundary row with no previous member.",
                "The requested relative position can lie outside the partition.",
                (
                    "Treat the missing comparison explicitly rather than "
                    "assuming a fabricated zero-valued previous row."
                ),
            ),
            t(
                "Transfer the distinction to the last three measurements of a sensor.",
                "Three observations can span unequal elapsed time.",
                (
                    "A three-row window is appropriate only if observation "
                    "count is the intended unit; use a time interval for "
                    "elapsed-time questions."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/window-function-dax",
            "https://learn.microsoft.com/en-us/dax/index-function-dax",
            "https://learn.microsoft.com/en-us/dax/offset-function-dax",
        ],
    ),
    lesson(
        39,
        "Inventory balances are semi-additive",
        ["snapshot", "semi-additive", "closing balance", "last known", "staleness"],
        ("Choose a time aggregation that matches a balance rather than summing repeated states."),
        (
            "Inventory snapshots record a state at a date. Summing "
            "different products at the same snapshot can be "
            "meaningful; summing the same stock across several dates "
            "usually counts repeated states. This is semi-additive "
            "behavior: additivity depends on the dimension over which "
            "aggregation occurs.\n\nThe analytical fixture totals 35 "
            "units at January 31 and 30 at February 28. Adding all six "
            "snapshot rows gives 65, which is not the ending "
            "inventory. A closing balance at the last selected "
            "snapshot is 30. If the question asks for average stock "
            "instead, it needs a stated time-weighting rule; the sum "
            "65 divided by an arbitrary row count does not "
            "automatically provide that rule.\n\nA last-known-value "
            "policy is another choice, not a new observation. At "
            "February 15 the latest available snapshots are January "
            "31. Carrying Notebook 10 and Mug 5 forward gives 15 for "
            "those two products under an explicit "
            "hold-between-observations assumption. That is not proof "
            "their physical stock stayed unchanged. State a staleness "
            "limit and report missing or too-old values rather than "
            "silently carrying them indefinitely."
        ),
        (
            "Case A compares a sum over two snapshot dates with the "
            "balance at the last selected Date. Case B finds a last "
            "eligible Inventory date for each selected product before "
            "an as-of cutoff, then retrieves that product's balance. "
            "Product context must remain while Date filters are "
            "changed."
        ),
        [
            r(
                "Two states are not one closing balance",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "SummedSnapshots", SUM ( '
                    'Inventory[Units] ), "ClosingUnits", CALCULATE ( SUM ( '
                    "Inventory[Units] ), LASTDATE ( 'Date'[Date] ) ) ), "
                    "'Date'[Year] = 2025, 'Date'[MonthNumber] IN { 1, 2 } )"
                ),
                [("SummedSnapshots", "integer"), ("ClosingUnits", "integer")],
                [[65, 30]],
                (
                    "Analytics model; January and February 2025; all products; "
                    "complete snapshots on January 31 and February 28."
                ),
                [
                    "January 31 has 10 + 20 + 5 = 35 units.",
                    "February 28 has 8 + 15 + 7 = 30 units.",
                    "All snapshot rows sum to 65; the closing selected-date balance is 30.",
                ],
                (
                    "The incorrect sum can still be useful as an intermediate "
                    "check, but it must not be labeled inventory on hand at "
                    "period end."
                ),
            ),
            r(
                "An explicitly carried-forward subset",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "CarriedUnits", SUMX ( '
                    "VALUES ( Product[ProductKey] ), VAR Cutoff = DATE ( 2025, "
                    "2, 15 ) VAR LastKnown = CALCULATE ( MAX ( "
                    "Inventory[SnapshotDate] ), REMOVEFILTERS ( 'Date' ), "
                    "Inventory[SnapshotDate] <= Cutoff ) RETURN CALCULATE ( "
                    "SUM ( Inventory[Units] ), REMOVEFILTERS ( 'Date' ), "
                    "Inventory[SnapshotDate] = LastKnown ) ) ), "
                    "Product[ProductKey] IN { 1, 3 } )"
                ),
                [("CarriedUnits", "integer")],
                [[15]],
                (
                    "Notebook and Mug only; as-of February 15; carry the last "
                    "eligible snapshot under an explicit policy."
                ),
                [
                    (
                        "For each selected product, the last snapshot not after "
                        "February 15 is January 31."
                    ),
                    "Notebook has 10 and Mug has 5 at that snapshot.",
                    "The policy-derived carried total is 15, with 15 days of staleness.",
                ],
                (
                    "This is a model-based as-of estimate, not a measured "
                    "February 15 snapshot. Real systems may require stricter "
                    "freshness or complete change-event accounting."
                ),
            ),
        ],
        [
            t(
                "Predict the closing balance for Notebook and Mug at February 28.",
                "Use their latest observed snapshot values.",
                (
                    "It is 8 + 7 = 15, coincidentally equal to the earlier "
                    "carried subset for different reasons."
                ),
            ),
            t(
                "Remove Mug's February snapshot conceptually.",
                "Compare a shared last-date policy with per-product last-known selection.",
                (
                    "A shared February 28 date can omit Mug, while per-product "
                    "carry-forward would use January 31's5. The policies must "
                    "be named separately."
                ),
            ),
            t(
                "Write a staleness acceptance rule for carried balances.",
                "Include cutoff minus the chosen snapshot date.",
                (
                    "For example, retain a balance only if its age is at most "
                    "a declared number of days; otherwise return BLANK and a "
                    "missing/stale indicator."
                ),
            ),
            t(
                (
                    "Diagnose dividing 65 by six rows and calling it average "
                    "inventory over two months."
                ),
                "Rows count product snapshots, not elapsed time.",
                (
                    "The result mixes product and temporal weighting. Define "
                    "whether the desired average is across products, "
                    "observation dates or time intervals."
                ),
            ),
            t(
                "Explain a product with no snapshot before the cutoff.",
                "No observed state can be selected under this policy.",
                (
                    "Return an explicit unavailable result; do not invent a "
                    "zero or use a later snapshot that leaks future "
                    "information."
                ),
            ),
            t(
                "Transfer semi-additivity to account balances.",
                "A balance is a state, while transactions are flows.",
                (
                    "Sum compatible accounts at a date, but use "
                    "closing/average-balance rules over time rather than "
                    "summing repeated states."
                ),
            ),
        ],
        model="analytics",
        sources=[
            "https://learn.microsoft.com/en-us/dax/lastdate-function-dax",
            "https://learn.microsoft.com/en-us/dax/lastnonblank-function-dax",
        ],
    ),
    lesson(
        40,
        "Cohorts, retention denominators and unobserved ages",
        ["cohort", "retention", "eligibility", "observation age", "censoring"],
        "Separate enrolled members, active members and unavailable follow-up periods.",
        (
            "A cohort groups units by an entry event or date. "
            "Retention compares later activity with a specified "
            "eligible cohort population. It is not automatically a "
            "count of events divided by another event count. Repeated "
            "activity must not turn one member into several retained "
            "units, and inactive but eligible members must not "
            "disappear from the denominator.\n\nCohortMember contains "
            "two January entrants and two February entrants. January "
            "members 100 and 200 are both active at entry; only 100 is "
            "active in February, so one-month retention is 1/2. In the "
            "February cohort, only 300 is active at entry while 400 is "
            "not, giving entry-month activity 1/2 under the "
            "full-enrollment denominator.\n\nMarch is beyond the "
            "available activity window in this fixture. February's "
            "month-one retention is therefore unavailable, not zero. A "
            "cohort matrix that fills those future cells with zero can "
            "falsely imply that newer cohorts perform worse. Define "
            "calendar month versus elapsed-day age, eligibility and "
            "observation coverage separately before comparing cohorts."
        ),
        (
            "The CohortMember-to-Activity relationship restricts the "
            "activity fact to the selected cohort. DISTINCTCOUNT "
            "counts active member identities, not activity rows. A "
            "declared LastObservedMonth guards an unavailable future "
            "result. The examples use literal month keys; do not "
            "implement month arithmetic by adding one to a YYYYMM "
            "integer across December."
        ),
        [
            r(
                "January cohort at one-month age",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "EligibleMembers", '
                    'COUNTROWS ( CohortMember ), "ActiveAtEntry", CALCULATE ( '
                    "DISTINCTCOUNT ( Activity[MemberKey] ), Activity[MonthKey] "
                    '= 202501 ), "ActiveAtAgeOne", CALCULATE ( DISTINCTCOUNT ( '
                    "Activity[MemberKey] ), Activity[MonthKey] = 202502 ), "
                    '"RetentionAtAgeOne", DIVIDE ( CALCULATE ( DISTINCTCOUNT ( '
                    "Activity[MemberKey] ), Activity[MonthKey] = 202502 ), "
                    "COUNTROWS ( CohortMember ) ) ), CohortMember[CohortMonth] "
                    "= 202501 )"
                ),
                [
                    ("EligibleMembers", "integer"),
                    ("ActiveAtEntry", "integer"),
                    ("ActiveAtAgeOne", "integer"),
                    ("RetentionAtAgeOne", "number"),
                ],
                [[2, 2, 1, 0.5]],
                (
                    "Analytics cohort population; January entrants 100/200; "
                    "activity observed through February 2025."
                ),
                [
                    "Both January members remain in the eligible denominator.",
                    "Both are active in January, but only 100 is active in February.",
                    (
                        "One-month retention is 1/2, regardless of how many events "
                        "member 100 generated."
                    ),
                ],
                (
                    "This denominator is the entry cohort, not the subset "
                    "observed active in a later month. Filtering to active "
                    "members before counting eligibility would inflate "
                    "retention."
                ),
            ),
            r(
                "A newer cohort has unavailable follow-up",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "EligibleMembers", '
                    'COUNTROWS ( CohortMember ), "ActiveAtEntry", CALCULATE ( '
                    "DISTINCTCOUNT ( Activity[MemberKey] ), Activity[MonthKey] "
                    '= 202502 ), "EntryActivityRate", DIVIDE ( CALCULATE ( '
                    "DISTINCTCOUNT ( Activity[MemberKey] ), Activity[MonthKey] "
                    "= 202502 ), COUNTROWS ( CohortMember ) ), "
                    '"RetentionAtAgeOne", IF ( 202503 > LastObservedMonth, '
                    "BLANK(), DIVIDE ( CALCULATE ( DISTINCTCOUNT ( "
                    "Activity[MemberKey] ), Activity[MonthKey] = 202503 ), "
                    "COUNTROWS ( CohortMember ) ) ) ), "
                    "CohortMember[CohortMonth] = 202502 )"
                ),
                [
                    ("EligibleMembers", "integer"),
                    ("ActiveAtEntry", "integer"),
                    ("EntryActivityRate", "number"),
                    ("RetentionAtAgeOne", "number"),
                ],
                [[2, 1, 0.5, None]],
                (
                    "February entrants 300/400; March follow-up is outside the "
                    "declared observed months."
                ),
                [
                    "Both members are enrolled, but only 300 has February activity.",
                    "Entry activity is 1/2.",
                    (
                        "Month-one retention asks about March, so the coverage "
                        "guard returns BLANK rather than an invented zero."
                    ),
                ],
                (
                    "The two 50-percent values in the lesson have different "
                    "ages and meanings. A matrix must expose both cohort month "
                    "and observation age."
                ),
            ),
        ],
        defines="DEFINE\n    VAR LastObservedMonth = 202502\n",
        model="analytics",
        sources=[
            "https://learn.microsoft.com/en-us/dax/distinctcount-function-dax",
            "https://learn.microsoft.com/en-us/dax/edate-function-dax",
        ],
        practice=[
            t(
                "Predict January retention if member 100 has three February events.",
                "Count retained identities, not event rows.",
                "Retention stays 1/2. An event-count numerator would incorrectly inflate it.",
            ),
            t(
                "Add a February event for member 200.",
                "The January eligible population is unchanged.",
                "Both January members would be active at age one, so retention becomes 1.",
            ),
            t(
                "Write a cohort metric contract.",
                "State entry rule, eligible denominator, activity criterion and observed age.",
                (
                    "For this fixture: enrolled members by signup month, any "
                    "observed activity in the target calendar month, distinct "
                    "member count, full enrollment denominator and a coverage "
                    "guard."
                ),
            ),
            t(
                (
                    "Diagnose dropping inactive member 400 before calculating "
                    "the February entry rate."
                ),
                "The denominator would become conditional on the outcome.",
                "It would turn 1/2 into 1/1 and conceal inactive eligible members.",
            ),
            t(
                "Explain why 202512 + 1 is not a valid next-month calculation.",
                "YYYYMM is a label, not a continuous month counter.",
                (
                    "It gives 202513. Use a date-aware calendar mapping or "
                    "EDATE with explicit period membership."
                ),
            ),
            t(
                "Transfer the coverage rule to survival follow-up.",
                "Incomplete follow-up is not automatically a failure event.",
                (
                    "Retain observation time and censoring status; choose an "
                    "estimator matching those assumptions rather than "
                    "zero-filling future outcomes."
                ),
            ),
        ],
    ),
    lesson(
        41,
        "Budget comparisons require compatible grains",
        ["monthly budget", "grain mismatch", "TREATAS", "full-period guard", "allocation"],
        (
            "Align actuals with a monthly category budget without "
            "copying a whole-month target into a daily metric."
        ),
        (
            "Budget is recorded at month/category grain, while Sales "
            "is recorded at order-line grain. A daily product-level "
            "query does not automatically have a comparable target. "
            "Relating a monthly budget to an arbitrary date key can "
            "make it appear only on one day; copying the entire "
            "monthly value into every day can multiply it. The model "
            "must state the intended temporal and category "
            "mapping.\n\nThe analytical fixture leaves Budget "
            "disconnected and transfers selected MonthKey and Category "
            "values explicitly with TREATAS. For January Paper, actual "
            "revenue is 47 and budget is 60, so the variance is -13. "
            "The reference permits that comparison only when the "
            "selected Date population is the complete single calendar "
            "month.\n\nOn January 2 alone, actual Paper revenue is 27. "
            "The monthly budget 60 is not a daily target, so the "
            "guarded measure returns BLANK rather than an invented "
            "variance. A genuine daily allocation needs an explicit "
            "weighting policy whose allocated values reconcile to the "
            "original monthly amount. Uniform, working-day and "
            "forecast-weighted allocation are different business "
            "choices."
        ),
        (
            "HASONEVALUE and the date-row count form this fixture's "
            "single-complete-month guard. DAY(EOMONTH(...)) gives the "
            "calendar month length. TREATAS maps the retained month "
            "and category sets to the disconnected Budget columns. The "
            "guard is a documented comparison policy, not a universal "
            "pattern for every fiscal calendar."
        ),
        [
            r(
                "A comparable full-month category",
                (
                    "EVALUATE CALCULATETABLE ( VAR FullMonth = HASONEVALUE ( "
                    "'Date'[MonthKey] ) && COUNTROWS ( VALUES ( 'Date'[Date] ) "
                    ") = DAY ( EOMONTH ( MAX ( 'Date'[Date] ), 0 ) ) VAR "
                    "Target = IF ( FullMonth, CALCULATE ( SUM ( Budget[Amount] "
                    "), TREATAS ( VALUES ( 'Date'[MonthKey] ), "
                    "Budget[MonthKey] ), TREATAS ( VALUES ( Product[Category] "
                    '), Budget[Category] ) ) ) RETURN ROW ( "Actual", '
                    '[NetRevenue], "ComparableBudget", Target, "Variance", IF '
                    "( NOT ISBLANK ( Target ), [NetRevenue] - Target ) ), "
                    "'Date'[Year] = 2025, 'Date'[MonthNumber] = 1, "
                    'Product[Category] = "Paper" )'
                ),
                [("Actual", "number"), ("ComparableBudget", "number"), ("Variance", "number")],
                [[47, 60, -13]],
                (
                    "FullJanuary 2025 and Paper category; Budget is "
                    "monthly/category-grained and disconnected."
                ),
                [
                    "January has 31 selected dates, satisfying the complete single-month guard.",
                    "Paper actuals are S4 and S5: 27 + 20 = 47.",
                    "The mapped budget is 60, so actual minus budget is -13.",
                ],
                (
                    "The sign convention is part of the metric: here negative "
                    "means below the revenue target, not necessarily a generic "
                    "unfavorable variance for every account type."
                ),
            ),
            r(
                "A daily selection is not assigned the monthly target",
                (
                    "EVALUATE CALCULATETABLE ( VAR FullMonth = HASONEVALUE ( "
                    "'Date'[MonthKey] ) && COUNTROWS ( VALUES ( 'Date'[Date] ) "
                    ") = DAY ( EOMONTH ( MAX ( 'Date'[Date] ), 0 ) ) VAR "
                    "Target = IF ( FullMonth, CALCULATE ( SUM ( Budget[Amount] "
                    "), TREATAS ( VALUES ( 'Date'[MonthKey] ), "
                    "Budget[MonthKey] ), TREATAS ( VALUES ( Product[Category] "
                    '), Budget[Category] ) ) ) RETURN ROW ( "Actual", '
                    "[NetRevenue], \"ComparableBudget\", Target ), 'Date'[Date] "
                    '= DATE ( 2025, 1, 2 ), Product[Category] = "Paper" )'
                ),
                [("Actual", "number"), ("ComparableBudget", "number")],
                [[27, None]],
                "One observed day in January 2025; no daily budget allocation policy exists.",
                [
                    "The selected date count is 1 rather than January's31.",
                    "Actual revenue on the day is 27.",
                    (
                        "The guard refuses to present the whole-month 60 as a "
                        "comparable daily budget."
                    ),
                ],
                (
                    "BLANK protects an undefined comparison. If a daily target "
                    "is required, add and explain an allocation policy rather "
                    "than removing the guard without replacement."
                ),
            ),
        ],
        model="analytics",
        sources=[
            "https://learn.microsoft.com/en-us/dax/treatas-function-dax",
            "https://learn.microsoft.com/en-us/dax/hasonevalue-function-dax",
            "https://learn.microsoft.com/en-us/dax/eomonth-function-dax",
        ],
        practice=[
            t(
                "Predict February Home actual and budget.",
                "Use S8 and the matching monthly budget row.",
                "Actual 36, budget 50 and variance -14.",
            ),
            t(
                "Combine both January categories.",
                "Add compatible monthly targets and actuals once each.",
                "Actual 67, budget 90 and variance -23.",
            ),
            t(
                "Specify a uniform daily allocation for January Paper.",
                "Allocated daily weights must sum to one over the intended month.",
                (
                    "Each of 31 calendar days receives 60/31; the "
                    "complete-month allocation reconciles to 60. This is a "
                    "chosen policy, not an observed daily target."
                ),
            ),
            t(
                "Diagnose attaching 60 to every January sales line then summing.",
                "The monthly budget is being repeated at a lower grain.",
                (
                    "The result depends on transaction count and overstates "
                    "the budget. Aggregate or allocate at a compatible grain."
                ),
            ),
            t(
                "Explain a missing category-budget row.",
                "Missing target is not necessarily a zero target.",
                (
                    "Keep an unavailable-budget signal or a declared "
                    "exclusion; do not invent a variance by silently "
                    "coalescing the target to zero."
                ),
            ),
            t(
                "Transfer the rule to headcount plans and employee events.",
                "Plans and events often have different time and organizational grains.",
                (
                    "Define comparable populations and allocation before "
                    "joining or summing them, and reconcile the allocated "
                    "total to the plan."
                ),
            ),
        ],
    ),
    lesson(
        42,
        "Currency conversion belongs at the rate's grain",
        ["exchange rate", "LOOKUPVALUE", "currency unit", "rate date", "quality gate"],
        (
            "Convert compatible transactions before aggregation and "
            "diagnose a misleading latest-rate shortcut."
        ),
        (
            "Amounts in different currencies cannot be added into a "
            "meaningful monetary total without a conversion policy. "
            "The ordinary retail Sales table is already USD; this "
            "lesson instead uses the separate ForeignSales fixture. "
            "Its LocalAmount must be paired with Currency and SaleDate "
            "before selecting the rate expressed as USD per local "
            "currency unit.\n\nA January 100 EUR transaction at 1.1 "
            "USD/EUR converts to 110 USD; a February 50 EUR "
            "transaction at 1.2 converts to 60 USD. Their correct "
            "combined USD amount is 170. Multiplying the local EUR sum "
            "150 by the latest rate 1.2 gives 180, which applies the "
            "wrong temporal rate to the earlier transaction.\n\nThe rate "
            "table's uniqueness and completeness are prerequisites. "
            "LOOKUPVALUE over date and currency can retrieve the "
            "matching scalar in this tiny fixture, but missing or "
            "ambiguous matches require diagnosis. A BLANK rate must "
            "not silently make an unconverted transaction disappear "
            "from SUMX. In a larger project, validate rate coverage "
            "and the chosen accounting convention before publishing "
            "any converted total."
        ),
        (
            "SUMX supplies each ForeignSales row's amount, date and "
            "currency. LOOKUPVALUE matches both rate-key columns. The "
            "second case intentionally computes a wrong latest-rate "
            "comparison under an EUR-only selection and exposes the "
            "exact ten-USD discrepancy derived below. Keep that "
            "arithmetic explicit rather than relying on a reassuring "
            "formatted total."
        ),
        [
            r(
                "Convert each transaction before adding",
                (
                    'EVALUATE ROW ( "ConvertedUSD", SUMX ( ForeignSales, '
                    "ForeignSales[LocalAmount] * LOOKUPVALUE ( "
                    "ExchangeRate[USDPerUnit], ExchangeRate[RateDate], "
                    "ForeignSales[SaleDate], ExchangeRate[Currency], "
                    "ForeignSales[Currency] ) ) )"
                ),
                [("ConvertedUSD", "number")],
                [[270]],
                (
                    "Analytics model; three ForeignSales rows; each "
                    "date/currency rate key exists exactly once."
                ),
                [
                    "F1 is 100 USD at rate 1, contributing 100 USD.",
                    (
                        "F2 is 100 EUR at 1.1, contributing 110 USD; F3 is 50 EUR "
                        "at 1.2, contributing 60 USD."
                    ),
                    "The compatible converted amounts sum to 270 USD.",
                ],
                (
                    "The raw local sum 250 mixes USD and EUR and is not itself "
                    "a legitimate currency total."
                ),
            ),
            r(
                "A latest-rate shortcut changes the policy",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "LocalEUR", SUM ( '
                    'ForeignSales[LocalAmount] ), "CorrectUSD", SUMX ( '
                    "ForeignSales, ForeignSales[LocalAmount] * LOOKUPVALUE ( "
                    "ExchangeRate[USDPerUnit], ExchangeRate[RateDate], "
                    "ForeignSales[SaleDate], ExchangeRate[Currency], "
                    'ForeignSales[Currency] ) ), "NaiveLatestRateUSD", SUM ( '
                    "ForeignSales[LocalAmount] ) * MAXX ( FILTER ( "
                    'ExchangeRate, ExchangeRate[Currency] = "EUR" ), '
                    "ExchangeRate[USDPerUnit] ) ), ForeignSales[Currency] = "
                    '"EUR" )'
                ),
                [
                    ("LocalEUR", "number"),
                    ("CorrectUSD", "number"),
                    ("NaiveLatestRateUSD", "number"),
                ],
                [[150, 170, 180]],
                (
                    "EUR-only transactions; contrast transaction-date rates "
                    "with one selected maximum rate in this tiny "
                    "increasing-rate fixture."
                ),
                [
                    "The local EUR amounts sum to 150.",
                    "Transaction-date conversion gives 110 + 60 = 170 USD.",
                    "Multiplying 150 by 1.2 gives 180 USD, ten more than the stated policy.",
                ],
                (
                    "MAX rate happens to equal the latest rate in this "
                    "fixture. A real latest-date policy must select by date, "
                    "not assume rates increase monotonically."
                ),
            ),
        ],
        model="analytics",
        sources=[
            "https://learn.microsoft.com/en-us/dax/lookupvalue-function-dax",
            "https://learn.microsoft.com/en-us/dax/sumx-function-dax",
        ],
        practice=[
            t(
                "Predict the converted amount for F 3 alone.",
                "Use its February date and EUR currency key.",
                "50 times 1.2 gives 60 USD.",
            ),
            t(
                "Change the FebruaryEUR rate to 1.0.",
                "The maximum rate would no longer be the latest rate.",
                (
                    "Correct EUR conversion becomes 110 + 50 = 160 USD. A "
                    "MAX-rate shortcut would use 1.1 and still be wrong."
                ),
            ),
            t(
                "Write a rate-coverage quality rule.",
                "Each transaction needs exactly one compatible rate under the chosen policy.",
                (
                    "Reject or flag missing and duplicate date/currency "
                    "matches before conversion; publish no apparently complete "
                    "total while transactions are unconverted."
                ),
            ),
            t(
                "Diagnose substituting zero when a rate is missing.",
                "Zero conversion makes recorded value disappear.",
                (
                    "It understates the total and hides missing data. Keep an "
                    "unavailable result and an explicit count of affected "
                    "transactions."
                ),
            ),
            t(
                "Explain whether dividing by the rate would be correct.",
                "Read the rate's unit, USD per EUR.",
                (
                    "For EUR to USD multiply by USD/EUR; dividing implements a "
                    "different direction. Reciprocal conventions must be "
                    "labeled."
                ),
            ),
            t(
                "Transfer the grain rule to tax rates or indexed prices.",
                "A rate can depend on jurisdiction, date and transaction type.",
                (
                    "Match the complete rate key and effective interval before "
                    "aggregation, and test missing or overlapping validity "
                    "periods."
                ),
            ),
        ],
    ),
]

# Absolute position and relative-row cases complete the ordering comparison.
LESSONS[1]["cases"].extend(
    [
        r(
            "INDEX chooses one absolute position",
            (
                "EVALUATE INDEX ( 1, ALL ( Sales[SaleID], Sales[NetAmount] "
                "), ORDERBY ( Sales[SaleID], ASC ) )"
            ),
            [("SaleID", "text"), ("NetAmount", "number")],
            [["S1", 20]],
            ("One unpartitioned relation ordered by the unique SaleID; no outer row required."),
            [
                "ALL exposes all eight line identities and amounts.",
                "The declared unique order starts with S1.",
                "Absolute position one therefore returns S1 and amount 20.",
            ],
            (
                "INDEX selects a position in the declared order. Position "
                "zero or a position beyond this eight-row relation would "
                "return an empty table."
            ),
        ),
        r(
            "OFFSET identifies a previous row",
            (
                "EVALUATE CALCULATETABLE ( OFFSET ( -1, ALL ( "
                "Sales[SaleID] ), ORDERBY ( Sales[SaleID], ASC ) ), "
                'Sales[SaleID] = "S4" )'
            ),
            [("SaleID", "text")],
            [["S3"]],
            (
                "The outer context identifies S4; the relation contains "
                "every SaleID in ascending unique order."
            ),
            [
                "The outer filter supplies exactly one current SaleID: S4.",
                ("The explicit ALL relation permits movement outside that current-row selection."),
                (
                    "Moving one position backward reaches S3; a backward move "
                    "from S1 would be empty."
                ),
            ],
            (
                "OFFSET needs an unambiguous current-row contract. Adding "
                "columns, partitions or ties can change matching "
                "requirements; specify MATCHBY where identity differs from "
                "sort columns."
            ),
        ),
    ]
)
LESSONS[1]["sources"].extend(
    [
        "https://learn.microsoft.com/en-us/dax/index-function-dax",
        "https://learn.microsoft.com/en-us/dax/offset-function-dax",
    ]
)


REASONING = {
    37: [
        (
            (
                "Without the 80 tie, the four scores 100, 80, 79 and 50 are distinct. DENSE and "
                "SKIP differ only after a tie, so both give 1, 2, 3 and 4."
            ),
            (
                "Expecting Delta to keep SkipRank 4 and DenseRank 3, as in case A. That gap came "
                "from the Beta and Gamma tie, which no longer exists."
            ),
            "With Gamma at 79 in the DATATABLE, both rank columns read 1, 2, 3, 4.",
        ),
        (
            (
                "TOPN keeps every row tied with the last selected value. At N = 1 the last value "
                "is Alpha's 100, which nobody shares, so the tie-breaker has nothing to decide."
            ),
            (
                "Concluding from case B that TOPN always returns extra rows. Ties only add rows "
                "when they fall at the cutoff, as the 80s do at N = 2."
            ),
            "Both COUNTROWS expressions return 1 at N = 1.",
        ),
        (
            (
                "State the population first. In the retail model, products ranked over "
                "ALL(Product[ProductName]) by NetRevenue give Mug 96, Notebook 67, Pen 24 and Bag "
                "BLANK. Within the Paper category, Notebook ranks first."
            ),
            (
                "Writing RANKX(ALL(Product), [NetRevenue]) for a by-category visual ranks Notebook "
                "2 globally when the reader expected 1 within Paper. The filter-removal choice is "
                "part of the spec."
            ),
            (
                "The spec lists the population, the score measure, ALL versus ALLSELECTED, DESC, "
                "the DENSE or SKIP policy and ProductName as the display key."
            ),
        ),
        (
            (
                "RANKX compares stored values. Scores such as 80.4 and 79.6 both display as 80 at "
                "zero decimals but still rank 2 and 3."
            ),
            (
                "Assuming a format string creates the tie readers see. It only changes the "
                "display, so two rows that look equal get different ranks."
            ),
            (
                "If rounded ties are intended, rank `ROUND ( [Score], 0 )`; both rows then get "
                "rank 2 under DENSE, matching the display."
            ),
        ),
        (
            (
                "A blank score is still ranked unless it is excluded. Ranked by NetRevenue over "
                "all products, Bag's BLANK sorts below every positive value and takes rank 4."
            ),
            (
                "Leaving Bag in the population and reporting four ranked products when the "
                "business population was products with sales."
            ),
            (
                "Filtering the table to products where NOT ISBLANK([NetRevenue]) leaves three "
                "ranked products, with Pen last at 3."
            ),
        ),
        (
            (
                "Capacity is exact, so the rule must break ties and say how. At two slots, Beta "
                "and Gamma tie at 80 for the second place."
            ),
            (
                "Using Name as the tie-breaker and presenting Beta as a better candidate than "
                "Gamma. Alphabetical order is a disclosed rule, not evidence of merit."
            ),
            (
                "TOPN by score alone returns 3 rows; with the Name tie-breaker it returns 2 (Alpha "
                "and Beta). The program notes should say the second slot was decided by name "
                "between equal scores."
            ),
        ),
    ],
    38: [
        (
            (
                "INDEX picks a position from the same ALL(Sales[SaleID], Sales[NetAmount]) "
                "relation and SaleID order as case A, so position 1 is S1, amount 20."
            ),
            (
                "Changing the order to NetAmount ascending without noticing: position 1 then holds "
                "S2, amount 4, because the order defines the positions."
            ),
            "The case C query returns one row, S1 with 20, matching the first row of case A.",
        ),
        (
            (
                "The outer filter identifies S4, and OFFSET looks one step back in the full "
                "ascending SaleID relation. That is S3, amount 40."
            ),
            (
                "Passing the filtered table as the relation, so the relation holds only S4. There "
                "is then no row before it and OFFSET returns an empty table."
            ),
            "Case D returns S3; add Sales[NetAmount] to the ALL list and the row shows 40.",
        ),
        (
            (
                "Partition by CustomerKey, then order by OrderDate with SaleID as the tie-breaker. "
                "Ada's lines are S1 and S2 on 2024-01-02, then S4."
            ),
            (
                "Ordering by OrderDate without a partition or tie-breaker. S1 and S2 share a date, "
                "and S4's previous row becomes Bo's S3 rather than Ada's S2."
            ),
            (
                "With PARTITIONBY(Sales[CustomerKey]) and ORDERBY(Sales[OrderDate], ASC, "
                "Sales[SaleID], ASC), OFFSET(-1) from S4 returns S2, amount 4."
            ),
        ),
        (
            (
                "NetAmount alone does not identify lines here: S1, S5, S6 and S7 all have 20, so "
                "their order relative to one another is unspecified."
            ),
            (
                "Relying on the engine to extend the order with other columns and reading the "
                "result as a business answer. The previous row for S5 could be any of the 20s."
            ),
            (
                "Ascending amounts are 4, 20, 20, 20, 20, 27, 36, 40. Adding SaleID as a "
                "tie-breaker gives S1, S5, S6, S7 for the 20s."
            ),
        ),
        (
            (
                "Each partition's first row has no previous member. In the per-customer order, "
                "Ada's S1, Bo's S3 and Cy's S5 have nothing before them."
            ),
            (
                "Coalescing the missing previous value to 0 reports S1 as a change of +20 from a "
                "sale that never existed."
            ),
            (
                "For S1, OFFSET(-1) returns an empty table, and the change measure should return "
                "BLANK while S4 returns 27 - 4 = 23."
            ),
        ),
        (
            (
                "A window of three rows counts observations, not time. Readings at 09:00, 09:01 "
                "and 12:00 are three rows spanning three hours."
            ),
            (
                'Calling WINDOW(-2, REL, 0, REL) "the last few minutes". Over sparse readings, '
                "three rows can cover minutes or days."
            ),
            (
                "For elapsed-time questions, filter timestamps to an interval such as the last 15 "
                "minutes and count the readings inside it; the three-row window and the interval "
                "can disagree."
            ),
        ),
    ],
    39: [
        (
            (
                "Inventory is a state. At February 28 the closing balance for Notebook and Mug is "
                "that date's snapshot: 8 + 7 = 15."
            ),
            (
                "Summing both month-end snapshots for the two products gives 10 + 5 + 8 + 7 = 30, "
                "which counts each product twice."
            ),
            (
                "Under 'Date'[Date] = DATE(2025, 2, 28) and ProductKey IN {1, 3}, "
                "SUM(Inventory[Units]) returns 15; case B's 15 comes from the January 31 values 10 "
                "+ 5."
            ),
        ),
        (
            (
                "Without Mug's February row, the two policies differ. A shared last date (February "
                "28) has only Notebook, while per-product carry-forward takes Mug's last known 5 "
                "from January 31."
            ),
            (
                "Using LASTDATE('Date'[Date]) or the latest snapshot across all products and "
                "calling it per-product last known. Mug silently drops out."
            ),
            (
                "The shared-date policy gives 8; per-product carry-forward gives 8 + 5 = 13. Label "
                "which one the measure implements."
            ),
        ),
        (
            (
                "A carried balance has an age: cutoff minus the snapshot used. At the February 15 "
                "cutoff, the January 31 snapshots are 15 days old."
            ),
            (
                "Carrying the last known value with no age limit, so a snapshot that is months old "
                "still shows as current stock."
            ),
            (
                "With a 31-day limit, February 15 returns 15; with a 7-day limit it returns BLANK "
                "plus a stale flag for both products."
            ),
        ),
        (
            (
                "The six rows are three products at two dates. Daily totals are 35 on January 31 "
                "and 30 on February 28."
            ),
            (
                "65 / 6, about 10.83, mixes products and dates: it is the mean per "
                "product-snapshot, not the average stock held."
            ),
            (
                "AVERAGEX(VALUES(Inventory[SnapshotDate]), CALCULATE(SUM(Inventory[Units]))) "
                "returns 32.5 units averaged over the two snapshot dates."
            ),
        ),
        (
            (
                "If the cutoff is January 15, 2025, no snapshot is on or before it, so LastKnown "
                "is BLANK and no rows match. Bag (ProductKey 4) has no snapshots at all."
            ),
            (
                "Returning 0 for these products, or using the February 28 snapshot, which reports "
                "stock not yet known on January 15."
            ),
            (
                "Case B with Cutoff set to DATE(2025, 1, 15) returns BLANK, and the report should "
                "flag the products with no available balance."
            ),
        ),
        (
            (
                "Account balances behave like inventory. If an account shows 100 on January 31 and "
                "120 on February 28, the two-month closing balance is 120."
            ),
            (
                "Summing the two month-end balances to 220, while the 20 of net transactions "
                "across February is the flow that explains the change."
            ),
            (
                "The closing balance (120) equals the opening balance (100) plus February "
                "transactions (20); balances add across accounts on one date, not across dates."
            ),
        ),
    ],
    40: [
        (
            (
                "Retention counts retained members, not events. DISTINCTCOUNT(Activity[MemberKey]) "
                "counts member 100 once however many February rows exist."
            ),
            (
                "Using COUNTROWS(Activity) for the numerator gives 3 / 2 = 1.5, a retention rate "
                "above 100 percent."
            ),
            (
                "With three February events for member 100, ActiveAtAgeOne stays 1 and "
                "RetentionAtAgeOne stays 0.5."
            ),
        ),
        (
            (
                "The denominator is the January cohort (100 and 200), fixed at entry. A February "
                "event for 200 adds to the numerator only."
            ),
            (
                "Counting the new event as a new member, or letting the denominator follow the "
                "activity, gives a ratio that is no longer defined by the cohort."
            ),
            "ActiveAtAgeOne becomes 2 with EligibleMembers still 2, so retention is 1.",
        ),
        (
            (
                "Each part of the contract has a number here: cohorts by CohortMonth (202501 for "
                "100 and 200), activity as any Activity row in the target month, a distinct member "
                "count, and observation through 202502."
            ),
            (
                "Defining the cohort by first activity instead of enrollment. A member with no "
                "activity would never enter the denominator."
            ),
            (
                "The contract reproduces case A (2 eligible, 1 active, 0.5) and case B (BLANK at "
                "age one)."
            ),
        ),
        (
            (
                "Members 300 and 400 enrolled in February. Only 300 was active, so the February "
                "entry activity rate is 1 / 2."
            ),
            (
                "Removing member 400 because it has no activity makes the rate 1 / 1. Filtering on "
                "the outcome removes the evidence it should measure."
            ),
            (
                "Case B returns EligibleMembers 2 and EntryActivityRate 0.5; "
                "COUNTROWS(CohortMember) must not depend on Activity."
            ),
        ),
        (
            (
                "MonthKey is a YYYYMM label. Adding 1 works inside a year, 202501 to 202502, but "
                "gives 202513 after December."
            ),
            (
                "Writing the next-month filter as MonthKey + 1 because it works for both cohorts "
                "here. It fails at the first year boundary."
            ),
            (
                "Derive the next month from a date: EDATE(DATE(2025, 12, 1), 1) is 2026-01-01, "
                "giving 202601 through 'Date'[MonthKey]."
            ),
        ),
        (
            (
                "Survival needs follow-up time and censoring. The February cohort has no month "
                "after entry in the observed range, so its members are censored, not lost."
            ),
            (
                "Counting members 300 and 400 as churned at age one gives 0 / 2 retention, which "
                "conflicts with case B's BLANK."
            ),
            (
                "Record each member's observed months; the February cohort contributes entry month "
                "only, and an estimator such as Kaplan-Meier uses that."
            ),
        ),
    ],
    41: [
        (
            (
                "February Home has one sale, S8 at 36, and one monthly budget row, 202502 Home 50. "
                "The full-month guard holds, so variance is 36 - 50."
            ),
            (
                "Leaving out the Category TREATAS assigns the whole February budget, 25 + 50 = 75, "
                "to Home."
            ),
            (
                "With MonthNumber 2 and Category Home, expect Actual 36, ComparableBudget 50 and "
                "Variance -14."
            ),
        ),
        (
            (
                "Without a category filter, VALUES(Product[Category]) returns every category, so "
                "TREATAS picks both January budget rows, 60 + 30. Actuals are 47 + 20."
            ),
            (
                "Averaging the category attainment ratios, 47 / 60 (0.783) and 20 / 30 (0.667), "
                "gives 0.725 instead of the combined 67 / 90, about 0.744."
            ),
            (
                "For full January 2025 without a category filter, expect Actual 67, "
                "ComparableBudget 90 and Variance -23."
            ),
        ),
        (
            (
                "A uniform policy gives each of January's 31 days 60 / 31, about 1.94, and the "
                "days add back to 60."
            ),
            (
                "Dividing by the 2 days with Paper sales (January 2 and 3) puts 30 on each, so the "
                "target depends on when sales happened."
            ),
            (
                "January 2 gets about 1.94 against an actual of 27; the 31 daily allocations sum "
                "to 60."
            ),
        ),
        (
            (
                "Budget is monthly by category. January Paper has two lines, S4 and S5, so "
                "attaching the target to each line repeats it."
            ),
            (
                "Using `SUMX ( Sales, 60 )` for January Paper gives 120, double the target, and "
                "would grow with every extra line."
            ),
            "The compatible-grain target is 60; compare it with an actual of 47.",
        ),
        (
            (
                "Travel has no budget row, and if 202502 Home were missing, February Home would "
                "have no target either."
            ),
            (
                "Coalescing a missing target to 0 turns February Home into a variance of +36 when "
                "it has no target."
            ),
            (
                "With the row removed, ComparableBudget should be BLANK and the measure should "
                "flag a missing budget rather than return 36."
            ),
        ),
        (
            (
                "Headcount plans are often by department and quarter, while hires and exits are "
                "individual events with dates. Like Budget against Sales, compare them at the "
                "plan's grain."
            ),
            (
                "Joining the quarterly plan to each hire event and summing repeats the plan per "
                "hire, just as 60 per sales line did."
            ),
            (
                "Aggregate events to department and quarter, compare with the plan, and if "
                "allocating to months, check that the months add back to the plan."
            ),
        ),
    ],
    42: [
        (
            (
                "F3 is 50 EUR on 2025-02-03, and the rate key (2025-02-03, EUR) gives 1.2 USD per "
                "EUR. 50 x 1.2 = 60."
            ),
            (
                "Using the latest January rate, 1.1, because the rate is looked up by currency "
                "only. That gives 55."
            ),
            'Filtering ForeignSales[ForeignID] = "F3" in case A\'s measure returns 60.',
        ),
        (
            (
                "Converting each row at its own date's rate gives F2 at 100 x 1.1 = 110 and F3 at "
                "50 x 1.0 = 50, so EUR converts to 160."
            ),
            (
                "The MAX-rate shortcut now takes 1.1 for all 150 EUR, giving 165, which is wrong "
                "because it ignores dates."
            ),
            (
                "After the change, CorrectUSD reads 160 and NaiveLatestRateUSD reads 165; overall "
                "ConvertedUSD becomes 100 + 160 = 260."
            ),
        ),
        (
            (
                "Every ForeignSales row needs exactly one rate for its (SaleDate, Currency). Here "
                "all three rows match one rate each."
            ),
            (
                "Checking only that the rate table has no blanks. A transaction on a date with no "
                "rate is a missing join, not a blank rate value."
            ),
            (
                "COUNTROWS(FILTER(ForeignSales, ISBLANK(LOOKUPVALUE(ExchangeRate[USDPerUnit], "
                "...)))) returns 0, and the rate table's (RateDate, Currency) key stays unique."
            ),
        ),
        (
            (
                "A missing rate means the USD value is unknown. If the 2025-02-03 EUR rate were "
                "absent, F3's 50 EUR would have no conversion."
            ),
            (
                "Coalescing the missing rate to 0 makes F3 contribute nothing, so the total drops "
                "to 210 without warning."
            ),
            (
                'Return BLANK for the total, or show 210 with "1 transaction unconverted" beside '
                "it, instead of a 210 that looks complete."
            ),
        ),
        (
            "USDPerUnit is USD per one unit of local currency, so EUR times USD/EUR gives USD.",
            (
                "Dividing instead gives 100 / 1.1 + 50 / 1.2, about 132.58 USD for the EUR rows, "
                "which treats the rate as EUR per USD."
            ),
            (
                "Unit check: EUR x (USD / EUR) = USD. Converted EUR should be 170, above 150 "
                "local, while each rate is above 1."
            ),
        ),
        (
            (
                "Tax rates and price indexes also have full keys: jurisdiction, product class and "
                "effective date range, like (RateDate, Currency) here."
            ),
            (
                "Joining by jurisdiction only and taking the latest rate repeats the MAX-rate "
                "mistake."
            ),
            (
                "For each transaction, count the matching rates: zero means missing and two means "
                "overlapping validity, and both should fail before aggregation."
            ),
        ),
    ],
}

explain(LESSONS, REASONING)

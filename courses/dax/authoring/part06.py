"""Stage six: explicit calendar sets, period completeness and date roles."""

from .common import lesson
from .common import result as r
from .common import task as t

LESSONS = [
    lesson(
        31,
        "A complete date dimension is not a list of sale dates",
        ["date table", "calendar grain", "missing dates", "mark as date table", "coverage"],
        ("Distinguish calendar coverage, observed facts and data-availability boundaries."),
        (
            "A Date dimension contains calendar members, including "
            "days with no sales. A list of distinct OrderDate values "
            "contains only days on which facts were recorded. Using "
            "the latter as a calendar confuses the absence of an event "
            "with the absence of a date, and can change time-window "
            "denominators or break classic time-intelligence "
            "assumptions.\n\nThe course Date fixture has one unique, "
            "nonblank date for every day of 2024 and 2025. The model "
            "contract marks that Date column for classic time "
            "intelligence. January 2025 therefore has 31 calendar rows "
            "even though sales occur on only January 2,3 and 5. A "
            "zero-sales day remains a date that can belong in an "
            "average or rolling interval.\n\nCalendar extent is not the "
            "same as observation completeness. This fixture declares "
            "sales observation through 2025-02-28; dates later in the "
            "calendar do not imply those periods were observed. A "
            "future blank cell should not automatically become zero "
            "demand. Track the available-data boundary separately from "
            "the maximum date in the dimension."
        ),
        (
            "Case A compares calendar dates with distinct fact dates "
            "under the same month selection. Case B looks at a known "
            "observed date with no sale. The date row exists and the "
            "fact result is empty. A complete Date table is a model "
            "requirement, not a claim that every day has an event."
        ),
        [
            r(
                "January calendar versus event dates",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "CalendarDates", '
                    "COUNTROWS ( 'Date' ), \"OrderDatesWithSales\", "
                    "DISTINCTCOUNT ( Sales[OrderDate] ) ), 'Date'[Year] = "
                    "2025, 'Date'[MonthNumber] = 1 )"
                ),
                [("CalendarDates", "integer"), ("OrderDatesWithSales", "integer")],
                [[31, 3]],
                (
                    "January 2025, active OrderDate relationship; observed "
                    "coverage includes the full month."
                ),
                [
                    "The complete Date table contains January 1 through 31.",
                    "Sales occur on January 2,3 and 5.",
                    "The calendar count is 31 while observed event-date count is 3.",
                ],
                (
                    "A sales-day average and a calendar-day average use "
                    "different denominators. Neither should be called a "
                    "generic daily average without that qualification."
                ),
            ),
            r(
                "A date exists without a sale",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "CalendarDates", '
                    "COUNTROWS ( 'Date' ), \"SalesRows\", COUNTROWS ( Sales ), "
                    "\"Revenue\", [NetRevenue] ), 'Date'[Date] = DATE ( 2025, 1, "
                    "4 ) )"
                ),
                [("CalendarDates", "integer"), ("SalesRows", "integer"), ("Revenue", "number")],
                [[1, None, None]],
                ("2025-01-04 is inside declared observation coverage but has no OrderDate fact."),
                [
                    "The Date selection contains one valid date.",
                    "No Sales row has OrderDate 2025-01-04.",
                    "The fact count and revenue are BLANK; the calendar row is not missing.",
                ],
                (
                    "If this were beyond observation coverage, the same blank "
                    "visual appearance would need a different interpretation. "
                    "Availability metadata prevents that ambiguity."
                ),
            ),
        ],
        [
            t(
                "Predict the number of Date rows in February 2024.",
                "The fixture includes a leap year.",
                "There are 29 unique calendar dates.",
            ),
            t(
                "Change case B to January 2,2025.",
                "One sale was ordered that day.",
                "CalendarDates is 1, SalesRows is 1 and Revenue is 27.",
            ),
            t(
                "Write a date-table quality checklist.",
                "Separate uniqueness, completeness, type and extent.",
                (
                    "Check one row per date, no blanks or gaps in the required "
                    "classic calendar, correct date type, explicit coverage "
                    "and the intended active fact relationship."
                ),
            ),
            t(
                "Diagnose using MAX(Date[Date]) as the latest observed sales date.",
                "The dimension extends through December 2025.",
                (
                    "It is a calendar extent, not an observation watermark. "
                    "Use a declared availability boundary or the appropriate "
                    "fact-date contract."
                ),
            ),
            t(
                (
                    "Explain why filling every future blank with zero can "
                    "distort a forecast baseline."
                ),
                "Future dates can be present without observed outcomes.",
                ("It inserts invented zero-demand observations after the availability boundary."),
            ),
            t(
                "Transfer the distinction to working days.",
                ("A business calendar is a declared population, not simply observed event days."),
                (
                    "Define working-day membership explicitly and reconcile "
                    "the denominator, rather than deleting dates with no "
                    "transactions."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables",
            "https://learn.microsoft.com/en-us/dax/datesytd-function-dax",
        ],
    ),
    lesson(
        32,
        "Year-to-date means a specific included-date set",
        ["DATESYTD", "year to date", "date filter", "anchor date", "reconciliation"],
        ("Derive a YTD measure by enumerating its date boundary and eligible fact rows."),
        (
            "A year-to-date calculation expands a date selection to "
            "the start of the relevant year through its current "
            "last date. The returned date table becomes a filter "
            "for the measure. It does not multiply a current-day "
            "value by the number of days, and it does not mean the "
            "full calendar year when the anchor is early in that "
            "year.\n\nOn January 3, 2025 the current day has 20 of "
            "revenue, while YTD includes January 2's 27 and January "
            "3's 20, totaling 47. On February 3 the YTD set "
            "includes all five 2025 sales lines, totaling 123. "
            "These are fixed results for the named reference's "
            "anchor dates; the Date fixture's later unused dates do "
            "not shift the anchor because the query explicitly "
            "supplies it.\n\nClassic time intelligence relies on the "
            "marked, complete date-column contract. Keep date roles "
            "clear: this lesson uses OrderDate. The same calendar "
            "expansion with an explicitly selected shipment "
            "relationship would ask a different question. A "
            "reproducible YTD result needs its anchor, calendar "
            "definition, date role and observation completeness, "
            "not just the label YTD."
        ),
        (
            "DATESYTD returns a date table. CALCULATE reevaluates "
            "NetRevenue using that date set. The outer CALCULATETABLE "
            "establishes the single anchor date. The current-day "
            "measure and YTD measure are intentionally shown together "
            "so the expansion is visible."
        ),
        [
            r(
                "An early January anchor",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "CurrentDay", '
                    '[NetRevenue], "YTD", CALCULATE ( [NetRevenue], DATESYTD ( '
                    "'Date'[Date] ) ) ), 'Date'[Date] = DATE ( 2025, 1, 3 ) )"
                ),
                [("CurrentDay", "number"), ("YTD", "number")],
                [[20, 47]],
                (
                    "Anchor 2025-01-03; classic Gregorian year; active "
                    "OrderDate; coverage is available."
                ),
                [
                    "The current date contains S5 and revenue 20.",
                    "The YTD set begins January 1 and ends January 3.",
                    "S4 and S 5 contribute 27 +20 =47.",
                ],
                (
                    "An empty January 1 date does not disappear from the "
                    "calendar set. It simply contributes no fact amount."
                ),
            ),
            r(
                "An anchor in February",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "CurrentDay", '
                    '[NetRevenue], "YTD", CALCULATE ( [NetRevenue], DATESYTD ( '
                    "'Date'[Date] ) ) ), 'Date'[Date] = DATE ( 2025, 2, 3 ) )"
                ),
                [("CurrentDay", "number"), ("YTD", "number")],
                [[36, 123]],
                "Anchor 2025-02-03; same calendar and date role.",
                [
                    "S8 contributes 36 on the current day.",
                    "The YTD set includes January plus February 1 through 3.",
                    "S4..S8 sum 27 +20 +20 +20 +36 =123.",
                ],
                (
                    "The measure reevaluates over an expanded set, not over "
                    "the text currently visible in one table cell."
                ),
            ),
        ],
        [
            t(
                "Predict YTD at January 2,2025.",
                "Only the first 2025 sale is within the period.",
                "YTD is 27.",
            ),
            t(
                "Change the February anchor to February 2.",
                "Exclude S8 on February 3.",
                "YTD falls from 123 to 87.",
            ),
            t(
                "Write a YTD audit ledger.",
                "Name the included-date interval and contributing SaleIDs.",
                (
                    "For February 3: Gregorian January 1 through February 3, "
                    "OrderDate role, S4..S8, amount 123."
                ),
            ),
            t(
                "Diagnose current-day revenue multiplied by elapsed days.",
                "Events are not uniformly distributed across dates.",
                (
                    "It estimates a different quantity and does not reproduce "
                    "the observed sum over the actual YTD date set."
                ),
            ),
            t(
                "Explain a YTD result after the declared data watermark.",
                "Calendar presence does not establish observed outcomes.",
                (
                    "Label the result as based on data available through the "
                    "watermark; do not imply full coverage through a later "
                    "requested anchor."
                ),
            ),
            t(
                "Transfer the pattern to shipped revenue.",
                "The expanded dates can be the same while the fact-date role differs.",
                (
                    "Use an explicitly selected shipment relationship and "
                    "reconcile shipment dates within the same YTD interval."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/datesytd-function-dax",
            "https://learn.microsoft.com/en-us/dax/totalytd-function-dax",
        ],
    ),
    lesson(
        33,
        "Prior periods and comparable completeness",
        ["SAMEPERIODLASTYEAR", "year-over-year", "period completeness", "comparison denominator"],
        ("Separate a full-period comparison from an as-of comparison and explain the sign change."),
        (
            "A growth calculation needs comparable populations in "
            "time. Comparing a partial current month with a "
            "complete prior month can produce a misleading decline "
            "even when the formula is syntactically valid. The date "
            "set, availability watermark and seasonal calendar "
            "policy should be written before calculating a "
            "percentage.\n\nFull January 2025 revenue is 67 and "
            "January 2024 is 64, giving growth 3/64. Through "
            "January 3, 2025 the current amount is 47, while the "
            "corresponding prior-year dates contain 64, "
            "giving-17/64. These signs differ because the included "
            "current facts differ. The prior fixture happens to "
            "have no later January sales, so its partial and full "
            "totals coincide; that coincidence must not become a "
            "rule in the model.\n\nSAMEPERIODLASTYEAR shifts a date "
            "set, not a business guarantee about equivalent working "
            "days or leap-day treatment. Other comparisons may "
            "require fiscal periods, week definitions or a "
            "comparable-day policy. Preserve a date-level "
            "reconciliation and label an as-of result rather than "
            "letting a report title imply completed months."
        ),
        (
            "The first case filters a complete January month. The "
            "second uses DATESBETWEEN to define an explicit January "
            "1-through 3 interval. Prior revenue is reevaluated over "
            "SAMEPERIODLASTYEAR of the selected dates. DIVIDE "
            "expresses relative change against the prior amount and "
            "preserves an undefined comparison when that denominator "
            "is unavailable."
        ),
        [
            r(
                "Completed January versus completed January",
                (
                    "EVALUATE CALCULATETABLE ( VAR CurrentRevenue = "
                    "[NetRevenue] VAR PriorRevenue = CALCULATE ( [NetRevenue], "
                    "SAMEPERIODLASTYEAR ( 'Date'[Date] ) ) RETURN ROW ( "
                    '"Current", CurrentRevenue, "Prior", PriorRevenue, '
                    '"Growth", DIVIDE ( CurrentRevenue - PriorRevenue, '
                    "PriorRevenue ) ), 'Date'[Year] = 2025, "
                    "'Date'[MonthNumber] = 1 )"
                ),
                [("Current", "number"), ("Prior", "number"), ("Growth", "number")],
                [[67, 64, 3 / 64]],
                (
                    "Full January 2025 versus the shifted January 2024 date "
                    "set; both periods are within available data."
                ),
                [
                    "Current January contains S4,S5,S6, totaling 67.",
                    "Prior January contains S1,S2,S3, totaling 64.",
                    "The difference 3 divided by prior 64 is 0.046875.",
                ],
                (
                    "That is approximately 4.69 percent growth for this "
                    "defined monthly population, not a universal growth rate "
                    "across every date role."
                ),
            ),
            r(
                "An explicit as-of comparison",
                (
                    "EVALUATE CALCULATETABLE ( VAR CurrentRevenue = "
                    "[NetRevenue] VAR PriorRevenue = CALCULATE ( [NetRevenue], "
                    "SAMEPERIODLASTYEAR ( 'Date'[Date] ) ) RETURN ROW ( "
                    '"Current", CurrentRevenue, "Prior", PriorRevenue, '
                    '"Growth", DIVIDE ( CurrentRevenue - PriorRevenue, '
                    "PriorRevenue ) ), DATESBETWEEN ( 'Date'[Date], DATE ( "
                    "2025, 1, 1 ), DATE ( 2025, 1, 3 ) ) )"
                ),
                [("Current", "number"), ("Prior", "number"), ("Growth", "number")],
                [[47, 64, -17 / 64]],
                (
                    "January 1..3,2025 compared with January 1..3,2024; "
                    "explicitly as-of rather than full-month."
                ),
                [
                    "The current interval excludes S6 on January 5, leaving 47.",
                    (
                        "The prior interval still contains all three prior-year "
                        "fixture lines, totaling 64."
                    ),
                    "The difference-17 divided by 64 is-0.265625.",
                ],
                (
                    "The changed result is explained by the period definition. "
                    "Do not repair it by choosing the more attractive "
                    "percentage."
                ),
            ),
        ],
        [
            t(
                "Predict current revenue through January 5,2025.",
                "Include S6 on the fifth day.",
                ("It is 67; the selected current interval now contains all January fixture sales."),
            ),
            t(
                "Add a hypothetical prior-year sale on January 20.",
                "It belongs to the full-month case but not the January 1..3 comparison.",
                (
                    "Only the first case's prior denominator changes; the two "
                    "comparison windows must stay distinct."
                ),
            ),
            t(
                "Write a metric title that exposes the as-of boundary.",
                "Include the date interval and the comparable prior interval.",
                (
                    "For example: Order revenue, January 1-3 versus the same "
                    "dates last year, data available through the stated "
                    "watermark."
                ),
            ),
            t(
                "Diagnose selecting a period merely because it makes growth positive.",
                "The analysis definition must precede the observed result.",
                (
                    "That is outcome-driven selection. State and retain a "
                    "defensible completeness policy before inspecting the "
                    "effect."
                ),
            ),
            t(
                "Explain a zero prior revenue denominator.",
                "An absolute difference can exist without a defined relative growth rate.",
                (
                    "Report the absolute difference and an explicit undefined "
                    "or special-case growth policy rather than silently "
                    "dividing by zero."
                ),
            ),
            t(
                "Transfer the issue to experiment cohorts enrolled at different times.",
                "Cohorts can have unequal follow-up opportunity.",
                (
                    "Compare the same observation age or explicitly model "
                    "differing follow-up; calendar-month labels alone do not "
                    "make cohorts comparable."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/sameperiodlastyear-function-dax",
            "https://learn.microsoft.com/en-us/dax/datesbetween-function-dax",
        ],
    ),
    lesson(
        34,
        "Rolling windows: calendar days versus event days",
        ["DATESINPERIOD", "rolling window", "calendar weighting", "zero versus blank"],
        (
            "Explain why a mean over observed sale days differs from "
            "revenue per eligible calendar day."
        ),
        (
            "A rolling window requires an anchor, direction, interval "
            "size and boundary convention. For the three-day window "
            "ending February 3,2025, the included dates are February "
            "1,2 and 3. DATESINPERIOD with a negative day count "
            "describes that backward interval. The interval token DAY "
            "is an enumeration, not a quoted text value.\n\nThe window "
            "contains revenue 56 on two sale dates, but three eligible "
            "calendar dates. Revenue per calendar day is 56/3. "
            "AVERAGEX over the date set with a revenue measure "
            "excludes a blank day and instead averages 20 and 36, "
            "giving 28. Replacing each known empty day's measure with "
            "zero changes that average back to 56/3.\n\nZero-filling is "
            "justified here only because the entire window is inside "
            "the fixture's declared observation coverage. An "
            "unavailable future date is not an observed zero. This "
            "population rule should be part of a metric contract, "
            "especially when dashboards compare windows with different "
            "coverage or event intensity."
        ),
        (
            "The reference binds the window table once, then uses it "
            "as a CALCULATE filter. The second case iterates that same "
            "date set to contrast blank-excluding and zero-filled "
            "averages. Context transition occurs when [NetRevenue] is "
            "invoked for each date row."
        ),
        [
            r(
                "A three-calendar-day denominator",
                (
                    "EVALUATE CALCULATETABLE ( VAR WindowDates = DATESINPERIOD "
                    "( 'Date'[Date], MAX ( 'Date'[Date] ), -3, DAY ) VAR "
                    "RevenueInWindow = CALCULATE ( [NetRevenue], WindowDates ) "
                    'RETURN ROW ( "Days", COUNTROWS ( WindowDates ), '
                    '"Revenue", RevenueInWindow, "RevenuePerCalendarDay", '
                    "DIVIDE ( RevenueInWindow, COUNTROWS ( WindowDates ) ) ), "
                    "'Date'[Date] = DATE ( 2025, 2, 3 ) )"
                ),
                [("Days", "integer"), ("Revenue", "number"), ("RevenuePerCalendarDay", "number")],
                [[3, 56, 56 / 3]],
                "AnchorFebruary 3,2025; included calendar days February 1,2,3; all observed.",
                [
                    (
                        "February 1 has no order, February 2 contributes 20 and "
                        "February 3 contributes 36."
                    ),
                    "Window revenue is 56 and the Date table supplies three eligible dates.",
                    "The calendar-day ratio is 56/3.",
                ],
                (
                    "The denominator is independent of whether a sale happened "
                    "on a given included date. That is what makes it a "
                    "calendar-day rate."
                ),
            ),
            r(
                "Two different averages over the same window",
                (
                    "EVALUATE CALCULATETABLE ( VAR WindowDates = DATESINPERIOD "
                    "( 'Date'[Date], MAX ( 'Date'[Date] ), -3, DAY ) RETURN "
                    'ROW ( "SaleDayAverage", AVERAGEX ( WindowDates, '
                    '[NetRevenue] ), "ObservedCalendarAverage", AVERAGEX ( '
                    "WindowDates, COALESCE ( [NetRevenue], 0 ) ) ), "
                    "'Date'[Date] = DATE ( 2025, 2, 3 ) )"
                ),
                [("SaleDayAverage", "number"), ("ObservedCalendarAverage", "number")],
                [[28, 56 / 3]],
                (
                    "Same three observed calendar dates; contrast exclusion of "
                    "BLANK with an explicit zero policy."
                ),
                [
                    "The unfilled values are BLANK,20,36.",
                    "The blank-excluding average is 56/2 =28.",
                    "The zero-filled observed-calendar values 0,20,36 average 56/3.",
                ],
                (
                    "Neither name should be shortened to average daily revenue "
                    "without identifying the denominator. A small "
                    "blank-handling change can alter the business meaning."
                ),
            ),
        ],
        [
            t(
                "Predict the two-day window ending February 3.",
                "Only February 2 and 3 are included.",
                (
                    "Revenue is 56 and both dates have sales, so both "
                    "daily-average definitions give 28."
                ),
            ),
            t(
                "Move the three-day anchor to January 4,2025.",
                "The dates are January 2,3,4.",
                (
                    "Revenue is 47; the calendar-day average is 47/3, while "
                    "the sale-day average is 47/2."
                ),
            ),
            t(
                "Write a complete rolling-window contract.",
                "Include time role, boundary, coverage and weighting unit.",
                (
                    "For this case: OrderDate, three calendar days ending "
                    "February 3 inclusive, complete available data, USD per "
                    "calendar day."
                ),
            ),
            t(
                (
                    "Diagnose averaging only returned visual rows when "
                    "zero-sale dates were suppressed."
                ),
                "The display may have removed eligible denominator rows.",
                (
                    "Use an explicit calendar set rather than assuming visible "
                    "event dates represent every eligible day."
                ),
            ),
            t(
                "Explain why a window ending after February 28 needs another check.",
                "The model's calendar extends beyond its observation watermark.",
                (
                    "Later blanks can be unavailable outcomes; do not coalesce "
                    "them to observed zero without a coverage policy."
                ),
            ),
            t(
                "Transfer the denominator to an availability percentage.",
                "Choose whether all scheduled intervals or only recorded observations count.",
                (
                    "A missing telemetry interval may be unknown rather than "
                    "available or unavailable; define its treatment before "
                    "aggregating."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/datesinperiod-function-dax",
            "https://learn.microsoft.com/en-us/dax/averagex-function-dax",
        ],
    ),
    lesson(
        35,
        "Fiscal labels, boundaries and as-of totals",
        ["fiscal year", "date role", "year label", "as-of boundary", "calendar policy"],
        (
            "Define a fiscal year explicitly and distinguish "
            "fiscal-to-date from a completed fiscal year."
        ),
        (
            "A fiscal-year label is a convention over dates, not an "
            "intrinsic property of an integer called Year. Our "
            "ordinary FiscalYear ends in June: July 1,2024 begins FY "
            "2025, while June 30,2024 ends FY 2024. Labeling a fiscal "
            "year by its ending year is a deliberate rule that should "
            "be written in the date dictionary.\n\nA fiscal-year-to-date "
            "question also needs an as-of date. FY 2025 spans July "
            "2024 through June 2025, but this fixture's sales "
            "observation ends February 28,2025. Summing available FY "
            "2025 facts gives 123; calling that a completed-year total "
            "would overstate the temporal coverage. A complete "
            "calendar table can represent future fiscal dates without "
            "supplying their outcomes.\n\nClassic time-intelligence "
            "functions can support shifted Gregorian year boundaries "
            "with their documented year-end arguments. The reference "
            "here instead shows the explicit fiscal column and as-of "
            "date filter so the included population is easy to "
            "inspect. More irregular calendars need additional "
            "metadata and, potentially, the version-sensitive "
            "calendar-based features introduced next."
        ),
        (
            "Case A inspects two neighboring boundary dates and their "
            "stored FiscalYear labels. Case B applies an explicit "
            "fiscal-year filter and a maximum available date. The code "
            "does not infer a financial reporting standard from the "
            "word fiscal; the fixture's convention is the authority."
        ),
        [
            r(
                "Two neighboring fiscal labels",
                (
                    "EVALUATE SELECTCOLUMNS ( FILTER ( 'Date', 'Date'[Date] IN "
                    '{ DATE ( 2024, 6, 30 ), DATE ( 2024, 7, 1 ) } ), "Day", '
                    "'Date'[Date], \"FiscalYear\", 'Date'[FiscalYear] )\nORDER BY "
                    "[Day]"
                ),
                [("Day", "date"), ("FiscalYear", "integer")],
                [["2024-06-30", 2024], ["2024-07-01", 2025]],
                "The declared fiscal year starts July 1 and is named by its ending year.",
                [
                    "June 30 belongs to the fiscal year ending in 2024.",
                    "The next day starts the fiscal year ending in 2025.",
                    (
                        "A one-day boundary changes the fiscal label without "
                        "changing the Gregorian year."
                    ),
                ],
                (
                    "Using Gregorian Year for both rows would miss the fiscal "
                    "transition. A label convention belongs in the model "
                    "specification."
                ),
            ),
            r(
                "Available fiscal-year-to-date revenue",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "FiscalYTDRevenue", '
                    "[NetRevenue] ), 'Date'[FiscalYear] = 2025, 'Date'[Date] "
                    "<= DATE ( 2025, 2, 28 ) )"
                ),
                [("FiscalYTDRevenue", "number")],
                [[123]],
                (
                    "FY 2025 under the July-start convention, observed only "
                    "through 2025-02-28; active OrderDate."
                ),
                [
                    "The fiscal interval starts July 1,2024.",
                    "The as-of boundary stops at February 28,2025, not June 30.",
                    "The available matching sales are S4..S8, totaling 123.",
                ],
                (
                    "There happen to be no second-half 2024 sales in this "
                    "fixture. That does not make Gregorian and fiscal-year "
                    "measures generally equivalent."
                ),
            ),
        ],
        [
            t(
                ("Predict FiscalYear for January 3, 2025."),
                "It lies between July 2024 and June 2025.",
                "The fiscal label is 2025.",
            ),
            t(
                "Change the naming convention to the starting year.",
                "The included dates can stay the same while their label changes.",
                (
                    "July 1,2024 would be labeled FY 2024. Update labels and "
                    "documentation without pretending the population changed."
                ),
            ),
            t(
                "Write a fiscal-to-date metric caption.",
                "Include the fiscal convention and observation date.",
                (
                    "For example: FY 2025 order revenue through February "
                    "28,2025, fiscal year ending June 30."
                ),
            ),
            t(
                (
                    "Diagnose comparing this 123 with a complete prior fiscal "
                    "year as if coverage matched."
                ),
                "Align the follow-up boundary or disclose the difference.",
                (
                    "A partial-versus-full comparison mixes period "
                    "completeness and performance. Construct a comparable "
                    "prior as-of period."
                ),
            ),
            t(
                ("Explain why a fiscal label alone cannot define a 4-4-5 retail calendar."),
                "Week/period membership requires an explicit calendar mapping.",
                (
                    "Month shifting is insufficient for irregular week-based "
                    "periods; provide and validate the intended calendar "
                    "metadata."
                ),
            ),
            t(
                "Transfer the boundary review to an accounting close.",
                "A posted period and an event date can have distinct meanings.",
                (
                    "Model the chosen accounting period explicitly and retain "
                    "reconciliation to transaction dates rather than silently "
                    "substituting one for the other."
                ),
            ),
        ],
        sources=[
            "https://learn.microsoft.com/en-us/dax/datesytd-function-dax",
            "https://learn.microsoft.com/en-us/power-bi/guidance/model-date-tables",
        ],
    ),
    lesson(
        36,
        "Calendar-based time intelligence is a metadata-dependent continuation",
        [
            "calendar metadata",
            "calendar-based time intelligence",
            "preview",
            "tagged columns",
            "compatibility",
        ],
        (
            "Explain why a calendar reference can represent a "
            "different year definition than a classic date column."
        ),
        (
            "Calendar-based time intelligence uses a named calendar's "
            "tagged metadata rather than assuming that every time "
            "function receives a classic Date column. The metadata "
            "tells the engine which columns represent day, year and "
            "other temporal categories. A calendar name is not an "
            "arbitrary alias for a Date column; its definition is part "
            "of the formula's input contract.\n\nFor this optional "
            "conceptual continuation, the model specification declares "
            "RetailCalendar over Date with RetailYear beginning "
            "February 1 and named by its ending year. At February "
            "3,2025 its year-to-date set contains February 1..3 and "
            "revenue 56. Classic Gregorian YTD at the same date "
            "contains January 1..February 3 and revenue 123. The "
            "difference comes from year membership, not a faster or "
            "more accurate sum.\n\nThe classroom does not create that "
            "engine calendar object. The second source case is "
            "complete relative to the stated calendar contract, and "
            "its result is hand-derived from the tagged-year "
            "population. Actual use requires a compatible external "
            "engine and correctly configured calendar metadata. The "
            "stable beginner path remains available through the "
            "classic and explicit-date-set examples."
        ),
        (
            "The classic overload receives 'Date'[Date]. The calendar "
            "overload receives the declared RetailCalendar reference. "
            "Both use the same revenue measure and anchor. Model JSON "
            "records the intended tags as a reviewable offline "
            "specification; it is not a claim that a Power BI project "
            "was loaded or that preview behavior was engine-tested."
        ),
        [
            r(
                "Classic Gregorian YTD",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "GregorianYTD", TOTALYTD '
                    "( [NetRevenue], 'Date'[Date] ) ), 'Date'[Date] = DATE ( "
                    "2025, 2, 3 ) )"
                ),
                [("GregorianYTD", "number")],
                [[123]],
                "Classic marked Date column; Gregorian year; anchor 2025-02-03.",
                [
                    "The classic year begins January 1.",
                    "January revenue 67 and February-to-date 56 are included.",
                    "Gregorian YTD is 123.",
                ],
                (
                    "This case requires only the already described classic "
                    "date-table contract. It provides a stable baseline for "
                    "comparing another calendar definition."
                ),
            ),
            r(
                "The declared February-start retail calendar",
                (
                    'EVALUATE CALCULATETABLE ( ROW ( "RetailYTD", TOTALYTD ( '
                    "[NetRevenue], RetailCalendar ) ), 'Date'[Date] = DATE ( "
                    "2025, 2, 3 ) )"
                ),
                [("RetailYTD", "number")],
                [[56]],
                (
                    "Assume the optional RetailCalendar metadata has been "
                    "configured exactly as specified; RetailYear starts "
                    "February 1."
                ),
                [
                    "The anchor belongs to RetailYear 2026 under the ending-year naming rule.",
                    "Its year-to-date date set begins February 1,2025.",
                    "S7 and S 8 contribute 20 +36 =56; January belongs to the prior retail year.",
                ],
                (
                    "This is a reference derivation under a declared metadata "
                    "assumption, not observed preview-engine output. An "
                    "undefined calendar name would not be a usable external "
                    "query."
                ),
                note=(
                    "Hand-derived under the explicitly specified optional "
                    "calendar metadata. No preview engine, model authoring or "
                    "execution was performed."
                ),
            ),
        ],
        [
            t(
                "Predict the retail-year label for January 31,2025.",
                "The February-start year has not rolled over yet.",
                "It is RetailYear 2025; February 1 begins RetailYear 2026.",
            ),
            t(
                "Change the declared calendar to Gregorian year tags.",
                "The calendar metadata, not the function name alone, defines the year.",
                (
                    "At the same anchor the intended calendar YTD population "
                    "would match the Gregorian set and total 123."
                ),
            ),
            t(
                "Write a review checklist for adding an external calendar object.",
                "Check tags, relationships, compatibility and boundary fixtures.",
                (
                    "Verify the calendar name, day/year/month tags, member "
                    "uniqueness, date role, feature availability and observed "
                    "results around year and leap boundaries."
                ),
            ),
            t(
                "Diagnose copying the second query into a model with only a Date table.",
                "A named calendar definition is additional metadata.",
                (
                    "The reference is missing an input contract there. A "
                    "similarly named table or column does not automatically "
                    "create RetailCalendar."
                ),
            ),
            t(
                ("Explain why sparse-calendar support does not prove complete observation data."),
                "Calendar membership and available outcomes remain separate.",
                (
                    "A feature accepting sparse dates does not certify that "
                    "every relevant event or reporting period was observed."
                ),
            ),
            t(
                "Transfer the distinction to a week-based retail calendar.",
                "Publish the exact period membership before choosing a function.",
                (
                    "Define the 4-4-5 pattern, year boundary and extra-week "
                    "policy, then test date sets and measures rather than "
                    "treating calendar labels as interchangeable."
                ),
            ),
        ],
        feature=(
            "As reviewed on 2026-10-25, Microsoft's calendar-based "
            "time-intelligence documentation labels the feature "
            "preview. It is an optional, metadata-dependent "
            "continuation. The offline course requires neither a "
            "preview engine nor a Power BI installation; do not "
            "confuse this status with the separate generally available "
            "DAX UDF feature."
        ),
        sources=[
            (
                "https://learn.microsoft.com/en-us/power-bi/transform-model"
                "/desktop-time-intelligence"
            ),
            "https://learn.microsoft.com/en-us/dax/totalytd-function-dax",
        ],
    ),
]

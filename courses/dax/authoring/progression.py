"""Direct prerequisite edges and chapter-specific editable scaffolds."""

PREREQUISITES = {
    1: [],
    2: [1],
    3: [2],
    4: [3],
    5: [1, 2],
    6: [2, 3, 5],
    7: [5],
    8: [7],
    9: [3, 7],
    10: [2, 8, 9],
    11: [10],
    12: [9, 11],
    13: [3, 9],
    14: [3, 10],
    15: [12, 14],
    16: [15],
    17: [13, 15],
    18: [8, 10, 17],
    19: [15, 16],
    20: [11, 19],
    21: [13, 17],
    22: [12, 21],
    23: [11, 21],
    24: [20, 23],
    25: [4, 8, 10],
    26: [18, 21, 25],
    27: [17, 26],
    28: [25, 27],
    29: [4, 15],
    30: [27, 28],
    31: [4, 7],
    32: [15, 31],
    33: [11, 32],
    34: [21, 31],
    35: [32, 33],
    36: [31, 35],
    37: [18, 21, 23],
    38: [26, 37],
    39: [29, 31, 34],
    40: [11, 27, 34],
    41: [23, 27, 31],
    42: [11, 13, 21],
    43: [11, 21, 29],
    44: [23, 43],
    45: [44],
    46: [7, 8, 12, 43],
    47: [15, 17, 46],
    48: [23, 32, 38],
    49: [21, 26],
    50: [26, 49],
    51: [16, 19, 49],
    52: [4, 20, 26, 51],
    53: [49, 50, 51],
    54: [43, 50, 53],
    55: [4, 31, 52],
    56: [15, 20, 52],
    57: [27, 56],
    58: [29, 41, 42, 43],
    59: [10, 11, 23, 40],
    60: [54, 55, 57, 58, 59],
}

STARTERS = {
    1: 'EVALUATE\nROW ( "Visible sales lines", BLANK(), "Net revenue", BLANK() )',
    2: 'EVALUATE\nROW ( "Order lines", BLANK(), "Distinct orders", BLANK() )',
    3: (
        "DEFINE MEASURE Sales[DraftRevenue] = "
        "BLANK()\nEVALUATE\nSUMMARIZECOLUMNS ( Product[Category], "
        '"Revenue", [DraftRevenue] )'
    ),
    4: 'EVALUATE\nROW ( "Dimension products", BLANK(), "Products sold", BLANK() )',
    5: (
        'EVALUATE\nSELECTCOLUMNS ( Sales, "Line", Sales[SaleID], '
        '"Amount to explain", BLANK() )\nORDER BY [Line]'
    ),
    6: ('EVALUATE\nROW ( "Duplicate dimension keys", BLANK(), "Unmatched foreign keys", BLANK() )'),
    7: 'EVALUATE\nROW ( "Numeric amount", BLANK(), "Display label", "Draft" )',
    8: ('EVALUATE\nROW ( "No eligible rows", BLANK(), "Measured zero", 0, "Comparison", BLANK() )'),
    9: (
        "DEFINE MEASURE Sales[DraftRevenue] = BLANK()\nEVALUATE ROW "
        '( "Reusable measure", [DraftRevenue] )'
    ),
    10: 'EVALUATE\nROW ( "Rows", BLANK(), "Orders", BLANK(), "Customers", BLANK() )',
    11: (
        'EVALUATE\nROW ( "Net amount", BLANK(), "Quantity", BLANK(), "Amount per unit", BLANK() )'
    ),
    12: (
        "EVALUATE\nVAR BeforeFilter = BLANK()\nRETURN ROW ( "
        '"Captured value", BeforeFilter, "Reevaluated value", '
        "BLANK() )"
    ),
    13: 'EVALUATE\nADDCOLUMNS ( Sales, "Current row calculation", BLANK() )',
    14: (
        'EVALUATE\nROW ( "Selected products", BLANK(), "Selected '
        'customers", BLANK(), "Visible amount", BLANK() )'
    ),
    15: (
        "DEFINE MEASURE Sales[DraftRevenue] = "
        'BLANK()\nEVALUATE\nCALCULATETABLE ( ROW ( "Selected '
        'amount", [DraftRevenue] ), Product[Color] = "Blue" )'
    ),
    16: (
        'EVALUATE\nROW ( "Sibling filter interpretation", BLANK(), '
        '"Nested interpretation", BLANK() )'
    ),
    17: ('EVALUATE\nADDCOLUMNS ( VALUES ( Product[ProductKey] ), "Per-product amount", BLANK() )'),
    18: "EVALUATE\nFILTER ( VALUES ( Product[ProductKey] ), FALSE() )",
    19: ('EVALUATE\nROW ( "Replacement result", BLANK(), "Intersection result", BLANK() )'),
    20: (
        'EVALUATE\nROW ( "Numerator", BLANK(), "Declared denominator", BLANK(), "Share", BLANK() )'
    ),
    21: ('EVALUATE\nROW ( "Sum of line expressions", BLANK(), "Mean of admitted lines", BLANK() )'),
    22: (
        "EVALUATE\nVAR OutsideValue = BLANK()\nRETURN ROW ( "
        '"Captured outside iterator", OutsideValue, "Evaluated '
        'inside iterator", BLANK() )'
    ),
    23: ('EVALUATE\nROW ( "Recomputed total", BLANK(), "Sum of visible ratios", BLANK() )'),
    24: (
        'EVALUATE\nSUMMARIZECOLUMNS ( Product[Category], "Amount", '
        'BLANK(), "Selected total", BLANK() )'
    ),
    25: (
        'EVALUATE\nROW ( "Stored product keys", BLANK(), '
        '"Relationship values", BLANK(), "Unknown amount", BLANK() '
        ")"
    ),
    26: ('EVALUATE\nADDCOLUMNS ( VALUES ( Product[Category] ), "Category amount", BLANK() )'),
    27: ('EVALUATE\nVAR ChosenKeys = { 1, 3 }\nRETURN ROW ( "Transferred selection", BLANK() )'),
    28: (
        "EVALUATE\nVAR FirstSet = { 10, 20 }\nVAR SecondSet = { 20, "
        '30 }\nRETURN ROW ( "Union rows", BLANK(), "Intersection '
        'rows", BLANK() )'
    ),
    29: 'EVALUATE\nROW ( "Order-date amount", BLANK(), "Ship-date amount", BLANK() )',
    30: (
        'EVALUATE\nROW ( "Newsletter", BLANK(), "Prospects", BLANK(), "Distinct union", BLANK() )'
    ),
    31: (
        'EVALUATE\nROW ( "Calendar days", BLANK(), "Observed sales '
        'dates", BLANK(), "Missing dates", BLANK() )'
    ),
    32: 'EVALUATE\nROW ( "Current period", BLANK(), "Year to date", BLANK() )',
    33: (
        'EVALUATE\nROW ( "Current comparable interval", BLANK(), '
        '"Prior interval", BLANK(), "Growth", BLANK() )'
    ),
    34: (
        "EVALUATE\nVAR Anchor = DATE ( 2025, 2, 3 )\nRETURN ROW ( "
        '"Anchor", Anchor, "Calendar-day window", BLANK(), '
        '"Observed-day mean", BLANK() )'
    ),
    35: 'EVALUATE\nROW ( "Fiscal boundary", "June 30", "Fiscal amount", BLANK() )',
    36: (
        'EVALUATE\nROW ( "Gregorian year to date", BLANK(), '
        '"Declared retail year to date", BLANK() )'
    ),
    37: (
        "EVALUATE\nADDCOLUMNS ( VALUES ( Product[ProductKey] ), "
        '"Amount", BLANK(), "Dense rank", BLANK() )'
    ),
    38: (
        'EVALUATE\nROW ( "First ordered line", BLANK(), "Previous '
        'line", BLANK(), "Window total", BLANK() )'
    ),
    39: (
        "EVALUATE\nVAR AsOfDate = DATE ( 2025, 2, 15 )\nRETURN ROW ( "
        '"As of", AsOfDate, "Closing units", BLANK(), "Snapshot '
        'age days", BLANK() )'
    ),
    40: (
        'EVALUATE\nROW ( "Eligible members", BLANK(), "Observed '
        'active members", BLANK(), "Retention", BLANK() )'
    ),
    41: (
        'EVALUATE\nROW ( "Actual", BLANK(), "Budget at matching '
        'grain", BLANK(), "Variance", BLANK() )'
    ),
    42: (
        'EVALUATE\nROW ( "Local transactions", BLANK(), "Converted '
        'USD", BLANK(), "Missing rates", BLANK() )'
    ),
    43: (
        "DEFINE\n    MEASURE Sales[DraftCost] = BLANK()\n    MEASURE "
        'Sales[DraftProfit] = BLANK()\nEVALUATE ROW ( "Cost", '
        '[DraftCost], "Profit", [DraftProfit] )'
    ),
    44: (
        "// Draft a calculation-item definition separately from "
        'this query expansion.\nEVALUATE ROW ( "Transformed '
        'revenue", BLANK(), "Unaffected quantity", BLANK() )'
    ),
    45: ('EVALUATE\nROW ( "Scale outside addition", BLANK(), "Addition outside scale", BLANK() )'),
    46: (
        "// Declare a numeric fee function and its input policy "
        'above the query.\nEVALUATE ROW ( "Default fee", BLANK(), '
        '"Boundary fee", BLANK() )'
    ),
    47: (
        "// Compare the same amount passed as VAL and as "
        'EXPR.\nEVALUATE ROW ( "Eager value", BLANK(), "Deferred '
        'expression", BLANK() )'
    ),
    48: (
        "// This is an explicit snapshot, not a live "
        "visual-calculation definition.\nEVALUATE DATATABLE ( "
        '"Month", STRING, "Revenue", INTEGER, { { "January 2025", '
        '67 }, { "February 2025", 56 } } )'
    ),
    49: (
        'EVALUATE\nROW ( "Fact rows", BLANK(), "Product groups", '
        'BLANK(), "Arithmetic operations to explain", BLANK() )'
    ),
    50: ('EVALUATE\nROW ( "Candidate combinations", BLANK(), "Observed combinations", BLANK() )'),
    51: (
        'EVALUATE\nROW ( "Replacement population", BLANK(), '
        '"Preserved intersection population", BLANK() )'
    ),
    52: 'EVALUATE\nROW ( "Requested pairs", BLANK(), "Existing pairs", BLANK() )',
    53: (
        "// These are supplied scenario numbers, not measured "
        'engine timings.\nEVALUATE DATATABLE ( "Trial", INTEGER, '
        '"Milliseconds", INTEGER, { { 1, 20 }, { 2, 21 }, { 3, 19 '
        "} } )"
    ),
    54: ('EVALUATE\nROW ( "Line-grain cost", BLANK(), "Equivalent grouped cost", BLANK() )'),
    55: ('EVALUATE\nROW ( "Fixed snapshot", BLANK(), "Hypothetical later source", BLANK() )'),
    56: (
        "// State whether each case assumes an ordinary filter or "
        'an externally enforced role.\nEVALUATE ROW ( "Visible '
        'revenue", BLANK(), "After ordinary filter removal", '
        "BLANK() )"
    ),
    57: (
        "// Record the synthetic principal and default-deny role "
        'assumption in notes.\nEVALUATE ROW ( "Permitted '
        'customers", BLANK(), "Visible amount", BLANK() )'
    ),
    58: (
        'EVALUATE\nROW ( "Core revenue", BLANK(), "Attributed '
        'refunds", BLANK(), "Budget variance", BLANK(), "Separate '
        'converted USD", BLANK() )'
    ),
    59: (
        'EVALUATE\nROW ( "Assigned units", BLANK(), "Converted '
        'units", BLANK(), "Unit-level rate", BLANK(), "Uncertainty '
        'boundary", "Draft" )'
    ),
    60: (
        "// Record role, model version, freshness and numerical "
        'equivalence separately.\nEVALUATE ROW ( "Role-specific '
        'revenue", BLANK(), "Baseline cost", BLANK(), "Rewritten '
        'cost", BLANK() )'
    ),
}

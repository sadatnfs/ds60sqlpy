# viz-001: explanatory solutions

Compare with your attempt when you choose to reveal the reference. These answers explain the six tasks in the guide. The complete Python and browser references use the same scientific fixture.

## Exercise 1

Sort complete records: u2/Beta/5, u3/Gamma/3, u1/Alpha/2. Their total is ten. Keeping identity beside value prevents a silent label shuffle.

## Exercise 2

Construct one bar trace from the sorted records, then set a Team x axis and Elapsed hours y axis with a zero baseline. The title states these are measured completion times, not estimates of treatment effect.

## Exercise 3

Change the u3 record's value to four, then derive both trace and table again. The total becomes eleven; the other IDs and values remain unchanged.

## Exercise 4

Alphabetizing only labels pairs Alpha with five and Beta with three, contradicting the source. Sorting the record tuples repairs the mapping; changing colors cannot repair it.

## Exercise 5

Branch before constructing a data trace when the record list is empty. Show a no-observations caption and an empty table; do not invent zero values for absent categories.

## Exercise 6

Use three new IDs with distances 1.5,2,2.5 and update every unit label to kilometers. Sum equals six. A copied hours caption would remain a substantive error despite correct heights.

## Solution reasoning

**Approach.** `case_01` holds each observation as one tuple of record ID, team and hours: u1/Alpha/2, u2/Beta/5 and u3/Gamma/3. It sorts the whole tuples by hours in descending order with `sorted(records, key=lambda row: row[2], reverse=True)` and only then builds the bar trace, drawing x, y, text and `customdata` from the same ordered list. The x axis is titled Team, the y axis Elapsed hours with `rangemode="tozero"`, and the hover template repeats the record ID so a reader can trace every bar back to its source row. The caption and the primitive table are produced from that same ordered list, so figure and table cannot drift apart.

**Why it is correct.** Because the sort moves complete tuples, a team name can never be separated from its own value: the ordered list is u2/Beta/5, u3/Gamma/3, u1/Alpha/2. The reference asserts two things after building the figure. First, the values sum to 10 and the first record is u2. Second, zipping the drawn x and y arrays gives exactly the mapping Beta to 5, Gamma to 3 and Alpha to 2. The second check reads the figure itself, not the input, so it would catch a mistake introduced while constructing the trace. A zero baseline keeps bar length proportional to hours, so Beta's bar is two and a half times Alpha's, matching 5 divided by 2.

**A plausible wrong approach.** A tempting shortcut is to sort the labels and the values as two separate lists, for example alphabetizing the team names for a tidy axis while leaving the hours in descending order. The chart still draws three plausible bars, but Alpha now sits over 5 and Beta over 3, which contradicts the source. Exercise 4 describes exactly this failure. Changing bar colors or adding a legend does not repair it, because the error is in the pairing, not the styling. The mapping assertion in `case_01` fails for this version, which is why it exists. Another weak approach lets the y axis start at 1.5, which exaggerates the gap between Gamma and Alpha.

**How to verify.** Run the Python reference with `.venv/bin/python courses/data-visualization/references/viz-001.py`. It prints the title, the caption, the header `record | team | hours` and the rows u2/Beta/5.0, u3/Gamma/3.0 and u1/Alpha/2.0, then `viz-001 Plotly complete`. For exercise 3, change u3 to 4 and confirm the total assertion must become 11 and the other rows are unchanged. For exercise 4, deliberately sort the labels alone and confirm the dictionary assertion raises an AssertionError. In the browser variant, hover each bar and check that the record ID shown matches the table row with the same team.

## Complete references and evidence

[Python reference](../references/viz-001.py) and [JavaScript reference](../references/viz-001.js) are complete programs for their declared hosts. Python figure construction and browser rendering are separate observations. Test numerical values, real interaction, table access, narrow layouts and source persistence separately. No completion marker certifies scientific validity or learner mastery.

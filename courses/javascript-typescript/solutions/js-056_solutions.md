# js-056: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

An interaction connects a user action to application state. D3 event handlers receive the event and the datum associated with the selected node. Pointer position is measured in a coordinate space; using page coordinates as SVG data values mixes two spaces and often produces misplaced tooltips or selections.

A tooltip is supplemental information, not the only place essential values should exist. A pointer-only tooltip excludes keyboard and some touch users. Provide focusable controls or an alternative data list, and keep a visible summary. Use text insertion so a data label containing markup characters remains text.

Native HTML buttons provide keyboard activation behavior. Making every SVG circle act like a button requires deliberate semantics, focus and key handling. For a small chart, a parallel list of native buttons can offer a simpler accessible route to selecting each datum.

`d3.pointer(event, node)` returns coordinates relative to the chosen node. A handler can update a selected ID and a text summary. Do not retain the event object as long-term application state; retain the meaningful data selection instead.

The reference draws circles and creates native buttons beneath the SVG. Both pointer and keyboard activation reach the same select function. It programmatically activates one button for a deterministic check, while the learner must still perform the real keyboard navigation.

## Exercise 1: Predict literal markup in a text label.

Text insertion is the appropriate default for data labels. Do not use HTML parsing merely to make labels easier to style.

**Expected:** It remains text instead of becoming executable HTML.

## Exercise 2: Activate the same record by pointer and keyboard.

Input methods should converge on application state, not implement subtly different data transformations.

**Expected:** Both produce the same selection summary.

## Exercise 3: Build an accessible selection list beside the chart.

A chart can have a rich visual layer while retaining a simple semantic interaction route.

**Expected:** Native buttons are reachable and reveal exact record values.

## Exercise 4: Diagnose a tooltip offset after SVG scaling.

Choose the target coordinate system and use the corresponding conversion. Arbitrary pixel offsets hide the mismatch only at one size.

**Expected:** Coordinates were measured in the wrong space.

## Exercise 5: Keep essential values available without hover.

Hover is not universal. Touch, keyboard and assistive-technology users need a reliable route to the same information.

**Expected:** A summary or data list remains visible and usable.

## Exercise 6: Review focus and announcement behavior.

Avoid moving focus on every hover or announcing a large changing DOM. Test the actual keyboard sequence rather than assuming ARIA alone implements it.

**Expected:** Focus stays predictable and the live summary is concise.

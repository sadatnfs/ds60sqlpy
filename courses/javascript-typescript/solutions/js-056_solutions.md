# js-056: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

An interaction connects a user action to application state. D3 event handlers receive the event and the datum associated with the selected node. Pointer position is measured in a coordinate space; using page coordinates as SVG data values mixes two spaces and often produces misplaced tooltips or selections.

A tooltip is supplemental information, not the only place essential values should exist. A pointer-only tooltip excludes keyboard and some touch users. Provide focusable controls or an alternative data list, and keep a visible summary. Use text insertion so a data label containing markup characters remains text.

Native HTML buttons provide keyboard activation behavior. Making every SVG circle act like a button requires deliberate semantics, focus and key handling. For a small chart, a parallel list of native buttons can offer a simpler accessible route to selecting each datum.

`d3.pointer(event, node)` returns coordinates relative to the chosen node. A handler can update a selected ID and a text summary. Do not retain the event object as long-term application state; retain the meaningful data selection instead.

The reference draws circles and creates native buttons beneath the SVG. Both pointer and keyboard activation reach the same select function. It programmatically activates one button for a deterministic check, while the learner must still perform the real keyboard navigation.

## Exercise 1: Predict literal markup in a text label.

Text insertion is the appropriate default for data labels. Do not use HTML parsing merely to make labels easier to style. If a row id were "<b>A</b>", selection.text writes it as characters, so the status shows the tags literally and no b element appears. Using .html for convenience would parse it as markup, and a hostile string could include an onerror handler. Check host.querySelector("b") is null.

**Expected:** It remains text instead of becoming executable HTML.

## Exercise 2: Activate the same record by pointer and keyboard.

Input methods should converge on application state, not implement subtly different data transformations. Both pointerenter on a circle and click on a button call selectRow, so hovering B and clicking "Inspect B" both set the status to "B: 7" and stroke B. Writing a separate hover handler that formats the value differently would let the two routes disagree. Compare status text after each route.

**Expected:** Both produce the same selection summary.

## Exercise 3: Build an accessible selection list beside the chart.

A chart can have a rich visual layer while retaining a simple semantic interaction route. The reference joins rows to native button elements labeled "Inspect A" and "Inspect B" beside circles of radius 15 and 35. A div with a click handler is not reachable by Tab. The check calls buttons.nodes()[1].click() and confirms every node is an HTMLButtonElement.

**Expected:** Native buttons are reachable and reveal exact record values.

## Exercise 4: Diagnose a tooltip offset after SVG scaling.

Choose the target coordinate system and use the corresponding conversion. Arbitrary pixel offsets hide the mismatch only at one size. If the SVG is scaled by CSS, event.offsetX is in CSS pixels while circles use the 640-wide viewBox. Use d3.pointer(event, svg.node()) to convert, then resize the window and confirm the tooltip still sits on the circle.

**Expected:** Coordinates were measured in the wrong space.

## Exercise 5: Keep essential values available without hover.

Hover is not universal. Touch, keyboard and assistive-technology users need a reliable route to the same information. The status paragraph and buttons keep "B: 7" reachable on touch screens; a hover-only tooltip would leave those users without values. Test on a touch device or emulator.

**Expected:** A summary or data list remains visible and usable.

## Exercise 6: Review focus and announcement behavior.

Avoid moving focus on every hover or announcing a large changing DOM. Test the actual keyboard sequence rather than assuming ARIA alone implements it. Tab to each button and listen: aria-live="polite" should read "B: 7" once per selection, and focus should stay on the button you pressed.

**Expected:** Focus stays predictable and the live summary is concise.

## After comparison

Add a tooltip that follows the pointer and a details panel driven by focus. Test at two SVG widths to confirm the tooltip stays beside the hovered mark, and check that the details panel alone exposes every value the tooltip shows.

# js-044: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A selection is a group of DOM nodes, not a copy of their HTML. A data join relates an array of records to selected nodes. Records without corresponding nodes enter; nodes with corresponding records update; surplus nodes exit. This makes repeated rendering a reconciliation operation rather than an instruction to append duplicates forever.

The selector describes the nodes you intend to manage. `selectAll('circle')` can begin empty; the subsequent data join creates the required nodes. `join('circle')` handles the common enter/update/exit case. Attribute callbacks then assign geometry from each bound record.

A render function should produce the intended state when called again. Calling append for every record on every update leaves stale marks and inflates counts. Start with a small sequence, such as three values followed by two, and verify both node count and attributes after the second render.

`selection.data(values).join('circle')` binds the current values and returns the merged entered/updated selection. Without a key, matching is by index within a group. This can be correct when positions are identities, but the next lesson shows why stable entity IDs often need keys.

An attribute callback `(d, i) => ...` receives the record as d and its current group index as i. Returning undefined for a required coordinate can remove or invalidate the intended attribute. Inspect the derived values before blaming SVG rendering.

## Exercise 1: Predict the node count after two draws.

The exit selection is removed by the standard join. Repeated rendering should reflect current input cardinality.

**Expected:** Two circles after changing three records to two.

## Exercise 2: Change the second input to an empty array.

An empty dataset is a valid state. Exit handling should remove old marks rather than showing stale data.

**Expected:** No managed circles remain.

## Exercise 3: Write a render function using a data join.

Separate creation policy from attributes so the function can update existing nodes instead of appending duplicates.

**Expected:** Repeated calls produce exactly one mark per current record.

## Exercise 4: Diagnose a chart that doubles its nodes on every click.

Check the selector and join boundary first. Styling cannot correct an ever-growing stale DOM.

**Expected:** It uses unconditional append or selects the wrong managed nodes.

## Exercise 5: Add an explicit invalid-value rejection.

Geometry has a domain contract. Silent invalid attributes make a bad input look like a missing data point.

**Expected:** A negative radius input is refused before drawing.

## Exercise 6: Apply the same pattern to an HTML list.

The mechanism is about data-to-node relationships, not SVG alone. Preserve text safety when labels are external.

**Expected:** Current records reconcile to current list items.

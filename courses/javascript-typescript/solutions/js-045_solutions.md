# js-045: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A key identifies the same entity across different arrays. It should be stable and unique within the joined group. An array index identifies a position, which can change after sorting or filtering. Confusing identity with position can attach the wrong interaction state or transition to a record.

A keyed join lets a DOM node continue representing the same entity even when the record order changes. The node can receive new values while preserving its identity. Exit removes entities no longer present; enter adds new identities. This is especially important for animated updates and keyboard focus.

Duplicate keys violate the intended one-entity-one-node relationship. D3 has defined matching behavior, but relying on it to silently fix bad input is a poor data contract. Validate uniqueness before drawing and decide explicitly whether repeated categories should be aggregated or represented by distinct IDs.

Use `.data(records, d => d.id)` to match by identity. Save a node reference for entity A, reorder the records and redraw, then compare with `===`. This checks actual DOM reuse, not just a similar-looking chart.

Sort a copied array when you want display order without mutating a source collection owned elsewhere. Keep the key based on identity rather than the value being sorted. A value can change while the entity remains the same.

## Exercise 1: Predict which node should survive reordering.

Keys express entity identity. Reordering changes placement, not which object the node represents.

**Expected:** The node for A remains the same object.

## Exercise 2: Update A value while retaining its ID.

An entity can change attributes without being replaced. This distinction supports coherent transitions and focus behavior.

**Expected:** The existing A node receives new geometry.

## Exercise 3: Implement a keyed redraw with two records.

Test object equality as well as visible geometry. A fresh identical-looking node would not prove the reuse contract.

**Expected:** Node identity and current data values both match expectations.

## Exercise 4: Diagnose using a sorted index as the key.

The bug may be invisible until stateful interactions or animation are added. Choose an ID independent of ordering.

**Expected:** Position changes can associate a node with a different entity.

## Exercise 5: Reject duplicate IDs before rendering.

Validation belongs near the data boundary. If duplicates are legitimate, define an aggregation or a composite identity deliberately.

**Expected:** A clear error precedes ambiguous joins.

## Exercise 6: Transfer identity reasoning to a live leaderboard.

The chart should show movement of known participants rather than replacement of anonymous ranked positions.

**Expected:** Scores change and ranks reorder while participant IDs remain stable.

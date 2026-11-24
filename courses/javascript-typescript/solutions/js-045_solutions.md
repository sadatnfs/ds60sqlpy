# js-045: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A key identifies the same entity across different arrays. It should be stable and unique within the joined group. An array index identifies a position, which can change after sorting or filtering. Confusing identity with position can attach the wrong interaction state or transition to a record.

A keyed join lets a DOM node continue representing the same entity even when the record order changes. The node can receive new values while preserving its identity. Exit removes entities no longer present; enter adds new identities. This is especially important for animated updates and keyboard focus.

Duplicate keys violate the intended one-entity-one-node relationship. D3 has defined matching behavior, but relying on it to silently fix bad input is a poor data contract. Validate uniqueness before drawing and decide explicitly whether repeated categories should be aggregated or represented by distinct IDs.

Use `.data(records, d => d.id)` to match by identity. Save a node reference for entity A, reorder the records and redraw, then compare with `===`. This checks actual DOM reuse, not just a similar-looking chart.

Sort a copied array when you want display order without mutating a source collection owned elsewhere. Keep the key based on identity rather than the value being sorted. A value can change while the entity remains the same.

## Exercise 1: Predict which node should survive reordering.

Keys express entity identity. Reordering changes placement, not which object the node represents. The key function (d) => d.id ties the node to A, so after the second draw svg.select('[data-id="A"]').node() is the same object captured as before. Without a key, the first node would be rebound to B because it is first in the new array. Compare the two references with ===.

**Expected:** The node for A remains the same object.

## Exercise 2: Update A value while retaining its ID.

An entity can change attributes without being replaced. This distinction supports coherent transitions and focus behavior. A moves from v 3 to v 6, so its radius goes from 24 to 48 because r is d.v * 8. Removing and re-adding the node would also give 48, but the identity check would fail. The reference checks both before === the current A node and r === 48.

**Expected:** The existing A node receives new geometry.

## Exercise 3: Implement a keyed redraw with two records.

Test object equality as well as visible geometry. A fresh identical-looking node would not prove the reuse contract. Draw [A 3, B 5], capture both nodes, then draw [B 4, A 6]. Verify that each captured node still has its own data-id and that their cx values swapped: A moves from 150 to 400 and B from 400 to 150.

**Expected:** Node identity and current data values both match expectations.

## Exercise 4: Diagnose using a sorted index as the key.

The bug may be invisible until stateful interactions or animation are added. Choose an ID independent of ordering. A key of (d, i) => i behaves like no key: after reordering, the node at index 0 now represents B. With only fill and radius the picture looks right, but a focus ring or tooltip attached to A would jump to B. Check the data-id on the captured node after reordering.

**Expected:** Position changes can associate a node with a different entity.

## Exercise 5: Reject duplicate IDs before rendering.

Validation belongs near the data boundary. If duplicates are legitimate, define an aggregation or a composite identity deliberately. The reference compares new Set(ids).size with rows.length, so two A rows throw before the join. Letting D3 bind them would keep one A node and send the other to enter, with no error. The rejected flag confirms the throw.

**Expected:** A clear error precedes ambiguous joins.

## Exercise 6: Transfer identity reasoning to a live leaderboard.

The chart should show movement of known participants rather than replacement of anonymous ranked positions. Key on participant ID, not rank, so a score change moves the same node; check one participant's node is reused after two rank swaps.

**Expected:** Scores change and ranks reorder while participant IDs remain stable.

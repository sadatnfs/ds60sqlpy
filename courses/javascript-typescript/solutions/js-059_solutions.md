# js-059: explanatory solutions

Compare after your own attempt or an explicit reveal. The separate .js reference is a complete offline browser program. These explanations discuss the six practice tasks; a visual resemblance alone is not a data or behavior check.

## Mechanism review

A hierarchy represents parent-child relationships without cycles. A tree has one root and a unique path from that root to each node. This differs from a general network, where nodes can have several relationships and cycles. Choosing a tree layout for data that is not a tree can hide important structure.

`d3.hierarchy` wraps nested input in nodes with parent, children, depth and traversal methods. Layout algorithms add geometry to these wrapper nodes. The original data remains available as node.data. A tree layout uses topology, not a numeric magnitude, to position nodes.

The reference visualizes a small learning taxonomy. Labels explain the nodes, and links show parent-child relationships. A hierarchy can be deep or broad, so a reusable view must address label collisions, collapse state and keyboard navigation rather than assuming every tree fits one screen.

Construct the hierarchy from an object whose children field contains nested objects. Apply `d3.tree().size([height,width])` to compute coordinates. For a left-to-right tree, use the layout y coordinate as horizontal position and x as vertical position.

`root.links()` returns source-target pairs; `d3.linkHorizontal` converts each pair into a path. Check node and edge counts: a connected tree with n nodes has n-1 parent edges. This is a structural invariant, not a visual preference.

## Exercise 1: Predict node and edge counts.

Each non-root node has one parent edge. This invariant catches missing or duplicated structural relationships.

**Expected:** Three nodes and two links in the small example.

## Exercise 2: Add a grandchild under A.

The new relationship changes topology. Its position should follow the layout rather than a manually chosen unrelated coordinate.

**Expected:** Depth 2 appears and counts become 4 nodes, 3 links.

## Exercise 3: Render a labeled left-to-right tree.

Use the same layout coordinates for both marks and links. Swapping x and y inconsistently produces misleading connections.

**Expected:** Links connect the matching source and target nodes.

## Exercise 4: Diagnose using a tree for a cyclic relationship graph.

A general network needs a different representation or an explicitly chosen spanning tree whose omissions are disclosed.

**Expected:** The data model does not satisfy tree assumptions.

## Exercise 5: Handle long labels in a narrow view.

Truncation needs a discoverable full value. Geometric fit alone does not establish usable reading.

**Expected:** Labels remain readable or an alternate list exposes full names.

## Exercise 6: Design a collapsible taxonomy state model.

Do not encode collapse only by deleting data permanently. Keep the source hierarchy and view state distinct.

**Expected:** Stable node IDs and explicit collapsed sets preserve identity.

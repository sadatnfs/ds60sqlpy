# js-061: explanatory solutions

Compare after your own attempt; the separate `.js` file is the complete reference program.

## Mechanism review

A network or graph contains nodes and edges. Unlike a tree, it can contain cycles and multiple routes. A force-directed layout assigns positions by iteratively applying simulated forces such as attraction along links and repulsion between nodes. The result is a layout heuristic, not evidence that geometric distance is a measured relationship strength.

D3 force simulation mutates node objects with position and velocity fields and can replace link endpoint IDs with node references. Copy input records before giving them to a simulation if another component owns immutable source data. Stable node IDs define link identity.

An automatically running simulation has a timer and a lifecycle. For a small deterministic lesson, stop it and advance a fixed number of ticks with a seeded random source. This makes checks repeatable and prevents a background timer from continuing after the lesson result is recorded.

Create node and link copies, configure `forceLink(...).id(d=>d.id)`, charge and centering forces, and call `.stop()` before manual ticks. Each tick updates the layout. A finite position check verifies basic numerical health but does not prove the chosen force parameters produce a useful explanation.

Render links from their resolved source and target nodes and render labeled circles for nodes. A larger graph needs aggregation, filtering, interaction and performance planning. Do not call a dense hairball an informative visualization merely because every edge is drawn.

## Exercise 1: Distinguish graph relationships from layout distance.

A short geometric distance can be an artifact of parameters rather than a measured similarity. Links A-B, B-C and C-A are the data; forceLink distance 140 and charge -150 decide how far apart circles end up. Two nodes drawn close together have not been measured as similar. Change distance to 80 and the triangle shrinks while the three links stay the same.

**Expected:** Edges are data; force positions are a chosen visual arrangement.

## Exercise 2: Copy node and link objects before simulation.

This protects shared application state. Shallow copies are sufficient only when the mutable fields are at the copied level. forceSimulation writes x, y, vx and vy onto node objects. The reference maps sourceNodes to shallow copies, so the check that no source node has "x" passes. Passing sourceNodes directly would leave layout state in the original data.

**Expected:** Original inputs remain free of layout mutation.

## Exercise 3: Build a bounded three-node network.

Validate topology before layout. An unknown endpoint should fail clearly rather than create an unexplained missing edge. The reference stops the simulation, seeds randomSource with d3.randomLcg(0.5) and runs tick(100) synchronously, then draws three lines and three circles. Because of the seed, reruns produce the same positions. The checks confirm finite positions and that every link source and target became an object.

**Expected:** All positions are finite and every link resolves to known IDs.

## Exercise 4: Diagnose a reference that never stops animating.

Stop or dispose of owned work. A completed lesson receipt should not leave unnecessary background computation. Without .stop(), the simulation keeps a timer running after the lesson finishes. The reference stops it and ticks a fixed 100 steps; check no further tick events fire. In an interactive version, call simulation.stop() when the component is removed.

**Expected:** The simulation timer lacks a lifecycle boundary.

## Exercise 5: Test duplicate or unknown node IDs.

Identity validation prevents ambiguous link resolution. A visually plausible graph can still represent the wrong entities. A link to "D" makes forceLink throw "node not found: D". Validate ids against a Set and reject duplicates before building the simulation.

**Expected:** The input is rejected before misleading layout.

## Exercise 6: Choose a strategy for a dense network.

Drawing every possible edge can obscure structure. Explain the retained relationships and any information omitted. For hundreds of edges, keep only links above a weight threshold and say how many were dropped. Aggregating nodes by community, then drawing one edge per community pair, is another option. Either way the three-node reference shows the checks to keep: finite positions, resolved links and untouched source data.

**Expected:** Filter or aggregate according to an analytical question.

## After comparison

Load a 20-node synthetic graph, validate its IDs and run a seeded simulation for a fixed number of ticks. Add a control that filters edges by weight, check that removed edges never leave dangling references, and report each node's degree in a table.

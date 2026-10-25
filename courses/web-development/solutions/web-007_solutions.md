# web-007: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A table represents data whose meaning depends on row and column relationships. It should not be the default layout tool for unrelated page regions. A caption identifies the table's topic, units or scope. Header cells identify a column or row so a reading tool can associate values with their context. Visual boldness alone cannot establish that relationship.

Keep a table simple when possible. A dataset with two independent header axes can use column and row scope. More complex spans may require explicit header associations and careful testing. For a narrow screen, preserve the relationships instead of hiding important columns. A scrollable region can keep the table intact when the data genuinely needs two dimensions.

Use thead for the header group, tbody for records, th for headers and td for values. `scope="col"` identifies a column header and `scope="row"` identifies a row header. Numeric alignment is presentation, while the units belong in the content. Tables must remain useful when colors or zebra stripes are unavailable.

## Exercise 1: Explain what a single cell value means with both headers.

40 means forty minutes of HTML study, not an unlabeled count.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a caption that states the reporting period.

The visible caption explains the table's scope.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a three-row study table with correct header relationships.

The caption, row headers and column headers identify every value.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Replace a table used to align unrelated navigation and article content.

Use semantic regions plus CSS layout rather than false data relationships.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Inspect the table at a narrow width without deleting data.

A bounded overflow region keeps all columns reachable.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain when a chart should keep a supporting table.

Exact values and nonvisual interpretation often benefit from a tabular equivalent.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

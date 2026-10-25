# web-028: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A data interface connects records to a representation. Keep the original records separate from the filtered view so a user can clear a filter without reconstructing lost input. A table is useful for exact values; a chart emphasizes patterns. Both need labels, units and a declared handling of missing values. A visually impressive chart can still tell an incorrect story if its filtering or scale is wrong.

This lesson uses a tiny local array and a semantic table. A select changes the derived records, then one render function replaces the table body with safely created cells. An empty result receives an explicit message rather than an unexplained blank area. The JavaScript D3 specialization builds on the same principles for richer scales, joins and interaction; it is a continuation, not a replacement for data validation.

Use array.filter to derive records without mutating the source array. Create cells with createElement and textContent. Count the resulting rows and compare with the stated filter. For later D3 work, preserve stable record identities and separate data transformation from visual encoding. Never imply that a client-side filter is access control over confidential data already sent to the browser.

## Exercise 1: Predict the rows retained for a forty-minute threshold.

Only the records whose minutes are at least forty remain.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a clear filter label and a result count.

The user can identify the active condition and its effect.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a filterable local study table with an explicit empty state.

Changing the selection updates rows and count while preserving the original data.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a filter that permanently removes source records.

Keep immutable input and derive a new view for each render.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test a threshold that returns no records.

The interface explains the empty result and allows the filter to be cleared.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain how this table connects to D3 without changing the statistical claim.

The same validated records can drive a visual encoding with explicit scales, units and an accessible equivalent.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

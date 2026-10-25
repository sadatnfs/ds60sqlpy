# web-012: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Typography controls the effort required to read. A font stack lists preferred fonts followed by a generic fallback, so text remains usable when a particular font is absent. This course uses system fonts and makes no external font request. Relative units allow the design to respond to user settings. A rem is relative to the root font size; em often depends on the current element's font size, with property-specific details.

Line length, line height and spacing interact. Very long lines make it difficult to find the next line; very short lines create constant interruptions. A max-width expressed in ch can approximate a readable character measure, though it is based on the zero glyph width rather than an exact count of all characters. A unitless line-height scales naturally with the element's font size.

Use `font: 1rem/1.6 system-ui, sans-serif` to set size, unitless line-height and family. Avoid fixing the root to a tiny pixel size to make arithmetic convenient. Preserve user zoom. Headings can use a bounded fluid size with clamp, while body text should remain comfortable and predictable. Text alignment is content-sensitive; full justification can create distracting gaps in narrow columns.

## Exercise 1: Explain the reference for rem and a typical em use.

Rem uses the root font size; em commonly scales with the relevant element's font size.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Apply a system font stack without network dependencies.

The page remains readable offline on different operating systems.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a reading page with bounded measure and scalable headings.

Text stays comfortable at wide and narrow sizes without fixed-height clipping.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose text that overlaps after zooming.

Inspect fixed heights, line heights and positioned containers rather than disabling zoom.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test at increased browser zoom with long content.

Reading order, text visibility and controls remain intact.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain why ch is a useful approximation rather than a word-count guarantee.

It measures the font's zero glyph, and actual character widths vary.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

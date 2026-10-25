# web-003: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Semantic markup tells the browser and reader what a piece of content is. A main region contains the page's primary content. Navigation groups major navigation links; a header introduces a page or section; a footer provides related closing information. These elements are not a promise of any particular position on screen. A header can appear inside an article and need not be a fixed top bar.

Headings provide a hierarchy that a screen reader and a visual reader can use to scan. Use the main topic as h1 and its major subdivisions as h2, with h3 for nested detail. Choose levels for structure, not because the browser's default font size looks attractive. A section normally benefits from a heading; a generic div is appropriate when there is no additional semantic meaning.

Draw the content outline before assigning tags. Use one visible main region for the primary task. Give repeated navigation regions distinct accessible labels such as `aria-label="Course"`. A skip link points to the main region's id and lets a keyboard user bypass repeated controls. Native HTML supplies roles automatically; redundant roles rarely add value.

## Exercise 1: Draw the heading outline of the first example.

Study notes contains HTML as one second-level section.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a sibling CSS section at the correct level.

CSS and HTML both use h2 because they have the same parent topic.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a study page with landmarks and a working skip link.

Header, labeled navigation, one main and footer have meaningful content; the skip target exists.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Replace a heading used only for large text with an appropriate element.

A visual callout uses CSS without corrupting the document outline.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Check the document with CSS disabled or unavailable.

The reading order and heading relationships remain coherent.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain when a div is more appropriate than section.

Use a generic container when grouping does not introduce a meaningful headed section.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

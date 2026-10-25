# web-002: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

An attribute adds information to an opening tag. In `<html lang="en">`, the attribute name is lang and its value identifies the document language. Attribute values should be quoted consistently. Nesting means one element's content contains another element; the resulting parent-child relationship matters to styling, accessibility and scripts. A paragraph can contain emphasized text, but a list does not belong inside that paragraph.

HTML has special syntax characters. A less-than sign begins markup, so literal comparison text may need `&lt;`. An ampersand begins a character reference and is commonly represented as `&amp;`. Escaping means representing text so a parser treats it as data. It is different from deleting characters and different from making an unsafe URL safe.

Close nested elements in reverse order: open paragraph, open strong, close strong, close paragraph. Void elements such as `br` and `img` have no closing tag. A `data-*` attribute stores page-specific metadata; it does not create a visible label. `id` must uniquely identify an element in the document. Class names may repeat because they group related elements.

## Exercise 1: Predict the text content after character references are parsed.

The browser displays comparison signs and an ampersand, not the entity source.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add a language attribute and explain its role.

The root lang attribute identifies the language for pronunciation and processing.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a notes paragraph with nested importance and literal angle brackets.

The structure remains a paragraph and the comparison is text rather than an element.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Repair overlapping emphasis tags by drawing their tree.

Each opened element is closed before its parent closes.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Add two related notes without duplicating an id.

Shared class names group them while each id remains unique.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain escaping versus validation with a text and URL example.

Escaping preserves literal text; URL validation separately restricts allowed schemes and destinations.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

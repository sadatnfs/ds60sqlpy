# web-002: explanatory solutions

Open this after your own attempt. Each answer explains the lesson's synthetic fixtures; it does not show that your work or a deployment passed. The mechanism is explained in `courses/web-development/guides/web-002.md`.

## Exercise 1: Predict the text content after character references are parsed.

**Expected answer:** The browser displays comparison signs and an ampersand, not the entity source.

**Why:** Character references are decoded during parsing, so the text node holds the real < and & characters while the source keeps them escaped.

## Exercise 2: Add a language attribute and explain its role.

**Expected evidence:** The root lang attribute identifies the language for pronunciation and processing.

**Why:** lang tells assistive technology which pronunciation rules to apply and lets browsers use language-specific hyphenation and quotation marks.

## Exercise 3: Build a notes paragraph with nested importance and literal angle brackets.

**Expected evidence:** The structure remains a paragraph and the comparison is text rather than an element.

**Why:** Escaping keeps the comparison as text so the parser does not open a new element, while nested inline elements add importance without breaking the paragraph.

## Exercise 4: Repair overlapping emphasis tags by drawing their tree.

**Expected evidence:** Each opened element is closed before its parent closes.

**Why:** Elements form a tree, so a child must close before its parent closes. Crossing tags force the parser to repair the tree, which can split or extend the emphasis unexpectedly.

## Exercise 5: Add two related notes without duplicating an id.

**Expected evidence:** Shared class names group them while each id remains unique.

**Why:** An id names one element for fragments, labels and scripts, so it must be unique; a class can mark any number of elements.

## Exercise 6: Explain escaping versus validation with a text and URL example.

**Expected answer:** Escaping preserves literal text; URL validation separately restricts allowed schemes and destinations.

**Why:** Escaping changes how a value is written in one output context so it stays text; validation rejects values such as a javascript: URL that remain dangerous even when correctly escaped.

## Reference comparison

Open `courses/web-development/solutions/web-002_solution.html` only after saving your attempt, and compare decisions rather than identifiers. A different implementation is acceptable when it shows the same behavior and rejects the same invalid cases. The reference checks only its named synthetic cases; its success message is not an accessibility audit or proof of responsive behavior at every size.

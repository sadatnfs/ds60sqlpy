# web-005: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

Lists express relationships that paragraphs do not. An ordered list describes a sequence where position matters. An unordered list groups peers without requiring order. A description list pairs terms with explanations. These structures help reading tools announce item counts and relationships. A row of hyphens in plain text may look like a list but does not expose that structure.

A quotation identifies borrowed language and should have a source when appropriate. Code identifies literal program text, while pre preserves whitespace. The combination pre and code is useful for multiline snippets. Long lines still need an overflow policy. Never use a quotation element simply to indent text or a list merely to create a visual column.

A list contains li elements; nested lists belong inside the parent li they elaborate. A description list contains dt terms and dd explanations. A short inline token uses code without pre. Literal less-than signs in displayed code must be escaped because the containing HTML still has to parse correctly.

## Exercise 1: Choose a list type for steps and an unordered tool collection.

Steps use ol; interchangeable peer tools use ul.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Add two vocabulary terms with definitions.

A dl contains paired dt and dd elements.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a study checklist with a code example and glossary.

The page exposes list, code and definition structures without relying on spacing.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Repair a nested list placed as a sibling of its parent item.

The nested list belongs inside the associated li.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Test a long code line in a narrow preview.

The code region can scroll without making the entire page horizontally overflow.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain the difference between preserving whitespace and preserving meaning.

Pre preserves formatting; semantic elements additionally communicate content roles.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

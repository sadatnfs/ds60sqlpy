# web-037: explanatory solutions

Compare after your own attempt or an explicit solution reveal. This file explains the supplied deterministic fixtures. It does not claim that a learner or a production deployment passed.

## Why the mechanism works

A PHP string is a sequence of bytes. UTF-8 is an encoding that represents characters using one or more bytes, so strlen counts bytes rather than user-perceived characters. A visible character can also consist of multiple code points, such as a letter with a combining mark. Code-point count and grapheme count are therefore different concepts. Choose the measure that matches the product requirement.

This worker does not assume every optional internationalization extension. The examples use valid UTF-8 and demonstrate byte-level behavior plus a Unicode-aware regular expression. Production text normalization, locale-aware sorting and grapheme handling need deliberate library and extension choices. Do not truncate arbitrary UTF-8 bytes and then assume the result remains valid text.

Use explicit UTF-8 when escaping HTML output. JSON requires valid Unicode data and can fail on invalid UTF-8. A Unicode regular expression with the u modifier interprets the pattern as UTF-8, but it is not a universal grapheme library. Keep validation, normalization and output encoding separate because they solve different problems.

## Exercise 1: Predict the UTF-8 byte length of é.

It occupies two bytes in the supplied source encoding.

Trace the smallest example before editing. Name which values are source and which are observations.

## Exercise 2: Encode a Unicode label as JSON with explicit error handling.

The output is valid JSON or a visible encoding exception.

Change only the named feature. Compare with the unchanged example and explain any unaffected behavior.

## Exercise 3: Build a text inspection report that labels bytes honestly.

The program does not present strlen as a count of user-perceived characters.

Sketch the structure or data contract first. Reuse the mechanism from the examples without copying the reference.

## Exercise 4: Diagnose a truncated string that splits a multibyte sequence.

Byte slicing can create invalid UTF-8; use a suitable text-aware operation for the intended unit.

Keep the failing input. Identify the first layer where the observed result differs from the intended contract.

## Exercise 5: Compare a plain ASCII label and a Unicode label.

The byte counts differ from intuitive character counts when multibyte data appears.

Predict the boundary before running it. Add an explicit check or manual observation that would detect a regression.

## Exercise 6: Explain validation, normalization and output escaping separately.

Validation checks a contract, normalization chooses an equivalent representation, and escaping protects a destination context.

Explain your choice to someone who has not seen the code. Include one limitation and the evidence needed to remove it.

## Reference comparison and limits

Read the separate executable reference, where supplied, only after retaining your attempt. Compare structure and decisions rather than matching every identifier. A different implementation is acceptable when it satisfies the same behavior, preserves accessibility and rejects the same invalid cases. The checked reference uses tiny synthetic inputs so that each transformation can be inspected. It is not a ready-to-deploy authenticated application. Server lifecycle, persistence, concurrency and security require their own integration evidence.

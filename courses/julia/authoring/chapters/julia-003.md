## Text has several useful lengths

Julia strings use UTF -8. A byte is a storage unit, a Unicode scalar value is represented by a `Char`, and a visible grapheme may contain several scalar values. These notions coincide for simple ASCII text but diverge for accented characters and many other writing systems.

String indices identify valid character-start positions in the underlying code-unit sequence. They are not necessarily consecutive character counts. A generic loop should use `eachindex`, `nextind` or character iteration rather than incrementing a byte index and assuming that every position begins a valid character. `length` counts characters, while `ncodeunits` exposes the underlying code-unit count.

A `Char` uses single quotes and a `String` uses double quotes. Interpolation inserts a value into a string, while concatenation combines string contents. Converting bytes or normalizing text requires an explicit policy. A program should not replace invalid or meaningful distinctions simply to make two strings compare equal.

## Worked case A: UTF -8 character starts

The two-character string containing an accented Latin character and a Greek character occupies four bytes. Its valid start indices are 1 and 3. Index 2 is inside the first character and raises `StringIndexError`. Iterating over valid indices or characters produces the expected two characters without assuming a one-byte representation.

{{WORKED_A}}

## Worked case B: canonical normalization

A precomposed accented character and a letter followed by a combining accent can look alike while having different code-point sequences. Unicode normalization can map these canonically equivalent forms to a common representation. The example distinguishes character count from grapheme count and checks normalization explicitly.

{{WORKED_B}}

## Define a comparison policy

Case conversion, whitespace normalization and canonical Unicode normalization answer different questions. A user identifier, source-code symbol and natural-language search query may need different rules. Removing accents or applying compatibility normalization can erase distinctions that matter to the application. Keep the original value when provenance or exact display is important.

For bounded text processing, state whether offsets refer to bytes, characters or graphemes. A passage citation that stores byte offsets cannot be reconstructed by blindly counting visible letters. If the text is normalized before indexing, retain the normalized version and its identity; offsets into another version are not interchangeable.

## Diagnose boundary errors

An ASCII-only fixture can hide indexing mistakes. Add multibyte and combining examples, empty strings and invalid positions. Use the exception to identify the failed assumption, not to catch every indexing error and silently skip text. An empty input also needs a defined policy before taking a first character.

Text length should not be treated as a language-independent measure of information or effort. A byte budget is useful for storage and transport. A grapheme count may be useful for a user interface. A model tokenizer provides another representation with its own boundaries. These counts should not be substituted for one another without an explicit purpose.

The examples operate on authored literal strings and standard Unicode functions. They do not prove that a normalization policy is suitable for every language, identifier system or security boundary. They establish inspectable byte/character/grapheme distinctions needed before building reliable parsers, annotations and scientific text workflows.

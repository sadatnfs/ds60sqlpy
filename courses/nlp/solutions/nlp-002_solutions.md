# nlp-002: Explanatory solutions

Run `nlp-002_solution.py` to inspect the deterministic checks, then compare the reasoning below. Unicode behavior must be explained at a specified representation: bytes, code points, normalized strings or grapheme clusters. A terminal screenshot alone cannot establish which sequence was stored.

## Exercise 1: Distinguish code points from encoded bytes

The composed string contains `c`, `a`, `f` and U+00E9. UTF-8 encodes the first three in one byte each and the last in two, giving four code points and five bytes. The decomposed form replaces the last code point with U+0065 followed by U+0301. It therefore has five code points and six UTF-8 bytes.

Python string equality compares the sequences; it does not automatically apply canonical normalization. Both may display as the same word, but the strings are unequal. The reference checks numeric lengths and equality directly, so its conclusion is independent of how the console's font combines the accent. Keep the explicit encoding in the calculation because byte counts can change under a different encoding.

**Expected:** code-point lengths 4 and 5, UTF-8 lengths 5 and 6, raw inequality.

## Exercise 2: Choose and verify an equivalence rule

Both NFC outputs use the composed representation; both NFD outputs use a decomposed representation. The two inputs agree within a chosen canonical form. NFC and NFD outputs are not required to have identical sequences to each other. Treating “normalized” as a Boolean without recording the form would lose that distinction.

The idempotence loop applies each form once and then again to accents, compatibility characters, case-sensitive text and an emoji sequence. It checks that the second application does not change the first result. Passing these fixtures does not prove that normalization preserves your application semantics. For example, an identifier policy might deliberately distinguish raw values that NFKC merges. Keep the algorithmic invariant and the task-specific information policy separate.

**Expected:** equal inputs after a common canonical form, NFC length 4, NFD length 5 and idempotence for all supplied cases.

## Exercise 3: Preserve the preimages of a transformed key

A dictionary can group raw values under their NFKC result. The group under `1` contains the ordinary and circled digit. The group under `café` contains the canonically equivalent accent forms. The reference retains lists of raw values rather than using a set of normalized keys as a replacement corpus.

Those two collisions have different interpretations. The accent pair is canonically equivalent. The circled digit merge follows a compatibility policy that may be suitable for search but unsuitable for a faithful transcription. The audit makes that policy choice visible. If the same raw value appears twice, distinguish repeated observations from two different raw representations; a group size alone is not always enough to diagnose the cause.

**Expected:** two groups of two raw values, and the original list unchanged.

## Exercise 4: Do not use a matching form as a display guarantee

Case folding expands the German sharp s in `Straße` into `ss`, giving the seven-code-point string `strasse`. This is useful evidence that a case-insensitive matching transformation can change length. The Latin and Cyrillic small a remain unequal under NFC because visual resemblance is not canonical equivalence.

Preserving raw display values avoids pretending that the transformed key is the original spelling. A separate identifier-security policy may restrict script combinations or inspect confusables, but that is not implemented by NFC. The lesson's comparison is deliberately limited to a concrete pair; it does not claim that every visually similar string behaves the same way.

**Expected:** `strasse`, length 7, and unequal NFC results for the cross-script pair.

## Exercise 5: Surface corrupt bytes and retain the source evidence

The byte `0xff` cannot appear as a valid standalone UTF-8 character. Strict decoding identifies its half-open location `[3,4)`. Replacement mode yields U+FFFD at that position. The reference checks both the failure coordinates and the exact replacement code point, then asserts that the input bytes are still present.

The choice between rejecting, quarantining and accepting a marked preview belongs to the ingestion contract. A search preview may tolerate a replacement while an exact extraction audit may not. Ignoring the byte would discard evidence silently. Also distinguish decoder failure from a guessed encoding: successful decoding under some other encoding does not by itself establish what the sender intended.

**Expected:** the explicit strict error, the exact replacement output and unchanged raw bytes.

## Exercise 6: Bind annotations to their text version

The raw decomposed word has a valid span `[0,5)`. Its NFC derivative has only four code points. Python slicing normally clips an excessive end index, so merely obtaining a substring would not reveal this invalid coordinate transfer. The reference's `checked_span` explicitly checks the bounds before slicing and rejects the derivative paired with the old span.

Expansion creates a second failure. In raw `Straße`, `[4,5)` selects `ß`. In the case-folded version, the same offsets select only one `s`, although the corresponding transformed content is `ss`. Thus even offsets within bounds can be semantically wrong after a transformation. A robust design stores the raw version and spans, or maintains an explicit alignment that handles composition, expansion and deletion. A constant adjustment cannot solve every case.

**Expected:** valid raw slice, rejected out-of-range derivative coordinates and the expansion counterexample.

## Transfer after comparison

Design a record with raw bytes, decoded text, normalization form, normalized text and an annotation version. State which field each span indexes. Then add a rule that trims leading whitespace and explain how that changes your alignment needs. Do not claim the schema proves correct alignment; it makes the relevant evidence available for checks.

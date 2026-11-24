# llm-006: worked solutions

Use this unicode, bytes and tokenizer round trips reference after your own attempt. The [learner guide](../guides/llm-006.md) keeps the fixture and Expected/Verify contracts for *Trace the encoding units* to *Choose identity before splitting*, six separate actions; any implementation is acceptable if *Reject malformed UTF-8* still fails on that input.

`verify()` in the [executable reference](llm-006_solution.py) uses the Python standard library and literals only; on failure, keep the *Reject malformed UTF-8* input. A pass says nothing beyond these unicode, bytes and tokenizer round trips fixtures, so next explain code point from memory on a changed fixture. The reading worksheet remains a reading exercise, regardless of the optional arithmetic checker.

## Exercise 1: Trace the encoding units

The ASCII cat fixture has three code points and three bytes. café contains four code points but its accented character occupies two UTF-8 bytes, giving five. The single code point 🙂 occupies four bytes. These are exact fixture counts. A visible grapheme may contain several code points, so len(str) is not a universal user-perceived-character counter. Preserve the byte hex if another stage needs to prove exactly what it read rather than merely how text was displayed.

**Expected:** Counts (3,3), (4,5) and (1,4), respectively.

**Verify:** Assert all six counts and retain each encoded byte sequence as hex for inspection.

## Exercise 2: Construct a strict round trip

Under policy none, encoding with UTF-8 and decoding strictly returns each original Python string and re-encodes to the same bytes. Return the chosen policy with the record so a caller does not confuse this with normalization. No remote tokenizer is required. Strict decoding is important: accepting malformed bytes with an ignored or replacement policy could produce readable text while losing the original payload, invalidating the promised exact round trip.

**Expected:** With policy none, every fixture returns exactly its original string and bytes.

**Verify:** Assert decode(encode(text)) equality and compare raw payload hex rather than relying on visual appearance.

## Exercise 3: Diagnose canonical duplicates

Composed é has one code point and two UTF-8 bytes. The decomposed e plus combining accent has two code points and three bytes. Their raw byte hashes differ. NFC maps the decomposed version to the composed representation, so normalized strings and hashes agree. Keep both original inputs to show the normalization was deliberate. The normalized result does not preserve which raw spelling occurred, and it should not be labeled a byte-preserving transformation.

**Expected:** Raw counts are 1 versus 2 code points and 2 versus 3 bytes; NFC strings and normalized hashes match.

**Verify:** Inspect raw hashes separately from normalized hashes and preserve the original strings.

## Exercise 4: Reject malformed UTF-8

The single byte 0xff is invalid in UTF-8 and strict decoding raises UnicodeDecodeError. The explicit replacement policy yields U+FFFD, whose UTF-8 encoding is a different byte sequence. This diagnostic makes data loss observable rather than treating a successful display as evidence of a valid round trip. Another pipeline could choose replacement as its policy, but it must disclose the loss and avoid claiming that the original bytes are recoverable from the resulting text.

**Expected:** Strict decoding raises UnicodeDecodeError; replacement produces U+FFFD and cannot reproduce the original 0xff byte.

**Verify:** Capture the named exception and assert replacement re-encoding differs from the original bytes.

## Exercise 5: Handle empty and unknown policies

The empty string is a valid text value and its UTF-8 payload is b"". Strict decoding returns the same empty string. An unknown normalization policy raises ValueError instead of choosing NFC or none without permission. Valid text representation does not imply a later probabilistic score has a valid denominator: an empty target list still requires its own explicit policy. Keep these interfaces separate instead of forcing all stages to treat emptiness identically.

**Expected:** Empty text maps to empty bytes and returns empty text; unknown policy raises ValueError.

**Verify:** Assert the empty values and capture the unsupported-policy exception without selecting a fallback silently.

## Exercise 6: Choose identity before splitting

The three raw documents are distinct strings, but the two café variants normalize to one NFC identity. With tea, there are two normalized identities. If canonicalized content defines a source family, group those variants before constructing train/validation/test partitions. Otherwise validation can appear novel by filename while containing the same canonical text. This exact normalization check does not detect all semantic paraphrases; retain the broader family metadata and provenance policy for a real corpus.

**Expected:** Three raw strings but two NFC identities; the two café spellings must not be presented as independent unseen canonical sources.

**Verify:** Record raw and normalized hashes for all three documents and assert the duplicate normalized pair is grouped before partitioning.

## Inspectable reference functions

*Inspect bytes and code points* validates and reduces its input in the functions below; the executable file covers all six unicode, bytes and tokenizer round trips exercises. Keep the *Reject malformed UTF-8* assertion and its invalid-input case; never replace them with a default.

```python
from __future__ import annotations
import hashlib
import unicodedata


def encode_record(text, policy="none"):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    if policy not in {"none", "NFC"}:
        raise ValueError("policy must be none or NFC")
    normalized = text if policy == "none" else unicodedata.normalize("NFC", text)
    payload = normalized.encode("utf-8")
    return {
        "text": normalized,
        "payload": payload,
        "code_points": len(normalized),
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "policy": policy,
    }


def decode_utf8(payload):
    return bytes(payload).decode("utf-8")
```

## Retrieval and alternatives

Without the examples, explain why len(text), len(text.encode("utf-8")) and token count can all differ. Then choose a fresh combining-character fixture and state which identity policy your duplicate check uses.

Next, pick a fixture unlike *Inspect bytes and code points* to test independent recall, and explain why *Reject malformed UTF-8* rejects its case rather than naming the exception. Any notation works if code point and its denominator stay explicit; these unicode, bytes and tokenizer round trips checks say nothing about unseen model quality or safety.

# llm-006: worked solutions

Open this reference after an attempt or an explicit reveal request. Preserve
your own version beside it. The [learner guide](../guides/llm-006.md) contains
the public fixture and its independent Expected/Verify contracts. These six
sections correspond to the same six learner actions, rather than six answer
steps for one task. A different implementation is acceptable when it preserves
the stated input policy, observations and evidence boundary.

The [executable reference](llm-006_solution.py) exposes a `verify()` helper for
authors and later comparison. It uses only local literals and the declared
Python/NumPy environment. An assertion failure should retain its actual input
and smallest failing observation. A passing reference is evidence about these
fixed cases; use a changed fixture and a closed-reference explanation before
recommending progression. The reading worksheet remains a reading exercise,
regardless of the optional arithmetic checker.

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

The core functions below make the input and reduction policies explicit. The
separate executable file adds all six exercise checks. Do not replace a failed
assertion with a flattering default value or remove the invalid-input case.

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

After revealing this file, choose another fixture before treating the answer
as independent retrieval evidence. Explain why the rejected case is invalid,
not merely which exception class appeared. Alternative notation, array layout
or a direct calculation is welcome when its domain meaning and denominator
remain explicit. Keep implementation correctness separate from broad claims
about unseen model quality, reliability or safety.

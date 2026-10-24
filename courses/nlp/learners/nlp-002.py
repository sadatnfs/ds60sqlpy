"""nlp-002 learner workspace. All fixtures are local and intentionally small."""

import unicodedata as ud

composed = "café"
decomposed = "cafe\u0301"
print("Raw forms:", repr(composed), repr(decomposed))
print("NFC forms:", repr(ud.normalize("NFC", composed)), repr(ud.normalize("NFC", decomposed)))

# Exercise 1: Inspect code-point counts, UTF-8 bytes and equality for both forms.
# Expected: raw inequality, lengths4/5 and byte lengths5/6.
# Exercise 2: Compare NFC/NFD and test normalization idempotence for four forms.
# Expected: common-form equality, NFC length4 and NFD length5.
# Exercise 3: Group 1, circled1 and both accent forms by NFKC while retaining raw values.
# Expected: two groups of two distinct raw representations.
# Exercise 4: Compare case folding of Straße and the Latin/Cyrillic a pair.
# Expected: strasse length7; cross-script pair remains unequal under NFC.
# Exercise 5: Decode b"caf\xff" strictly and with replacement, preserving bytes.
# Expected: failure at byte3 and replacement U+FFFD.
# Exercise 6: Explain why raw code-point spans cannot be blindly copied after normalization.
# Expected: invalid old end5 for NFC word length4, plus a case-fold expansion counterexample.
# Add your code, assertions, policy decisions and raw evidence below.

# java-005: explanatory solutions

Open this after an attempt; see [using the solutions](../STUDY-GUIDE.md#use-the-solutions).

## Mechanism review

An array is a fixed-length indexed container. A String is immutable text represented in UTF-16 code units. Those code units are not always complete Unicode characters: an emoji outside the basic multilingual plane uses a surrogate pair. String.length counts code units, while codePointCount counts Unicode code points. Even code points do not always equal user-perceived characters, because combining marks can join a base letter. Indexing and slicing therefore need a declared unit. Immutability means a transformation returns a new String rather than editing the original; it does not mean every object containing a String is immutable.

**Array index:** A zero-based position in a fixed-length container.

**UTF-16 code unit:** A16-bit storage unit used by Java String indexing.

**Code point:** A Unicode scalar identity represented by one or two UTF-16 units.

## Reading the reference

Array indices start at 0 and stop before length. Arrays.copyOf creates a separate array, while assigning another variable shares the original array reference. String.codePoints produces integer Unicode values. substring uses UTF-16 offsets and can split a surrogate pair if given an arbitrary index. Normalizer.normalize with NFC is an explicit identity policy, not an automatic rule for every text field.

## Exercise 1: Copy array storage: change one input

Task: Change `int[] original = { 1, 2, 3 };` to `int[] original = { 2, 2, 3 };` in Example A and predict which assertion fails and why.

The new array owns its storage. A simple assignment copy=original would alias the same array and make the mutation visible through both variables.

The unchanged code is the part that Example A adds:

```java
int[] original = { 1, 2, 3 };
int[] copy = Arrays.copyOf(original, original.length);
copy[0] = 9;
assert original[0] == 1 && copy[0] == 9;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `original[0] == 1 && copy[0] == 9`.

**Verify:** Name the value that makes `original[0] == 1 && copy[0] == 9` false, then restore the line.

## Exercise 2: Count text units: diagnose an edited check

Task: Example B's new assertion was edited to `assert text.codePointCount(1, text.length()) == 2;`. Explain why it fails for unchanged state and restore it.

The emoji occupies a surrogate pair. Treating length as a visible-character count would overcount this simple example.

The unchanged code is the part that Example B adds:

```java
String text = "A\ud83d\ude42";
assert text.length() == 3;
assert text.codePointCount(0, text.length()) == 2;
```

**Expected:** The edited run fails with an `AssertionError` from the assertion on `text.codePointCount(0, text.length()) == 2`; the restored assertion passes.

**Verify:** Explain why the edited assertion rejects the state that `text.codePointCount(0, text.length()) == 2` accepts.

## Exercise 3: Observe String immutability

Task: Convert lowercase red to uppercase and retain both references.

The method returns a new value rather than changing lower. Locale.ROOT makes the case policy explicit for a language-neutral fixture.

```java
String lower = "red";
String upper = lower.toUpperCase(Locale.ROOT);
assert lower.equals("red") && upper.equals("RED");
```

**Expected:** original red; new RED.

**Verify:** Control: changing `String lower = "red";` to `String lower = "red!";` must fail the assertion on `lower.equals("red") && upper.equals("RED")`.

## Exercise 4: Select by code-point offset

Task: Find the UTF-16 offset of the second code point and take the remaining substring.

Converting a code-point position to a UTF-16 offset respects surrogate boundaries. Arbitrarily slicing at the second surrogate would create malformed text.

```java
int offset = text.offsetByCodePoints(0, 1);
String emoji = text.substring(offset);
assert emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1;
```

**Expected:** substring is the intact emoji with length 2.

**Verify:** Control: changing `int offset = text.offsetByCodePoints(0, 1);` to `int offset = text.offsetByCodePoints(1, 1);` must fail the assertion on `emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1`.

## Exercise 5: Normalize deliberately

Task: Compare composedé ande plus combining acute before and after NFC.

Normalization can merge representations that look equivalent. Whether that is appropriate for an identifier, password or display field is a domain decision.

```java
String composed = "é";
String decomposed = "é";
assert !composed.equals(decomposed);
assert java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(
  composed
);
```

**Expected:** raw strings differ; normalized strings equal.

**Verify:** Control: changing `String composed = "é";` to `String composed = "é!";` must fail the assertion on `java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed)`.

## Exercise 6: Reject an invalid array index

Task: Read index 3 from a length 3 array and catch the boundary failure.

The highest valid index is length-1. A container having three elements does not make index 3 valid.

```java
boolean invalid = false;
try {
  int ignored = original[3];
} catch (ArrayIndexOutOfBoundsException expected) {
  invalid = true;
}
assert invalid;
```

**Expected:** ArrayIndexOutOfBoundsException.

**Verify:** Control: changing `invalid = true;` to `invalid = false;` must fail the assertion on `invalid`.

## After comparing the answer

Add a fixture with a letter followed by a combining mark and show that `codePointCount` reports 2 even though a reader sees one character; that case needs grapheme-level tools such as `java.text.BreakIterator`.

Run the complete reference with `java -ea Main` first; the [review routine](../STUDY-GUIDE.md#use-the-solutions) covers the rest.

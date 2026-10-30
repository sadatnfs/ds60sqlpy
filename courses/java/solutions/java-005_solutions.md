# java-005: explanatory solutions

Open after an attempt or an explicit solution reveal. The executable reference runs the six exercise checks together as `Main.java`. The guide contains independent worked examples, while this file explains the choices and failure cases in the complete answer.

## Mechanism review

An array is a fixed-length indexed container. A String is immutable text represented in UTF-16 code units. Those code units are not always complete Unicode characters: an emoji outside the basic multilingual plane uses a surrogate pair. String.length counts code units, while codePointCount counts Unicode code points. Even code points do not always equal user-perceived characters, because combining marks can join a base letter. Indexing and slicing therefore need a declared unit. Immutability means a transformation returns a new String rather than editing the original; it does not mean every object containing a String is immutable.

**Array index:** A zero-based position in a fixed-length container.

**UTF-16 code unit:** A16-bit storage unit used by Java String indexing.

**Code point:** A Unicode scalar identity represented by one or two UTF-16 units.

## Reading the reference

Array indices start at0 and stop before length. Arrays.copyOf creates a separate array, while assigning another variable shares the original array reference. String.codePoints produces integer Unicode values. substring uses UTF-16 offsets and can split a surrogate pair if given an arbitrary index. Normalizer.normalize with NFC is an explicit identity policy, not an automatic rule for every text field.

## Exercise 1: Copy array storage

Task: Copy array 1,2,3,mutate the copy and compare the original.

The new array owns its storage. A simple assignment copy=original would alias the same array and make the mutation visible through both variables.

```java
int[] original = { 1, 2, 3 };
int[] copy = Arrays.copyOf(original, original.length);
copy[0] = 9;
assert original[0] == 1 && copy[0] == 9;
```

**Expected:** original starts 1; copy starts 9.

**Verify:** Compare the program values or named exception with original starts 1; copy starts 9. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 2: Count text units

Task: Inspect stringA followed by an emoji.

The emoji occupies a surrogate pair. Treatinglength as a visible-character count would overcount this simple example.

```java
String text = "A\ud83d\ude42";
assert text.length() == 3;
assert text.codePointCount(0, text.length()) == 2;
```

**Expected:** length3 code units;2 code points.

**Verify:** Compare the program values or named exception with length3 code units;2 code points. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 3: Observe String immutability

Task: Convert lowercasered to uppercase and retain both references.

The method returns a new value rather than changing lower. Locale.ROOT makes the case policy explicit for a language-neutral fixture.

```java
String lower = "red";
String upper = lower.toUpperCase(Locale.ROOT);
assert lower.equals("red") && upper.equals("RED");
```

**Expected:** originalred;newRED.

**Verify:** Compare the program values or named exception with originalred;newRED. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 4: Select by code-point offset

Task: Find the UTF-16 offset of the second code point and take the remaining substring.

Converting a code-point position to a UTF-16 offset respects surrogate boundaries. Arbitrarily slicing at the second surrogate would create malformed text.

```java
int offset = text.offsetByCodePoints(0, 1);
String emoji = text.substring(offset);
assert emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1;
```

**Expected:** substring is the intact emoji withlength2.

**Verify:** Compare the program values or named exception with substring is the intact emoji withlength2. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 5: Normalize deliberately

Task: Compare composedé ande plus combining acute before and afterNFC.

Normalization can merge representations that look equivalent. Whether that is appropriate for an identifier, password or display field is a domain decision.

```java
String composed = "é";
String decomposed = "é";
assert !composed.equals(decomposed);
assert java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(
  composed
);
```

**Expected:** raw strings differ;normalized strings equal.

**Verify:** Compare the program values or named exception with raw strings differ;normalized strings equal. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## Exercise 6: Reject an invalid array index

Task: Readindex3 from a length3 array and catch the boundary failure.

The highest valid index islength-1. A container having three elements does not makeindex3 valid.

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

**Verify:** Compare the program values or named exception with ArrayIndexOutOfBoundsException. Keep the input that distinguishes this case from the preceding exercise. The assertion must be capable of failing when that condition is broken.

## After comparing the answer

Run the complete reference with assertions enabled, then return to your own implementation. Recreate one check with different values and explain its expected result before execution. A compiler error, an expected domain exception and an assertion failure represent different stages and should be reported separately. Preserve ownership boundaries when adapting file, network or concurrency examples. The reference never authorizes access to a shared service or deletion of learner state. Use a fresh tiny fixture when you need to distinguish two interpretations of an API contract.

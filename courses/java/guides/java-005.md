# java-005: Arrays, strings and Unicode

## Level and prerequisites

Beginner, approximately 90 minutes. Direct prerequisites: `java-004`

## Learning objectives

Copy arrays safely and count, slice and normalize strings by code point instead of by UTF-16 unit.

The six exercises practice these steps:

- Copy array storage.
- Count text units.
- Observe String immutability.
- Select by code-point offset.
- Normalize deliberately.
- Reject an invalid array index.

## Purpose and mental model

An array is a fixed-length indexed container. A String is immutable text represented in UTF-16 code units. Those code units are not always complete Unicode characters: an emoji outside the basic multilingual plane uses a surrogate pair. String.length counts code units, while codePointCount counts Unicode code points. Even code points do not always equal user-perceived characters, because combining marks can join a base letter. Indexing and slicing therefore need a declared unit. Immutability means a transformation returns a new String rather than editing the original; it does not mean every object containing a String is immutable.

## Vocabulary and concepts

**Array index:** A zero-based position in a fixed-length container.

**UTF-16 code unit:** A16-bit storage unit used by Java String indexing.

**Code point:** A Unicode scalar identity represented by one or two UTF-16 units.

## How to run this lesson

Example B and Exercise 4 build an emoji from a surrogate pair and Exercise 5 uses an accented letter; the checks count code units and code points, so how your terminal draws them does not affect any result.

Classroom and native JDK steps, the exercise controls and the hint routine are in the [Java study guide](../STUDY-GUIDE.md).



## Syntax anatomy and execution trace

Array indices start at 0 and stop before length. Arrays.copyOf creates a separate array, while assigning another variable shares the original array reference. String.codePoints produces integer Unicode values. substring uses UTF-16 offsets and can split a surrogate pair if given an arbitrary index. Normalizer.normalize with NFC is an explicit identity policy, not an automatic rule for every text field.

## Worked example / walkthrough

### Example A: Copy array storage

The new array owns its storage. A simple assignment copy=original would alias the same array and make the mutation visible through both variables.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int[] original = { 1, 2, 3 };
    int[] copy = Arrays.copyOf(original, original.length);
    copy[0] = 9;
    assert original[0] == 1 && copy[0] == 9;
  }
}
```

**Expected:** original starts 1; copy starts 9.

### Example B: Count text units

The emoji occupies a surrogate pair. Treating length as a visible-character count would overcount this simple example.

```java
import java.util.*;

public class Main {

  public static void main(String[] args) throws Exception {
    int[] original = { 1, 2, 3 };
    int[] copy = Arrays.copyOf(original, original.length);
    copy[0] = 9;
    assert original[0] == 1 && copy[0] == 9;

    String text = "A\ud83d\ude42";
    assert text.length() == 3;
    assert text.codePointCount(0, text.length()) == 2;
  }
}
```

**Expected:** length 3 code units; 2 code points.

## Prediction before your attempt

Before running Example A, decide whether setting `copy[0]` to 9 also changes `original[0]`, and what would happen if the copy were made with `copy = original`. For Example B, write the values of `text.length()` and `text.codePointCount(0, text.length())` for the letter A followed by one emoji. Then predict what `text.substring(0, 2)` holds: the letter and only the first half of the surrogate pair.

## Exercises

1. **Copy array storage: change one input.** Change `int[] original = { 1, 2, 3 };` to `int[] original = { 2, 2, 3 };` in Example A and predict which assertion fails and why.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `original[0] == 1 && copy[0] == 9`.
   **Verify:** Name the value that makes `original[0] == 1 && copy[0] == 9` false, then restore the line.

2. **Count text units: diagnose an edited check.** Example B's new assertion was edited to `assert text.codePointCount(1, text.length()) == 2;`. Explain why it fails for unchanged state and restore it.
   **Expected:** The edited run fails with an `AssertionError` from the assertion on `text.codePointCount(0, text.length()) == 2`; the restored assertion passes.
   **Verify:** Explain why the edited assertion rejects the state that `text.codePointCount(0, text.length()) == 2` accepts.

3. **Observe String immutability.** Convert lowercase red to uppercase and retain both references.
   **Expected:** original red; new RED.
   **Verify:** Control: changing `String lower = "red";` to `String lower = "red!";` must fail the assertion on `lower.equals("red") && upper.equals("RED")`.

4. **Select by code-point offset.** Find the UTF-16 offset of the second code point and take the remaining substring.
   **Expected:** substring is the intact emoji with length 2.
   **Verify:** Control: changing `int offset = text.offsetByCodePoints(0, 1);` to `int offset = text.offsetByCodePoints(1, 1);` must fail the assertion on `emoji.length() == 2 && emoji.codePointCount(0, emoji.length()) == 1`.

5. **Normalize deliberately.** Compare composedé ande plus combining acute before and after NFC.
   **Expected:** raw strings differ; normalized strings equal.
   **Verify:** Control: changing `String composed = "é";` to `String composed = "é!";` must fail the assertion on `java.text.Normalizer.normalize(decomposed, java.text.Normalizer.Form.NFC).equals(composed)`.

6. **Reject an invalid array index.** Read index 3 from a length 3 array and catch the boundary failure.
   **Expected:** ArrayIndexOutOfBoundsException.
   **Verify:** Control: changing `invalid = true;` to `invalid = false;` must fail the assertion on `invalid`.

## Common pitfalls and diagnosis

The usual mistake is treating `length()` and `charAt` as counting characters. They count UTF-16 code units, so slicing at an arbitrary index can split a surrogate pair and produce malformed text; convert a code-point position with `offsetByCodePoints` first. Another mistake is assuming that strings that look identical are `equals`: é can be one code point, or e plus a combining accent, until you normalize. For arrays, `copy = original` copies a reference, not the elements.

General compiler, runtime and assertion triage: [diagnose a failure](../STUDY-GUIDE.md#diagnose-a-failure).

## Progressive hints

Read one rung at a time, as described in [using hints](../STUDY-GUIDE.md#use-hints-one-at-a-time).

- **Exercise 1:** First note that the edit changes the first element of `original` to 2 before any copy is made. Then trace which array the later write of 9 changes. Finally, compare `original[0]` with the 1 the assertion expects and say which half of the condition fails.
- **Exercise 2:** First locate the code units of the fixture: index 0 holds A, and indexes 1 and 2 hold the surrogate pair. Then count the code points in the range the edited assertion uses, which starts at index 1. Finally, compare that count with 2 and decide whether the text or the claim changed.
- **Exercise 3:** First call `toUpperCase(Locale.ROOT)` on `lower` and keep the result in a second variable. Then compare the two variables with "red" and "RED". Finally, explain why no method on `String` can change the original object.
- **Exercise 4:** First convert the code-point index 1 to a UTF-16 offset with `offsetByCodePoints(0, 1)`. Then take the substring from that offset to the end. Finally, assert that the result has two code units but one code point, which shows the surrogate pair stayed intact.
- **Exercise 5:** First build one string with the precomposed é and one with e followed by the combining acute accent `\u0301`. Then compare them with `equals` before normalizing. Finally, normalize both with `Normalizer.Form.NFC`, compare again, and decide whether your field should treat them as the same.
- **Exercise 6:** First read index 3 of a three-element array inside a `try` block. Then catch `ArrayIndexOutOfBoundsException` and record that it happened. Finally, explain why the largest valid index is `length - 1`.

## Self-check and retrieval

From memory, explain the difference between a code unit, a code point and a user-perceived character, using the emoji fixture as your example. Say why `toUpperCase` leaves the original string unchanged, why the last valid index of a length-3 array is 2, and when NFC normalization is a domain decision rather than an automatic fix.

## Next step

Continue with `java-006`: Lists, sets and maps. Keep your six observations; see [moving on](../STUDY-GUIDE.md#move-to-the-next-lesson).

## Sources and verification status

[Official Java 21 API or language reference](https://docs.oracle.com/en/java/javase/21/docs/api/index.html), reviewed 2026-10-22. Evidence levels: [sources and evidence](../STUDY-GUIDE.md#sources-and-evidence).

## Ask an AI tutor about this lesson

```text
Use $guide-ds60sqlpy-learning for java-005: Arrays, strings and Unicode.
Read courses/java/guides/java-005.md and courses/java/lessons/java-005.java. Direct prerequisites: `java-004`.
Explain the mechanism, ask for a prediction, review my attempt, give one hint,
request compiler/runtime evidence, and ask a fresh retrieval question.
Keep courses/java/solutions/ closed until I request comparison or show an attempt.
Use Java 21 and the declared offline fixture. Done when I can explain the state
transitions, pass all six exercise contracts, diagnose one failure and solve a
new boundary case without copying the solution.
```

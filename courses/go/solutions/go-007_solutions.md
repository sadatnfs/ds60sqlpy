# go-007: explained solutions

Compare after an attempt ([using solutions](../STUDY-GUIDE.md#use-the-solutions)). `courses/go/solutions/go-007_solution.go` implements all six cases.

## Mechanism

A Go string is an immutable sequence of bytes, not necessarily valid Unicode text. Source string literals are commonly UTF-8, but strings can contain arbitrary bytes. Indexing a string returns one byte. Ranging over a string decodes runes, which are Unicode code points; malformed encodings produce replacement runes. A user-perceived character can contain multiple code points, such as a letter plus combining accent. Byte length, rune count and displayed-character count therefore answer different questions. Choose a unit before slicing, counting or truncating text. Immutability protects a string value, while conversion to a mutable byte slice creates a separate editing representation.

len(text) counts bytes. []byte(text) and []rune(text) choose different element units. utf8.RuneCountInString counts decoded code points, while utf8.ValidString checks encoding validity. strings.TrimSpace removes surrounding Unicode whitespace and returns a string. A rune literal uses single quotes and has a numeric code-point value; a string literal uses double quotes.

## 1. Count two units: change one input

Copy worked example 1, change `text := "A🙂"` to `text := "A🙂!"` and predict the failure before running; then restore the line.

The unchanged code is worked example 1:

```go
text := "A🙂"
check(len(text) == 5 && utf8.RuneCountInString(text) == 2, "text units")
```

**Expected:** The edited run panics with `text units` because `len(text) == 5 && utf8.RuneCountInString(text) == 2` no longer holds.

**Verify:** Restoring `text := "A🙂"` makes the check pass again with the worked observation: there are 5 bytes and 2 runes.

The ASCII letter occupies one byte and this emoji occupies four. Neither count is a general grapheme-cluster algorithm.

**Approach.** Count the edited string in two units. `A` and `!` are one byte each and U+1F642 needs four bytes in UTF-8, so `len(text)` becomes 6 while `utf8.RuneCountInString(text)` becomes 3.

**Why it holds here.** `len` on a string always reports bytes, so the first operand `len(text) == 5` is false as soon as one more ASCII byte is appended, and `check` panics with `text units`.

**A plausible wrong approach.** Assuming the emoji counts as two units, as `"🙂".length` does in JavaScript's UTF-16 strings, and predicting lengths of 3 and 4 for the original and edited strings. Go strings hold UTF-8 bytes, so the lengths really are 5 and 6.

**Verify.** Print `len(text), utf8.RuneCountInString(text)`: the edited run shows `6 3` before the `text units` panic, and the restored line shows `5 2` and the success line.

## 2. Edit a copied byte slice: debug a regression

A one-token regression in worked example 2 makes a line read `data[1] = 'b'`. Repair it without changing the check.

The unchanged code is worked example 2:

```go
original := "cat"
data := []byte(original)
data[0] = 'b'
check(original == "cat" && string(data) == "bat", "copy edit")
```

**Expected:** The defective run panics with `copy edit`; after restoring `data[0] = 'b'`, the original is cat and the new string is bat.

**Verify:** The failing run shows message `copy edit`; after the repair `original == "cat" && string(data) == "bat"` holds again.

The mutable byte slice provides an explicit editing boundary. This example uses ASCII so replacing one byte does not split a multibyte encoding.

**Approach.** Trace the copy and the edit separately. `[]byte(original)` allocates new storage holding `c a t`, and the regressed `data[1] = 'b'` overwrites the `a`, producing `cbt`.

**Why it holds here.** `original` is untouched in both versions because strings are immutable and the conversion copied its bytes, so the failing operand is `string(data) == "bat"`. Writing index 0 replaces the `c` and restores `bat`.

**A plausible wrong approach.** Trying to edit the string directly with `original[0] = 'b'`. The compiler rejects it because string bytes cannot be assigned, which is exactly why the lesson converts to a byte slice first.

**Verify.** Print `original, string(data)`: the regression shows `cat cbt` and the repair shows `cat bat`, and only the repaired run reaches the success line.

## 3. Reject malformed encoding

Build a string from the single byte 0xff.

```go
text := string([]byte{0xff})
check(!utf8.ValidString(text), "invalid encoding")
```

**Expected:** UTF-8 validation returns false.

**Verify:** Your solution must keep `!utf8.ValidString(text)` true. Control: changing `check(!utf8.ValidString(text), "invalid encoding")` to `check(utf8.ValidString(text), "invalid encoding")` panics with message `invalid encoding`; revert it.

A string can exist without being valid UTF-8. Validation is a separate input contract, not an automatic property of the string type.

**Approach.** Build a one-byte string from 0xff and ask `utf8.ValidString` about it, expecting false.

**Why it holds here.** No UTF-8 sequence can start with 0xff, and the conversion `string([]byte{0xff})` copies bytes without checking them, so the string exists but fails validation.

**A plausible wrong approach.** Testing validity with `utf8.RuneCountInString(text) == 0`. It returns 1 because each invalid byte is counted as one `utf8.RuneError`, so the malformed input would look like a normal one-rune string.

**Verify.** Print `len(text)`, `utf8.ValidString(text)` and `[]rune(text)`: the output is `1`, `false` and `[65533]`, where 65533 is the replacement character produced by decoding.

## 4. Slice by rune position

Convert A and the emoji to runes and retain the second rune.

```go
r := []rune("A🙂")
check(string(r[1:]) == "🙂", "rune slice")
```

**Expected:** The resulting string is the intact emoji.

**Verify:** Your solution must keep `string(r[1:]) == "🙂"` true. Control: changing `check(string(r[1:]) == "🙂", "rune slice")` to `check(string(r[2:]) == "🙂", "rune slice")` panics with message `rune slice`; revert it.

The conversion makes code-point indexing explicit. Arbitrary byte slicing could instead cut through the emoji encoding.

**Approach.** Convert `"A🙂"` to `[]rune`, which yields two code points, and slice from index 1 so the emoji stays whole.

**Why it holds here.** Rune indexes count code points rather than bytes, so `r[1:]` holds exactly U+1F642 and converting it back encodes the same four bytes.

**A plausible wrong approach.** Byte-slicing the original string as `"A🙂"[1:2]` to get the second character. That yields the single lead byte 0xf0, which is invalid UTF-8 and prints as a replacement character instead of the emoji.

**Verify.** Print `len(r)` and `len(string(r[1:]))` to see 2 and 4, and confirm `utf8.ValidString(string(r[1:]))` is true while the byte slice `[1:2]` is not valid.

## 5. Separate combining forms

Count runes in e followed by a combining accent.

```go
text := "e\u0301"
check(utf8.RuneCountInString(text) == 2, "combining")
```

**Expected:** There are 2 runes even though it can display as one character.

**Verify:** Your solution must keep `utf8.RuneCountInString(text) == 2` true. Control: changing `text := "e\u0301"` to `text := "e\u0301!"` panics with message `combining`; revert it.

A code point is not always a complete displayed character. Normalization and grapheme segmentation are distinct operations beyond this counting primitive.

**Approach.** Count runes in `"e\u0301"`: the letter `e` plus U+0301 COMBINING ACUTE ACCENT, which is two code points even though it can display as one character.

**Why it holds here.** `RuneCountInString` counts code points, so the result is 2. The string is three bytes because the combining mark needs two bytes in UTF-8.

**A plausible wrong approach.** Expecting 1 because the output looks like `é`, or comparing it with the precomposed `"\u00e9"`. That form is one rune, and `"e\u0301" == "\u00e9"` is false because Go compares bytes and the standard library does not normalize.

**Verify.** Print `utf8.RuneCountInString` and `len` for both spellings: `"e\u0301"` gives 2 runes and 3 bytes, while `"\u00e9"` gives 1 rune and 2 bytes.

## 6. Transfer a whitespace policy

Trim surrounding whitespace from a label without changing its internal space.

```go
label := strings.TrimSpace(" \tblue sky\n")
check(label == "blue sky", "trim")
```

**Expected:** The result is blue sky.

**Verify:** Your solution must keep `label == "blue sky"` true. Control: changing `label := strings.TrimSpace(" \tblue sky\n")` to `label := strings.TrimSpace(" \tblue sky\n!")` panics with message `trim`; revert it.

Trimming is a domain policy. It is appropriate for this display label, but could corrupt a field where leading spaces are meaningful.

**Approach.** Apply `strings.TrimSpace` to `" \tblue sky\n"`, which removes leading and trailing Unicode whitespace and leaves interior characters alone.

**Why it holds here.** The leading space and tab and the trailing newline are all whitespace, while the space between `blue` and `sky` is interior, so the result is exactly `blue sky`.

**A plausible wrong approach.** Using `strings.Trim(raw, " ")` or `strings.ReplaceAll(raw, " ", "")` on the raw input. The first trims only spaces, leaving the tab and newline, and the second also deletes the interior space and returns `\tbluesky\n`.

**Verify.** Print with `fmt.Printf("%q\n", label)` so invisible characters show: it prints `"blue sky"`, while the `Trim` version prints `"\tblue sky\n"`.

## Transfer after comparison

Repeat the measurements with `"naïve"` written with the precomposed U+00EF. Predict 6 bytes and 5 runes, take the first three runes as `naï` with a rune slice, show that the byte slice `[:3]` gives `na` plus a broken lead byte, and trim `"\n naïve \t"` to `naïve`. Explain which check byte indexing or a space-only trim would fail.

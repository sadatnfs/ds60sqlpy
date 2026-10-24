# go-007: explained solutions

These are comparison material after an attempt or explicit reveal. The executable reference implements all six cases in one `main.go`.

## Mechanism

A Go string is an immutable sequence of bytes, not necessarily valid Unicode text. Source string literals are commonly UTF-8, but strings can contain arbitrary bytes. Indexing a string returns one byte. Ranging over a string decodes runes, which are Unicode code points; malformed encodings produce replacement runes. A user-perceived character can contain multiple code points, such as a letter plus combining accent. Byte length, rune count and displayed-character count therefore answer different questions. Choose a unit before slicing, counting or truncating text. Immutability protects a string value, while conversion to a mutable byte slice creates a separate editing representation.

len(text) counts bytes. []byte(text) and []rune(text) choose different element units. utf8.RuneCountInString counts decoded code points, while utf8.ValidString checks encoding validity. strings.TrimSpace removes surrounding Unicode whitespace and returns a string. A rune literal uses single quotes and has a numeric code-point value; a string literal uses double quotes.

## 1. Count two units

Inspect A followed by a smiling face.

```go
text := "A🙂"
check(len(text) == 5 && utf8.RuneCountInString(text) == 2, "text units")
```

**Expected:** There are 5 bytes and 2 runes.

The ASCII letter occupies one byte and this emoji occupies four. Neither count is a general grapheme-cluster algorithm.

## 2. Edit a copied byte slice

Convert cat to bytes, replace c with b and retain the original.

```go
original := "cat"
data := []byte(original)
data[0] = 'b'
check(original == "cat" && string(data) == "bat", "copy edit")
```

**Expected:** The original is cat and the new string is bat.

The mutable byte slice provides an explicit editing boundary. This example uses ASCII so replacing one byte does not split a multibyte encoding.

## 3. Reject malformed encoding

Build a string from the single byte 0xff.

```go
text := string([]byte{0xff})
check(!utf8.ValidString(text), "invalid encoding")
```

**Expected:** UTF-8 validation returns false.

A string can exist without being valid UTF-8. Validation is a separate input contract, not an automatic property of the string type.

## 4. Slice by rune position

Convert A and the emoji to runes and retain the second rune.

```go
r := []rune("A🙂")
check(string(r[1:]) == "🙂", "rune slice")
```

**Expected:** The resulting string is the intact emoji.

The conversion makes code-point indexing explicit. Arbitrary byte slicing could instead cut through the emoji encoding.

## 5. Separate combining forms

Count runes in e followed by a combining accent.

```go
text := "e\u0301"
check(utf8.RuneCountInString(text) == 2, "combining")
```

**Expected:** There are 2 runes even though it can display as one character.

A code point is not always a complete displayed character. Normalization and grapheme segmentation are distinct operations beyond this counting primitive.

## 6. Transfer a whitespace policy

Trim surrounding whitespace from a label without changing its internal space.

```go
label := strings.TrimSpace(" \tblue sky\n")
check(label == "blue sky", "trim")
```

**Expected:** The result is blue sky.

Trimming is a domain policy. It is appropriate for this display label, but could corrupt a field where leading spaces are meaningful.

## Transfer after comparison

Return to your own pad and reproduce one check with a new input. Explain why the check rejects a plausible wrong implementation. Keep the distinction between a pure model, an in-process fake, and a real external system visible in your notes.

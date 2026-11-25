# csharp-004: explanation and comparison

Reference program: [csharp-004_solution.cs](csharp-004_solution.cs), covering both examples and the executed answers.

Attempt the tasks first; see [comparing with the explanation](../STUDY-GUIDE.md#comparing-with-the-explanation).

## Why the two examples differ

**Immutable transformations:** Assignment of the returned value is necessary to keep a transformation. An explicit comparison policy prevents dependence on ambient culture. The original remains data while the result is DATA.

**Choose the counting unit:** The fixture disproves the assumption that Length is a universal character count. One scalar occupies two UTF-16 units and four UTF-8 bytes.

## Task answers

### Task 1: Predict and explain

Predict both string values after ToUpperInvariant and explain ownership of the result.

**Written answer.** After the call, `original` is still `"data"` and `changed` is `"DATA"`. `ToUpperInvariant` does not alter the string it is called on; it builds and returns a new string object, and the caller owns that result through `changed`.

**Why it is correct.** `string` is immutable in .NET: no method can change the characters of an existing instance. Every transforming method such as `ToUpperInvariant`, `Trim` or `Replace` returns a new instance, and the original variable keeps referring to the original object.

**Plausible wrong approach.** Predicting that both variables now hold `"DATA"` treats the call as in-place mutation. Code built on that idea, such as calling `name.ToUpperInvariant();` on its own line, discards the result and leaves `name` unchanged.

**How to verify.** Example A already checks `original == "data" && changed == "DATA"`. Add `Check(!ReferenceEquals(original, changed), "new object")` to confirm the result is a separate string.

### Task 2: Guided modification

Build an interpolated label containing a count and a unit.

**Reference answer.** It runs as the `Task 2` block of the reference program.

```csharp
string Label(int count) {
  string unit = count == 1 ? "file" : "files";
  return $"{count} {unit}";
}
Check(Label(3) == "3 files", "plural label");
Check(Label(1) == "1 file", "singular label");
Check(Label(0) == "0 files", "zero uses the plural");
```

**Observe:** The labels are 3 files, 1 file and 0 files.

The interpolated string `$"{count} {unit}"` formats the number and inserts the unit chosen just before it. Choosing the unit in a separate line keeps the grammar rule visible and testable, and checking 1 and 0 covers the two counts where English plurals usually go wrong.

**Plausible wrong approach.** Writing `$"{count} file(s)"` avoids the decision and produces `1 file(s)` for every count. Hardcoding `"files"` instead produces the incorrect `1 files`.

**How to verify.** Call `Label(1000)` and check the result is `1000 files`: `int` formatting adds no group separator by default. If a display needs `1,000`, format with an explicit culture and test that string separately.

### Task 3: Independent construction

Implement case-insensitive machine-key comparison with an explicit policy.

**Reference answer.** It runs as the `Task 3` block of the reference program.

```csharp
bool SameKey(string left, string right) {
  return string.Equals(left, right, StringComparison.OrdinalIgnoreCase);
}
Check(SameKey("Report-ID", "report-id"), "case-insensitive match");
Check(!SameKey("report-id", "report_id"), "different characters differ");
Check(SameKey("i", "I"), "ordinal policy, no culture rules");
```

**Observe:** Keys that differ only by ASCII case match; a different separator does not.

OrdinalIgnoreCase compares machine keys by code unit with simple case folding, so the result does not depend on the current culture.

### Task 4: Diagnose a defect

Diagnose code that takes one char from the emoji and assumes it is a complete symbol.

**Written answer.** `char first = symbol[0];` for `symbol = "😀"` yields `\uD83D`, the high surrogate of the pair that encodes U+1F600. It is half of a symbol: printed or encoded on its own it becomes the replacement character, not a smiley. Take a whole scalar with `Rune.GetRuneAt(symbol, 0)` or `symbol.EnumerateRunes().First()`, whose value is 0x1F600.

**Why it is correct.** A `char` is one UTF-16 code unit. Code points above U+FFFF need two units, a high surrogate followed by a low surrogate, which is why Example B reports `Length == 2`. Indexing returns a single unit, so it cannot represent the emoji.

**Plausible wrong approach.** Using `symbol.Substring(0, 1)` instead of indexing has the same flaw, because it also counts UTF-16 units. Truncating display names with `name[..20]` can likewise cut through an emoji and leave a broken surrogate at the end.

**How to verify.** Check `char.IsHighSurrogate(symbol[0])` is true and `Rune.GetRuneAt(symbol, 0).Value == 0x1F600`. Also check `Encoding.UTF8.GetString(Encoding.UTF8.GetBytes(symbol[0].ToString())) == "\uFFFD"` to see the damaged half.

### Task 5: Boundary evidence

Compare ASCII, an emoji and a combining-mark sequence using code units and text elements.

**Reference answer.** It runs as the `Task 5` block of the reference program.

```csharp
string ascii = "A";
string emoji = "\U0001F600";
string accented = "e\u0301";
int Elements(string text) => new StringInfo(text).LengthInTextElements;
Check(ascii.Length == 1 && Elements(ascii) == 1, "ASCII");
Check(emoji.Length == 2 && Elements(emoji) == 1, "emoji");
Check(accented.Length == 2 && Elements(accented) == 1, "combining mark");
Check(accented.EnumerateRunes().Count() == 2, "two scalars");
```

**Observe:** Each input is one text element, but the emoji and the accented e each use two UTF-16 code units.

`A` is one code unit and one text element. The emoji is one scalar stored as two code units. `e` followed by U+0301 COMBINING ACUTE ACCENT is two scalars and two code units that a reader sees as one character, so `StringInfo.LengthInTextElements` reports 1 for all three while `Length` reports 1, 2 and 2.

**Plausible wrong approach.** Counting runes instead of code units fixes the emoji but not the accent: `EnumerateRunes` still sees two scalars in `e\u0301`. Only text elements match what a reader counts as characters.

**How to verify.** Normalize the accented string with `accented.Normalize(NormalizationForm.FormC)` and check its `Length` becomes 1, because the precomposed é exists. A flag emoji such as U+1F1FA U+1F1F8 shows the opposite: four code units, two runes and one text element.

### Task 6: Transfer and justify

Design a text-field limit and explain whether its contract measures bytes, scalars or user-visible graphemes.

No single answer exists; extend task 3 using the [open transfer routine](../STUDY-GUIDE.md#open-transfer-tasks).

## Mechanism and diagnostic reasoning

A string is an immutable sequence of UTF-16 code units. Immutability means an operation such as replacement returns a new string; it does not edit the original object. Human-visible characters are more complicated than code units: some Unicode scalar values need two units, and a visible grapheme can combine several scalar values. Choose the unit that matches the task before counting or slicing text.

Text comparison also has a policy. Machine identifiers usually need ordinal comparison; user-facing sorting can need culture rules. Encoding turns text into bytes for a file or protocol. UTF-8 byte length is not string Length, and neither is automatically the number of visible characters. Keep these boundaries distinct when limiting input.

`$"item {count}"` interpolates a value. `StringComparison.OrdinalIgnoreCase` makes a comparison policy explicit. `EnumerateRunes()` visits Unicode scalar values. `Encoding.UTF8.GetByteCount` measures an encoded representation.

Indexing a string can split a surrogate pair. Invariant casing is useful for stable transformations but is not a universal user-language display rule. Normalization and comparison are separate policies.

## Review before continuing

Run the reference and confirm it prints `csharp-004: passed`, then rerun the guide's counterexample.

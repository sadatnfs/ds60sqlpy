# js-008: explanatory solutions

Use these answers after an attempt or an explicit reveal. The reference uses the same literal fixtures as the guide and keeps the exercises in separate scopes. A successful run checks these examples; explaining a changed input is a separate learning goal.

## Mechanism review

JavaScript strings are sequences of UTF-16 code units. length and indexing count those units, which do not always correspond to complete Unicode codepoints. A supplementary emoji occupies a surrogate pair, and a visible letter can combine several codepoints. Iteration with for...of or spread uses codepoints, while grapheme segmentation requires an additional text policy. Normalization can map canonically equivalent spellings to one representation, but should not be applied silently to every identifier or secret.

Regular expressions are programs over text, not literal string containers. User text containing dots, brackets or quantifiers can change a pattern if inserted without escaping. The prepared Node 24 runtime supports RegExp.escape for literal pattern construction. Bound pattern and input size when regex work is exposed externally; not every complex pattern has predictable linear cost.

**UTF-16 code unit:** The storage/indexing unit used by JavaScript String.

**Code point:** A Unicode identity represented by one or two code units.

**Normalization:** A declared mapping between equivalent Unicode sequences.

**Pattern escaping:** Treating input text as literal characters rather than regex syntax.

## Reading the implementation

Use codePointAt and string iteration to inspect codepoints. normalize('NFC') applies a declared canonical normalization. The u flag enables Unicode-aware regex semantics for codepoints, but does not turn codepoints into grapheme clusters. RegExp.escape converts a literal string into a safe pattern fragment. A global regex carries lastIndex state across calls, so reuse requires understanding or resetting that cursor.

## Exercise 1: Count code units and codepoints

Task: Inspect A followed by one emoji.

The emoji uses two code units. Taking a one-unit substring from its middle would not produce a complete codepoint.

```javascript
const text = 'A🙂';
assert.equal(text.length, 3);
assert.equal([...text].length, 2);
assert.equal(text.codePointAt(1), 0x1f642);
```

**Expected:** length 3; spread count 2.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 2: Compare canonical spellings

Task: Compare composed é with e plus combining acute before and after NFC.

Canonical normalization changes representation identity under an explicit policy. It does not solve every homoglyph or language-specific comparison problem.

```javascript
const composed = 'é';
const decomposed = 'é';
assert.notEqual(composed, decomposed);
assert.equal(decomposed.normalize('NFC'), composed);
```

**Expected:** raw strings differ; normalized strings equal.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 3: Match a literal regex fragment

Task: Escape a.b+ and match it exactly rather than interpreting dot and plus.

The escaped fragment preserves the user text as data. Concatenating raw text into a regex would change the accepted language.

```javascript
const literal = 'a.b+';
const pattern = new RegExp(`^${RegExp.escape(literal)}$`, 'u');
assert.equal(pattern.test('a.b+'), true);
assert.equal(pattern.test('axbb'), false);
```

**Expected:** literal accepted; axbb rejected.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 4: Observe global regex cursor state

Task: Call /a/g repeatedly on aa and inspect lastIndex.

The same pattern object is stateful when global or sticky. Reusing it as a pure predicate can produce surprising alternating results.

```javascript
const pattern = /a/g;
assert.equal(pattern.test('aa'), true);
assert.equal(pattern.lastIndex, 1);
assert.equal(pattern.test('aa'), true);
assert.equal(pattern.lastIndex, 2);
assert.equal(pattern.test('aa'), false);
assert.equal(pattern.lastIndex, 0);
```

**Expected:** matches at 0 then 1; third call false resets cursor 0.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 5: Use Unicode-aware dot matching

Task: Compare `/^.$/` and `/^.$/u` on one emoji.

The u flag changes codepoint handling. It does not guarantee one user-perceived character for every combining sequence.

```javascript
assert.equal(/^.$/.test('🙂'), false);
assert.equal(/^.$/u.test('🙂'), true);
```

**Expected:** without u false; with u true.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## Exercise 6: Bound a text-validation input

Task: Reject a string longer than 20 code units before applying an anchored ASCII identifier pattern.

The bound and grammar are explicit. An application needing international identifiers would require a different policy rather than quietly widening this one.

```javascript
assert.equal(identifier('item_1'), 'item_1');
assert.throws(() => identifier('a'.repeat(21)), TypeError);
assert.throws(() => identifier('two words'), TypeError);
```

**Expected:** item_1 accepted; oversized input rejected.

**Verify:** Compare the actual observation with this expectation. Keep the input that makes the check distinguish the intended mechanism from the tempting wrong approach.

## After comparison

Return to your saved implementation and repeat a case with different values. Keep compiler diagnostics, process output and browser observations separate. Do not suppress a failing assertion or use a type assertion to declare an unvalidated value safe. Resource-owning examples must finish cleanup even when work fails. Describe each result with its actual host and fixture scope rather than as production acceptance.

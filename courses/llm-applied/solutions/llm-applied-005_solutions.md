# llm-applied-005: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Chunking divides documents into retrieval units. Small chunks can isolate relevant facts but lose context; large chunks preserve context but consume more budget and may dilute lexical or embedding signals. Overlap repeats boundary text so a fact crossing a split is less likely to disappear, but it also creates duplicate evidence and additional storage. Preserve source offsets so a retrieved chunk can cite the exact original span. Chunk identity should include document version and chunk boundaries, not just its ordinal position in a list.

The default splitter uses whitespace tokens only as a transparent fixture. Actual language-model tokenization may split a word into several tokens and add chat-template markers, so its counts must be measured with the intended tokenizer. A chunker should reject impossible overlap settings and handle an empty document deliberately. Evaluation should include facts at boundaries, repeated headings and documents whose key definition depends on an earlier section. No single chunk size is universally optimal; choose it through task-specific retrieval and answer evaluation.

**Chunk:** A bounded source span used as a retrieval unit.

**Overlap:** Repeated boundary material shared by adjacent chunks.

**Source offset:** A character boundary in the original document.

**Context budget:** The allowed amount of material supplied to an answerer.

## Reading the implementation

re.finditer over non-whitespace spans records exact start/end offsets in the original text. A window of size tokens advances bysize-overlap. The chunk text is sliced from the first token start to the last token end, preserving internal whitespace. Each output recordsdocument_id, version, start, end, text. Validate0<=overlap<size before looping so a zero or negative step cannot hang the process.

## Derive windows, duplication and citation coordinates

Let a nonempty document have n whitespace-token spans, window size s and overlap o, with \(0\le o<s\). The advance is \(d=s-o\). The first chunk covers up to s spans; further chunks begin at d, 2d and so on until one reaches the end. For this helper, the number of chunks is one when \(n\le s\) and otherwise1+ceil((n-s)/d). Empty input produces zero chunks under the declared policy.

For \(n=7\), \(s=3\), \(o=1\), \(d=2\) and the chunk count is1+ceil(4/2)=3. The span-index groups are[0, 1, 2], [2, 3, 4], [4, 5, 6]. Stored token occurrences total nine while unique source positions total seven. Positions2 and 4 are repeated once. The redundancy ratio for this finite fixture is9/7, about1.286; it is not nine independent observations supporting the answer.

For a long uniform document with full windows, stored token occurrences per newly covered position approach \(\frac{s}{s-o}\). Overlap near the window size can therefore create a large storage and retrieval cost. At \(s=100\), \(o=90\), the advance is ten and the interior duplication factor approaches ten. That arithmetic does not prove an optimal overlap policy; it identifies a cost to measure beside evidence recall.

The loop stops when a chunk reaches the end. Without that break, the range of starts could produce another tail containing only already-covered final tokens. For the seven-token example, continuing after the window beginning at four would add a window beginning at six containing only seven. Preventing that duplicate tail is a policy decision visible in the helper, not an automatic property of overlapping windows.

Citation coordinates have units. Python string offsets count Unicode code points, while a UTF-8 byte stream and a model tokenizer can have different lengths. For example, the character β occupies one Python-string position but two UTF-8 bytes. Combining marks can make a visually single character contain multiple code points. The fixture's offsets belong to the original Python string, and its tests correctly slice that same string. Calling them byte offsets would be inaccurate.

Internal whitespace remains intact because chunk text is sliced from the first selected token's start to the last token's end. In a source containing alpha, two spaces, beta, a newline and gamma, the first two-token chunk retains two spaces between alpha and beta. Joining selected token strings with one space would produce different text and break the source-slice equality. The splitter excludes leading/trailing whitespace outside the selected token endpoints, which should also be understood when comparing full-document reconstruction.

Overlap can improve boundary coverage without making each chunk self-sufficient. If a formula appears in one section and its eligibility rule appears several sections earlier, a one-token overlap does not recover that dependency. A retrieved passage saying “divide by the eligible population” may be insufficient without the definition of eligibility. Evaluate whether the selected context jointly covers all required facts, not only whether one answer phrase appears in any chunk.

### Interview reasoning with explanatory answers

**Why not increase overlap until recall is perfect?** Duplication consumes storage and context, can return several copies of the same evidence and can displace a complementary source. Recall and useful context sufficiency are different measurements.

**What should identify a chunk?** The source/version and boundaries plus the splitter representation policy. An ordinal such as chunk3 can refer to different content after an earlier section changes.

**Can a whitespace chunk count predict model-token use?** Only under an explicitly verified mapping, which this fixture does not supply. The intended tokenizer and rendered chat format must measure the actual model budget.

## Exercise 1: Split a fixed document

The question is: Chunk one two three four five six seven with size 3 and overlap 1.

The step is two tokens, so each adjacent pair shares one token. The final full window reaches the document end without creating a duplicate tail chunk.

```python
text='one two three four five six seven'; chunks=chunk(text,'d',1,3,1)
assert [c['text'] for c in chunks]==['one two three','three four five','five six seven']
```

**Expected:** chunks one two three, three four five and five six seven.

**Verify:** Compare the computed values or written argument with chunks one two three, three four five and five six seven.

## Exercise 2: Verify citation offsets

The question is: For every chunk, slice the original text using its start and end offsets.

Offsets remain meaningful only relative to the exact source version. Reconstructing chunk text with join could normalize whitespace and break this equality.

```python
assert all(text[c['start']:c['end']]==c['text'] for c in chunks)
assert chunks[1]['start']==text.index('three')
```

**Expected:** every source slice equals the stored chunk text.

**Verify:** Compare the computed values or written argument with every source slice equals the stored chunk text.

## Exercise 3: Preserve unusual whitespace

The question is: Chunk alpha, two spaces, beta, a newline and gamma with size 2 and overlap 0.

The splitter counts token spans but retains original characters inside the chunk. Citation fidelity and tokenization are separate concerns.

```python
odd='alpha  beta\ngamma'; pieces=chunk(odd,'odd',2,2,0)
assert pieces[0]['text']=='alpha  beta' and pieces[1]['text']=='gamma'
```

**Expected:** first chunk retains the double space; second chunk is gamma.

**Verify:** Compare the computed values or written argument with first chunk retains the double space; second chunk is gamma.

## Exercise 4: Measure overlap duplication

The question is: Count total stored chunk token occurrences versus original source token positions in the first fixture.

Repeated context is not independent evidence. A retrieval result returning adjacent overlapping chunks should avoid counting the shared sentence twice in answer support.

```python
assert sum(len(c['text'].split()) for c in chunks)==9
assert len(text.split())==7
```

**Expected:** 9 stored token occurrences versus7 source positions.

**Verify:** Compare the computed values or written argument with 9 stored token occurrences versus7 source positions.

## Exercise 5: Reject invalid policies

The question is: Try overlap equal to window size, negative overlap and size 0.

The validation protects termination as well as semantics. A step of zero would otherwise repeat the same window forever.

```python
for size,overlap in [(3,3),(3,-1),(0,0)]:
    try: chunk(text,'d',1,size,overlap)
    except ValueError: pass
    else: raise AssertionError('invalid chunk policy')
```

**Expected:** all policies raise ValueError before iteration.

**Verify:** Compare the computed values or written argument with all policies raise ValueError before iteration.

## Exercise 6: Handle empty and short sources

The question is: Chunk empty text and a two-token string with size 5.

A short source should not be padded with invented text. An empty source contributes no retrievable evidence and should remain distinguishable from a valid zero-length quote.

```python
assert chunk('','empty',1,5,1)==[]
short=chunk('only two','short',1,5,1); assert len(short)==1 and short[0]['text']=='only two'
```

**Expected:** empty list for empty text; one short chunk for the two-token source.

**Verify:** Compare the computed values or written argument with empty list for empty text; one short chunk for the two-token source.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

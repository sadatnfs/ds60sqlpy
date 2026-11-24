# llm-applied-005: Chunking, overlap, offsets and context budgets

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-applied-004` (Corpus provenance, versions and evaluation isolation). They introduce the notation this lesson needs for chunk and overlap.

## Learning objectives

Chunking determines the unit that retrieval can find and the context an answer can inspect. This chapter follows a handbook definition through competing splitting policies, connecting boundary choices to evidence sufficiency, citation coordinates and the budget available for other facts.

## Purpose and mental model

Chunking divides documents into retrieval units. Small chunks can isolate relevant facts but lose context; large chunks preserve context but consume more budget and may dilute lexical or embedding signals. Overlap repeats boundary text so a fact crossing a split is less likely to disappear, but it also creates duplicate evidence and additional storage. Preserve source offsets so a retrieved chunk can cite the exact original span. Chunk identity should include document version and chunk boundaries, not just its ordinal position in a list.

The default splitter uses whitespace tokens only as a transparent fixture. Actual language-model tokenization may split a word into several tokens and add chat-template markers, so its counts must be measured with the intended tokenizer. A chunker should reject impossible overlap settings and handle an empty document deliberately. Evaluation should include facts at boundaries, repeated headings and documents whose key definition depends on an earlier section. No single chunk size is universally optimal; choose it through task-specific retrieval and answer evaluation.

## Retrieve a complete meaning, not merely a matching sentence

The Methods Desk handbook defines conversion in one paragraph, lists exclusions in a table and explains the assignment unit in the next section. A question about the formula may need only the first paragraph. A question about yesterday's reported value also needs the exclusions. A question about uncertainty needs the assignment and observation structure. The appropriate retrieval unit therefore depends on the claims the answer must support.

A fixed-length chunker cannot know all of those dependencies from token positions alone. It can provide a predictable storage and retrieval unit, but a boundary can separate a term from its definition, a table value from its header or an exception from the rule it qualifies. The design task is to preserve enough local structure that relevant context can be recovered under a finite budget.

Consider a two-sentence policy: “Count purchases over eligible visits. Test accounts are excluded from the eligible population.” A split after the first sentence creates a concise formula chunk and a separate exclusion chunk. That may work well if the query retrieves both. If only the formula enters the answer context, the model can produce a complete-looking calculation while omitting the eligibility rule. Increasing overlap can reduce some boundary failures, but it does not guarantee that every required relationship stays together.

## Separate indexing units, evidence units and answer context

Three units are useful to distinguish. The indexing unit is what the retriever scores. The evidence unit is the smallest source material that establishes a required fact or relationship. The answer context is the assembled set of material supplied to the model. These units can differ without being inconsistent.

For example, a short paragraph can be an effective indexing unit because its vector or lexical score focuses on one topic. Once selected, the application might also include the section heading and a linked eligibility table in the answer context. That expansion must remain versioned and budgeted. It should not silently fetch unauthorized material or add unrelated neighboring text merely because it is nearby.

A long chunk offers more surrounding information but can make retrieval less discriminating. If a passage covers conversion, retention, experiment design and logging together, a similarity score may be influenced by several topics. A short chunk can isolate the intended topic but lose the qualifications that make its statements valid. There is no universal boundary size that resolves both tensions for every question.

This suggests evaluating chunking at the claim level. For a formula question, label the formula span. For an eligibility question, label the rule and its scope. For a multi-part analytical question, record the set of required evidence and whether alternatives are interchangeable or jointly necessary. A single document-level relevance label can hide the fact that the returned chunk omitted the useful part of that document.

## Tables and headings need an explicit representation

Suppose a table contains columns `account_type`, `eligible` and reason. A row containing `test,false,internal traffic` is hard to interpret if retrieved without its column labels. A structure-aware representation can attach those labels to the row or preserve a small table region. If the representation repeats labels for retrieval, keep a separate link to the original source span so the generated text is not falsely presented as a verbatim quote.

Headings have a similar role. The sentence “Use account-level resampling” under “Repeated visits within accounts” has a more specific meaning than the same sentence in isolation. A chunk can carry the heading as metadata or expanded context. Repeating the heading into every indexed chunk also changes lexical frequencies and embedding inputs, so it becomes part of the retrieval policy rather than a neutral display choice.

Preserving meaning does not mean inventing it. A missing table header should not be guessed from a plausible neighboring section. An extracted PDF row with damaged column order may need quarantine or a source-specific parser. The assistant can be fluent about a malformed representation, which is precisely why source-format failures need independent checks before answer generation.

## Overlap changes both cost and apparent support

The window calculation later in this chapter makes duplication measurable. With size 3 and overlap 1, seven source tokens occupy nine stored token positions. At larger scales, overlapping chunks can cause several high-ranked candidates to repeat the same fact. Returning three such chunks may look like three supporting sources while actually supplying one piece of evidence three times.

Deduplication should preserve evidence identity. Removing every repeated phrase blindly can discard a phrase that has different scope in two sources. Keeping every repeated chunk wastes context and can overstate corroboration. Source version, offsets and semantic role help distinguish exact overlap from independent evidence.

The context budget introduces an opportunity cost. If redundant chunks consume the space needed for an exclusion rule or an independent contradictory source, higher raw retrieval recall can produce worse answers. A meaningful comparison records the unique evidence covered, the number of repeated positions, context cost and supported-answer outcome. It should not reward a splitter solely for producing many candidates that contain an answer keyword.

## Rebuilding chunks changes the experiment

A splitter update can alter chunk identities, offsets, document frequencies, vectors and cached answers even when the original handbook is unchanged. The new index is therefore a new system configuration. Preserve the old policy long enough to reproduce a prior answer, and evaluate the new one on frozen questions before attributing an improvement to another component.

Boundary tests should include negation, exceptions, units, table headers and references such as “the rule above.” Short-source and empty-source behavior also matters: a source should not acquire invented padding text merely to satisfy a window size. The literal splitter below provides a transparent baseline for those coordinate and termination checks. Structure-aware splitting can then be judged by whether it improves the actual evidence path, rather than by whether its chunks look more natural to the author.

Once chunks have stable identities and meaningful boundaries, the next problem is ranking them. The lexical chapter begins with a method whose terms and scores can be calculated directly, giving the assistant a baseline that can be inspected before introducing learned geometry.

## Design decisions and when to use this method

Use sentence, paragraph or structure-aware chunks when the task depends on complete definitions, tables or procedure steps. Preserve headings and document metadata as separate context rather than blindly repeating them into every embedding. For tables, a row alone may lose column meanings; a chunk needs enough schema context to interpret its values. For code or formulas, splitting at arbitrary whitespace can destroy syntax or assumptions.

Evaluate chunk policies on authored boundary questions. Measure retrieval recall, citation fidelity, duplicate rate, answer support and context consumption together. A policy that increases recall by returning many near-duplicate chunks may leave less room for other necessary evidence. Do not tune chunk size on the final test set. Record splitter version and tokenization policy so rebuilding an index does not silently change the experiment.

Choose the retrieval unit from the question's required evidence. A definition may fit in one paragraph, while a table answer may require a row, header, units and footnote together. Evaluate a splitter on those dependencies instead of optimizing only chunk length or embedding throughput.

Keep a chunk's original-source identity and its representation for retrieval separate. An index may add a heading or normalize whitespace for encoding, but citation offsets still need to refer to the admitted original text. Record the transformation rather than assuming the encoded string can be sliced back out unchanged.

## Vocabulary and concepts

**Chunk:** A bounded source span used as a retrieval unit.

**Overlap:** Repeated boundary material shared by adjacent chunks.

**Source offset:** A character boundary in the original document.

**Context budget:** The allowed amount of material supplied to an answerer.

## How to run this lesson

Run `courses/llm-applied/lessons/llm-applied-005.py` in the declared `python-core` profile. *Split a fixed document*, *Verify citation offsets* and *Preserve unusual whitespace* need only the Python standard library and literal fixtures.

Copy it to `.learning/expansion/llm-applied-005/` or the saved pad before editing; nothing is installed or downloaded.

Run Examples A to C in one scratch file: *Verify citation offsets* and *Preserve unusual whitespace* reuse the helper and fixture introduced in *Split a fixed document*. Before running Example A, write its intermediate quantities by hand and predict the result. It should give: Chunks one two three, three four five and five six seven. Example B should give: Every source slice equals the stored chunk text. Example C should give: First chunk retains the double space; second chunk is gamma. Use the tolerance in each assertion; counts, identities and decisions must match exactly.

## Syntax anatomy and reasoning sequence

re.finditer over non-whitespace spans records exact start/end offsets in the original text. A window of size tokens advances by size-overlap. The chunk text is sliced from the first token start to the last token end, preserving internal whitespace. Each output records document_id, version, start, end, text. Validate 0<=overlap<size before looping so a zero or negative step cannot hang the process.

## Derive windows, duplication and citation coordinates

Let a nonempty document have n whitespace-token spans, window size s and overlap o, with \(0\le o<s\). The advance is \(d=s-o\). The first chunk covers up to s spans; further chunks begin at d, 2d and so on until one reaches the end. For this helper, the number of chunks is one when \(n\le s\) and otherwise \(1+\left\lceil \frac{n-s}{d}\right\rceil\). Empty input produces zero chunks under the declared policy.

For \(n=7\), \(s=3\), \(o=1\), \(d=2\) and the chunk count is \(1+\left\lceil \frac{4}{2}\right\rceil=3\). The span-index groups are `[0, 1, 2], [2, 3, 4], [4, 5, 6]`. Stored token occurrences total nine while unique source positions total seven. Positions 2 and 4 are repeated once. The redundancy ratio for this finite fixture is \(\frac{9}{7}\), about 1.286; it is not nine independent observations supporting the answer.

For a long uniform document with full windows, stored token occurrences per newly covered position approach \(\frac{s}{s-o}\). Overlap near the window size can therefore create a large storage and retrieval cost. At \(s=100\), \(o=90\), the advance is ten and the interior duplication factor approaches ten. That arithmetic does not prove an optimal overlap policy; it identifies a cost to measure beside evidence recall.

The loop stops when a chunk reaches the end. Without that break, the range of starts could produce another tail containing only already-covered final tokens. For the seven-token example, continuing after the window beginning at four would add a window beginning at six containing only seven. Preventing that duplicate tail is a policy decision visible in the helper, not an automatic property of overlapping windows.

Citation coordinates have units. Python string offsets count Unicode code points, while a UTF-8 byte stream and a model tokenizer can have different lengths. For example, the character β occupies one Python-string position but two UTF-8 bytes. Combining marks can make a visually single character contain multiple code points. The fixture's offsets belong to the original Python string, and its tests correctly slice that same string. Calling them byte offsets would be inaccurate.

Internal whitespace remains intact because chunk text is sliced from the first selected token's start to the last token's end. In a source containing alpha, two spaces, beta, a newline and gamma, the first two-token chunk retains two spaces between alpha and beta. Joining selected token strings with one space would produce different text and break the source-slice equality. The splitter excludes leading/trailing whitespace outside the selected token endpoints, which should also be understood when comparing full-document reconstruction.

Overlap can improve boundary coverage without making each chunk self-sufficient. If a formula appears in one section and its eligibility rule appears several sections earlier, a one-token overlap does not recover that dependency. A retrieved passage saying “divide by the eligible population” may be insufficient without the definition of eligibility. Evaluate whether the selected context jointly covers all required facts, not only whether one answer phrase appears in any chunk.

### Interview reasoning with explanatory answers

**Why not increase overlap until recall is perfect?** Duplication consumes storage and context, can return several copies of the same evidence and can displace a complementary source. Recall and useful context sufficiency are different measurements.

**What should identify a chunk?** The source/version and boundaries plus the splitter representation policy. An ordinal such as chunk 3 can refer to different content after an earlier section changes.

**Can a whitespace chunk count predict model-token use?** Only under an explicitly verified mapping, which this fixture does not supply. The intended tokenizer and rendered chat format must measure the actual model budget.

## Worked example / walkthrough

### Example A: Split a fixed document

The step is two tokens, so each adjacent pair shares one token. The final full window reaches the document end without creating a duplicate tail chunk.

```python
import re


def chunk(text, document_id, version, size, overlap):
    if type(size) is not int or type(overlap) is not int or size <= 0 or not 0 <= overlap < size:
        raise ValueError("0<=overlap<size required")
    spans = list(re.finditer(r"\S+", text))
    result = []
    step = size - overlap
    for begin in range(0, len(spans), step):
        end = min(begin + size, len(spans))
        start_char = spans[begin].start()
        end_char = spans[end - 1].end()
        result.append(
            {
                "document_id": document_id,
                "version": version,
                "start": start_char,
                "end": end_char,
                "text": text[start_char:end_char],
            }
        )
        if end == len(spans):
            break
    return result


text = "one two three four five six seven"
chunks = chunk(text, "d", 1, 3, 1)
assert [c["text"] for c in chunks] == ["one two three", "three four five", "five six seven"]
```

**Expected:** chunks one two three, three four five and five six seven.

### Example B: Verify citation offsets

Offsets remain meaningful only relative to the exact source version. Reconstructing chunk text with join could normalize whitespace and break this equality.

```python
assert all(text[c["start"] : c["end"]] == c["text"] for c in chunks)
assert chunks[1]["start"] == text.index("three")
```

**Expected:** every source slice equals the stored chunk text.

### Example C: Preserve unusual whitespace

The splitter counts token spans but retains original characters inside the chunk. Citation fidelity and tokenization are separate concerns.

```python
odd = "alpha  beta\ngamma"
pieces = chunk(odd, "odd", 2, 2, 0)
assert pieces[0]["text"] == "alpha  beta" and pieces[1]["text"] == "gamma"
```

**Expected:** first chunk retains the double space; second chunk is gamma.

## Prediction before your attempt

Before reading the code for *Verify citation offsets*, predict its result from the prompt alone: For every chunk, slice the original text using its start and end offsets. Write the guess beside the stated outcome (every source slice equals the stored chunk text). Then predict how the decisive case, *Handle empty and short sources*, should end: Chunk empty text and a two-token string with size 5. For chunking, overlap, offsets and context budgets, the finish condition is: Chunks one two three, three four five and five six seven. Empty list for empty text; one short chunk for the two-token source.

## Exercises

1. **Split a fixed document.** Chunk one two three four five six seven with size 3 and overlap 1.
   **Expected:** chunks one two three, three four five and five six seven.
   **Verify:** Save the assertion results for exercise 1, including chunks one two three, three four five and five six seven.
   **Transfer:** This repeats Example A; reproduce it closed-book, then change one literal and predict the new result before running it.

2. **Verify citation offsets.** For every chunk, slice the original text using its start and end offsets.
   **Expected:** every source slice equals the stored chunk text.
   **Verify:** Save the assertion results for exercise 2, including every source slice equals the stored chunk text.
   **Transfer:** This repeats Example B; reproduce it closed-book, then change one literal and predict the new result before running it.

3. **Preserve unusual whitespace.** Chunk alpha, two spaces, beta, a newline and gamma with size 2 and overlap 0.
   **Expected:** first chunk retains the double space; second chunk is gamma.
   **Verify:** Save the assertion results for exercise 3, including first chunk retains the double space; second chunk is gamma.
   **Transfer:** This repeats Example C; reproduce it closed-book, then change one literal and predict the new result before running it.

4. **Measure overlap duplication.** Count total stored chunk token occurrences versus original source token positions in the first fixture.
   **Expected:** 9 stored token occurrences versus 7 source positions.
   **Verify:** Save the assertion results for exercise 4, including 9 stored token occurrences versus 7 source positions.

5. **Reject invalid policies.** Try overlap equal to window size, negative overlap and size 0.
   **Expected:** all policies raise ValueError before iteration.
   **Verify:** Save the assertion results for exercise 5, including all policies raise ValueError before iteration.

6. **Handle empty and short sources.** Chunk empty text and a two-token string with size 5.
   **Expected:** empty list for empty text; one short chunk for the two-token source.
   **Verify:** Save the assertion results for exercise 6, including empty list for empty text; one short chunk for the two-token source.

## Common pitfalls and diagnosis

If citation text differs, compare coordinate units, exact source version and normalization history. If a splitter loops or repeats indefinitely, inspect the positive advance s-o before considering content. If the last chunk duplicates an already-covered tail, inspect the termination rule.

If retrieval returns many near-identical passages, deduplicate by source spans or evidence identity before treating them as corroboration. If recall appears high but answers miss exclusions or units, inspect whether the relevant evidence set was defined as an isolated phrase instead of the complete dependency. Tune split policy on validation families, then retain unseen boundary cases for assessment.

## Progressive hints

Hint 1: restate chunk and overlap for the fixture in *Split a fixed document*. Hint 2: change one literal in *Verify citation offsets* and note which intermediate value moves. Hint 3: compare your fourth exercise, *Measure overlap duplication*, with its stated result (9 stored token occurrences versus 7 source positions). If *Handle empty and short sources* accepts an input it should reject, look for the missing check rather than widening a tolerance.

## Self-check and retrieval

Close the examples and explain chunk, overlap and source offset using *Split a fixed document*. Recompute its result (chunks one two three, three four five and five six seven) from the inputs. Change one input in *Preserve unusual whitespace* and predict whether the stated result (first chunk retains the double space; second chunk is gamma) still holds. Say which part of chunking, overlap, offsets and context budgets the code guarantees and which part would need new observations.

## Next step

If *Split a fixed document* cannot be reconstructed without the solution, revisit `llm-applied-004` (Corpus provenance, versions and evaluation isolation). Otherwise keep the six observations from chunking, overlap, offsets and context budgets and continue to `llm-applied-006` (Lexical retrieval and BM25 from first principles).

## Sources and verification status

Reference for chunk: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixtures for *Split a fixed document*, *Verify citation offsets* and *Preserve unusual whitespace* and the six exercises are original course material.

Execution gates are described in [validation](../../../docs/validation.md); CI artifacts show which checks ran for each revision.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-005, Chunking, overlap, offsets and context budgets.
Read courses/llm-applied/guides/llm-applied-005.md and courses/llm-applied/lessons/llm-applied-005.py. Direct prerequisites: `llm-applied-004`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

# nlp-005: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Retain grammatical context

The table expresses four authored lexical relations. The ambiguous saw entries show why surface-only normalization loses information. Returning a lowercased fallback outside the table is a conservative computational convention, not proof of a true dictionary lemma.

**Expected:** saw/VERB -> see; saw/NOUN -> saw; studies/NOUN -> study; better/ADJ -> good.

## Exercise 2: Trace the context rule

The rule reproduces the authored cases because the determiner is directly adjacent only in the noun example. It is a baseline with a declared context window. It does not infer phrase structure or resolve all uses of saw.

**Expected:** I saw her gives VERB; the saw broke gives NOUN.

## Exercise 3: Preserve a known error

The counterexample isolates a specific limitation. Adding a two-token lookback may repair this phrase but still fails broader grammar. The appropriate lesson is to evaluate on new constructions and identify the required context, not to claim one patch completes a tagger.

**Expected:** The rule returns VERB, and the error is recorded rather than relabeled as correct.

## Exercise 4: Validate head indices

A repeated node in one chain is a cycle. Exactly one root plus valid acyclic head chains yields a rooted tree. Negative indices other than -1 must be rejected because Python would otherwise interpret them as valid indexing from the end.

**Expected:** Accept [1,-1,1]; reject [1,0,-1],[-1,-1],[2,-1] and empty input.

## Exercise 5: Separate structure from meaning

The validator has no access to a grammatical gold analysis. Passing its checks proves a data-structure invariant, not linguistic accuracy. A parser evaluation must compare token-aligned heads and labels against an appropriate annotation convention.

**Expected:** Both structurally valid; only the first matches the intended head assignment.

## Exercise 6: Choose task-specific normalization

A retrieval system may benefit from matching study and studies, while an event extractor may need tense or participant number. There is no universally harmless cleaning step. The record should retain original spelling and the normalization method so later users know which information remains available.

**Expected:** A concrete policy preserves raw text and names at least one lost distinction for each transformation.

## Transfer and limits

Linguistic structure supplies distinctions that a sequence of token IDs does not explain by itself. Morphology concerns word formation and meaningful parts; syntax concerns how words combine into phrases and grammatical relationships. A tokenizer chooses computational units, which may cut across morphemes or combine punctuation. A BPE fragment is therefore not automatically a linguistic root, and a short tokenization is not evidence of correct grammatical analysis.

This lesson uses a few deliberately authored English examples to distinguish stemming, lemmatization, part-of-speech tagging and dependency structure. It does not download a tagger or parser. The small lookup and context rule are intentionally incomplete so you can see what they do, why one counterexample defeats them and which checks establish only structural validity.

A surface form is the observed spelling, such as saw. A lemma is a dictionary-like base form under a grammatical interpretation. Saw as a past-tense verb can have lemma see, while saw as a cutting-tool noun retains lemma saw. The same character string therefore needs context before normalization can safely collapse it.

## Mechanism review and counterexample

A dependency representation links each token to a head token, with a root marking the main organizing predicate under a chosen annotation scheme. For tokens [I,saw,her], heads [1,-1,1] attach I and her to saw, which is the root. Indices refer to token positions, and -1 is the explicit root sentinel in this lesson.

A structural validator checks legal indices, exactly one root and absence of cycles. Following each head chain should eventually reach -1. These conditions establish that the array forms one rooted tree. They do not establish that the attachments or relation labels are linguistically correct. Heads [1,-1,0] also form a tree but attach her to I, which is not the intended analysis of this sentence.

The distinction matters for learned parsers and language-model-generated structures. A schema-valid parse can be wrong. Measure attachment accuracy against an annotation contract, inspect coordination and long-distance dependencies, and account for tokenization alignment. Projectivity is an additional property that some parsing algorithms assume; it is not required by this basic tree validator.

# llm-applied-012: Evaluating retrieval and answers with oracle controls

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-011`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

An evaluation should answer the engineering question that motivated the system change. This chapter builds a question-and-evidence benchmark, separates retrieval and answer metrics, and develops oracle controls that identify useful interventions without overstating what a single score proves.

## Purpose and mental model

A RAG evaluation should identify where the pipeline failed. Retrieval recall asks whether relevant evidence entered the candidate or context set. Ranking metrics ask how early it appeared. Answer correctness asks whether the response satisfies the question. Support asks whether its claims are established by supplied evidence. Appropriate abstention asks whether the system declined cases lacking evidence. These measurements can disagree, and combining them into one number too early hides actionable information.

An oracle-context control supplies the authored relevant evidence directly while leaving the question and answer rubric unchanged. An improvement shows that the context intervention helped under that protocol; narrower controls are needed to attribute it to a particular retrieval failure. If it still fails, the answer stage or task definition needs attention. The local fixture uses saved deterministic answer labels, not fabricated model execution. Every result is keyed by question ID and linked to an authored relevance set. Questions with no relevant documents need a separate answerability category because recall has an empty denominator.

## Begin with the work the assistant is supposed to help perform

The Methods Desk needs to answer current definitions, explain eligibility rules, calculate validated descriptive quantities and recognize when a requested conclusion exceeds the evidence. An evaluation containing only easy definition lookups would miss much of that job. The test set should represent the tasks and failure boundaries that determine usefulness.

Useful case families include a supported definition, an eligibility exception, a historical-version question, missing evidence, an access-restricted question, a deterministic calculation, an unsupported causal request and an ambiguous term. These are categories for designing evaluation, not a claim that eight examples suffice for a production decision. Each needs representative variation and a clear expected behavior under the request's access and time policy.

Answerability is conditional on that policy. A restricted document may contain an answer, but the public caller's admissible evidence set may not. A historical question may be answerable only when older versions remain available. An ambiguous question may require clarification rather than a guessed interpretation. Labels should describe the intended behavior, not merely whether a string appears somewhere in the global corpus.

## Store enough information to score the right thing

A case should retain a stable question ID, family, requested scope and period, relevant evidence identities, required claims, allowed alternatives and scoring decisions. Some questions need any one of several equivalent sources; others require a set of facts jointly. A flat list of relevant documents does not express that distinction automatically.

Candidate recall asks whether useful evidence entered an early pool. Final-context recall asks whether it survived ranking, deduplication and the token budget. Answer correctness asks whether the returned response satisfies the question. Support asks whether the response's substantive claims are established by its admitted evidence and calculations. Appropriate abstention asks whether the system declined the cases it should decline while still answering useful cases.

These measurements can disagree for meaningful reasons. A generator may guess a correct answer despite a retrieval miss, which fails a source-grounded contract. A correct citation can accompany an irrelevant answer. A perfectly supported quotation can omit the requested computation. Keeping the metrics separate allows the report to identify those outcomes instead of averaging them into an opaque score.

The runnable metric helper below operates on explicit IDs and relevance sets. The saved answer labels are authored examples showing how a result table would be processed. They are not evidence that a named model generated those answers. An actual benchmark run needs the rendered inputs, model outputs and rubric decisions that connect the computation to observed behavior.

## Compare candidates on the same identified cases

Suppose an illustrative eight-question evaluation finds that candidate A answers seven, with five accepted answers and two unsupported failures. Candidate B answers five, all accepted, and refuses three. Both produce five accepted answers overall, but their coverage and error profiles differ. A headline accuracy among answered cases would favor B; a task that strongly values coverage may need to inspect which questions B refused. The acceptance policy determines the relevant tradeoff.

Pairing by question ID preserves that comparison. If one candidate is evaluated on a different mix of questions, a score difference can reflect difficulty rather than system quality. Family labels matter too: many paraphrases of one question can dominate a row average without adding independent evidence about new domains. The next chapter develops the corresponding paired and family-level uncertainty calculations.

Freeze the rubric before using results to select a candidate. A new interpretation of correctness that appears only after inspecting a favored system can turn evaluation into another tuning step. Annotation disagreements should remain visible, especially for paraphrases, partial answers and legitimate abstentions. A deterministic answer key is useful where the task permits one, but a rubric is still needed for semantic scope and support.

## Use oracle context as a controlled diagnostic

An oracle-context run supplies known sufficient evidence to the answer stage. If the response improves, the intervention was useful under that protocol. To attribute the improvement specifically to a missing passage, hold other context properties as stable as possible. Replacing a long noisy context with one short perfect paragraph changes both evidence presence and distraction, and may expose a context-use failure as well as a retrieval miss.

A useful sequence can compare the observed context, observed context plus the missing required source, and a minimal sufficient context. The first change probes whether supplying the missing fact helps under the original distractions. The second probes whether the answerer struggles with competing or irrelevant material. These controls are not always equally realistic serving options, but they help locate the failure.

If the oracle result still fails, inspect the answer model, prompt, source interpretation and rubric. The source may not actually be sufficient, or the required computation may be absent. Calling every oracle failure “generation error” would hide those alternatives. The purpose of the control is to make a narrower investigation possible, not to assign blame automatically.

## Evaluate a judge before using it to evaluate the assistant

A model-based judge can help triage large numbers of responses, but it is another measurement system. Test it on known corruptions such as a swapped denominator, an unsupported universal claim, a valid citation attached to the wrong proposition and a legitimate paraphrase with little word overlap. Compare its decisions with deterministic checks and reviewed labels, and preserve cases of disagreement.

Judge prompts, versions and evidence access affect the measurement. A judge shown the answer key may answer a different question from one asked to determine support using only supplied context. A judge that knows which system produced an answer may introduce another source of bias. Record those conditions so the resulting scores can be interpreted and reproduced.

The final report should connect metrics to decisions. If candidate recall is the main limitation, investigate retrieval or corpus coverage. If evidence arrives but the formula changes in prose, repair the calculation-to-explanation interface. If unsupported claims are concentrated in causal requests, improve the task contract and assessment for those requests. The evaluation is most useful when it tells the team what evidence would justify the next change.

## Design decisions and when to use this method

Use a layered evaluation when choosing between retrievers, chunkers, rerankers or answer models. Freeze relevance labels and task rubrics before tuning. Include exact-match, paraphrase, multi-hop, unanswerable, stale and adversarial cases. Keep the context budget equal across candidates so a system does not win simply by receiving more evidence.

Do not rely exclusively on an unvalidated LLM judge. A judge can be useful for triage, but its disagreement with human or deterministic checks should be measured. Citation existence, JSON validity and fluent wording are weak proxies for support and correctness. Preserve representative failures and oracle controls in the report so a reviewer can see which engineering change is justified. Use independent question families for final assessment rather than many near-duplicate variants of the tuning examples.

Design evaluation around stage-specific questions. Candidate recall measures which relevant IDs were available; final-context recall measures what the answerer actually saw; answer correctness and claim support measure the returned artifact. Fix the corpus, authorized scope, question families, budget and scoring rubric before comparing configurations.

Treat an oracle-context experiment as an intervention with its own protocol. Keep the question, model, prompt policy and scoring rule fixed, and record exactly how the context changed. Removing distractors and changing context length as well as adding a missing source can reveal an answer-stage sensitivity, not only a retrieval omission.

## Vocabulary and concepts

**Retrieval recall:** Coverage of authored relevant evidence in retrieved results.

**Reciprocal rank:** Inverse position of the first relevant result.

**Oracle-context control:** Known relevant evidence supplied to isolate answer behavior.

**Failure taxonomy:** Separate named categories locating pipeline problems.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-012/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-012.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Recall@k is the number of relevant IDs retrieved divided by total relevant IDs. Reciprocal rank is 1 divided by the first relevant rank, or 0 when none appears. For unanswerable questions, return None for recall and score abstention separately. Keep retrieval misses, unsupported claims, incorrect answers and appropriate abstentions as distinct counters. Compare observed and oracle results by the same question ID.

## Calculate metrics without losing the task's evidence structure

For relevant IDs R={a, c} and retrieved list[b, c, a], both relevant documents appear, giving recall \(\frac{2}{2}=1\). The first relevant item is at rank two, giving reciprocal rank \(\frac{1}{2}\). If the caller truncates to the first two items, recall becomes \(\frac{1}{2}\) while reciprocal rank remains \(\frac{1}{2}\). The helper accepts the supplied list as its evaluation depth; it has no separate k argument. Name that cutoff when reporting Recall@k.

A first-hit metric cannot establish multi-evidence sufficiency. If a question requires both a definition and its exclusion rule, retrieving only one can give reciprocal rank one but an incomplete answer context. Conversely, a relevance set may contain several interchangeable documents, where any one is sufficient. The evaluation label should distinguish all required evidence from alternative supporting sources. The set arithmetic alone cannot infer that logic.

Duplicate retrieved IDs are rejected before metrics. Without that boundary, a naive count could reward repeated evidence. The current recall uses a set intersection, which prevents numerator inflation, but duplicate list entries would still distort ranks and consumed budget. Requiring unique identities makes the evaluation unit explicit.

For an unanswerable question, the relevant set is empty. Recall has a zero denominator, so the helper returns None and separately assigns reciprocal rank zero. Treating undefined recall as one would reward a system merely for facing a question with no evidence. Treating it as zero inside every average would confound retriever quality on answerable cases with the prevalence of unanswerable cases. Report the number of answerable cases and score abstention separately.

Suppose one question has one relevant document and retrieves it, while another has nine relevant documents and retrieves one. Macro-average recall is(1+1/9)/2=5/9. Micro recall over all relevant IDs is \(\frac{2}{10}=0.2\). Neither arithmetic result is inherently wrong: one weights questions equally, the other weights relevant-document opportunities equally. The population and task contract must choose the estimand before seeing which number looks better.

The oracle fixture contains saved labels observed={q1:0, q2:0} and oracle={q1:1, q2:0}. It calculates a paired gain of one for q1 and zero for q2, averaging 0.5 over those two fixed IDs. No language model is invoked by those dictionaries, and the values are not empirical measurements of a named model. They demonstrate how an actual paired result would be represented and analyzed.

In a real oracle run, improvement after supplying sufficient evidence suggests that context selection was a useful intervention. A remaining failure may concern answer behavior, prompt construction, source interpretation or an incorrect rubric. If oracle context is much shorter or removes conflicting passages, its improvement does not isolate missing-document recall alone. Preserve those differences and use narrower ablations when causal attribution between engineering components matters.

Support and correctness form separate axes. A correct-looking answer with unsupported citations may have come from memorized knowledge or chance; an accurately quoted but irrelevant source may be supported in a literal sense while failing the question. Define support at the claim level under the question's intended meaning. Schema validity, fluent text and citation count should remain diagnostic signals rather than substitutes for the full rubric.

### Interview reasoning with explanatory answers

**Why inspect oracle context?** It helps test whether the answer stage can succeed when sufficient evidence is supplied. It is a controlled diagnostic, not a guarantee that every remaining error belongs exclusively to generation.

**Which average should a retrieval report use?** The one matching the intended evaluation unit, with its denominator stated. Report enough counts to reconstruct it and avoid silently mixing undefined unanswerable cases with answerable recall.

**Can an LLM judge replace the reference labels?** It can supply another measurement proposal, but its disagreement, bias and repeatability need validation. Deterministic identity/format checks and human-reviewed support cases remain valuable independent anchors.

## Worked example / walkthrough

### Example A: Calculate recall and reciprocal rank

Both relevant documents are retrieved, but the first appears second. Recall alone would not reveal that ordering.

```python
def retrieval_metrics(retrieved, relevant):
    if len(retrieved) != len(set(retrieved)):
        raise ValueError("duplicate retrieved ID")
    recall = None if not relevant else len(set(retrieved) & relevant) / len(relevant)
    rank = next((i for i, key in enumerate(retrieved, 1) if key in relevant), None)
    return recall, 0.0 if rank is None else 1 / rank


recall, rr = retrieval_metrics(["b", "c", "a"], {"a", "c"})
assert recall == 1 and rr == 0.5
```

**Expected:** recall 1; reciprocal rank 0.5.

### Example B: Measure a retrieval miss

The answer stage cannot use evidence absent from its context. This is a retrieval failure even if a language model guesses the answer from prior training.

```python
assert retrieval_metrics(["b", "c"], {"a"}) == (0.0, 0.0)
```

**Expected:** recall 0; reciprocal rank 0.

### Example C: Handle an unanswerable question

A denominator of zero does not mean perfect recall. The correct task behavior is evaluated through an explicit answerability and abstention policy.

```python
assert retrieval_metrics(["b"], set()) == (None, 0.0)
result = {"question": "q-missing", "answerable": False, "abstained": True}
assert not result["answerable"] and result["abstained"]
```

**Expected:** recall None; appropriate abstention True.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: recall 1; reciprocal rank 0.5. duplicate ID detected. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Calculate recall and reciprocal rank.** Use relevant IDs a, c and retrieved b, c, a.
   **Expected:** recall 1; reciprocal rank 0.5.
   **Verify:** Save the assertion results for exercise 1, including recall 1; reciprocal rank 0.5.

2. **Measure a retrieval miss.** Use relevant a and retrieved b, c.
   **Expected:** recall 0; reciprocal rank 0.
   **Verify:** Save the assertion results for exercise 2, including recall 0; reciprocal rank 0.

3. **Handle an unanswerable question.** Use an empty relevant set and a saved abstention result.
   **Expected:** recall None; appropriate abstention True.
   **Verify:** Save the assertion results for exercise 3, including recall None; appropriate abstention True.

4. **Separate support from correctness.** Record a correct-looking answer whose cited context does not support it.
   **Expected:** correct True but supported False.
   **Verify:** Save the assertion results for exercise 4, including correct True but supported False.

5. **Apply an oracle-context control.** Compare q1 observed incorrect with oracle-context correct under the same rubric.
   **Expected:** paired improvement 1 for q1.
   **Verify:** Save the assertion results for exercise 5, including paired improvement 1 for q1.

6. **Reject duplicate result identities.** Validate one score row per question and inject a duplicateq 1.
   **Expected:** duplicate ID detected.
   **Verify:** Save the assertion results for exercise 6, including duplicate ID detected.

## Common pitfalls and diagnosis

If an aggregate score changes, inspect question identity, cutoff, relevant-set size and missing-case handling before attributing the change to a model. If recall is high but answers fail, check whether all required evidence survived the final context budget and whether the answer used it correctly.

If oracle results improve, compare context length, distractors and source versions as well as missing-document coverage. If a report calls saved labels observed model performance, locate the missing execution artifact. If two systems are compared on different question IDs or families, repair the pairing before calculating a gain or uncertainty interval.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Retrieval recall, Reciprocal rank, Oracle-context control using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-011` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-012, Evaluating retrieval and answers with oracle controls.
Read courses/llm-applied/guides/llm-applied-012.md and courses/llm-applied/lessons/llm-applied-012.py. Direct prerequisites: `llm-applied-011`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

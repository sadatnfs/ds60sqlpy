# llm-applied-011: Grounded claims, citations and evidence-based abstention

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-010`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A grounded answer is a set of claims connected to the evidence appropriate for each claim. This chapter builds that connection for a data-science request, distinguishing quotations, computations, interpretations and useful abstention instead of treating citations as decoration.

## Purpose and mental model

Grounded answering requires a connection between each substantive claim and supporting evidence. A citation that points to a real document is not enough if the document does not establish the claim. Preserve document version and character offsets so the cited span can be inspected. Distinguish source quotation, paraphrase and computed result. A deterministic calculation should cite its input records and method, while a quoted policy should cite the exact policy version.

This chapter implements an extractive subject-assistant baseline. It selects an authored supported span and returns it with metadata, or abstains when no supported answer exists. It is deliberately not called a generative LLM. The baseline makes the evidence contract testable before adding a model that may paraphrase or invent claims. Exact substring checks establish span integrity, not general semantic entailment; the fixture includes hand-authored claim-to-span labels for that separate support judgment. Conflicting versions and missing evidence should remain visible rather than be resolved by fluent guesswork.

## Decompose the answer the analyst will read

The Methods Desk is ready to respond to the conversion question. A concise answer might say: “For the selected reporting period, conversion was 30% after excluding test accounts. This descriptive result alone does not establish that the checkout change caused an improvement.” That paragraph contains several claims, each requiring a different supporting artifact.

The metric definition supplies the numerator and denominator rule. The eligibility source establishes the exclusion. The validated data artifact supplies three purchases and ten eligible visits for the stated period. The calculation artifact supplies \(\frac{3}{10}=0.3\). The interpretation statement concerns the absence of a sufficient causal design in the supplied evidence. One citation at the paragraph's end does not automatically support all of those components.

A claim-level representation makes the dependencies visible. The formula claim points to the applicable policy span. The numeric claim points to the accepted inputs and deterministic calculation. The period claim points to the data selection. A causal-effect claim would need additional design and analysis evidence. This representation need not be exposed as raw JSON to the user, but it gives the application something more precise to validate than the answer's overall fluency.

## Quotation, paraphrase and inference have different obligations

An exact quotation has a strong integrity check: the cited source slice should reproduce the quoted text. A paraphrase adds a semantic question: does the new wording preserve the source's scope, conditions and uncertainty? An inference adds another question: do the premises and method justify the conclusion? These obligations build on one another rather than replacing each other.

For example, “test accounts are excluded from this experiment's eligible population” does not establish that every company metric excludes them. A paraphrase that drops “this experiment” broadens the claim. A passage recommending account-level resampling under independent accounts does not establish that such resampling resolves missing outcomes or confounding. Retaining the source's conditions is part of grounding.

Source truth and source attribution also differ. A policy document can establish what the policy states, while an empirical claim may require data beyond that document. When two applicable sources conflict, accurately quoting each can establish that a conflict exists without establishing which one is correct. A useful assistant should expose that state and the declared precedence rule instead of inventing a smooth reconciliation.

The extractive baseline below deliberately makes only a narrow construction: it creates a source-span record or returns unknown when no document is supplied. Its separate support examples show why record construction is not a general entailment validator. Adding a generative stage should preserve that distinction rather than labeling any answer with a valid document ID as grounded.

## Keep the computed artifact as the numerical authority

Numerical explanations are especially easy to corrupt through paraphrase. The tool can return 0.3 while the prose rounds it incorrectly, changes the denominator, describes it as a30-percentage-point improvement or treats it as a treatment effect. Those are different statements even though they share the number 30.

A report interface can bind a numerical claim to a result field and its units. The percentage representation of 0.3 is 30%; a difference of 0.03 between two rates is three percentage points; a relative change from 0.3 to 0.33 is 10%. The requested comparison determines which expression is appropriate. A language model should not choose among them solely because one sounds more persuasive.

The underlying data selection remains part of the claim. “Yesterday” needs a resolved date, timezone and availability cutoff. A late-arriving event may change a revised report without implying that an earlier calculation was arithmetically wrong. Preserve the period and snapshot identity so the explanation describes the result that was actually computed.

For statistical interpretation, retain the method and assumptions alongside the numeric output. A p-value, confidence interval or posterior quantity has a specific meaning under its model and design. A generated description should be checked against that computed artifact and the relevant statistical definition. The [statistics book](../../statistics-ml/README.md) develops those distinctions; a citation-bearing language model response is not a substitute for them.

## Abstention is a task outcome, not an apology

The assistant can be useful while declining a stronger claim. It may explain a known formula while saying that the required count is missing, report a descriptive difference while withholding a causal conclusion, or identify a source conflict that requires a policy decision. A specific limitation tells the analyst what would make the next step possible.

Coverage prevents selective answering from hiding the cost of refusal. In an illustrative set of 100 requests, suppose the system answers 80 and 72 satisfy the full correctness-and-support contract. Its coverage is 0.8 and conditional accuracy is 0.9. The remaining 20 refusals and eight failed answers still matter. A report that presents only 90% accuracy omits how often the system helped and what kinds of errors it made.

The appropriate tradeoff depends on the task. If an accepted answer earns one unit of benefit and a failed answer costs nine, those 72 successes and eight failures have net utility \(72-9\cdot 8=0\) before considering refusal costs. This is an illustrative utility calculation, not a universal deployment threshold. It shows why a seemingly high average accuracy can be insufficient for a particular use. Any score used to select answers must be evaluated for the relevant event and population; cosine similarity is not automatically that probability.

## Evaluate support with deliberate corruptions

Useful negative cases alter one claim while leaving the rest plausible. Swap eligible visits for all visits. Preserve a citation but replace its quote. Remove a condition such as “under independent accounts.” Attach a current version label to old text. Quote the correct formula but invent the count. Each corruption probes a different link in the evidence chain.

A support evaluator should also accept legitimate paraphrases and calculations, so it does not reward only copied wording. Human review, deterministic checks and a model-based judge can contribute different observations. If a judge is used, measure its failures on these controlled cases and on representative real requests before treating its score as a trusted acceptance decision.

The next chapter turns these observations into an evaluation dataset. The aim is to know not only whether a candidate improved, but which stage improved, which cases remain unresolved and what the result can support about the intended assistant.

## Design decisions and when to use this method

Use extractive baselines when citation precision matters and the domain answers are directly present in text. They provide a useful lower-complexity comparison for a generative system. Add generation when synthesis or explanation materially helps, but keep the same claim and citation contract. A generated paraphrase should be evaluated for support, and a computed conclusion should identify its data and method.

Do not confuse an answer containing many citations with a well-supported answer. One citation can be irrelevant, stale or contradicted by another source. Report conflict explicitly and define a source-precedence policy before evaluation. Abstention should be measured through both correctness and coverage: refusing every question avoids unsupported claims but fails the task. Tune the policy on validation cases containing answerable, unanswerable and conflicting-evidence questions.

Use a claim-level record when an answer combines source statements and calculations. Each substantive claim should identify whether it is a quotation, paraphrase, computation or inference, and retain the evidence appropriate to that type. A citation to one document should not silently cover an entire paragraph of unrelated claims.

Choose an abstention policy against the task's cost and coverage requirements. A system that refuses every answer has no unsupported positive claims but provides no useful answers. Compare supported-answer coverage, unsupported-answer rate and important failure cases together.

## Vocabulary and concepts

**Grounded claim:** A statement linked to evidence that supports its content.

**Citation integrity:** Agreement between a citation span and the referenced source bytes.

**Entailment:** The evidence actually establishes the meaning of a claim.

**Abstention policy:** A rule for returning unknown instead of unsupported content.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-011/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-011.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

An answer record contains status, claims and citations. Each citation includes document_id, version, start, end. The examples check source-slice equality and inspect an authored support map separately. The helper constructs the span record; a complete caller must enforce semantic claim support before accepting it. For missing evidence, return status unknown with an empty claim list and a reason. Do not use a low retrieval score alone as a universal answerability threshold without calibration.

## Separate the four questions behind a citation

A citation can answer four different questions: does the referenced document exist, does the stored span reproduce the quoted text, does that text support the stated claim, and is the source itself reliable/applicable? Passing an earlier question does not imply a later one. An exact quote from an obsolete policy has perfect span integrity and can still be the wrong answer to a current-policy question.

The helper extractive_answer constructs a record from a supplied document, span and claim ID. It validates a nonempty in-range span or returns unknown when no document is supplied. It does not look up the claim ID in a semantic support map. The separate exercise inspects an authored support map to show why that gate is necessary. A real caller must establish support before treating the constructed record as a validated grounded answer.

For the metric fixture, the first sentence ends at the first period. The returned quote includes that period and the citation stores document_id, version, start, end. Changing the quote to “Conversion rate is always one” while retaining the span fails the slice-equality test. Changing the claim to statistical significance while retaining the correct metric quote passes slice integrity but fails semantic support. These counterexamples localize two different failures.

An answer can also preserve the words while changing the scope. Suppose a source says “Exclude test accounts from this experiment's eligible population.” A generated claim that all company metrics exclude test accounts adds a universal scope not established by that sentence. Citation existence and overlapping vocabulary are weak proxies for entailment. Human rubrics or a separately validated support evaluator must assess the actual proposition.

Computed claims need a different lineage. The result 0.3 comes from purchases 3 divided by eligible visits 10. A useful record preserves those inputs, the formula, relevant definition version and calculation output. The source definition supports the formula; it does not itself supply the measured count values. A generated explanation should consume the computed artifact rather than recomputing an approximate number from memory. Neither the ratio nor the definition establishes a causal treatment effect.

Abstention is a decision under uncertainty about support. In a simple illustrative utility model, a correct supported answer earns benefit B, an incorrect or unsupported answer incurs cost C, and abstention has utility zero. If p were a calibrated probability of meeting the complete answer contract, answering is favored when pB-(1-p)C>0, or \(p>\frac{C}{B+C}\). This is a derivation under explicit assumptions, not permission to interpret a retrieval score as p. Additional answer costs or asymmetric abstention costs change the threshold.

Coverage and conditional quality must be reported together. If a system answers six of ten questions and five answers satisfy the full contract, coverage is 0.6 and accepted-answer accuracy is \(\frac{5}{6}\). Reporting only \(\frac{5}{6}\) hides the four refusals; reporting only five successes hides whether the failures were unsupported answers or appropriate unknowns. The final task population and cost policy determine which tradeoff is useful.

Conflicting sources need a policy too. A newer version may supersede an older one for current questions, but historical questions can require the older rule. Two simultaneously applicable sources may disagree. Preserve the conflict and source-precedence rule rather than using fluent synthesis to erase it. A supported quote from each side can establish that a conflict exists without establishing which side is correct.

### Interview reasoning with explanatory answers

**Does an exact substring prove an answer is grounded?** It proves a quote matches a declared source span. The question's proposition, source applicability and support relation require additional checks.

**Why can a correct answer still fail this task?** It may be guessed from prior knowledge or use unauthorized/stale evidence. An evidence-grounded task includes the support and access contract, not only the final words.

**How can abstention improve a system without hiding failure?** Declare its policy and report coverage, supported accuracy and failure categories. Keep refusals on answerable questions visible beside successful refusals on unanswerable ones.

## Worked example / walkthrough

### Example A: Return a supported extractive answer

The answer is a controlled source extract. It demonstrates citation construction without claiming that a model inferred the definition independently.

```python
def extractive_answer(document, start, end, claim_id):
    if document is None:
        return {"status": "unknown", "claims": [], "citations": [], "reason": "missing evidence"}
    if not 0 <= start < end <= len(document["text"]):
        raise ValueError("valid nonempty source span required")
    return {
        "status": "answered",
        "claims": [{"id": claim_id, "quote": document["text"][start:end]}],
        "citations": [
            {
                "document_id": document["id"],
                "version": document["version"],
                "start": start,
                "end": end,
            }
        ],
    }


text = "Conversion rate equals purchases divided by eligible visits. Exclude test accounts."
document = {"id": "metric-v1", "version": 1, "text": text}
end = text.index(".") + 1
answer = extractive_answer(document, 0, end, "conversion-definition")
assert answer["status"] == "answered" and len(answer["claims"]) == 1
assert (
    text[answer["citations"][0]["start"] : answer["citations"][0]["end"]]
    == answer["claims"][0]["quote"]
)
```

**Expected:** status answered; one claim; citation slices the exact sentence.

### Example B: Reject a corrupted span

A document ID alone would still look valid. Comparing the exact source slice detects a citation that no longer matches its claimed quote.

```python
bad = {"quote": "Conversion rate is always one."}
assert text[0:end] != bad["quote"]
```

**Expected:** citation integrity check returns False.

### Example C: Abstain on missing evidence

An empty evidence set should not be converted into a confident answer from unrelated top-ranked text. The unknown result is a successful execution of the declared policy.

```python
unknown = extractive_answer(None, 0, 0, "comet-period")
assert unknown == {"status": "unknown", "claims": [], "citations": [], "reason": "missing evidence"}
```

**Expected:** status unknown; claims empty; reason missing evidence.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: status answered; one claim; citation slices the exact sentence. rate.3 with input counts preserved. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Return a supported extractive answer.** Answer the conversion-definition question from the metric document and its first sentence.
   **Expected:** status answered; one claim; citation slices the exact sentence.
   **Verify:** Save the assertion results for exercise 1, including status answered; one claim; citation slices the exact sentence.

2. **Reject a corrupted span.** Change the stored quote while leaving citation offsets unchanged.
   **Expected:** citation integrity check returns False.
   **Verify:** Save the assertion results for exercise 2, including citation integrity check returns False.

3. **Abstain on missing evidence.** Request an unsupported comet-period answer with no admitted supporting document.
   **Expected:** status unknown; claims empty; reason missing evidence.
   **Verify:** Save the assertion results for exercise 3, including status unknown; claims empty; reason missing evidence.

4. **Separate a valid citation from support.** Cite the metric document for a claim about statistical significance and inspect the authored support map.
   **Expected:** document exists but significance claim unsupported.
   **Verify:** Save the assertion results for exercise 4, including document exists but significance claim unsupported.

5. **Bind the source version.** Compare a citation requiring version 1 with a supplied version 2 document.
   **Expected:** version mismatch blocks citation reuse.
   **Verify:** Save the assertion results for exercise 5, including version mismatch blocks citation reuse.

6. **Keep arithmetic separate from prose.** Compute 3 purchases over 10 visits and attach the deterministic result to an explanation record.
   **Expected:** rate.3 with input counts preserved.
   **Verify:** Save the assertion results for exercise 6, including rate.3 with input counts preserved.

## Common pitfalls and diagnosis

If a citation opens correctly but the claim is wrong, inspect the proposition and scope rather than only the offsets. If a quote no longer matches, compare source version and coordinate system. If a computed number differs from the report, trace the validated input and output artifact instead of asking a model to justify the discrepancy.

If unsupported answers fall only because the system answers fewer questions, inspect coverage and the mix of refused cases. If the helper is described as an entailment validator, locate the absent support-map enforcement and separate record construction from acceptance. Preserve conflicting evidence as an explicit state rather than silently choosing the most convenient passage.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Grounded claim, Citation integrity, Entailment using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-010` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-011, Grounded claims, citations and evidence-based abstention.
Read courses/llm-applied/guides/llm-applied-011.md and courses/llm-applied/lessons/llm-applied-011.py. Direct prerequisites: `llm-applied-010`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

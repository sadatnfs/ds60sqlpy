# llm-applied-001: The subject assistant decision: prompts, retrieval or fine-tuning

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-014`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A subject assistant is a system that helps someone perform a bounded task using a defined body of knowledge. The central investigation is concrete: Describe a request for the current conversion-rate definition requiring a citation. The finish condition is route retrieval; reason current cited evidence. contract has exact fields, an abstention policy and a family split. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A subject assistant is a system that helps someone perform a bounded task using a defined body of knowledge. It is not created merely by adding “you are an expert” to a prompt. Begin with the prediction or decision unit: extracting a study design field, finding a current metric definition, explaining a calculation, or deciding whether evidence supports a claim. Each task needs a measurable output contract and a failure policy. Prompting changes instructions and examples presented at inference. Retrieval supplies selected external evidence without changing model weights. Supervised fine-tuning changes weights using examples of desired behavior. These mechanisms can be combined, but they address different deficiencies.

For a data-science assistant, a current metric definition belongs in versioned retrieval because it may change and needs a source. A repeated formatting failure may justify prompt improvement or fine-tuning after a baseline is measured. Exact aggregation belongs in deterministic code with a validated input schema. Causal interpretation still requires a defensible study design; a model can help inspect that design but cannot make an observational comparison causal by describing it confidently. This lesson builds an explicit decision policy over task characteristics, not an artificial intelligence model.

## Design decisions and when to use this method

Use a prompt baseline when the desired behavior can be specified with instructions and a few examples. Use retrieval when answers depend on changing, attributable or access-controlled documents. Consider adaptation when a stable pattern repeatedly fails despite a measured prompt baseline and governed training examples are available. Do not fine-tune merely because the domain has a specialized name. Fine-tuning can reproduce stale facts, encode annotation mistakes and make failures harder to trace to a document version. It also introduces model, data and optimizer artifacts that need evaluation and rollback.

A useful comparison holds questions, scoring rules and evidence access fixed. Compare prompt-only, retrieved-context and adapted variants on the same held-out families, then inspect failure categories rather than selecting only by average score. A hybrid design can retrieve facts, use an adapted model to follow a response schema, and delegate arithmetic to code. The design is justified by the task evidence, not by the number of components.

## Vocabulary and concepts

**Subject assistant:** A bounded task system with domain sources, tools and evaluation.

**RAG:** Retrieval-augmented generation: external evidence supplied during answering.

**SFT:** Supervised fine-tuning: weight updates from target output examples.

**Task contract:** Accepted inputs, output schema, metric and failure behavior.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-001/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-001.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-001.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Represent a task as named fields rather than one free-form paragraph. A route decision should expose its reason and required evidence. Check exact-computation needs before choosing a text-generation strategy. Check freshness and citation needs before considering weight updates. Fine-tuning requires a stable behavioral target, sufficient governed examples and a held-out evaluation. A missing prerequisite produces a “measure baseline first” decision, not an automatic training job.

## Worked example / walkthrough

### Example A: Route a changing definition

A definition can change after training, so its identity and version should remain inspectable outside model weights. Retrieval is a way to supply that evidence, not a guarantee the answer will use it faithfully.

```python
import numpy as np
def choose(task):
    if task['exact_computation']: return 'deterministic_tool','exact computation'
    if task['fresh_evidence'] or task['citation_required']: return 'retrieval','current cited evidence'
    if task['stable_behavior_gap'] and task['governed_examples']>=100: return 'adaptation_candidate','stable measured behavior'
    return 'measure_baseline','prompt and evaluation first'
task={'exact_computation':False,'fresh_evidence':True,'citation_required':True,'stable_behavior_gap':False,'governed_examples':0}
assert choose(task)==('retrieval','current cited evidence')
```

**Expected:** route retrieval; reason current cited evidence.

### Example B: Route an exact calculation

The assistant may explain the result, but the arithmetic should be performed by a bounded deterministic function. A fluent estimate is not an acceptable substitute for an exact total.

```python
task={'exact_computation':True,'fresh_evidence':False,'citation_required':False,'stable_behavior_gap':False,'governed_examples':0}
assert choose(task)==('deterministic_tool','exact computation')
```

**Expected:** route deterministic_tool; reason exact computation.

### Example C: Require evidence before fine-tuning

The threshold120 is a teaching admission rule, not a universal sample-size recommendation. A real decision needs learning curves, label quality and held-out task evidence.

```python
task={'exact_computation':False,'fresh_evidence':False,'citation_required':False,'stable_behavior_gap':True,'governed_examples':0}
assert choose(task)[0]=='measure_baseline'
task['governed_examples']=120; assert choose(task)[0]=='adaptation_candidate'
```

**Expected:** first measure_baseline; then adaptation_candidate.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: route retrieval; reason current cited evidence. contract has exact fields, an abstention policy and a family split. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Route a changing definition.** Describe a request for the current conversion-rate definition requiring a citation.
   **Expected:** route retrieval; reason current cited evidence.
   **Verify:** Save the assertion results for exercise 1, including route retrieval; reason current cited evidence.

2. **Route an exact calculation.** Describe a request to sum validated purchase amounts and return an integer-cent total.
   **Expected:** route deterministic_tool; reason exact computation.
   **Verify:** Save the assertion results for exercise 2, including route deterministic_tool; reason exact computation.

3. **Require evidence before fine-tuning.** Describe a stable schema-formatting gap with zero governed examples, then with 120 reviewed examples.
   **Expected:** first measure_baseline; then adaptation_candidate.
   **Verify:** Save the assertion results for exercise 3, including first measure_baseline; then adaptation_candidate.

4. **Keep mechanisms composable.** A task needs current policy citations and a stable response schema; state which stage retrieves evidence and which might be adapted.
   **Expected:** retrieval remains required; format adaptation is separate.
   **Verify:** Save the assertion results for exercise 4, including retrieval remains required; format adaptation is separate.

5. **Avoid training on secrets as an access mechanism.** Mark restricted facts as requiring an access policy and reject the idea that a fine-tuned model enforces per-user authorization.
   **Expected:** authorization remains an external gate.
   **Verify:** Save the assertion results for exercise 5, including authorization remains an external gate.

6. **Write a measurable subject-assistant contract.** Define an assistant for study-design extraction with fields assignment_unit, outcome and unknown status; name a held-out family split.
   **Expected:** contract has exact fields, an abstention policy and a family split.
   **Verify:** Save the assertion results for exercise 6, including contract has exact fields, an abstention policy and a family split.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Subject assistant, RAG, SFT using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-014` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-001, The subject assistant decision: prompts, retrieval or fine-tuning.
Read courses/llm-applied/guides/llm-applied-001.md and courses/llm-applied/lessons/llm-applied-001.py. Direct prerequisites: `llm-014`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

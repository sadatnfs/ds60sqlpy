# llm-applied-001: The subject assistant decision: prompts, retrieval or fine-tuning

## Level and prerequisites

Beginner; approximately 180 minutes. Direct prerequisites: `llm-014`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A useful subject-matter assistant must connect a question to the right knowledge, computation and evidence. This chapter develops that architecture from an analyst's concrete request, then explains how prompting, retrieval and fine-tuning change different parts of the system.

## Purpose and mental model

A subject assistant is a system that helps someone perform a bounded task using a defined body of knowledge. It is not created merely by adding “you are an expert” to a prompt. Begin with the prediction or decision unit: extracting a study design field, finding a current metric definition, explaining a calculation, or deciding whether evidence supports a claim. Each task needs a measurable output contract and a failure policy. Prompting changes instructions and examples presented at inference. Retrieval supplies selected external evidence without changing model weights. Supervised fine-tuning changes weights using examples of desired behavior. These mechanisms can be combined, but they address different deficiencies.

For a data-science assistant, a current metric definition belongs in versioned retrieval because it may change and needs a source. A repeated formatting failure may justify prompt improvement or fine-tuning after a baseline is measured. Exact aggregation belongs in deterministic code with a validated input schema. Causal interpretation still requires a defensible study design; a model can help inspect that design but cannot make an observational comparison causal by describing it confidently. This lesson builds an explicit decision policy over task characteristics, not an artificial intelligence model.

## A question that requires more than a plausible sentence

Imagine an analyst asking a Methods Desk assistant: “What was conversion yesterday, and should we conclude that the checkout change worked?” The assistant has access to a metric handbook and, through a reviewed tool, a small table of events. This is an illustrative design case rather than a recorded model experiment. Its purpose is to expose the decisions hidden inside an apparently simple question.

There are 12 recorded visits and four recorded purchases. Two visits belong to test accounts, and one of those visits contains a purchase. The handbook defines conversion using eligible visits and excludes test accounts. The descriptive calculation is therefore(4-1)/(12-2)=3/10=0.3. Dividing the raw totals gives \(\frac{4}{12}\), about 0.3333. Both expressions are easy to calculate; only one matches the stated eligibility policy. An arithmetic-capable model can still give the wrong answer if it selects the wrong definition or fails to apply the exclusion.

The second half of the question asks for a stronger conclusion. A comparison with an earlier day can reflect changes in traffic, measurement, user composition or the checkout itself. The assistant must know whether there was random assignment, which unit was assigned, which outcomes were observed and which analysis was planned. The number 0.3 is a descriptive result. It does not contain that design information. A helpful answer can report the value, identify the definition and computation, and explain what evidence is missing before interpreting the checkout change.

This decomposition gives the assistant a practical purpose: shorten the path from an analyst's question to a reviewable evidence chain. It should help find the applicable definition, preserve units, prepare a bounded tool request and explain the resulting artifact. The assistant's most valuable behavior may sometimes be noticing that the requested conclusion is stronger than the available evidence.

## What changes when a prompt, context or model changes

A causal language model represents a conditional distribution over continuations. For a generated answer y, one conceptual description is p_theta(y given I,q,C), where theta denotes learned parameters, I the instructions, q the question and C the supplied context. The actual model receives a serialized token sequence rather than these mathematical labels. The separation is useful for system design because it identifies what an intervention changes.

Prompt engineering changes how the task, examples and requested output are expressed in I and sometimes q. Retrieval chooses evidence to place in C. Fine-tuning changes theta using a training objective over examples. A single application can use all three: retrieve the current handbook paragraph, ask for a structured analysis request, and use an adapted model that has learned the organization's response format.

These mechanisms do not provide equivalent update paths. If the handbook changes tomorrow, replacing a versioned document and rebuilding the appropriate index can make the new evidence available without retraining the answer model. If the model repeatedly confuses assignment_unit with analysis_unit even when the correct source is present, the problem may concern interpretation or output behavior rather than missing knowledge. Better instructions, examples or supervised adaptation could then be useful. If the model invents a sum after receiving the right counts, the application can move that calculation into a deterministic tool.

A retrieval-augmented system can itself contain trained retrievers and trained generators. The distinction here is between supplying evidence during a particular inference and updating learned parameters. Saying that retrieval supplies context does not imply that every component in a RAG architecture is permanently untrained. Conversely, an adapted model can still require retrieval because learned response behavior does not eliminate the need for current, attributable evidence.

## Diagnose a failure before selecting a training method

Suppose the Methods Desk produces four failures. In the first, it cites an obsolete denominator definition. In the second, it reads the current definition correctly but emits a string where the required count is an integer. In the third, it receives valid counts but reports 0.33 after the tool returned 0.3. In the fourth, it describes an observational difference as a proven treatment effect.

These failures suggest different interventions. The stale definition points toward corpus/version selection. The type mismatch points toward output contracts and validation, with prompting or adaptation considered after observing the pattern. The changed numeric result points toward the interface between the computed artifact and its explanation. The causal overclaim points toward the interpretation rubric and the evidence supplied about study design. Training one model on a handful of corrected answers might reduce all four visible examples while leaving their underlying causes intact.

A controlled diagnosis starts with the least ambiguous experiment. Supply the correct definition directly and see whether the answer stage can use it. Supply already validated counts and check the calculation/explanation boundary. Give a counterexample with no randomized assignment and inspect the claim. Each intervention holds other conditions as stable as possible. The result is a reason to change a particular component, not a generic preference for a more complex architecture.

Fine-tuning becomes a defensible candidate when the desired behavior is stable, examples can teach it, and a measured baseline repeatedly fails. Examples should represent the variation that matters: different wording, missing information, ambiguous units, relevant distractors and legitimate unknowns. A hundred copies of one template do not provide the same information as a smaller set of independently informative cases. The admission count in the runnable fixture is a pedagogical rule, not a statistical sample-size calculation.

## Build a comparison that answers the engineering question

To decide whether retrieval helps, compare candidates on the same question families with a declared evidence policy. To decide whether adaptation helps, keep the evaluation questions and source access fixed and use real outputs from both parameter states. To decide whether a hybrid is worth its cost, include work, latency and failure categories alongside answer quality. A candidate should not win merely because it receives a larger context or is evaluated on easier questions.

The unit of evaluation is also part of the claim. If ten questions are paraphrases of one metric definition, they provide useful robustness checks but limited evidence about transfer to ten independent domains. A held-out handbook family or a new type of analytical request asks a harder question. The experiment should distinguish success on the training behavior from success on the intended deployment population.

This chapter's route selector does not run a language model. It makes the design decision visible through named inputs and reasons. The later adaptation chapters perform real updates, and the optional pretrained recipe records a revealing failure: training and reload succeeded, but a generated formula was wrong despite supplied evidence. That result belongs in the same engineering story. The model, retrieval, tool and evaluation contracts must each earn their part of the answer.

The next chapter takes the first concrete interface in that story: turning a source statement into a typed analytical record without losing its units, provenance or missingness.

## Design decisions and when to use this method

Use a prompt baseline when the desired behavior can be specified with instructions and a few examples. Use retrieval when answers depend on changing, attributable or access-controlled documents. Consider adaptation when a stable pattern repeatedly fails despite a measured prompt baseline and governed training examples are available. Do not fine-tune merely because the domain has a specialized name. Fine-tuning can reproduce stale facts, encode annotation mistakes and make failures harder to trace to a document version. It also introduces model, data and optimizer artifacts that need evaluation and rollback.

A useful comparison holds questions, scoring rules and evidence access fixed. Compare prompt-only, retrieved-context and adapted variants on the same held-out families, then inspect failure categories rather than selecting only by average score. A hybrid design can retrieve facts, use an adapted model to follow a response schema, and delegate arithmetic to code. The design is justified by the task evidence, not by the number of components.

For a metric assistant, separate four requests that may appear in one sentence: identify the applicable definition, extract the required inputs, compute the value and explain its interpretation. Retrieval can supply the definition; a proposal model can extract fields; trusted validation and code can compute the value. The final interpretation still depends on the study design. Choose the component to change from an observed failure at that stage.

The fixture's numeric admission rule is intentionally simple: at least 100 governed examples makes a stable behavior gap an adaptation candidate. The 120-example case passes that rule. It is not an instruction to train after collecting a magic number of rows. A small set of independently informative examples can differ greatly from many duplicated templates.

## Vocabulary and concepts

**Subject assistant:** A bounded task system with domain sources, tools and evaluation.

**RAG:** Retrieval-augmented generation: external evidence supplied during answering.

**SFT:** Supervised fine-tuning: weight updates from target output examples.

**Task contract:** Accepted inputs, output schema, metric and failure behavior.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-001/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-001.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Represent a task as named fields rather than one free-form paragraph. A route decision should expose its reason and required evidence. Check exact-computation needs before choosing a text-generation strategy. Check freshness and citation needs before considering weight updates. Fine-tuning requires a stable behavioral target, sufficient governed examples and a held-out evaluation. A missing prerequisite produces a “measure baseline first” decision, not an automatic training job.

## Trace a subject-assistant request through its evidence requirements

Consider: “What is our current account conversion rate, and did the new checkout cause it to improve?” This contains several distinct claims. The word current requires the correct effective definition and data period. Account requires a denominator and grouping unit. Conversion rate requires validated counts and arithmetic. Cause requires treatment assignment or defensible identification assumptions. One well-formed generated sentence cannot establish all four.

| Subtask | Required input | Inspectable output | Failure that belongs here |
| --- | --- | --- | --- |
| Find the definition | Authorized, effective source version | Source ID and supported formula | Wrong version or missing source |
| Extract fields | Source text or structured observations | Typed fields with provenance | Unsupported count or wrong unit |
| Calculate | Accepted inputs and declared formula | Reproducible numeric artifact | Wrong denominator or arithmetic |
| Interpret | Population and study design | Bounded claim with assumptions | Unsupported causal conclusion |

A trained model can participate in the first two interfaces or explain the last two, but its fluency does not replace their evidence. The routing helper returns one primary route, while the composed architecture may contain several stages. In particular, exact_computation takes precedence in the helper. That priority is a teaching decision about one requested operation; it does not mean a numerical tool can discover an unknown business definition on its own.

A simple probability decomposition explains why adding components is not automatically an improvement. Let R mean sufficient admissible evidence reached the answer stage, A mean the answer is correct and supported given that evidence, and V mean the result meets the required validation contract. The success probability for this complete path is P(R) times P(A given R) times P(V given A and R). These conditional factors do not require an independence assumption. In an illustrative calculation, 0.9 times 0.8 times 0.95 is 0.684. Those values are invented for arithmetic explanation, not measured model performance. Improving the last factor alone cannot recover all failures from missing evidence.

Use controlled comparisons to choose an intervention. A prompt baseline can reveal whether the task is already expressible without training. An oracle-context control can show whether answer behavior improves when relevant evidence is supplied directly. A retrieval intervention holds the answering configuration fixed while changing evidence selection. An adaptation comparison holds evaluation families and access conditions fixed while changing learned behavior. If all of those change together, an improved score does not identify the useful component.

Retrieval changes the inference evidence available to a model; adaptation changes the model's parameterized behavior. The original RAG work combined parametric generation with explicit retrieved memory, but this course's first route selector performs neither learned retrieval nor generation. Its role is to make decisions and prerequisites inspectable. [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401).

### Interview reasoning with explanatory answers

**Why not fine-tune current policy documents directly into the model?** Updates, source attribution and per-request access remain separate problems. A memorized fact does not expose which version supports it or whether the current principal may see it. Adaptation may still improve a stable response behavior, while retrieved evidence supplies current facts.

**When is a deterministic tool the right answer?** When the task requires an exact operation over validated inputs and a declared formula. The tool's correctness does not establish that the extracted inputs or chosen denominator were appropriate; retain those upstream contracts too.

**What makes an adaptation experiment informative?** A measured behavior gap, governed examples, a frozen comparison policy, independent evaluation families and real outputs from both candidates. A training loss by itself measures fit to training targets, not domain-assistant utility.

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

The example count 120 exceeds the helper's teaching admission threshold 100; neither number is a universal sample-size recommendation. A real decision needs learning curves, label quality and held-out task evidence.

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

If an assistant returns the right number under the wrong definition, debug definition/version selection before arithmetic. If a tool computes correctly from invented counts, the error is at extraction or validation. If a response follows the schema but invents a causal explanation, inspect the claim rubric and study-design evidence rather than only format compliance.

If every proposed fix adds another model, compare the existing stages against an oracle control first. If a report cites the 120-example demonstration as a sample-size law, return to the helper's actual threshold 100 and its explicitly artificial admission role. Record which route was chosen, which prerequisites were satisfied and which quality evidence remains unobserved.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Subject assistant, RAG, SFT using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-014` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-001, The subject assistant decision: prompts, retrieval or fine-tuning.
Read courses/llm-applied/guides/llm-applied-001.md and courses/llm-applied/lessons/llm-applied-001.py. Direct prerequisites: `llm-014`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

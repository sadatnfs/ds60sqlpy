# llm-applied-001: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A subject assistant is a system that helps someone perform a bounded task using a defined body of knowledge. It is not created merely by adding “you are an expert” to a prompt. Begin with the prediction or decision unit: extracting a study design field, finding a current metric definition, explaining a calculation, or deciding whether evidence supports a claim. Each task needs a measurable output contract and a failure policy. Prompting changes instructions and examples presented at inference. Retrieval supplies selected external evidence without changing model weights. Supervised fine-tuning changes weights using examples of desired behavior. These mechanisms can be combined, but they address different deficiencies.

For a data-science assistant, a current metric definition belongs in versioned retrieval because it may change and needs a source. A repeated formatting failure may justify prompt improvement or fine-tuning after a baseline is measured. Exact aggregation belongs in deterministic code with a validated input schema. Causal interpretation still requires a defensible study design; a model can help inspect that design but cannot make an observational comparison causal by describing it confidently. This lesson builds an explicit decision policy over task characteristics, not an artificial intelligence model.

**Subject assistant:** A bounded task system with domain sources, tools and evaluation.

**RAG:** Retrieval-augmented generation: external evidence supplied during answering.

**SFT:** Supervised fine-tuning: weight updates from target output examples.

**Task contract:** Accepted inputs, output schema, metric and failure behavior.

## Reading the implementation

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

A simple probability decomposition explains why adding components is not automatically an improvement. Let R mean sufficient admissible evidence reached the answer stage, A mean the answer is correct and supported given that evidence, and V mean the result meets the required validation contract. The success probability for this complete path is P(R) times P(A given R) times P(V given A and R). These conditional factors do not require an independence assumption. In an illustrative calculation, 0.9 times0.8 times0.95 is 0.684. Those values are invented for arithmetic explanation, not measured model performance. Improving the last factor alone cannot recover all failures from missing evidence.

Use controlled comparisons to choose an intervention. A prompt baseline can reveal whether the task is already expressible without training. An oracle-context control can show whether answer behavior improves when relevant evidence is supplied directly. A retrieval intervention holds the answering configuration fixed while changing evidence selection. An adaptation comparison holds evaluation families and access conditions fixed while changing learned behavior. If all of those change together, an improved score does not identify the useful component.

Retrieval changes the inference evidence available to a model; adaptation changes the model's parameterized behavior. The original RAG work combined parametric generation with explicit retrieved memory, but this course's first route selector performs neither learned retrieval nor generation. Its role is to make decisions and prerequisites inspectable. [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401).

### Interview reasoning with explanatory answers

**Why not fine-tune current policy documents directly into the model?** Updates, source attribution and per-request access remain separate problems. A memorized fact does not expose which version supports it or whether the current principal may see it. Adaptation may still improve a stable response behavior, while retrieved evidence supplies current facts.

**When is a deterministic tool the right answer?** When the task requires an exact operation over validated inputs and a declared formula. The tool's correctness does not establish that the extracted inputs or chosen denominator were appropriate; retain those upstream contracts too.

**What makes an adaptation experiment informative?** A measured behavior gap, governed examples, a frozen comparison policy, independent evaluation families and real outputs from both candidates. A training loss by itself measures fit to training targets, not domain-assistant utility.

## Exercise 1: Route a changing definition

The question is: Describe a request for the current conversion-rate definition requiring a citation.

A definition can change after training, so its identity and version should remain inspectable outside model weights. Retrieval is a way to supply that evidence, not a guarantee the answer will use it faithfully.

```python
task={'exact_computation':False,'fresh_evidence':True,'citation_required':True,'stable_behavior_gap':False,'governed_examples':0}
assert choose(task)==('retrieval','current cited evidence')
```

**Expected:** route retrieval; reason current cited evidence.

**Verify:** Compare the computed values or written argument with route retrieval; reason current cited evidence.

## Exercise 2: Route an exact calculation

The question is: Describe a request to sum validated purchase amounts and return an integer-cent total.

The assistant may explain the result, but the arithmetic should be performed by a bounded deterministic function. A fluent estimate is not an acceptable substitute for an exact total.

```python
task={'exact_computation':True,'fresh_evidence':False,'citation_required':False,'stable_behavior_gap':False,'governed_examples':0}
assert choose(task)==('deterministic_tool','exact computation')
```

**Expected:** route deterministic_tool; reason exact computation.

**Verify:** Compare the computed values or written argument with route deterministic_tool; reason exact computation.

## Exercise 3: Require evidence before fine-tuning

The question is: Describe a stable schema-formatting gap with zero governed examples, then with 120 reviewed examples.

The example count 120 exceeds the helper's teaching admission threshold100; neither number is a universal sample-size recommendation. A real decision needs learning curves, label quality and held-out task evidence.

```python
task={'exact_computation':False,'fresh_evidence':False,'citation_required':False,'stable_behavior_gap':True,'governed_examples':0}
assert choose(task)[0]=='measure_baseline'
task['governed_examples']=120; assert choose(task)[0]=='adaptation_candidate'
```

**Expected:** first measure_baseline; then adaptation_candidate.

**Verify:** Compare the computed values or written argument with first measure_baseline; then adaptation_candidate.

## Exercise 4: Keep mechanisms composable

The question is: A task needs current policy citations and a stable response schema; state which stage retrieves evidence and which might be adapted.

Fine-tuning a response style does not remove the need for current evidence. Separate stage metrics make it possible to diagnose a retrieval failure independently of a formatting failure.

```python
task={'exact_computation':False,'fresh_evidence':True,'citation_required':True,'stable_behavior_gap':True,'governed_examples':120}
assert choose(task)[0]=='retrieval'
architecture={'knowledge':'versioned retrieval','format':'prompt baseline, then measured adapter if needed'}
assert architecture['knowledge']=='versioned retrieval'
```

**Expected:** retrieval remains required; format adaptation is separate.

**Verify:** Compare the computed values or written argument with retrieval remains required; format adaptation is separate.

## Exercise 5: Avoid training on secrets as an access mechanism

The question is: Mark restricted facts as requiring an access policy and reject the idea that a fine-tuned model enforces per-user authorization.

Model weights are not a record-level permission system. Per-user access decisions must happen before evidence reaches the answer context and must also govern caches and logs.

```python
policy={'access_control':'external pre-retrieval filter','weights_are_acl':False}
assert not policy['weights_are_acl'] and 'pre-retrieval' in policy['access_control']
```

**Expected:** authorization remains an external gate.

**Verify:** Compare the computed values or written argument with authorization remains an external gate.

## Exercise 6: Write a measurable subject-assistant contract

The question is: Define an assistant for study-design extraction with fields assignment_unit, outcome and unknown status; name a held-out family split.

A task contract turns “expert assistant” into something testable. The unsupported-field rate catches confident invented values that a schema-validity metric alone would miss.

```python
contract={'fields':['assignment_unit','outcome','status'],'unknown_policy':'explicit unknown','split_unit':'study family','metric':'field exact match plus unsupported-field rate'}
assert contract['split_unit']=='study family' and 'unsupported' in contract['metric']
```

**Expected:** contract has exact fields, an abstention policy and a family split.

**Verify:** Compare the computed values or written argument with contract has exact fields, an abstention policy and a family split.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

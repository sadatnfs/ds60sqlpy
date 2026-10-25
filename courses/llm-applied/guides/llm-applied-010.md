# llm-applied-010: Query rewriting and bounded multi-hop retrieval

## Level and prerequisites

Intermediate; approximately 180 minutes. Direct prerequisites: `llm-applied-009`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

Some analytical questions need vocabulary translation or several linked sources. This chapter develops a bounded retrieval plan from a missing-evidence question, explains the meaning of each hop, and shows how to preserve intent, scope and termination while the evidence set grows.

## Purpose and mental model

Query rewriting can translate a user's phrasing into terms that a retriever understands. It can also distort intent, add unsupported assumptions or broaden the search beyond the authorized domain. A rewrite should be treated as a proposal with a provenance trail, not as a new trusted user instruction. Multi-hop retrieval performs another search using information found in an earlier result, useful when a question requires connecting a metric definition with an exclusion policy. Each hop should have a purpose, a bounded candidate count and a stopping rule.

This lesson uses a curated synonym map and a two-hop document graph. It does not ask a model to invent search plans. The deterministic baseline makes the failure modes visible: a rewrite can help lexical recall, but a cycle can repeatedly retrieve the same documents, and an unsupported bridge can lead to an irrelevant answer. Preserve the original question, each rewritten query, retrieved IDs and the reason for continuing. Authorization remains fixed across every hop.

## Ask what evidence is missing before asking another question

An analyst asks: “Our experiment randomized accounts, but outcomes are recorded as repeated visits. What should be resampled for an uncertainty estimate?” The Methods Desk may need an assignment-design source and a source describing the dependence of repeated observations. Finding only a generic bootstrap paragraph is insufficient because the resampling unit is the substantive issue.

A useful retrieval plan names that dependency. The first search locates the experiment's assignment and observation structure. The next search locates the method guidance relevant to independent accounts with repeated visits. The answer can then explain why treating all visits as independent would require an assumption not established by the design. It still needs the actual data and a justified analysis plan before producing an uncertainty estimate.

This is different from adding searches until the model feels confident. Each additional step should have a reason tied to an unresolved claim: a missing definition, an eligibility exception, a linked method or a conflicting source. Without that reason, more context can add noise and contradictions while consuming the budget intended for useful evidence.

## A rewrite is an interpretation that can be wrong

The controlled synonym rule below replaces buy with purchase. That can repair a simple vocabulary mismatch. A realistic rewrite may be more ambitious, expanding an abbreviation or translating a user's informal question into the corpus's terminology. The expansion can help retrieval while also changing the task.

For example, rewriting “Should test accounts be excluded?” into “conversion-rate definition” can lose the user's focus on an exception. Rewriting “Why did variance increase?” into “how to normalize feature variance” assumes that variance refers to preprocessing rather than sampling uncertainty. A good system retains the original question and treats the rewrite as a proposal that can be compared with it.

Important constraints should survive the transformation: entity, time period, units, negation, requested comparison and access scope. A rewrite that removes “not,” changes accounts to visits or substitutes a broader project identifier may retrieve plausible but unsuitable evidence. Preserving an original-query branch can protect exact terms while another branch explores paraphrases, but the combined work and final context must remain bounded.

## A link is a route to inspect, not a proof to adopt

The graph fixture represents a chain from a metric definition to exclusions and then to test-account details. Breadth-first traversal makes the edge-count meaning of a hop explicit. Starting at depth zero, the two-hop result includes nodes at distances zero, one and two. The visited set prevents a cycle from repeatedly emitting the same identity.

A real document link can have several meanings: an authoritative dependency, a related-topic suggestion, an obsolete reference or a navigation convenience. The existence of a path does not establish the logical relationship needed for the answer. If a metric page links to a general experimentation guide, the assistant still must determine whether the cited section applies to the experiment being analyzed.

This distinction is especially important in generated plans. A language model can propose a bridge that sounds plausible without source support. The application should retain why the bridge was followed and which admitted passage established the connection. A missing bridge is an incomplete-evidence state, not permission to synthesize a confident relationship between unrelated sources.

## Bound depth, breadth and actual work separately

The fixed graph walk has a depth limit and a visited set. Those controls prevent particular forms of repeated or over-deep traversal, but they do not bound every resource. A single node may have hundreds of outgoing links. A shallow search can therefore examine many candidates, and one remote request can take a long time even when the call count is small.

A complete retrieval loop may need separate budgets for hops, candidate IDs examined, documents fetched, model calls, context tokens and elapsed time. Each budget should specify what is charged when an operation fails or is retried. The local helper performs no network fetch, so its successful cycle test does not establish cancellation or timeout behavior for a remote service.

The integer validation also has a conceptual purpose. A hop count is discrete. Accepting 1.5 and comparing it with integer depths would not define a meaningful stopping boundary. The already-qualified implementation rejects that configuration before traversal. Input types can be part of the algorithm's termination proof, not merely a style preference.

## Stop when the contract is satisfied or cannot be satisfied

A useful stopping rule can depend on evidence sufficiency rather than the first positive score. If the answer requires a definition and an exclusion rule, finding only the definition does not finish the task. If an additional authorized source supplies the exclusion and both versions are applicable, the evidence requirement may be complete. If the work budget expires first, the response should identify the remaining limitation rather than treat partial retrieval as a complete answer.

Sufficiency labels are themselves part of the evaluation design. Some questions can be answered by any one of several equivalent passages; others require several facts jointly. A planner that stops after the first relevant hit may work on the former and fail systematically on the latter. Preserve that distinction in the held-out question set.

Measure each retrieval step's contribution. Did it add a required fact, repeat an existing source, introduce a contradiction or merely produce more text? Keep the original query, proposed rewrites, admitted candidates and termination reason in the trace. This record allows a reviewer to improve the plan without attributing every failure to the final generator.

The following chapter turns the selected evidence into claims. The boundary becomes stricter: a retrieved passage is a candidate source, while a grounded answer must explain exactly what that source supports and which requested claims remain unresolved.

## Design decisions and when to use this method

Use rewriting when relevance tests show a systematic vocabulary mismatch, and use multiple hops when the task genuinely needs linked evidence rather than one passage. Keep the original query as a retrieval branch so a bad rewrite does not erase exact identifiers. For a model-generated plan, validate each proposed query and link against the same scope and budget rules as any other input.

Do not add hops merely because the first result looks uncertain. More retrieved text can introduce contradictions and consume answer context. Evaluate whether each hop improves evidence recall or answer support on held-out question families. Record duplicate rate, total documents examined and termination reasons. A missing bridge should lead to an explicit incomplete-evidence answer, not an invented connection between unrelated documents.

Retain the original query as a branch when a rewrite is intended to improve vocabulary coverage. The rewritten form can lose exact identifiers, negation or units. Compare both branches on the same admitted corpus and inspect which additional results improve actual evidence sufficiency.

Use a hop limit together with limits on examined candidates, total work and elapsed time. Depth alone does not bound a broad graph tightly. The local helper traverses an already materialized finite graph and now validates an integer depth budget; it does not implement remote deadlines or network cancellation.

## Vocabulary and concepts

**Query rewrite:** A transformed search query derived from an original question.

**Multi-hop retrieval:** A bounded sequence of searches or evidence-link traversals.

**Bridge evidence:** A source that justifies connecting one retrieval step to another.

**Stopping rule:** A condition ending retrieval before unbounded exploration.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-010/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. Use the Docker classroom as the default route and select the declared `python-core` profile. For a separately prepared native environment, invoke its explicitly selected interpreter on `courses/llm-applied/lessons/llm-applied-010.py` from the repository root. The general repository `.venv` is not assumed to include the heavy model dependencies.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the tolerance stated in each assertion. Many analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone does not determine a universal error bound. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Tokenize the query, apply only declared synonym substitutions and retain the original text in a trace. A bounded breadth-first traversal uses a queue, visited set and maximum-hop count. Follow only explicit local document links. The visited set prevents cycles from consuming the budget indefinitely. A new query or link cannot add an unauthorized document because the same admitted corpus is used throughout.

## Trace the retrieval frontier and the stopping policy

The fixture starts at metric with depth zero. A queue entry records both node and distance in edges from the start. Removing metric from the queue emits it; if the depth is below the limit, its admitted neighbor exclusions is enqueued at depth one. Removing exclusions then enqueues test_accounts at depth two. At a maximum of two, that final node is emitted but its outgoing links are not followed.

| Step | Removed entry | Newly admitted queue entry | Emitted IDs so far |
| --- | --- | --- | --- |
| 1 | (metric, 0) | (exclusions, 1) | metric |
| 2 | (exclusions, 1) | (test_accounts, 2) | metric, exclusions |
| 3 | (test_accounts, 2) | none at the depth boundary | metric, exclusions, test_accounts |

The visited set is updated when a node is enqueued, not only when it is removed. That prevents two parent nodes from adding the same child repeatedly while it is already waiting. In an unweighted graph with this breadth-first order, the first discovered path has minimum edge count. A depth bound therefore has a precise interpretation. Weighted relevance or confidence costs would require a different search policy; breadth-first order does not optimize them.

The original validation only rejected a negative max_hops. A fractional value such as 1.5 could pass that check, but integer depths never equaled 1.5 at the stopping comparison, so the walk could continue across the whole finite graph. The repaired contract requires a nonnegative Python integer and rejects Boolean, fractional and NaN values before traversal. This is a real configuration boundary, not a numerical-tolerance issue.

Even an integer hop limit can admit many nodes. With branching factor b and depth h in a tree without merging, the number reachable through that depth is \(1+b+\cdots+b^h\). For \(b=10\), \(h=3\), that is 1111 nodes. A visited set prevents repeated identities, but it does not make all reachable evidence cheap. A remote retrieval service needs explicit candidate/work budgets and failure behavior beyond this bounded local graph.

Reachability is not support. An edge from a metric page to an exclusion page may be a navigation link, a reference or merely a related-topic connection. To conclude that an exclusion applies to the metric, the system must inspect the bridge's meaning and version. A graph path alone cannot license a factual inference. The fixture's edges are authored to demonstrate traversal; they do not implement semantic entailment.

Likewise, the rewrite maps lowercased whitespace tokens through a curated dictionary. It replaces buy with purchase but does not perform contextual disambiguation. A phrase such as “buy back shares” can have a different meaning from a retail purchase question. Punctuation attached to a token also follows this simple split policy. A learned rewriter may handle more cases, but it adds its own unsupported-expansion and intent-preservation risks.

Authorization remains fixed across hops. The helper follows a target only when it is a key in the admitted graph. A link to an excluded node is not permission to fetch it. A larger system must ensure the graph itself was constructed under the correct policy and recheck any external fetch; the walk does not authenticate a principal.

### Interview reasoning with explanatory answers

**Why preserve a visited set if a hop limit exists?** It prevents repeated work and duplicate evidence within the permitted depth. The depth limit and identity deduplication solve different problems.

**Does another hop always improve an answer?** It can add required evidence, irrelevant context or a contradiction. Continue only when a named missing dependency justifies the extra work, then measure sufficiency and support.

**What does a cycle test establish?** That this finite traversal emits each admitted node at most once. It does not establish that remote requests time out correctly or that every followed link supports an inference.

## Worked example / walkthrough

### Example A: Apply a controlled synonym rewrite

The substitution is explicitly authored. A learned rewrite would need evaluation for intent preservation and unsupported expansion.

```python
from collections import deque
def rewrite(query,synonyms): return ' '.join(synonyms.get(token,token) for token in query.lower().split())
def walk(start,graph,max_hops):
    if type(max_hops) is not int or max_hops<0: raise ValueError('nonnegative integer hop budget required')
    if start not in graph: return []
    queue=deque([(start,0)]); seen={start}; result=[]
    while queue:
        node,depth=queue.popleft(); result.append(node)
        if depth==max_hops: continue
        for target in graph[node]:
            if target in graph and target not in seen: seen.add(target); queue.append((target,depth+1))
    return result
original='buy rate'; rewritten=rewrite(original,{'buy':'purchase'})
assert rewritten=='purchase rate' and original=='buy rate'
```

**Expected:** rewrittenpurchase rate; original unchanged.

### Example B: Retain a rewrite trace

A retrieval failure can originate in the rewrite rather than the ranking model. Keeping both strings makes that stage diagnosable.

```python
trace={'original':original,'rewritten':rewritten,'policy':'synonyms-v1'}
assert set(trace)=={'original','rewritten','policy'}
```

**Expected:** trace includes all three fields.

### Example C: Follow two evidence hops

The depth counts edges from the starting evidence item. The final document is included because it is exactly two links away.

```python
graph={'metric':['exclusions'],'exclusions':['test_accounts'],'test_accounts':[]}
assert walk('metric',graph,2)==['metric','exclusions','test_accounts']
```

**Expected:** visited metric, exclusions, test_accounts.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: rewrittenpurchase rate; original unchanged. restricted document never appears. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Apply a controlled synonym rewrite.** Rewritebuy rate usingbuy->purchase while preserving the original question.
   **Expected:** rewrittenpurchase rate; original unchanged.
   **Verify:** Save the assertion results for exercise 1, including rewrittenpurchase rate; original unchanged.

2. **Retain a rewrite trace.** Record the original, rewritten query and policy version.
   **Expected:** trace includes all three fields.
   **Verify:** Save the assertion results for exercise 2, including trace includes all three fields.

3. **Follow two evidence hops.** Use graphmetric->exclusions->test_accounts with a two-hop bound.
   **Expected:** visited metric, exclusions, test_accounts.
   **Verify:** Save the assertion results for exercise 3, including visited metric, exclusions, test_accounts.

4. **Stop at the declared depth.** Run the same graph with a one-hop bound, then reject fractional, Boolean, NaN and negative budgets.
   **Expected:** test_accounts is absent; invalid budgets raise ValueError before traversal.
   **Verify:** Save the assertion results for exercise 4, including test_accounts is absent; invalid budgets raise ValueError before traversal.

5. **Break a retrieval cycle.** Addtest_accounts->metric and traverse with a larger bound.
   **Expected:** each document appears once.
   **Verify:** Save the assertion results for exercise 5, including each document appears once.

6. **Preserve authorization across hops.** Remove a restricted target from the admitted graph and ensure links to it are not followed.
   **Expected:** restricted document never appears.
   **Verify:** Save the assertion results for exercise 6, including restricted document never appears.

## Common pitfalls and diagnosis

If a traversal exceeds its intended depth, inspect the budget's type and the exact edge-count convention. If duplicate nodes appear, check when seen is updated. If the node count is unexpectedly large despite a small depth, inspect branching and add a separate work budget rather than assuming the depth limit is broken.

If a rewrite improves lexical matches but worsens answers, compare the original intent, rewritten terms and bridge evidence. If a restricted target appears, trace whether it entered the admitted graph or was fetched through an unguarded side path. If an answer invents a connection, distinguish graph reachability from semantic support.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Revisit the worked examples, then close them. Explain Query rewrite, Multi-hop retrieval, Bridge evidence using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-009` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. See [validation](../../../docs/validation.md) for execution gates. Check CI artifacts for the exact revision and platform to determine which runtime checks actually ran; authored content alone does not establish runtime execution.



## Ask an AI tutor about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-010, Query rewriting and bounded multi-hop retrieval.
Read courses/llm-applied/guides/llm-applied-010.md and courses/llm-applied/lessons/llm-applied-010.py. Direct prerequisites: `llm-applied-009`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

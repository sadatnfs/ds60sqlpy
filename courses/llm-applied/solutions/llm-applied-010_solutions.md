# llm-applied-010: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Query rewriting can translate a user's phrasing into terms that a retriever understands. It can also distort intent, add unsupported assumptions or broaden the search beyond the authorized domain. A rewrite should be treated as a proposal with a provenance trail, not as a new trusted user instruction. Multi-hop retrieval performs another search using information found in an earlier result, useful when a question requires connecting a metric definition with an exclusion policy. Each hop should have a purpose, a bounded candidate count and a stopping rule.

This lesson uses a curated synonym map and a two-hop document graph. It does not ask a model to invent search plans. The deterministic baseline makes the failure modes visible: a rewrite can help lexical recall, but a cycle can repeatedly retrieve the same documents, and an unsupported bridge can lead to an irrelevant answer. Preserve the original question, each rewritten query, retrieved IDs and the reason for continuing. Authorization remains fixed across every hop.

**Query rewrite:** A transformed search query derived from an original question.

**Multi-hop retrieval:** A bounded sequence of searches or evidence-link traversals.

**Bridge evidence:** A source that justifies connecting one retrieval step to another.

**Stopping rule:** A condition ending retrieval before unbounded exploration.

## Reading the implementation

Tokenize the query, apply only declared synonym substitutions and retain the original text in a trace. A bounded breadth-first traversal uses a queue, visited set and maximum-hop count. Follow only explicit local document links. The visited set prevents cycles from consuming the budget indefinitely. A new query or link cannot add an unauthorized document because the same admitted corpus is used throughout.

## Trace the retrieval frontier and the stopping policy

The fixture starts at metric with depth zero. A queue entry records both node and distance in edges from the start. Removing metric from the queue emits it; if the depth is below the limit, its admitted neighbor exclusions is enqueued at depth one. Removing exclusions then enqueues test_accounts at depth two. At a maximum of two, that final node is emitted but its outgoing links are not followed.

| Step | Removed entry | Newly admitted queue entry | Emitted IDs so far |
| --- | --- | --- | --- |
| 1 | (metric, 0) | (exclusions, 1) | metric |
| 2 | (exclusions, 1) | (test_accounts, 2) | metric, exclusions |
| 3 | (test_accounts, 2) | none at the depth boundary | metric, exclusions, test_accounts |

The visited set is updated when a node is enqueued, not only when it is removed. That prevents two parent nodes from adding the same child repeatedly while it is already waiting. In an unweighted graph with this breadth-first order, the first discovered path has minimum edge count. A depth bound therefore has a precise interpretation. Weighted relevance or confidence costs would require a different search policy; breadth-first order does not optimize them.

The original validation only rejected a negative max_hops. A fractional value such as1.5 could pass that check, but integer depths never equaled1.5 at the stopping comparison, so the walk could continue across the whole finite graph. The repaired contract requires a nonnegative Python integer and rejects Boolean, fractional and NaN values before traversal. This is a real configuration boundary, not a numerical-tolerance issue.

Even an integer hop limit can admit many nodes. With branching factor b and depth h in a tree without merging, the number reachable through that depth is1+b+...+b^h. For b=10, h=3, that is1111 nodes. A visited set prevents repeated identities, but it does not make all reachable evidence cheap. A remote retrieval service needs explicit candidate/work budgets and failure behavior beyond this bounded local graph.

Reachability is not support. An edge from a metric page to an exclusion page may be a navigation link, a reference or merely a related-topic connection. To conclude that an exclusion applies to the metric, the system must inspect the bridge's meaning and version. A graph path alone cannot license a factual inference. The fixture's edges are authored to demonstrate traversal; they do not implement semantic entailment.

Likewise, the rewrite maps lowercased whitespace tokens through a curated dictionary. It replaces buy with purchase but does not perform contextual disambiguation. A phrase such as “buy back shares” can have a different meaning from a retail purchase question. Punctuation attached to a token also follows this simple split policy. A learned rewriter may handle more cases, but it adds its own unsupported-expansion and intent-preservation risks.

Authorization remains fixed across hops. The helper follows a target only when it is a key in the admitted graph. A link to an excluded node is not permission to fetch it. A larger system must ensure the graph itself was constructed under the correct policy and recheck any external fetch; the walk does not authenticate a principal.

### Interview reasoning with explanatory answers

**Why preserve a visited set if a hop limit exists?** It prevents repeated work and duplicate evidence within the permitted depth. The depth limit and identity deduplication solve different problems.

**Does another hop always improve an answer?** It can add required evidence, irrelevant context or a contradiction. Continue only when a named missing dependency justifies the extra work, then measure sufficiency and support.

**What does a cycle test establish?** That this finite traversal emits each admitted node at most once. It does not establish that remote requests time out correctly or that every followed link supports an inference.

## Exercise 1: Apply a controlled synonym rewrite

The question is: Rewritebuy rate usingbuy->purchase while preserving the original question.

The substitution is explicitly authored. A learned rewrite would need evaluation for intent preservation and unsupported expansion.

```python
original='buy rate'; rewritten=rewrite(original,{'buy':'purchase'})
assert rewritten=='purchase rate' and original=='buy rate'
```

**Expected:** rewrittenpurchase rate; original unchanged.

**Verify:** Compare the computed values or written argument with rewrittenpurchase rate; original unchanged.

## Exercise 2: Retain a rewrite trace

The question is: Record the original, rewritten query and policy version.

A retrieval failure can originate in the rewrite rather than the ranking model. Keeping both strings makes that stage diagnosable.

```python
trace={'original':original,'rewritten':rewritten,'policy':'synonyms-v1'}
assert set(trace)=={'original','rewritten','policy'}
```

**Expected:** trace includes all three fields.

**Verify:** Compare the computed values or written argument with trace includes all three fields.

## Exercise 3: Follow two evidence hops

The question is: Use graphmetric->exclusions->test_accounts with a two-hop bound.

The depth counts edges from the starting evidence item. The final document is included because it is exactly two links away.

```python
graph={'metric':['exclusions'],'exclusions':['test_accounts'],'test_accounts':[]}
assert walk('metric',graph,2)==['metric','exclusions','test_accounts']
```

**Expected:** visitedmetric, exclusions, test_accounts.

**Verify:** Compare the computed values or written argument with visitedmetric, exclusions, test_accounts.

## Exercise 4: Stop at the declared depth

The question is: Run the same graph with a one-hop bound, then reject fractional, Boolean, NaN and negative budgets.

The budget is a real behavior constraint. Returning the deeper document would mean the implementation ignored the configured stopping rule.

```python
assert walk('metric',graph,1)==['metric','exclusions']
for bad_budget in [1.5,True,float('nan'),-1]:
    try: walk('metric',graph,bad_budget)
    except ValueError: pass
    else: raise AssertionError('invalid hop budget accepted')
```

**Expected:** test_accounts is absent; invalid budgets raise ValueError before traversal.

**Verify:** Compare the computed values or written argument with test_accounts is absent; invalid budgets raise ValueError before traversal.

## Exercise 5: Break a retrieval cycle

The question is: Addtest_accounts->metric and traverse with a larger bound.

A visited set prevents repeated evidence from masquerading as additional support and keeps cycles from consuming unlimited work.

```python
cyclic={**graph,'test_accounts':['metric']}; result=walk('metric',cyclic,10)
assert result==['metric','exclusions','test_accounts'] and len(result)==len(set(result))
```

**Expected:** each document appears once.

**Verify:** Compare the computed values or written argument with each document appears once.

## Exercise 6: Preserve authorization across hops

The question is: Remove a restricted target from the admitted graph and ensure links to it are not followed.

A link is not permission to access its target. The traversal follows only nodes present in the already admitted graph.

```python
admitted={'metric':['restricted'],'public':[]}
assert walk('metric',admitted,3)==['metric']
```

**Expected:** restricted document never appears.

**Verify:** Compare the computed values or written argument with restricted document never appears.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

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

The question is: Run the same graph with a one-hop bound.

The budget is a real behavior constraint. Returning the deeper document would mean the implementation ignored the configured stopping rule.

```python
assert walk('metric',graph,1)==['metric','exclusions']
```

**Expected:** test_accounts is absent.

**Verify:** Compare the computed values or written argument with test_accounts is absent.

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

# llm-042: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A defensible language-system decision compares candidate systems under one frozen task definition. The tiny transformer, count baseline and local retrieval variant have different capabilities, so use common questions and explicit correctness, support, abstention and resource criteria. Preserve tokenizer, data and model identities, verify causal and cache behavior, and report failure examples. A small local benchmark can justify a teaching conclusion or a no-go, but cannot establish broad deployment reliability. The capstone intentionally uses deterministic question records and a tiny decoder probe rather than pretending that fluent generated text is an automatic correctness test.

**Common evaluation contract:** The same questions,units and scoring rules used for every candidate.

**Go/no-go:** A decision applying declared acceptance gates to observed evidence.

**Unknown gate:** A required check lacking an execution or review receipt.

## Reading the implementation

Keep result tables keyed by question ID and grouped by family. Compare paired errors, not unaligned averages. A release dictionary records each required gate asTrue,False or None for unexecuted. OnlyTrue satisfies a required gate. Hash the literal fixture and model state, retain exact token budgets, and keep measured latency as an observation rather than a universal performance promise. The cache oracle compares one-token execution with full-prefix output.

## Exercise 1: Freeze common questions

The question is: Defineq1 answerable square sides,q2 answerable circle color,q3 missing comet period with stable families.

The task contract is frozen before comparing systems. The unanswerable case tests abstention rather than rewarding a fabricated response.

```python
import hashlib, json, time

questions = [
    {"id": "q1", "family": "shape", "answerable": True},
    {"id": "q2", "family": "color", "answerable": True},
    {"id": "q3", "family": "astronomy", "answerable": False},
]
fixture_hash = hashlib.sha256(json.dumps(questions, sort_keys=True).encode()).hexdigest()
assert len({q["id"] for q in questions}) == 3 and questions[2]["answerable"] is False
```

**Expected:** 3 distinct questions and a missing-evidence case.

**Verify:** Compare the computed values or written argument with 3 distinct questions and a missing-evidence case.

## Exercise 2: Compare saved candidate decisions

The question is: Use per-question correctness tiny[1,0,0],count[0,0,0],retrieval[1,1,1],whereq3correctmeansabstaining.

These are explicitly saved deterministic decision records, not claims that a newly trained model generated those answers. A real study must attach the actual answer artifacts and scoring rationale.

```python
results = {
    "tiny": {"q1": 1, "q2": 0, "q3": 0},
    "count": {"q1": 0, "q2": 0, "q3": 0},
    "retrieval": {"q1": 1, "q2": 1, "q3": 1},
}
ids = [q["id"] for q in questions]
assert {name: sum(rows[i] for i in ids) for name, rows in results.items()} == {
    "tiny": 1,
    "count": 0,
    "retrieval": 3,
}
```

**Expected:** scores1/3,0/3,3/3 on this fixture only.

**Verify:** Compare the computed values or written argument with scores1/3,0/3,3/3 on this fixture only.

## Exercise 3: Run model mechanism checks

The question is: Initialize the small decoder and compare full-prefix and incremental cached logits on2,5,7.

Mechanism parity is necessary for this decoder but does not certify its answer quality. The measured elapsed time belongs to this environment and fixture.

```python
torch.manual_seed(7)
model = TinyDecoder()
model.eval()
tokens = torch.tensor([[2, 5, 7]])
state = None
parts = []
start = time.perf_counter()
with torch.no_grad():
    full, _ = model(tokens)
    for i in range(3):
        out, state = model(tokens[:, i : i + 1], state)
        parts.append(out)
elapsed = time.perf_counter() - start
torch.testing.assert_close(torch.cat(parts, 1), full, atol=1e-6, rtol=0)
assert sum(p.numel() for p in model.parameters()) < 50000 and elapsed >= 0
```

**Expected:** parity within 1e-6;parameters below50000.

**Verify:** Compare the computed values or written argument with parity within 1e-6;parameters below50000.

## Exercise 4: Bind lineage and budgets

The question is: Hash model parameter bytes and record fixture hash,context3 and generated-token cap4.

Identity receipts help a reviewer reconstruct the exact state. They do not prove that a scoring table was produced by that model, so link actual outputs separately in a full experiment.

```python
model_hash = hashlib.sha256(
    b"".join(p.detach().numpy().tobytes() for p in model.parameters())
).hexdigest()
lineage = {
    "fixture": fixture_hash,
    "model": model_hash,
    "tokenizer": "literal-vocabulary-16",
    "context": 3,
    "generated_cap": 4,
    "elapsed_seconds": elapsed,
}
assert len(lineage["fixture"]) == len(lineage["model"]) == 64 and lineage["generated_cap"] == 4
```

**Expected:** two64-character hashes and cap4.

**Verify:** Compare the computed values or written argument with two64-character hashes and cap4.

## Exercise 5: Apply an honest release gate

The question is: Set mechanismTrue,trust-boundaryTrue,heldout-population evidenceNone and severe-failure gateFalse.

Unknown evidence and an explicit failure both block a required gate. A favorable toy score cannot turn either into a pass.

```python
gates = {
    "mechanism": True,
    "trust_boundary": True,
    "population_evidence": None,
    "severe_failures_absent": False,
}
decision = "go" if all(value is True for value in gates.values()) else "no-go"
assert decision == "no-go"
```

**Expected:** decisionno-go.

**Verify:** Compare the computed values or written argument with decisionno-go.

## Exercise 6: Write the reviewer decision

The question is: Record one failure example,missing evidence and next action beside theno-go.

The decision should be actionable without overstating the result. A no-go with a concrete failure and next evidence requirement is a complete capstone outcome.

```python
report = {
    "decision": decision,
    "failure": "q3: tiny candidate answered without evidence",
    "missing": "independent held-out families",
    "next": "repair abstention and collect a new frozen evaluation",
    "limits": "authored local teaching fixture",
}
assert (
    report["decision"] == "no-go" and "q3" in report["failure"] and "families" in report["missing"]
)
```

**Expected:** report namesq3 unsupported answer and new independent families needed.

**Verify:** Compare the computed values or written argument with report namesq3 unsupported answer and new independent families needed.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

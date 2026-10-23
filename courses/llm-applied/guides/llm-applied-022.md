# llm-applied-022: Structured tools for extraction, aggregation and data-science work

Status: authored applied LLM content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Advanced; approximately 240 minutes. Direct prerequisites: `llm-applied-021`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

An LLM can help propose data-science operations, but the application should execute only typed, bounded operations whose semantics are understood. The central investigation is concrete: Use rowsA1, A3, B10 and the admittedgroup_mean request. The finish condition is A count 2 mean2; B count 1 mean10. descriptive statisticavailable; causal claimnot established. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

An LLM can help propose data-science operations, but the application should execute only typed, bounded operations whose semantics are understood. A tool call is a request object, not a shell command. The dispatcher validates its schema, operation name, column choices, row limit and value types before computing. A model-generated SQL string is especially risky when treated as an unrestricted query; this lesson instead exposes a narrow grouped-mean operation over an in-memory fixture. The same principle can wrap reviewed parameterized SQL in a real system.

Separate extraction, computation and explanation. An extraction proposal becomes accepted data only after validation. A deterministic tool computes counts and means. The answerer then explains the returned artifact without inventing a different number or causal interpretation. A mean difference does not establish a treatment effect without a valid design. Missing values, booleans, nonfinite numbers and unsupported columns are explicit failures under this lesson contract. The code performs no network request, database mutation or arbitrary evaluation.

## Design decisions and when to use this method

Use typed tools when a subject assistant needs exact arithmetic, validated database reads, plots or data transformations. Keep the operation catalog small and explicit. Validate inputs before execution and outputs before explanation. For expensive tools, add real time, cancellation and resource bounds in the execution layer rather than relying only on a prompt asking the model to be concise.

Do not exposeeval, arbitrary filesystem paths or unrestricted SQL as a convenience shortcut. A model proposal can be malformed or influenced by retrieved text. A real database tool should use parameter binding, least-privilege access and an explicit target. Preserve the analysis code and input identity so a user can reproduce a result without trusting the generated prose. Statistical interpretation still depends on sampling, measurement and design assumptions beyond the tool's arithmetic correctness.

## Vocabulary and concepts

**Tool proposal:** A structured request awaiting trusted validation.

**Dispatcher:** Code mapping admitted operation names to fixed implementations.

**Deterministic analysis artifact:** A reproducible result calculated from accepted data.

**Interpretation boundary:** The distinction between a computed statistic and a broader claim.

## How to run this lesson

Use a prepared `python-core` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/llm-applied-022/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/llm-applied/lessons/llm-applied-022.py`. For macOS/Linux use `.venv/bin/python courses/llm-applied/lessons/llm-applied-022.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Distinguish a retrieval or extraction baseline from an actual trained language model; each example names what it implements. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

The tool request has exactlyoperation, group_by andvalue fields. Allowed values aregroup_mean, group andvalue. Input rows haveid, group, value with unique IDs and at most20 records. Rejectbool even though it is anint subclass. Group values with a dictionary, then emit sorted rows containinggroup, count, mean. Keep the tool result separate from any prose proposal and verify quoted numbers against it.

## Worked example / walkthrough

### Example A: Execute a bounded grouped mean

The output grain is one row pergroup. Counts remain beside means so a one-record group does not look as well supported as a larger group.

```python
import math
from collections import defaultdict
def dispatch(request,rows):
    if not isinstance(request,dict) or set(request)!={'operation','group_by','value'}: raise ValueError('exact tool fields required')
    if request!={'operation':'group_mean','group_by':'group','value':'value'}: raise ValueError('operation or columns not allowed')
    if not 1<=len(rows)<=20: raise ValueError('row budget1..20 required')
    if len({row['id'] for row in rows})!=len(rows): raise ValueError('duplicate row ID')
    groups=defaultdict(list)
    for row in rows:
        if set(row)!={'id','group','value'} or not isinstance(row['id'],str) or not isinstance(row['group'],str): raise ValueError('row schema')
        value=row['value']
        if type(value) not in (int,float): raise TypeError('numeric value required')
        if not math.isfinite(value): raise ValueError('finite value required')
        groups[row['group']].append(value)
    return [{'group':key,'count':len(values),'mean':sum(values)/len(values)} for key,values in sorted(groups.items())]
rows=[{'id':'a1','group':'A','value':1.},{'id':'a2','group':'A','value':3.},{'id':'b1','group':'B','value':10.}]
request={'operation':'group_mean','group_by':'group','value':'value'}
result=dispatch(request,rows)
assert result==[{'group':'A','count':2,'mean':2.},{'group':'B','count':1,'mean':10.}]
```

**Expected:** A count 2 mean2; B count 1 mean10.

### Example B: Reject an arbitrary operation

The dispatcher never interprets arbitrary text as code or SQL. A production SQL adapter would need a separate reviewed query template and target boundary.

```python
for proposal in [{'operation':'run_sql','group_by':'group','value':'value'},{**request,'query':'DROP TABLE anything'}]:
    try: dispatch(proposal,rows)
    except ValueError: pass
    else: raise AssertionError('unbounded operation accepted')
```

**Expected:** ValueError before any computation.

### Example C: Reject invalid numeric values

Silently dropping or coercing these values would change the denominator or meaning. A different missingness policy must be explicitly designed and reported.

```python
for bad in [True,float('nan'),None]:
    changed=[dict(r) for r in rows]; changed[0]['value']=bad
    try: dispatch(request,changed)
    except (TypeError,ValueError): pass
    else: raise AssertionError('invalid numeric value accepted')
```

**Expected:** each invalid row is rejected.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: A count 2 mean2; B count 1 mean10. descriptive statisticavailable; causal claimnot established. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Execute a bounded grouped mean.** Use rowsA1, A3, B10 and the admittedgroup_mean request.
   **Expected:** A count 2 mean2; B count 1 mean10.
   **Verify:** Save the assertion results for exercise 1, including A count 2 mean2; B count 1 mean10.

2. **Reject an arbitrary operation.** Submitoperationrun_sql or an extraquery field.
   **Expected:** ValueError before any computation.
   **Verify:** Save the assertion results for exercise 2, including ValueError before any computation.

3. **Reject invalid numeric values.** Replace onevalue withTrue, NaN orNone under the strict numeric policy.
   **Expected:** each invalid row is rejected.
   **Verify:** Save the assertion results for exercise 3, including each invalid row is rejected.

4. **Enforce identity and work limits.** Duplicatea1, then supply21 unique rows.
   **Expected:** duplicate identity and row-limit violations rejected.
   **Verify:** Save the assertion results for exercise 4, including duplicate identity and row-limit violations rejected.

5. **Verify an explanation against the artifact.** Check a proposed sentence saying groupAmean2 against the result; reject a proposedmean20.
   **Expected:** 2accepted; 20mismatch.
   **Verify:** Save the assertion results for exercise 5, including 2accepted; 20mismatch.

6. **Refuse an unsupported causal interpretation.** Attach a descriptive result to a claim that group caused the difference without assignment-design evidence.
   **Expected:** descriptive statisticavailable; causal claimnot established.
   **Verify:** Save the assertion results for exercise 6, including descriptive statisticavailable; causal claimnot established.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Tool proposal, Dispatcher, Deterministic analysis artifact using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `llm-applied-021` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [Python numeric types](https://docs.python.org/3.12/library/stdtypes.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/llm-applied-status.md`; authored content does not imply that a heavy runtime was executed.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for llm-applied-022, Structured tools for extraction, aggregation and data-science work.
Read courses/llm-applied/guides/llm-applied-022.md and courses/llm-applied/lessons/llm-applied-022.py. Direct prerequisites: `llm-applied-021`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/llm-applied/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

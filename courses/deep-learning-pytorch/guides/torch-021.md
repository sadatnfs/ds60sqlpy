# torch-021: Embeddings, padded sequences and recurrent models

Status: authored PyTorch course content. The manifest inventories complete teaching files; runtime readiness remains a separate, measured property.

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-020`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A padded sequence contains real positions and artificial storage positions. The central investigation is concrete: Use IDs2, 3, 0 and a fixed4x2table with zero padding row. The finish condition is embedding shape1, 3, 2; mask True, True, False. RuntimeError for invalid length. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A padded sequence contains real positions and artificial storage positions. Embedding lookup takes token IDs to feature vectors, but padding does not become an observation merely because it has a vector. PyTorch Embedding can use padding_idx to prevent gradient updates for that row, but a recurrent network still needs length or mask information to avoid processing padding as real time steps.

pack_padded_sequence lets an RNN or GRU process the valid prefixes and return a final state after the last real position. Without packing, a GRU can continue to update on padding because its biases and recurrent state are still active, even when padding embeddings are zero. Loss averages must also divide by valid target count, not padded width. The lesson uses a literal embedding table and fixed GRU weights so the distinction is observable.

## Design decisions and when to use this method



## Paired TensorFlow comparison

Compare [tf-021](../../deep-learning-tensorflow/guides/tf-021.md) after deriving the shared numerical contract.

Keras can propagate mask metadata from Embedding(mask_zero=True)through compatible layers. PyTorch often uses explicit lengths, masks or PackedSequence. padding_id x is not the same as automatic recurrent mask propagation. Both frameworks require a valid-token loss denominator.

## Vocabulary and concepts

**Padding index:** A vocabulary entry reserved for artificial storage positions.

**P ac k e d sequence:** A representation allowing recurrent layers to skip invalid tail positions.

**Final valid state:** The hidden state after the last real observation.

**Valid-target denominator:** The count of supervised positions included in the loss.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-021/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-021.py`. For macOS/Linux use `.venv/bin/python courses/deep-learning-pytorch/lessons/torch-021.py` from the repository root.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. For float64 arithmetic use an absolute tolerance of 1e-12 unless an exercise gives another bound. TensorFlow and PyTorch float32 comparisons use 1e-6. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use Embedding.from_pretrained with padding_idx0 and freeze=False for the known4x2table. Set batch_first=True on GRU so inputs are(batch, time, features). pack_padded_sequence receives CPU lengths and enforce_sorted=False for this tiny fixture. Compare the packed final state with an unpadded valid-prefix run. For loss, use an explicit boolean valid mask and reject an all-padding denominator.

## Worked example / walkthrough

### Example A: Lookup and mark padding

The mask comes from the vocabulary policy. A real token could have a zero vector, so vector magnitude is not a reliable padding detector.

```python
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F

table=torch.tensor([[0.,0.],[1.,0.],[2.,2.],[3.,-1.]])
embedding=nn.Embedding.from_pretrained(table,freeze=False,padding_idx=0); ids=torch.tensor([[2,3,0]]); values=embedding(ids); mask=ids!=0
assert tuple(values.shape)==(1,3,2) and mask.tolist()==[[True,True,False]]
```

**Expected:** embedding shape1, 3, 2; mask True, True, False.

### Example B: Verify padding-row gradient behavior

padding_id x controls that embedding row's gradient, but does not automatically mask every later operation in the model.

```python
values.sum().backward()
assert torch.count_nonzero(embedding.weight.grad[0]).item()==0
assert torch.count_nonzero(embedding.weight.grad[2:4]).item()>0
```

**Expected:** padding row gradient zero; rows2and3nonzero.

### Example C: Compare packed and valid-prefix GRU state

The packedsequence ends after two observations. This direct comparison establishes what the final state means without relying on a padded output index.

```python
gru=nn.GRU(2,2,batch_first=True)
with torch.no_grad():
    for parameter in gru.parameters(): parameter.fill_(.1)
packed=nn.utils.rnn.pack_padded_sequence(values.detach(),torch.tensor([2]),batch_first=True,enforce_sorted=False)
_,packed_state=gru(packed); _,prefix_state=gru(values.detach()[:,:2])
torch.testing.assert_close(packed_state,prefix_state,atol=1e-6,rtol=0)
```

**Expected:** final states match within1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: embedding shape1, 3, 2; mask True, True, False. RuntimeError for invalid length. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Lookup and mark padding.** Use IDs2, 3, 0 and a fixed4x2table with zero padding row.
   **Expected:** embedding shape1, 3, 2; mask True, True, False.
   **Verify:** Save the assertion results for exercise 1, including embedding shape1, 3, 2; mask True, True, False.

2. **Verify padding-row gradient behavior.** Sum embedding outputs and backpropagate.
   **Expected:** padding row gradient zero; rows2and3nonzero.
   **Verify:** Save the assertion results for exercise 2, including padding row gradient zero; rows2and3nonzero.

3. **Compare packed and valid-prefix GRU state.** Use fixed GRU parameters.1 and length2; compare packed run with the unpadded first two embeddings.
   **Expected:** final states match within1e-6.
   **Verify:** Save the assertion results for exercise 3, including final states match within1e-6.

4. **Expose an unmasked recurrent tail.** Run GRU overall three positions including zero embedding padding.
   **Expected:** final state differs from the valid-prefix state.
   **Verify:** Save the assertion results for exercise 4, including final state differs from the valid-prefix state.

5. **Average only valid token losses.** Use losses log2, log2, 100with the valid mask.
   **Expected:** mean log2, unchanged by the padding loss.
   **Verify:** Save the assertion results for exercise 5, including mean log2, unchanged by the padding loss.

6. **Reject zero-length recurrent input.** Attempt to pack a sequence with length0.
   **Expected:** RuntimeError for invalid length.
   **Verify:** Save the assertion results for exercise 6, including RuntimeError for invalid length.

## Common pitfalls and diagnosis

When a result disagrees, locate the first intermediate value that violates this explanation. Inspect shapes and identities before aggregates, and inspect counts before averages. Preserve the original fixture and introduce only one controlled change at a time. If an arithmetic identity passes but a data-boundary condition fails, the experiment is still invalid. If a runtime is unavailable, record the unexecuted code as unverified rather than replacing its output with the expected text. The separate explanation discusses why the tempting alternative in each case changes the result.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Padding index, P ac k e d sequence, Final valid state using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-020` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why do not zero embeddings make padding harmless for an R NN?**

The hidden state and biases can still change on a zero-input step. Length-aware execution or masking is needed for the intended final-state contract.

**Does padding_id x mask the loss?**

No. It controls gradient behavior for that embedding row. The loss still needs its own valid-target policy.



## Ask Codex about this lesson

```text
Use the checked-in $guide-ds60sqlpy-learning skill for torch-021, Embeddings, padded sequences and recurrent models.
Read courses/deep-learning-pytorch/guides/torch-021.md and courses/deep-learning-pytorch/lessons/torch-021.py. Direct prerequisites: `torch-020`.
Explain the mental model, ask me to predict the worked example, review my attempt,
give one hint, request output evidence, and ask a fresh retrieval question.
Keep courses/deep-learning-pytorch/solutions/ closed until I request comparison or show an attempt.
Use only the declared local fixtures. Distinguish arithmetic checks, code execution,
and evidence about generalization. Done when I can derive the worked values, pass all six exercise checks, explain a failed counterexample, and solve one fresh transfer case without solutions.
```

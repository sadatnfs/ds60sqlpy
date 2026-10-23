# torch-021: Embeddings, padded sequences and recurrent models

## Level and prerequisites

Intermediate; approximately 120 minutes. Direct prerequisites: `torch-020`. The prerequisite sequence introduces the notation used here; revisit its worked examples if an axis, probability or gradient is unfamiliar.

## Learning objectives

A padded sequence contains real positions and artificial storage positions. The central investigation is concrete: Use IDs 2, 3, 0 and a fixed 4 x2table with zero padding row. The finish condition is embedding shape 1, 3, 2; mask True, True, False. RuntimeError for invalid length. A useful explanation connects the calculation to the reason it is needed, rather than treating a function name as a definition.

## Purpose and mental model

A padded sequence contains real positions and artificial storage positions. Embedding lookup takes token IDs to feature vectors, but padding does not become an observation merely because it has a vector. PyTorch Embedding can use padding_idx to prevent gradient updates for that row, but a recurrent network still needs length or mask information to avoid processing padding as real time steps.

pack_padded_sequence lets an RNN or GRU process the valid prefixes and return a final state after the last real position. Without packing, a GRU can continue to update on padding because its biases and recurrent state are still active, even when padding embeddings are zero. Loss averages must also divide by valid target count, not padded width. The lesson uses a literal embedding table and fixed GRU weights so the distinction is observable.

## Design decisions and when to use this method

Use explicit lengths or masks whenever storage contains artificial positions. Choose whether the objective weights valid tokens equally or weights sequences equally, because unequal sequence lengths make those different learning problems. A reserved padding ID is a vocabulary policy, not a value inferred from an embedding's magnitude.

Use packing for the supported recurrent valid-prefix contract, or an explicit masked recurrent design when lengths do not describe the data. Keep integer token IDs, floating features, Boolean masks and CPU length tensors in their distinct roles. The fixed GRU fixture compares state semantics; it is not an end-to-end trained language model.

## Paired TensorFlow comparison

Compare [tf-021](../../deep-learning-tensorflow/guides/tf-021.md) after deriving the shared numerical contract.

Keras can propagate mask metadata from Embedding(mask_zero=True)through compatible layers. PyTorch often uses explicit lengths, masks or PackedSequence. padding_idx is not the same as automatic recurrent mask propagation. Both frameworks require a valid-token loss denominator.

## Vocabulary and concepts

**Padding index:** A vocabulary entry reserved for artificial storage positions.

**Packed sequence:** A representationallowing recurrent layers to skip invalid tail positions.

**Final valid state:** The hidden state after the last real observation.

**Valid-target denominator:** The count of supervised positions included in the loss.

## How to run this lesson

Use a prepared `llm-torch-cpu` environment. NumPy is a declared package. TensorFlow and PyTorch require their own prepared CPU profiles; a successful syntax check does not establish their runtime readiness. No package installation, dataset download, pretrained model or network service belongs in this lesson. Copy the learner source into ignored `.learning/expansion/torch-021/` before editing, or use the application's saved pad. The examples use literal local data and a bounded number of operations. For Windows use the interpreter selected by setup: `& $CoursePython courses/deep-learning-pytorch/lessons/torch-021.py`. For macOS/Linux, use the interpreter explicitly selected for a separately prepared native PyTorch environment, and invoke that interpreter on `courses/deep-learning-pytorch/lessons/torch-021.py` from the repository root. The repository's general `.venv` is not assumed to contain PyTorch; the prepared classroom profile is the default execution route.

Run the three worked blocks in order in one scratch file; later blocks reuse the earlier helper and fixture state. To reproduce a later block in a fresh process, include its preceding blocks. Start by reading Example A without running it. Write the intermediate quantities and their units on paper. Run the entire example in a fresh process, not only the final line in a notebook with hidden variables. Examples B and C change assumptions that matter to this mechanism. Compare value, gradient and state contracts separately. Equal forward numbers do not prove equal optimizer or training-mode behavior. Compare both observations before starting independent work. An assertion failure is a request to inspect an assumption, not a reason to widen every tolerance. Use the explicit tolerance in each assertion. Several analytic float64 fixtures use 1e-12 and float32 fixtures use 1e-6, but dtype alone is not a universal numerical-error bound. Finite differences, reductions and conditioning can require different justified tolerances. Integer counts, identities and boolean decisions should be exact.

## Syntax anatomy and reasoning sequence

Use Embedding.from_pretrained with padding_idx0 and freeze=False for the known 4 x2table. Set batch_first=True on GRU so inputs are(batch, time, features). pack_padded_sequence receives CPU lengths and enforce_sorted=False for this tiny fixture. Compare the packed final state with an unpadded valid-prefix run. For loss, use an explicit boolean valid mask and reject an all-padding denominator.

## Follow lookup, recurrent state and loss participation separately

The embedding table has shape(V, D)=(4, 2). IDs shaped(B, T)=(1, 3) select rows and produce values shaped(B, T, D)=(1, 3, 2). The mask has shape(1, 3), and the length vector has one entry per sequence, shape(1). IDs[2, 3, 0] select[2, 2], [3, -1], [0, 0], while the vocabulary rule marks only the first two positions valid. A genuine token could have a zero vector, so vector magnitude cannot replace that rule.

Example B differentiates the sum of all lookup outputs. Each used nonpadding row receives the sum of upstream vectors for its occurrences. Here rows 2 and 3 each receive[1, 1], unused row 1 receives zero, and padding row 0 receives zero from the lookup backward rule. If ID 2 appeared twice, its dense gradient contribution would be[2, 2]. Token indices themselves are discrete selectors, not floating parameters to differentiate through. [PyTorch 2.9 Embedding](https://docs.pytorch.org/docs/2.9/generated/torch.nn.Embedding.html).

padding_idx controls the embedding operation's gradient contribution. It does not automatically propagate a mask through a GRU, initialize every supplied pretrained padding row to zero, or protect a row from explicit mutation. Optimizer-wide operations such as decay on a nonzero row are a separate state/update question. The worked table deliberately supplies a zero padding row and performs no optimizer step, so its actual evidence is the stated gradient pattern. Keras mask_zero=True instead creates mask metadata for compatible consumers; that is not a mechanical synonym for PyTorch's padding-gradient rule.

With batch_first=True, the un-packed GRU input uses(B, T, D). Its final hidden state still uses(num_layers×directions, B, H), so the one-layer unidirectional fixture returns(1, 1, 2). batch_first does not reorder the hidden-state axes. A bidirectional final-state tensor has two directional entries per layer and cannot be replaced casually by the last padded output row. PackedSequence also carries ordering/length bookkeeping; enforce_sorted=False avoids requiring the caller to sort this tiny batch manually. Lengths describe positive valid prefixes and are supplied on CPU for this interface.

Why does a zero padding vector still change a recurrent state? A recurrent step includes the previous hidden state and biases. For a GRU, write r and z for reset/update gates, n for the candidate, and h_new=(1-z)n+z h_old. Even when \(x=0\), the recurrent affine terms and biases can make r, z, n nontrivial. The padded third step is therefore another computation, not an identity operation.

The fixed parameters make a compact analytic trace possible because both hidden coordinates remain equal. Let h denote either coordinate and let u be the sum of the two input features. With all weights and both bias vectors equal to 0.1, the gates are \(r=z=\operatorname{sigmoid}(0.1u+0.2h+0.2)\), the candidate is \(\tanh\!\bigl(0.1u+0.1+r(0.2h+0.1)\bigr)\), and the next coordinate is \((1-z)n+zh\). Starting at \(h=0\), the inputs have \(u=4\), 2, 0. The first two steps give the valid-prefix state; the third changes it even though \(u=0\). Packing with length 2 omits that third transition, which is why the packed and prefix states match while the full padded run differs.

Example C uses values.detach(). That explicitly disconnects the GRU comparison from the embedding graph whose backward was already exercised in Example B. It still permits gradients with respect to GRU parameters in an ordinary differentiable forward, but this fixture does not call a GRU backward or update them. Do not interpret matching packed/prefix forward states as evidence that an entire embedding-plus-GRU training graph was tested. In a fresh end-to-end training step, use a fresh lookup graph and preserve the intended gradient path instead of detaching it accidentally.

The masked token objective is L=(sum over b, t of m_bt×loss_bt)/(sum over b, t of m_bt). The two valid log 2 terms give numerator 2 log2 and denominator 2, so the mean is log 2. Dividing by padded width 3 gives 2 log2/3 and changes the scale whenever padding is appended. For this mean, the derivative with respect to each valid loss is \(\frac{1}{2}\) and the padding loss derivative is zero. An all-padding batch has no valid denominator and needs an explicit refusal or skip policy.

A per-sequence mean followed by averaging sequences is a different objective when lengths differ. A sequence with one token and one with nine tokens each receive half the weight under that policy, whereas a global token mean assigns one-tenth versus nine-tenths. Decide the statistical unit before implementing accumulation or batching. Keras mask propagation can help layers ignore padding, but it does not remove the need to inspect the objective's actual numerator and denominator.

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

**Expected:** embedding shape 1, 3, 2; mask True, True, False.

### Example B: Verify padding-row gradient behavior

padding_idx controls that embedding row's gradient, but does not automatically mask every later operation in the model.

```python
values.sum().backward()
assert torch.count_nonzero(embedding.weight.grad[0]).item()==0
assert torch.count_nonzero(embedding.weight.grad[2:4]).item()>0
```

**Expected:** padding row gradient zero; rows 2 and 3nonzero.

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

**Expected:** final states match within 1e-6.

## Prediction before your attempt

For the supplied fixture, name the input unit, the intermediate state and the final quantity that changes. Predict one normal result and one failure result before touching the code. In particular, explain this lesson's acceptance condition in your own words: embedding shape 1, 3, 2; mask True, True, False. RuntimeError for invalid length. Preserve the prediction beside your later observations so a correction is visible. A copied expected value is not a derivation.

## Exercises

1. **Lookup and mark padding.** Use IDs 2, 3, 0 and a fixed 4 x2table with zero padding row.
   **Expected:** embedding shape 1, 3, 2; mask True, True, False.
   **Verify:** Save the assertion results for exercise 1, including embedding shape 1, 3, 2; mask True, True, False.

2. **Verify padding-row gradient behavior.** Sum embedding outputs and backpropagate.
   **Expected:** padding row gradient zero; rows 2 and 3nonzero.
   **Verify:** Save the assertion results for exercise 2, including padding row gradient zero; rows 2 and 3nonzero.

3. **Compare packed and valid-prefix GRU state.** Use fixed GRU parameters.1 and length 2; compare packed run with the unpadded first two embeddings.
   **Expected:** final states match within 1e-6.
   **Verify:** Save the assertion results for exercise 3, including final states match within 1e-6.

4. **Expose an unmasked recurrent tail.** Run GRU overall three positions including zero embedding padding.
   **Expected:** final state differs from the valid-prefix state.
   **Verify:** Save the assertion results for exercise 4, including final state differs from the valid-prefix state.

5. **Average only valid token losses.** Use losses log 2, log 2, 100with the valid mask.
   **Expected:** mean log 2, unchanged by the padding loss.
   **Verify:** Save the assertion results for exercise 5, including mean log 2, unchanged by the padding loss.

6. **Reject zero-length recurrent input.** Attempt to pack a sequence with length 0.
   **Expected:** RuntimeError for invalid length.
   **Verify:** Save the assertion results for exercise 6, including RuntimeError for invalid length.

## Common pitfalls and diagnosis

If a final state changes when padding is appended, inspect packing/lengths and whether a recurrent layer processed the artificial tail. A zero embedding is insufficient when biases and hidden recurrence remain active. If hidden-state dimensions seem transposed, remember that batch_first changes input/output layout but not the final-state axis convention.

If the padding row has a lookup gradient, verify padding_idx and the actual ID convention. If a row changes despite zero lookup contribution, inspect optimizer decay, retained optimizer state and explicit writes separately. If embedding gradients disappear during recurrent training, locate detach/no_grad boundaries and compare with the deliberately detached worked comparison. If a masked loss shrinks as padded width grows, inspect the denominator; if results differ with batch composition, distinguish token-weighted and sequence-weighted objectives.

## Progressive hints

First draw the state described in the vocabulary section. Next use the smallest fixture that distinguishes the two interpretations in Example B. Finally compare your intermediate values with the exercise's expected count, shape or scalar. Ask for the first incorrect step, not a complete replacement implementation. Keep any counterexample that exposed the error as a regression test for the next lesson.

## Self-check and retrieval

Close both worked examples. Explain Padding index, Packed sequence, Final valid state using the lesson fixture. Reconstruct one computation from its inputs. Then change one input while retaining the mechanism and predict whether the conclusion survives. Write which part is guaranteed by the code and which part would need new observations. This last distinction prevents a tiny deterministic teaching example from being presented as evidence about an unseen population or a production model.

## Next step

Revisit the direct prerequisite `torch-020` if the calculation cannot be reconstructed without a solution. Otherwise preserve your independent implementation, the six exercise observations and a fresh transfer case, then continue along the course plan. For a capstone, treat a failed acceptance condition as a valid no-go decision and explain what evidence would be needed to revisit it.

## Sources and verification status

API and mechanism reference: [PyTorch2.9 reference](https://docs.pytorch.org/docs/2.9/index.html), reviewed 2026-10-22. The fixture, examples, counterexamples and exercise design are original course material. Current execution receipts are recorded in `docs/implementation/pytorch-content-status.md`; authored content does not imply that a heavy runtime was executed.

## Interview reasoning with worked answers

**Why do not zero embeddings make padding harmless for an R NN?**

The hidden state and biases can still change on a zero-input step. Length-aware execution or masking is needed for the intended final-state contract.

**Does padding_idx mask the loss?**

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

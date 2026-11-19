# llm-041: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Framework comparison requires translating mathematical contracts, not copying function names. NumPy arrays often express a row-vector projection as X@W. PyTorch Linear stores weights in output-by-input orientation and applies X@W.T. Keras Dense stores input-by-output kernels. Attention mask polarity differs even within PyTorch: functional scaled_dot_product_attention uses a boolean True to allow a position, while MultiheadAttention key_padding_mask uses True to ignore a key. Keras MultiHeadAttention attention_mask uses 1 or True for allowed attention. Mode flags and dropout arguments also matter. This optional worksheet requires no TensorFlow execution and is not a prerequisite for the final capstone.

**Weight layout:** The semantic orientation of stored parameter axes.

**Mask polarity:** Whether True means allowed or excluded.

**API parity:** Matching mathematical behavior after translating interface conventions.

## Reading the implementation

Write input shape, weight shape, output shape, mask meaning and training behavior for each API. Translate values with a non-symmetric matrix so an accidental transpose is visible. A causal lower triangle including its diagonal is allowed under the course convention. Invert it only for an API that expects forbidden positions. Functional PyTorch attention applies dropout according to dropout_p, so evaluation code must explicitly supply 0 when appropriate.

## Exercise 1: Translate a second weight matrix

The question is: Use row input [2, -1] and NumPy/Keras kernel [[1, 0, 2], [3, 1, 0]]. State the PyTorch Linear weight and the outputs.

PyTorch stores one row per output feature, so its weight is the transpose of the input-by-output kernel. A negative input entry makes a transposition mistake visible in the outputs.

```text
X shape (1, 2): [2, -1]
NumPy/Keras W shape (2, 3): [[1, 0, 2], [3, 1, 0]]
PyTorch Linear.weight shape (3, 2): [[1, 3], [0, 1], [2, 0]]
Output: [2*1-1*3, 2*0-1*1, 2*2-1*0] = [-1, -1, 4]
```

**Expected:** PyTorch weight [[1, 3], [0, 1], [2, 0]]; outputs [-1, -1, 4].

**Verify:** Check that the PyTorch weight has shape (3, 2) and equals the transpose, and that each output is the dot product of [2, -1] with one weight row: -1, -1 and 4.

## Exercise 2: Translate a padding mask

The question is: Three keys are k0, k1 and a padding key k2. Write the course allowed mask, the PyTorch key_padding_mask and the Keras attention_mask row.

The same exclusion has opposite boolean polarity in the two PyTorch arguments and in Keras. Writing all three side by side prevents a negation error from attending to padding.

```text
Keys: k0 real, k1 real, k2 padding
Course allowed mask: 1 1 0
PyTorch key_padding_mask: False False True (True ignores the key)
Keras attention_mask row: True True False (True attends)
```

**Expected:** allowed [1, 1, 0]; key_padding_mask [False, False, True]; Keras [True, True, False].

**Verify:** Check that the PyTorch key_padding_mask is the logical negation of the Keras row and that k2 is the only key excluded in all three representations.

## Exercise 3: Name exact mask APIs

The question is: Map course allowed masks to PyTorch functional SDPA, PyTorch key_padding_mask and Keras attention_mask.

A framework name alone does not define boolean semantics. The exact parameter and documented shape must be recorded before translating masks.

```text
PyTorch F.scaled_dot_product_attention attn_mask bool: True participates.
PyTorch MultiheadAttention key_padding_mask bool: True ignored.
Keras MultiHeadAttention attention_mask: 1/True allows.
These parameters have different shapes as well as polarity.
```

**Expected:** In SDPA and Keras masks True allows attention; in key_padding_mask True ignores the key.

**Verify:** Check each API row for polarity: SDPA attn_mask True participates, key_padding_mask True is ignored and Keras attention_mask True attends; the answer also notes the different shapes.

## Exercise 4: Specify evaluation dropout

The question is: Describe why model.eval alone is insufficient if functional SDPA is called with dropout_p=0.1.

A functional operation receives explicit arguments. The caller must connect the module mode to those arguments; otherwise evaluation can remain stochastic.

```text
Module evaluation policy:
training=True -> chosen training dropout probability
training=False -> dropout_p=0.0 passed to functional SDPA
Do not assume the functional call reads module.training automatically.
```

**Expected:** functional call must receive dropout_p=0.0 for deterministic evaluation.

**Verify:** Check that the policy passes dropout_p=0.0 explicitly when training=False and does not rely on module.eval() to change a functional call.

## Exercise 5: Design a cross-framework oracle

The question is: Use zero Q/K and V[[2, 0], [0, 2], [6, 6]], causal allowed mask, dropout 0. State expected outputs.

The expected values come from arithmetic, not from treating one framework as infallible. A nonuniform-score case should follow to test scaling and score orientation.

```text
Input width 2; scale 1/sqrt(2); zero scores.
Legal-key counts 1, 2, 3.
Outputs: V0,(V0+V1)/2,(V0+V1+V2)/3.
Compare float32 at atol 1e-6 and float64 at atol 1e-12.
```

**Expected:** \([[2,0],[1,1],[\frac{8}{3},\frac{8}{3}]]\) within declared dtype tolerance.

**Verify:** Recompute each output row as the mean of its legal value rows: [2, 0], ([2, 0] + [0, 2])/2 = [1, 1] and (2 + 0 + 6)/3 = 8/3 in both columns.

## Exercise 6: Preserve optionality

The question is: Write a verification record when only NumPy and PyTorch are prepared, with TensorFlow unavailable.

A comparison worksheet does not justify installing a second framework or inventing runtime evidence. Optional execution remains optional and explicitly reported.

```text
NumPy reasoning: checked separately.
PyTorch execution: record actual receipt if run.
TensorFlow: unavailable/unexecuted, not passed.
llm-042 does not require llm-041.
```

**Expected:** TensorFlow recorded as unexecuted; the final LLM capstone remains available.

**Verify:** Check that the record lists TensorFlow as unavailable and unexecuted rather than passed, keeps NumPy and PyTorch evidence separate and states that llm-042 does not depend on llm-041.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

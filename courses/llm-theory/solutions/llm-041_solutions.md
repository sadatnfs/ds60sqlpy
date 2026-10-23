# llm-041: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Framework comparison requires translating mathematical contracts, not copying function names. NumPy arrays often express a row-vector projection asX@W. PyTorch Linear stores weights in output-by-input orientation and appliesX@W.T. Keras Dense stores input-by-output kernels. Attention mask polarity differs even within PyTorch: functional scaled_dot_product_attention uses a boolean True to allow a position, while MultiheadAttention key_padding_mask uses True to ignore a key. Keras MultiHeadAttention attention_mask uses1 orTrue for allowed attention. Mode flags and dropout arguments also matter. This optional worksheet requires no TensorFlow execution and is not a prerequisite for the final capstone.

**Weight layout:** The semantic orientation of stored parameter axes.

**Mask polarity:** Whether True means allowed or excluded.

**API parity:** Matching mathematical behavior after translating interface conventions.

## Reading the implementation

Write input shape,weight shape,output shape,mask meaning and training behavior for each API. Translate values with a non-symmetric matrix so an accidental transpose is visible. A causal lower triangle including its diagonal is allowed under the course convention. Invert it only for an API that expects forbidden positions. Functional PyTorch attention applies dropout according to dropout_p, so evaluation code must explicitly supply0 when appropriate.

## Exercise 1: Translate linear weights

The question is: Use row input[1,2] and NumPy/Keras kernel[[1,2,3],[4,5,6]]. State the PyTorch Linear weight.

A square symmetric matrix would hide a transpose error. The rectangular fixture makes the orientation and output feature count explicit.

```text
X shape(1,2)
NumPy/Keras W shape(2,3): [[1,2,3],[4,5,6]]
PyTorch Linear.weight shape(3,2): [[1,4],[2,5],[3,6]]
Output: [1*1+2*4,1*2+2*5,1*3+2*6] = [9,12,15]
```

**Expected:** PyTorch weight[[1,4],[2,5],[3,6]];all outputs[9,12,15].

**Verify:** Compare the computed values or written argument with PyTorch weight[[1,4],[2,5],[3,6]];all outputs[9,12,15].

## Exercise 2: Translate a causal mask

The question is: Write the3x3 allowed lower triangle and its forbidden-mask complement.

The diagonal is allowed because inputs are paired with shifted next-token labels. Excluding it would remove the current token from its own prediction context.

```text
Allowed:
1 0 0
1 1 0
1 1 1
Forbidden:
0 1 1
0 0 1
0 0 0
```

**Expected:** allowedrows100,110,111;forbiddenrows011,001,000.

**Verify:** Compare the computed values or written argument with allowedrows100,110,111;forbiddenrows011,001,000.

## Exercise 3: Name exact mask APIs

The question is: Map course allowed masks to PyTorch functional SDPA,PyTorch key_padding_mask and Keras attention_mask.

A framework name alone does not define boolean semantics. The exact parameter and documented shape must be recorded before translating masks.

```text
PyTorch F.scaled_dot_product_attention attn_mask bool: True participates.
PyTorch MultiheadAttention key_padding_mask bool: True ignored.
Keras MultiHeadAttention attention_mask: 1/True allows.
These parameters have different shapes as well as polarity.
```

**Expected:** SDPA/KerasTrueallows;key_padding_maskTrueignores.

**Verify:** Compare the computed values or written argument with SDPA/KerasTrueallows;key_padding_maskTrueignores.

## Exercise 4: Specify evaluation dropout

The question is: Describe why model.eval alone is insufficient if functional SDPA is called withdropout_p=.1.

A functional operation receives explicit arguments. The caller must connect the module mode to those arguments; otherwise evaluation can remain stochastic.

```text
Module evaluation policy:
training=True -> chosen training dropout probability
training=False -> dropout_p=0.0 passed to functional SDPA
Do not assume the functional call reads module.training automatically.
```

**Expected:** functional call must receive dropout_p0 for deterministic evaluation.

**Verify:** Compare the computed values or written argument with functional call must receive dropout_p0 for deterministic evaluation.

## Exercise 5: Design a cross-framework oracle

The question is: Use zeroQ/K andV[[2,0],[0,2],[6,6]],causal allowed mask,dropout0. State expected outputs.

The expected values come from arithmetic, not from treating one framework as infallible. A nonuniform-score case should follow to test scaling and score orientation.

```text
Input width2;scale1/sqrt2;zero scores.
Legal-key counts1,2,3.
Outputs: V0,(V0+V1)/2,(V0+V1+V2)/3.
Compare float32 atatol1e-6 and float64 atatol1e-12.
```

**Expected:** \([[2,0],[1,1],[\frac{8}{3},\frac{8}{3}]]\) within declared dtype tolerance.

**Verify:** Compare the computed values or written argument with \([[2,0],[1,1],[\frac{8}{3},\frac{8}{3}]]\) within declared dtype tolerance.

## Exercise 6: Preserve optionality

The question is: Write a verification record when onlyNumPy andPyTorch are prepared,withTensorFlow unavailable.

A comparison worksheet does not justify installing a second framework or inventing runtime evidence. Optional execution remains optional and explicitly reported.

```text
NumPy reasoning: checked separately.
PyTorch execution: record actual receipt if run.
TensorFlow: unavailable/unexecuted, not passed.
llm-042 does not require llm-041.
```

**Expected:** TensorFlowunexecuted;LLMfinalcapstoneremainsavailable.

**Verify:** Compare the computed values or written argument with TensorFlowunexecuted;LLMfinalcapstoneremainsavailable.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

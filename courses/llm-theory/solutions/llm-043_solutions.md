# llm-043: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Transformer architecture describes which positions exchange information and how those representations are used. An encoder can let every source position attend to every other available source position. A causal decoder restricts a target position to its current and earlier input positions. An encoder-decoder combines a source encoder with a causal target decoder whose cross-attention can read the encoded source. These are information-flow choices, not three names for the same mask.

The training objective is another choice. A masked-token encoder predicts selected corrupted source positions using surrounding context. An autoregressive decoder predicts the next token from a prefix. A sequence-to-sequence model predicts target tokens conditioned on an entire source and an earlier target prefix. Teacher forcing supplies the correct previous target tokens during training; it does not permit the current target answer to leak into its own prediction. An encoder may use future source words because the complete source is available, but a streaming task may impose a different availability contract.

This lesson implements the three attention information patterns on literal vectors. It does not train BERT, T5 or a foundation model. The small calculation is enough to show which perturbations may affect which outputs, which axes a cross-attention score matrix has, and why objective masks and attention masks must be checked separately.

**Encoder:** A representation network over source positions whose complete context may be available.

**Causal decoder:** A network preserving the target-prefix information boundary.

**Cross-attention:** Attention whose queries and keys/values come from different sequences.

**Teacher forcing:** Using observed prior target tokens as decoder input during supervised training.

**Objective mask:** The target positions included in the loss,distinct from the attention access mask.

## Reading the implementation

The attention helper accepts Q shaped(Tq, d), K shaped(Tk, d), V shaped(Tk, dv) and a boolean allowed matrix(Tq, Tk). It validates nonempty legal rows, then uses a stable row-wise softmax of `Q @ K.T / sqrt(d)`. Encoder self-attention has Tq=Tk=source length and an all-allowed source mask. Causal decoder self-attention has a lower triangle over target-prefix positions. Cross-attention can be rectangular, with target queries and source keys/values. Labels and loss masks are constructed independently from these attention masks.

## Exercise 1: Compare bidirectional and causal mixtures

The question is: Use zero queries/keys and values[[2, 0], [0, 2], [6, 6]] under all-allowed and causal masks.

The score arithmetic is identical; the allowed information differs. A future source change may affect an encoder output when the whole source is available, while a future target change must not affect an earlier causal output.

```python
q=np.zeros((3,2)); values=np.array([[2.,0.],[0.,2.],[6.,6.]])
encoder,_=attention(q,q,values,np.ones((3,3),dtype=bool))
decoder,_=attention(q,q,values,np.tri(3,dtype=bool))
np.testing.assert_allclose(encoder,np.tile([8/3,8/3],(3,1)),atol=1e-12,rtol=0)
np.testing.assert_allclose(decoder,[[2,0],[1,1],[8/3,8/3]],atol=1e-12,rtol=0)
```

**Expected:** encoder rows all[8/3, 8/3]; decoder rows[2, 0], [1, 1], [8/3, 8/3].

**Verify:** Compare the computed values or written argument with encoder rows all[8/3, 8/3]; decoder rows[2, 0], [1, 1], [8/3, 8/3].

## Exercise 2: Trace rectangular cross-attention

The question is: Use two zero target queries, three zero source keys and the same source values.

The output count follows the query sequence, not the source length. A square-mask assumption would incorrectly reject or distort ordinary encoder-decoder attention.

```python
target_queries=np.zeros((2,2)); source_keys=np.zeros((3,2))
cross,weights=attention(target_queries,source_keys,values,np.ones((2,3),dtype=bool))
assert weights.shape==(2,3) and cross.shape==(2,2)
np.testing.assert_allclose(cross,np.tile([8/3,8/3],(2,1)),atol=1e-12,rtol=0)
```

**Expected:** score/weight shape(2, 3); output shape(2, 2); both outputs[8/3, 8/3].

**Verify:** Compare the computed values or written argument with score/weight shape(2, 3); output shape(2, 2); both outputs[8/3, 8/3].

## Exercise 3: Build shifted decoder targets

The question is: For target IDs[5, 7, 3], prepend BOS 1 and form input/label pairs.

The current decoder input is the previous target under this shifted convention. Allowing the diagonal is compatible with causality; copying the current answer into the same input position would not be.

```python
target=np.array([5,7,3]); inputs=np.concatenate([[1],target[:-1]]); labels=target.copy(); mask=np.tri(3,dtype=bool)
np.testing.assert_array_equal(inputs,[1,5,7]); np.testing.assert_array_equal(labels,[5,7,3])
assert mask[0,0] and not mask[0,1]
```

**Expected:** inputs[1, 5, 7]; labels[5, 7, 3]; diagonal allowed without seeing the target itself.

**Verify:** Compare the computed values or written argument with inputs[1, 5, 7]; labels[5, 7, 3]; diagonal allowed without seeing the target itself.

## Exercise 4: Separate masked-token supervision

The question is: Corrupt source[2, 5, 7] at the middle position with MASK 0 and supervise only that original token.

The source attention mask and the loss participation mask have different shapes and purposes. A masked-language objective does not require a causal triangle over the complete source.

```python
original=np.array([2,5,7]); corrupted=original.copy(); corrupted[1]=0; active=np.array([False,True,False])
np.testing.assert_array_equal(corrupted,[2,0,7]); assert original[active].tolist()==[5]
assert np.ones((3,3),dtype=bool)[1].all()
```

**Expected:** input[2, 0, 7]; one active label 5; bidirectional context remains allowed.

**Verify:** Compare the computed values or written argument with input[2, 0, 7]; one active label 5; bidirectional context remains allowed.

## Exercise 5: Perturb future target values

The question is: Change only the third value vector and compare the first two encoder/decoder outputs.

This is a direct information-flow test. The encoder behavior is valid for a fully available source but invalid if those same positions represent unavailable future targets.

```python
changed=values.copy(); changed[2]=[100,200]
new_encoder,_=attention(q,q,changed,np.ones((3,3),dtype=bool)); new_decoder,_=attention(q,q,changed,np.tri(3,dtype=bool))
assert not np.allclose(new_encoder[:2],encoder[:2])
np.testing.assert_allclose(new_decoder[:2],decoder[:2],atol=1e-12,rtol=0)
```

**Expected:** encoder prefix changes; causal decoder prefix stays fixed.

**Verify:** Compare the computed values or written argument with encoder prefix changes; causal decoder prefix stays fixed.

## Exercise 6: Combine source padding with cross-attention

The question is: Mark the third source position as padding for both target queries.

Padding describes source availability, not target causality. A decoder may need a causal self-attention mask and a separate source-padding cross-attention mask in the same block.

```python
allowed=np.array([[True,True,False],[True,True,False]])
masked,weights=attention(target_queries,source_keys,values,allowed)
np.testing.assert_allclose(masked,[[1,1],[1,1]],atol=1e-12,rtol=0)
np.testing.assert_array_equal(weights[:,2],[0,0])
```

**Expected:** both cross outputs[1, 1]; padded source weight 0.

**Verify:** Compare the computed values or written argument with both cross outputs[1, 1]; padded source weight 0.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

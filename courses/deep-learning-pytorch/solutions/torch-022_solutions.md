# torch-022: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

Attention forms weighted combinations of value vectors using query-key comparisons. A causal decoder restricts each query to current and earlier positions. PyTorch's functional scaled_dot_product_attention uses boolean True for allowed positions, while other attention APIs such as Multihead Attention key_padding_mask use True for ignored keys. Mask polarity belongs to the exact parameter contract, not to the framework name.

The functional API also applies dropout according to its dropout_p argument; calling an enclosing module.eval does not automatically change an explicit nonzero probability. For an evaluation oracle, pass dropout_p0. Equal queries and keys make legal scores uniform, so the expected outputs are prefix means. Nonuniform scores and future-only perturbations add stronger checks than causal-looking triangles alone.

**SDPA:** Scaled dot-product attention implemented by a functional API.

**Mask polarity:** Whether True means allowed or excluded for this parameter.

**Prefix invariance:** Agreement between a full sequence prefix and independent prefix execution.

**Dropout argument:** An explicit stochastic policy in the functional attention call.

## Reading the implementation

The checked helper accepts nonempty2D self-attention matrices and a boolean square allowed mask. Reject fully masked rows before normalization. F.scaled_dot_product_attention supplies the1/sqrt(key_width) scaling and normalizes over the key axis. A causal lower triangle includes its diagonal for shifted next-token targets. Independently recompute each prefix rather than slicing full weights.

## Exercise 1: Compute uniform causal mixtures

The question is: Use zero3x2queries/keys and values2, 0; 0, 2; 6, 6.

Each query averages its allowed values. The fixture exposes the meaning of both axes and the included diagonal.

```python
q=torch.zeros((3,2),dtype=torch.float64); v=torch.tensor([[2.,0.],[0.,2.],[6.,6.]],dtype=torch.float64); allowed=torch.ones((3,3),dtype=torch.bool).tril()
out=attention(q,q,v,allowed)
torch.testing.assert_close(out,torch.tensor([[2.,0.],[1.,1.],[8/3,8/3]],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** outputs2, 0; 1, 1; 8/3, 8/3.

**Verify:** Compare the computed values or written argument with outputs2, 0; 1, 1; 8/3, 8/3.

## Exercise 2: Perturb only the future

The question is: Change only the third value to100, 200.

The causal boundary is verified through behavior. A zeroed future weight plot would not detect every wrong normalization or upstream leak.

```python
future=v.clone(); future[2]=torch.tensor([100.,200.]); changed=attention(q,q,future,allowed)
torch.testing.assert_close(changed[:2],out[:2],atol=1e-12,rtol=0)
torch.testing.assert_close(changed[2],torch.tensor([34.,202/3],dtype=torch.float64),atol=1e-12,rtol=0)
```

**Expected:** first two rows unchanged; last34, 202/3.

**Verify:** Compare the computed values or written argument with first two rows unchanged; last34, 202/3.

## Exercise 3: Recompute nonuniform prefixes

The question is: UseQ=K rows1, 0; 0, 1; 1, 1 and compare cuts1..3.

Nonuniform scores exercise query-key arithmetic and scaling. The checker rebuild s the computation on the shorter inputs.

```python
non=torch.tensor([[1.,0.],[0.,1.],[1.,1.]],dtype=torch.float64); full=attention(non,non,v,allowed)
for cut in range(1,4): torch.testing.assert_close(attention(non[:cut],non[:cut],v[:cut],allowed[:cut,:cut]),full[:cut],atol=1e-12,rtol=0)
```

**Expected:** all prefix outputs match within1e-12.

**Verify:** Compare the computed values or written argument with all prefix outputs match within1e-12.

## Exercise 4: Reject an all-masked row

The question is: Set the second allowed row to False.

Different kernels may return zero for fully masked rows, but this course contract rejects a query with no legal probability support. The policy is explicit and portable.

```python
empty=allowed.clone(); empty[1]=False
try: attention(q,q,v,empty)
except ValueError: pass
else: raise AssertionError('undefined row accepted')
```

**Expected:** ValueError before the attention call.

**Verify:** Compare the computed values or written argument with ValueError before the attention call.

## Exercise 5: Translate mask polarity explicitly

The question is: Invert the allowed matrix to obtain a forbidden mask for APIs using True as blocked.

Do not pass this inverted mask to functional SDPA under its boolean allowed convention. The translation depends on the exact API parameter.

```python
forbidden=~allowed
assert forbidden[0].tolist()==[False,True,True]
```

**Expected:** first forbidden row False, True, True.

**Verify:** Compare the computed values or written argument with first forbidden row False, True, True.

## Exercise 6: Keep inference dropout disabled

The question is: Repeat functional attention with dropout_p0 and compare exact outputs.

The helper fixes dropout_p0, so its behavior is independent of the mode of any surrounding module. A training wrapper must pass its chosen probability explicitly.

```python
again=attention(q,q,v,allowed)
torch.testing.assert_close(again,out,atol=0,rtol=0)
```

**Expected:** repeated evaluation matches.

**Verify:** Compare the computed values or written argument with repeated evaluation matches.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

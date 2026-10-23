# llm-047: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

A mixture-of-experts layer routes each token to a subset of specialized transformations. The total model can contain many expert parameters while activating only a few per token. That does not make memory or communication free: all experts must be stored somewhere, and distributed routing moves token activations to the devices owning selected experts. Uneven routing can overload one expert while others remain idle.

The router produces scores or probabilities over experts. A top-k decision selects indices, then a declared gate rule weights the selected outputs. Some designs retain selected probabilities from the full softmax; others renormalize among selected experts. Those choices change gradients and output scale. This lesson states its rule explicitly: the top-k mixture renormalizes selected mass, while the capacity demonstration uses a unit-weight top1 expert delta inside a residual path.

Capacity bounds how many tokens an expert accepts in one batch. Overflow needs a visible policy, such as dropping the expert delta and using the residual path. A load-balancing auxiliary objective can encourage less concentrated routing, but it does not prove that a system achieves good load balance, quality or throughput. The reference uses literal linear experts and finite-difference router gradients; it does not launch expert-parallel workers or claim large-model scaling.

**Sparse expert activation:** Evaluating only selected experts for each token.

**Router:** A function producing expert-selection scores for each token.

**Capacity:** A bound on tokens admitted to an expert in one batch.

**Load-balancing loss:** An auxiliary objective encouraging a less concentrated routing distribution.

**Expert parallelism:** Placing different experts on different devices and moving activations between them.

## Reading the implementation

Inputs have shape(tokens, model_width), router logits(tokens, experts), and expert matrices(experts, model_width, output_width). Stable descending argsort declares a lowest-index tie policy. The selected gates are normalized before combining expert outputs. The capacity helper tracks assigned counts, accepted counts and dropped-token flags separately. A Switch-style auxiliary term uses hard assignment fractions f and mean router probabilities P, with the hard fractions held fixed for a local gradient calculation.

## Exercise 1: Calculate a top2 expert mixture

The question is: Use experts I, 2I, -I and three token/router rows with selected probabilities 3/4 and 1/4.

The third token combines a negative expert with a positive expert, so routing can change the function ratherthan merely selecting a faster implementation of the same computation.

```python
x=np.array([[1.,0.],[0.,1.],[1.,1.]])
experts=np.stack([np.eye(2),2*np.eye(2),-np.eye(2)])
logits=np.array([[np.log(3),0.,-100.],[0.,np.log(3),-100.],[-100.,0.,np.log(3)]])
output,indices,gates=mixture(x,logits,experts,2)
np.testing.assert_allclose(output,[[1.25,0],[0,1.75],[-.25,-.25]],atol=1e-12,rtol=0)
np.testing.assert_allclose(gates.sum(1),1,atol=1e-12,rtol=0)
```

**Expected:** outputs[1.25, 0], [0, 1.75], [-.25, -.25].

**Verify:** Compare the computed values or written argument with outputs[1.25, 0], [0, 1.75], [-.25, -.25].

## Exercise 2: Enforce expert capacity with residual fallback

The question is: Route four tokens to experts 0, 0, 1, 0 with capacity 2 and unit top1 gates.

The dropped token is not deleted from the sequence or loss denominator. Its residual path is explicit, and the drop count remains available for quality and load analysis.

```python
tokens=np.array([[1.,0.],[0.,1.],[1.,1.],[2.,1.]])
route_logits=np.array([[5.,0.],[4.,0.],[0.,4.],[3.,0.]])
residual,dropped,assigned,accepted=capacity_route(tokens,route_logits,experts[:2],2)
assert assigned.tolist()==[3,1] and accepted.tolist()==[2,1] and dropped.tolist()==[False,False,False,True]
np.testing.assert_allclose(residual,[[2,0],[0,2],[3,3],[2,1]],atol=1e-12,rtol=0)
```

**Expected:** assigned counts 3, 1; accepted 2, 1; last token drops its expert delta and keeps its input.

**Verify:** Compare the computed values or written argument with assigned counts 3, 1; accepted 2, 1; last token drops its expert delta and keeps its input.

## Exercise 3: Compute a load-balancing term

The question is: Use hard fractions f[.75, .25], mean router probabilities P[.7, .3], expert count 2 and coefficient .01.

The term measures a routing-related objective under the declared formula. A lower auxiliary value is not itself evidence that task loss, capacity drops or distributed utilization improved.

```python
fractions=np.array([.75,.25]); mean_probability=np.array([.7,.3]); coefficient=.01
loss=coefficient*2*np.dot(fractions,mean_probability)
np.testing.assert_allclose(loss,.012,atol=1e-12,rtol=0)
np.testing.assert_allclose(coefficient*2*np.dot([.5,.5],[.5,.5]),.01,atol=1e-12,rtol=0)
```

**Expected:** auxiliary loss .012; balanced fixture .01.

**Verify:** Compare the computed values or written argument with auxiliary loss .012; balanced fixture .01.

## Exercise 4: Trace a local router gradient

The question is: Perturb the first logit of the first top-2 mixture row without changing selected experts.

Within a fixedselectedset, the normalized gates vary smoothly. At a top-k membership boundary, the hard index choice is not differentiable in the same way. Do not interpret thislocal derivative as differentiating through everyrouting decision.

```python
h=1e-6; plus=logits.copy(); minus=logits.copy(); plus[0,0]+=h; minus[0,0]-=h
numeric=(mixture(x,plus,experts,2)[0][0,0]-mixture(x,minus,experts,2)[0][0,0])/(2*h)
np.testing.assert_allclose(numeric,-3/16,atol=1e-8,rtol=0)
```

**Expected:** derivative of first output coordinate is -3/16 within 1e-8.

**Verify:** Compare the computed values or written argument with derivative of first output coordinate is -3/16 within 1e-8.

## Exercise 5: Separate total and active parameter counts

The question is: Use 8 two-layer experts with width 64, hidden 128 and top-2 activation, excluding router and biases.

Inactive expert weights still occupy memory somewhere. Active-weight arithmetic does not measure peak memory, token dispatch cost orall-to-all communication.

```python
expert_count,width,hidden,active=8,64,128,2
assert expert_count*2*width*hidden==131072
assert active*2*width*hidden==32768
```

**Expected:** total 131072 expert weights; 32768 selected expert weights per token.

**Verify:** Compare the computed values or written argument with total 131072 expert weights; 32768 selected expert weights per token.

## Exercise 6: Validate routing policy and ties

The question is: Reject top-k 0 and capacity 0; check equal router logits choose lower indices deterministically.

Tie andoverflow policies affect reproducibility andwhich tokens receiveexpert computation. They must be explicit beforecomparing modelquality orload statistics.

```python
_,tied,_=mixture(np.ones((1,2)),np.zeros((1,3)),experts,2); assert tied.tolist()==[[0,1]]
for action in [lambda:mixture(x,logits,experts,0),lambda:capacity_route(tokens,route_logits,experts[:2],0)]:
    try: action()
    except ValueError: pass
    else: raise AssertionError('invalid routing policy accepted')
```

**Expected:** invalid policies raise ValueError; top-2 tie indices 0, 1.

**Verify:** Compare the computed values or written argument with invalid policies raise ValueError; top-2 tie indices 0, 1.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

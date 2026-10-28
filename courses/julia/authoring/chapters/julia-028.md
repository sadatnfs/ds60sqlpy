## Independent evidence starts with a specification

A function test is useful when its expectation comes from the intended behavior rather than the same implementation copied into a second function. Example tests cover named cases. Property tests describe relations that should hold for a family of inputs. Metamorphic tests change the input in a controlled way and predict how the output must change, which is valuable when a full oracle is difficult to calculate.

Consider normalizing nonnegative finite weights \(w_i\) into probabilities \(p_i=w_i/S\), where \(S=\sum_i w_i>0\). The output must preserve length, contain nonnegative entries and sum approximately to one. Multiplying all weights by a positive constant should preserve probabilities when arithmetic remains representable. Permuting inputs should permute outputs in the same way. These are separate properties with different bug-detection value.

## A numerically stable normalization

Directly summing very large finite values can overflow even though valid probabilities exist. Divide weights by their maximum before summing: \(s_i=w_i/\max_j w_j\), then \(p_i=s_i/\sum_j s_j\). At least one scaled value is one, so the denominator is positive. With a bounded vector the sum is manageable. Very small relative weights may still underflow to zero; document that finite-precision limitation rather than claiming arbitrary precision.

Validate empty input, negative weights and nonfinite values before normalization. A zero vector has no probability interpretation under this contract. Do not silently return uniform probabilities, because that substitutes an unrequested modeling assumption.

### Worked case A: hand-derived and extreme cases

The first program tests weights[1,2,1], whose probabilities are exactly[0.25,0.5,0.25], and two enormous equal weights. The latter case exposes an overflow bug that ordinary small examples would miss.

{{WORKED_A}}

The reference uses Float64 conversion deliberately. Generic input acceptance is bounded by whether conversion produces finite stored values. Arbitrary BigFloat precision is a separate design choice and should not be silently discarded in a scientific API that promises it.

### Worked case B: generated metamorphic checks

The second program uses a private seeded generator to produce bounded positive vectors. It checks normalization, positive scaling and permutation equivariance. The input generation is reproducible inside the pinned runtime. The tests do not assert that random generation explored all possible vectors.

{{WORKED_B}}

## Why several properties are necessary

Returning a uniform vector passes the sum-to-one and nonnegativity checks, yet loses the weights. It fails the hand-derived asymmetric example. Sorting probabilities passes normalization but violates permutation equivariance. Squaring weights before normalization can pass scaling invariance but violates known ratios. Combining tests reduces these blind spots; no finite collection proves correctness for an unrestricted domain.

Random seeds are provenance, not an independence guarantee. Two tests that reuse identical generated inputs have overlapping evidence. Preserve a failing input as a named regression case so that later generator changes cannot erase it. Print enough bounded context to diagnose a failure without exposing sensitive source records.

## Reproducibility and scientific reporting

Record code identity, input construction, package versions, numerical tolerances and the reasoning behind each tolerance. A tolerance should reflect floating error or a declared approximation, not be enlarged until the test passes. Statistical simulations need sampling-error arguments in addition to deterministic numerical checks.

Use `@test_throws` for deliberate contract violations and ordinary assertions for values, shapes and storage. Group related checks with `@testset` when a larger package needs readable failure reports. Keep end-to-end worker execution separate from source tests: a correct mathematical function is not evidence that the browser delivered the intended source, preserved its receipt or rendered its figure. The capstone ties these layers together while retaining each layer's limits.

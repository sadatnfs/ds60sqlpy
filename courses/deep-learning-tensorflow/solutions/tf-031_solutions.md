# tf-031: explanatory solutions

Compare these answers only after an attempt or an explicit solution reveal. They use the same literal inputs as the guide, so a discrepancy can be localized to a specific step. The executable companion runs the assertions; the explanation states why those assertions test the subject. Passing a reference function is rehearsal, and should be followed by a new input chosen without looking at the answer.

## Mechanism review

tf.function traces Python code to construct TensorFlow graphs specialized for input contracts. Tracing is setup work; graph execution is the tensor computation performed on later calls. A compatible shape and dtype can reuse a trace, while a new dtype or incompatible shape can require another concrete function. Python side effects run while tracing, so they are not a reliable record of how many times graph tensor operations executed.

This stage should be distinguished from explicitly requesting XLA compilation with jit_compile=True. A traced TensorFlow graph can run through the normal runtime and its available kernels. Graph construction, graph optimization, kernel execution and optional XLA machine-code compilation are related but separate stages. This lesson does not request or qualify XLA, and a successful tf.function call is not evidence that an XLA-compiled executable was used.

The fixture uses x*x+1 so eager output can be calculated independently. It compares eager and graph values, observes trace reuse and dtype specialization, and measures a small warmed-call interval. The timing boundary includes Python dispatch, tensor execution and NumPy materialization; it is not a GPU kernel benchmark. No measured speed ranking is claimed. A graph can add overhead for tiny work, while repeated larger computations may benefit from graph execution under a suitable runtime.

An input signature is both a reuse policy and an interface contract. TensorSpec([None],float32) allows different vector lengths while fixing rank and dtype. None does not mean any rank or any type. Broadening a signature can reduce retracing, but it must still describe the inputs the function can correctly handle. Reusing a graph is useful only when its computation and boundary remain valid.

**Trace:** Construction of a graph from Python execution and input signatures.

**Signature:** Input structure, dtype and shape constraints for graph reuse.

**Warmup:** Initial calls excluded from steady-state measurement.

## Reading the implementation

The decorator creates a polymorphic function wrapper. Its first compatible call traces the Python body using TensorFlow values and records operations in a graph. Concrete traces are selected using input structure, dtype and shape information, plus relevant Python arguments. experimental_get_tracing_count is an observation of traces created for this wrapper, not a count of tensor executions.

For f(value)=value*value+1, float32 [1,2] gives [2,5]. Calling float32 [3,4] changes values while retaining the same shape and dtype, so the compatible trace can be reused and gives [10,17]. Calling float64 [1,2] changes the dtype contract and creates another trace in this fixture. The resulting tensor is float64; identical displayed values do not establish identical precision, kernel choice or performance.

The second wrapper declares TensorSpec([None],tf.float32). Vectors of length two and three satisfy that contract, so both reuse the same declared graph interface. A rank-two array or float64 input does not satisfy it. An explicit signature can make such mistakes fail at the boundary rather than silently specializing a new graph.

Materializing result.numpy() before stopping the clock ensures the measured host observation includes completion of the requested result. Warmup is performed before the interval so initial graph construction is not mixed into steady repeated calls. Still, ten calls are only a small diagnostic sample. The experiment does not isolate every layer of dispatch overhead or establish a distribution of production latency.

## Exercise 1: Check eager arithmetic

The question is: Evaluate x*x+1 at float32[1,2].

The arithmetic provides a simple independent oracle. Correctness must be established before timing a graph implementation.

```python
x = tf.constant([1., 2.], dtype=tf.float32)
eager = x * x + 1
np.testing.assert_array_equal(eager.numpy(), [2, 5])
```

**Expected:** output[2,5].

**Verify:** Compare the computed values or written argument with output[2,5].

## Exercise 2: Trace a graph and compare

The question is: Wrap the expression in plain tf.function, run it and inspect the initial trace count.

The first call constructs a graph for the input contract. Matching its output with the eager oracle establishes this small calculation. It does not establish XLA compilation, a speedup or compatibility with every possible input.

```python
@tf.function
def f(value):
    return value * value + 1

np.testing.assert_array_equal(f(x).numpy(), eager.numpy())
first = f.experimental_get_tracing_count()
assert first >= 1
```

**Expected:** Graph output equals eager output; at least one trace exists. No XLA compilation is requested.

**Verify:** Compare the computed values or written argument with Graph output equals eager output; at least one trace exists. No XLA compilation is requested.

## Exercise 3: Reuse an equal signature

The question is: Call with float32[3,4] and inspect trace count.

Values change while shape and dtype remain the same. Reusing a trace demonstrates the intended separation between graph structure and tensor values.

```python
same_signature = tf.constant([3., 4.], dtype=tf.float32)
np.testing.assert_array_equal(f(same_signature).numpy(), [10, 17])
assert f.experimental_get_tracing_count() == first
```

**Expected:** output[10,17]; trace count unchanged.

**Verify:** Compare the computed values or written argument with output[10,17]; trace count unchanged.

## Exercise 4: Change dtype deliberately

The question is: Call with float64[1,2] and inspect trace count and output dtype.

Dtype changes can affect kernels and arithmetic. Reporting them separately prevents an apparent performance regression from being attributed to values alone.

```python
different_dtype = tf.constant([1., 2.], dtype=tf.float64)
output = f(different_dtype)
assert output.dtype == tf.float64
assert f.experimental_get_tracing_count() > first
np.testing.assert_array_equal(output.numpy(), [2, 5])
```

**Expected:** float64 result[2,5]; at least one new trace.

**Verify:** Compare the computed values or written argument with float64 result[2,5]; at least one new trace.

## Exercise 5: Measure only warmed calls

The question is: Warm the float32 graph, time ten completed calls, then check every collected result.

The measured interval excludes the initial trace. This small sample is a timing observation for the current environment, not evidence that graph execution always wins.

```python
import time

f(x).numpy()
start = time.perf_counter()
observations = [f(x).numpy() for _ in range(10)]
elapsed = time.perf_counter() - start
assert len(observations) == 10
assert elapsed >= 0
for observed in observations:
    assert np.isfinite(observed).all()
    np.testing.assert_array_equal(observed, [2, 5])
```

**Expected:** Ten finite [2,5] results and a nonnegative measured interval, without a speed-ranking claim.

**Verify:** Compare the computed values or written argument with Ten finite [2,5] results and a nonnegative measured interval, without a speed-ranking claim.

## Exercise 6: Separate shape contracts

The question is: Reuse a variable-length float32 vector signature at lengths two and three, then reject wrong rank and dtype.

An explicit signature can permit varying dimensions without retracing. It is also a contract that rejects incompatible rank or dtype instead of silently accepting every input.

```python
@tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
def g(value):
    return value * value + 1

g(tf.constant([1., 2.], dtype=tf.float32))
count = g.experimental_get_tracing_count()
output = g(tf.constant([1., 2., 3.], dtype=tf.float32))
assert tuple(output.shape) == (3,)
assert g.experimental_get_tracing_count() == count
for incompatible in [tf.constant([[1., 2.]], dtype=tf.float32), tf.constant([1., 2.], dtype=tf.float64)]:
    try:
        g(incompatible)
    except (TypeError, ValueError):
        pass
    else:
        raise AssertionError('incompatible signature accepted')
```

**Expected:** One declared trace is reused for both lengths; incompatible rank or dtype is rejected.

**Verify:** Compare the computed values or written argument with One declared trace is reused for both lengths; incompatible rank or dtype is rejected.

## Review after comparison

Repeat one case with a changed fixture and explain the difference before running it. Keep the original failure case as well as the repaired result. Record a missing framework separately from a failing assertion. No solution downloads data, calls an online model, deploys a service or changes a database.

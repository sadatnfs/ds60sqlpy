def deepen(spec):
    spec['mental'] = '''tf.function traces Python code to construct TensorFlow graphs specialized for input contracts. Tracing is setup work; graph execution is the tensor computation performed on later calls. A compatible shape and dtype can reuse a trace, while a new dtype or incompatible shape can require another concrete function. Python side effects run while tracing, so they are not a reliable record of how many times graph tensor operations executed.

This stage should be distinguished from explicitly requesting XLA compilation with jit_compile=True. A traced TensorFlow graph can run through the normal runtime and its available kernels. Graph construction, graph optimization, kernel execution and optional XLA machine-code compilation are related but separate stages. This lesson does not request or qualify XLA, and a successful tf.function call is not evidence that an XLA-compiled executable was used.

The fixture uses x*x+1 so eager output can be calculated independently. It compares eager and graph values, observes trace reuse and dtype specialization, and measures a small warmed-call interval. The timing boundary includes Python dispatch, tensor execution and NumPy materialization; it is not a GPU kernel benchmark. No measured speed ranking is claimed. A graph can add overhead for tiny work, while repeated larger computations may benefit from graph execution under a suitable runtime.

An input signature is both a reuse policy and an interface contract. TensorSpec([None],float32) allows different vector lengths while fixing rank and dtype. None does not mean any rank or any type. Broadening a signature can reduce retracing, but it must still describe the inputs the function can correctly handle. Reusing a graph is useful only when its computation and boundary remain valid.'''
    spec['anatomy'] = '''The decorator creates a polymorphic function wrapper. Its first compatible call traces the Python body using TensorFlow values and records operations in a graph. Concrete traces are selected using input structure, dtype and shape information, plus relevant Python arguments. experimental_get_tracing_count is an observation of traces created for this wrapper, not a count of tensor executions.

For f(value)=value*value+1, float32 [1,2] gives [2,5]. Calling float32 [3,4] changes values while retaining the same shape and dtype, so the compatible trace can be reused and gives [10,17]. Calling float64 [1,2] changes the dtype contract and creates another trace in this fixture. The resulting tensor is float64; identical displayed values do not establish identical precision, kernel choice or performance.

The second wrapper declares TensorSpec([None],tf.float32). Vectors of length two and three satisfy that contract, so both reuse the same declared graph interface. A rank-two array or float64 input does not satisfy it. An explicit signature can make such mistakes fail at the boundary rather than silently specializing a new graph.

Materializing result.numpy() before stopping the clock ensures the measured host observation includes completion of the requested result. Warmup is performed before the interval so initial graph construction is not mixed into steady repeated calls. Still, ten calls are only a small diagnostic sample. The experiment does not isolate every layer of dispatch overhead or establish a distribution of production latency.'''
    spec['mechanism_notes'] = '''## A trace is not an execution count

Imagine a Python counter increment placed in the decorated body. The counter changes when Python runs to construct a new trace, not necessarily every time an already built graph executes. A TensorFlow operation such as tf.print belongs to the graph and follows graph execution instead. Mixing these two kinds of side effects can make debugging output look inconsistent even when the graph is being reused correctly. Keep stateful I/O and tracing diagnostics deliberate.

Retracing can be legitimate: a different dtype or rank may require different operation contracts. It can also be accidental when a caller repeatedly supplies varying Python objects or creates a new decorated function inside a loop. Before changing performance settings, inspect wrapper lifetime, input signatures and the count of concrete traces. A model rebuilt per request cannot benefit from the same reuse as one stable model object.

## What optional XLA would change

jit_compile=True asks TensorFlow to compile a supported graph through XLA. That request has its own compatibility constraints, setup cost and runtime evidence. Some operations or dynamic behaviors may not be supported in a chosen compilation path. This chapter's plain tf.function examples do not test those conditions, and no XLA speedup is inferred from their successful output checks. Likewise, Python source syntax being valid does not establish graph tracing, and graph tracing does not establish production throughput.

## Read the measurement as a contract

The measured interval contains ten calls at a fixed float32 input after warmup. It also includes the host loop and synchronization/materialization needed to observe the results. The output assertions establish that those observations are finite and correct for the fixture. They do not say which implementation is fastest. A useful comparison would state the workload, warmup policy, repetitions, synchronization boundary, runtime versions and variability, then compare equivalent outputs under the same conditions.
'''
    spec['diagnosis'] = '''If the trace count grows unexpectedly, verify that the same decorated wrapper is reused and inspect input rank, dtype, shape and Python argument values. A changing scalar Python argument can specialize traces differently from a scalar Tensor argument. If Python print output appears only once, distinguish tracing from execution before assuming later calls were skipped.

If a declared signature rejects input, compare rank and dtype explicitly; a None dimension permits a size change only at that dimension. If graph output differs from eager output, reduce the function to the first differing tensor operation and inspect state captured from Python. If a benchmark changes drastically after its first call, separate setup from warmed execution and include result completion in the timing boundary. Finally, do not label the graph path as XLA merely because a variable or heading says compiled.'''
    codes = [
'''x = tf.constant([1., 2.], dtype=tf.float32)
eager = x * x + 1
np.testing.assert_array_equal(eager.numpy(), [2, 5])''',
'''@tf.function
def f(value):
    return value * value + 1

np.testing.assert_array_equal(f(x).numpy(), eager.numpy())
first = f.experimental_get_tracing_count()
assert first >= 1''',
'''same_signature = tf.constant([3., 4.], dtype=tf.float32)
np.testing.assert_array_equal(f(same_signature).numpy(), [10, 17])
assert f.experimental_get_tracing_count() == first''',
'''different_dtype = tf.constant([1., 2.], dtype=tf.float64)
output = f(different_dtype)
assert output.dtype == tf.float64
assert f.experimental_get_tracing_count() > first
np.testing.assert_array_equal(output.numpy(), [2, 5])''',
'''import time

f(x).numpy()
start = time.perf_counter()
observations = [f(x).numpy() for _ in range(10)]
elapsed = time.perf_counter() - start
assert len(observations) == 10
assert elapsed >= 0
for observed in observations:
    assert np.isfinite(observed).all()
    np.testing.assert_array_equal(observed, [2, 5])''',
'''@tf.function(input_signature=[tf.TensorSpec([None], tf.float32)])
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
        raise AssertionError('incompatible signature accepted')''',
]
    for exercise, code in zip(spec['exercises'], codes, strict=True):
        exercise['code'] = code
    spec['exercises'][1]['title'] = 'Trace a graph and compare'
    spec['exercises'][1]['prompt'] = 'Wrap the expression in plain tf.function, run it and inspect the initial trace count.'
    spec['exercises'][1]['expected'] = 'Graph output equals eager output; at least one trace exists. No XLA compilation is requested.'
    spec['exercises'][1]['why'] = 'The first call constructs a graph for the input contract. Matching its output with the eager oracle establishes this small calculation. It does not establish XLA compilation, a speedup or compatibility with every possible input.'
    spec['exercises'][4]['prompt'] = 'Warm the float32 graph, time ten completed calls, then check every collected result.'
    spec['exercises'][4]['expected'] = 'Ten finite [2,5] results and a nonnegative measured interval, without a speed-ranking claim.'
    spec['exercises'][5]['prompt'] = 'Reuse a variable-length float32 vector signature at lengths two and three, then reject wrong rank and dtype.'
    spec['exercises'][5]['expected'] = 'One declared trace is reused for both lengths; incompatible rank or dtype is rejected.'

# torch-031: explanatory solutions

Open these answers only after attempting Profiling, torch.compile and honest performance measurement yourself. They reuse the guide's literal inputs, starting from Example A, Establish an eager oracle, so a discrepancy points at one step. The executable companion runs the assertions; this page explains why each one tests Graph capture, Backend, Warmup. After a pass, choose a new input for exercise 6, State the backend limitation, without looking.

## Mechanism review

Compilation and profiling answer different questions. torch.compile captures eligible Python/tensor computation and sends graphs to a selected backend. An eager graph backend can demonstrate capture and specialization without compiling optimized native kernels. That is useful in a bounded classroom image but is not an Inductor speedup claim. Input dtype, shape and Python control can affect graph reuse or graph breaks.

Measure correctness before performance. The first call can include capture and setup, while later calls reuse prepared work. A small timing sample is an observation for one environment, not a universal ranking. The CPU profiler can identify which operations ran and where time was attributed, but profiling itself adds overhead. This lesson uses a custom backend that records captured graphs and returns their eager forward function, then separates warmup and steady-state measurements explicitly.

**Graph capture:** Representing eligible tensor computation as a reusable graph.

**Backend:** The implementation receiving a captured graph for execution or compilation.

**Warmup:** Initial setup calls separated from repeated-work measurement.

**Profiler overhead:** Extra work introduced by measurement instrumentation.

## Reading the implementation

torch.compile(function, backend=counting_backend, fullgraph=True, dynamic=False) passes captured FX graphs to a local backend. The backend records each graph and returns graph.forward. Repeated equal signatures should reuse the capture; changed dtype needs separate treatment. time.perf_counter measures elapsed wall time. torch.profiler.profile with CPU activities records eager tensor operations without assuming a GPU or native optimizing compiler.

## Separate capture, guards, execution and measurement

The eager function computes \(x\cdot x+1\). For [1, 2], the result is [2, 5]; for [3, 4], it is [10, 17]. These literal values establish correctness without relying on the compiled wrapper as its own oracle. The selected backend receives a captured FX graph and example inputs, appends that graph to a diagnostic list, and returns graph.forward. Tensor operations then execute through that eager graph function. No optimized native kernel generation is requested by this backend.

torch.compile is the entry to a larger capture/guard/backend system. fullgraph=True asks this function to be captured as one graph and reports unsupported graph breaks rather than quietly presenting a partly captured program as the intended full graph. dynamic=False specializes the relevant shapes in this example. Those options do not remove Python dispatch and guard checks before every later call. [PyTorch 2.9 torch.compile](https://docs.pytorch.org/docs/2.9/generated/torch.compile.html).

The graph-list length counts backend capture invocations, not tensor executions. The same float32 shape can be called again with different values and reuse its graph. The float64 call changes the operation contract and adds a capture in this fixture. Other relevant guards can involve shape, strides, device, requires_grad, module mode or Python values. A cache hit is useful only when those assumptions still describe the input correctly.

Data-dependent Python control is a different issue from merely changing tensor values. A branch based on a tensor converted to a Python scalar can force a graph break or require a separately supported representation. Do not infer that this pure arithmetic example qualifies arbitrary Python side effects or control flow. Counting captures can help locate recompilation, but it cannot by itself show that all application work was represented in one optimized graph.

The measured interval starts after a warm float32 call and contains twenty repeated calls at the same input. The current reference checks the final observed output after that interval; it does not retain a separate per-call output ledger. CPU tensor operations in this path complete before the observed result is used. The elapsed time includes wrapper dispatch and guard/execution costs, but excludes initial capture, model construction and a realistic input pipeline. It is a small diagnostic sample, not a latency distribution.

Setup amortization can be expressed without inventing a benchmark. If setup cost is C, an eager call costs E, and a prepared alternative costs G, then N calls cost approximately NE versus C+NG under a simple stationary model. A break-even \(N>\frac{C}{E-G}\) exists only if \(E>G\). Hypothetical C=200ms, E=1ms, G=0.5ms would require more than 400 calls. Those are illustrative units, not measurements from this lesson, and the eager graph backend may have no positive speedup to amortize at all.

Real measurements need a fixed mode, dtype, shape distribution, thread setting and input/output boundary. Dynamic request shapes can trigger additional setup that a one-signature loop omits. Memory allocation, caches, JIT warmup and concurrent host load also matter. If a future accelerator path launches asynchronously, a host timer without an appropriate completion boundary can measure enqueue time rather than finished work. This CPU lesson does not qualify that device timing path.

The profiler answers which operations ran and where instrumented time was attributed. aten::mul and aten::add are expected for the eager expression, while conversions or wrapper operations can also appear. Their presence is not evidence that an optimizer fused them. Inclusive operator times can contain child work, so summing every inclusive entry can double-count. Self time and total time answer different questions, and aggregate CPU work can differ from elapsed wall time when threads overlap. [PyTorch 2.9 profiler](https://docs.pytorch.org/docs/2.9/profiler.html).

Profiling itself adds work. Keep an instrumented diagnosis run separate from the ordinary timing comparison unless the overhead is explicitly part of the measured system. The paired TensorFlow guide similarly distinguishes tf.function tracing from XLA compilation and names its NumPy-materialization boundary. Those are analogous questions, not identical runtimes or a fair performance contest by default.

The useful result is a packet containing correct outputs, capture/reuse observations, actual operation names, the exact timing boundary and a limited conclusion. A nonnegative elapsed interval proves the timer ran; it does not establish that this backend is faster, that throughput scales, or that a deployment meets a latency target.

## Exercise 1: Establish a new eager oracle

The question is: Evaluate g(x)=2x-1 eagerly at the float32 inputs [0, 3].

The eager result is the oracle every captured or compiled version must match.

```python
def affine(value):
    return 2 * value - 1


points = torch.tensor([0.0, 3.0])
assert affine(points).tolist() == [-1.0, 5.0]
```

**Expected:** output [-1, 5].

**Verify:** In a fresh process, the exercise checks confirm `affine(points).tolist() == [-1.0, 5.0]`.

## Exercise 2: Capture the new function

The question is: Compile g with a counting backend that returns graph.forward and compare it with the eager output.

The transparent backend runs the captured graph unchanged, so equality tests capture rather than optimization.

```python
captured = []


def counting(graph, example_inputs):
    captured.append(graph)
    return graph.forward


compiled_affine = torch.compile(affine, backend=counting, fullgraph=True, dynamic=False)
torch.testing.assert_close(compiled_affine(points), affine(points), atol=0, rtol=0)
assert len(captured) >= 1
```

**Expected:** at least one captured graph; outputs match exactly.

**Verify:** In a fresh process, the exercise checks confirm `compiled_affine(points)` matches `affine(points)` exactly and `len(captured) >= 1`.

## Exercise 3: Predict recompilation for a new shape

The question is: Call the compiled function with a three-element input, then with a second three-element input.

With dynamic=False each new input shape fails a guard and is captured again; an identical signature passes the guard.

```python
before_three = len(captured)
compiled_affine(torch.tensor([1.0, 2.0, 3.0]))
after_three = len(captured)
compiled_affine(torch.tensor([4.0, 5.0, 6.0]))
assert after_three > before_three and len(captured) == after_three
```

**Expected:** the first three-element call adds a graph; the repeated shape reuses it.

**Verify:** In a fresh process, the exercise checks confirm `after_three > before_three` and `len(captured) == after_three`.

## Exercise 4: Measure warmed calls honestly

The question is: Warm the float32 path, then execute 20 calls and record elapsed time.

The interval excludes the initial capture. The tiny workload and eager backend make any speed conclusion limited; record the measurement without promising an improvement.

```python
import time

compiled(x)
start = time.perf_counter()
for _ in range(20):
    observed = compiled(x)
elapsed = time.perf_counter() - start
assert observed.tolist() == [2.0, 5.0] and elapsed >= 0
```

**Expected:** 20 correct outputs and nonnegative elapsed time.

**Verify:** In a fresh process, the exercise checks confirm `observed.tolist() == [2.0, 5.0]` and `elapsed >= 0`.

## Exercise 5: Inspect actual CPU operations

The question is: Profile one eager call and inspect operation names.

The profiler verifies which tensor operations were observed. Its own overhead means the measured run is not identical to an uninstrumented benchmark.

```python
with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU]) as profile:
    function(x)
operations = {event.key for event in profile.key_averages()}
assert "aten::mul" in operations and "aten::add" in operations
```

**Expected:** aten::mul and aten::add appear.

**Verify:** In a fresh process, the exercise checks confirm `'aten::mul' in operations` and `'aten::add' in operations`.

## Exercise 6: State the backend limitation

The question is: Record graph capture True, optimizing native backend False and GPU benchmark False.

A real Inductor or GPU study needs its prepared compiler/device environment, correctness checks and representative workload. This lesson isolates capture and measurement discipline.

```python
receipt = {
    "graph_capture_checked": True,
    "optimizing_native_backend": False,
    "gpu_benchmark": False,
    "warm_calls": 20,
}
assert (
    receipt["graph_capture_checked"]
    and not receipt["optimizing_native_backend"]
    and not receipt["gpu_benchmark"]
)
```

**Expected:** receipt does not claim universal speedup.

**Verify:** In a fresh process, the exercise checks confirm `receipt['graph_capture_checked']`, `not receipt['optimizing_native_backend']` and `not receipt['gpu_benchmark']`.

## Review after comparison

Repeat exercise 4, Measure warmed calls honestly, with one changed fixture value and predict the difference before running it. Keep your failing attempt at exercise 5, Inspect actual CPU operations, beside the repaired result. A missing framework is not a failing assertion. These solutions use only local fixtures.

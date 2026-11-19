"""torch-031: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Worked example A: Establish an eager oracle
    def function(value):
        return value * value + 1

    x = torch.tensor([1.0, 2.0])
    eager = function(x)
    assert eager.tolist() == [2.0, 5.0]

    # Worked example B: Capture with a transparent backend
    graphs = []

    def backend(graph, example_inputs):
        graphs.append(graph)
        return graph.forward

    compiled = torch.compile(function, backend=backend, fullgraph=True, dynamic=False)
    torch.testing.assert_close(compiled(x), eager, atol=0, rtol=0)
    first = len(graphs)
    assert first >= 1

    # Worked example C: Check signature reuse
    assert compiled(torch.tensor([3.0, 4.0])).tolist() == [10.0, 17.0] and len(graphs) == first
    assert (
        compiled(torch.tensor([1.0, 2.0], dtype=torch.float64)).tolist() == [2.0, 5.0]
        and len(graphs) > first
    )

    # Exercise 4: Measure warmed calls honestly
    import time

    compiled(x)
    start = time.perf_counter()
    for _ in range(20):
        observed = compiled(x)
    elapsed = time.perf_counter() - start
    assert observed.tolist() == [2.0, 5.0] and elapsed >= 0

    # Exercise 5: Inspect actual CPU operations
    with torch.profiler.profile(activities=[torch.profiler.ProfilerActivity.CPU]) as profile:
        function(x)
    operations = {event.key for event in profile.key_averages()}
    assert "aten::mul" in operations and "aten::add" in operations

    # Exercise 6: State the backend limitation
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

    # Exercise 1: Establish a new eager oracle
    def affine(value):
        return 2 * value - 1

    points = torch.tensor([0.0, 3.0])
    assert affine(points).tolist() == [-1.0, 5.0]

    # Exercise 2: Capture the new function
    captured = []

    def counting(graph, example_inputs):
        captured.append(graph)
        return graph.forward

    compiled_affine = torch.compile(affine, backend=counting, fullgraph=True, dynamic=False)
    torch.testing.assert_close(compiled_affine(points), affine(points), atol=0, rtol=0)
    assert len(captured) >= 1

    # Exercise 3: Predict recompilation for a new shape
    before_three = len(captured)
    compiled_affine(torch.tensor([1.0, 2.0, 3.0]))
    after_three = len(captured)
    compiled_affine(torch.tensor([4.0, 5.0, 6.0]))
    assert after_three > before_three and len(captured) == after_three
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

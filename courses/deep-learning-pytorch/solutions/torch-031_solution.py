"""torch-031: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import torch
from torch import nn
from torch.nn import functional as F


def verify():
    # Exercise 1: Establish an eager oracle
    def function(value):
        return value * value + 1

    x = torch.tensor([1.0, 2.0])
    eager = function(x)
    assert eager.tolist() == [2.0, 5.0]

    # Exercise 2: Capture with a transparent backend
    graphs = []

    def backend(graph, example_inputs):
        graphs.append(graph)
        return graph.forward

    compiled = torch.compile(function, backend=backend, fullgraph=True, dynamic=False)
    torch.testing.assert_close(compiled(x), eager, atol=0, rtol=0)
    first = len(graphs)
    assert first >= 1

    # Exercise 3: Check signature reuse
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
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

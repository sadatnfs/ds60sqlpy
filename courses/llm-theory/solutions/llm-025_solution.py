"""llm-025: bounded local reference checks. No network or persistent data writes."""

import numpy as np


def verify():
    # Worked example A: Count attention scores
    b, h = 1, 2
    counts = [b * h * t * t for t in [16, 32]]
    assert counts == [512, 2048]

    # Worked example B: Count raw cache bytes
    cache = [2 * 1 * 1 * 2 * t * 16 * 4 for t in [16, 32]]
    assert cache == [4096, 8192]

    # Exercise 3: Compare element precision
    assert 2 * 1 * 1 * 2 * 32 * 16 * 2 == 4096
    assert 2 * 1 * 1 * 2 * 32 * 16 * 4 == 8192

    # Exercise 4: Scale batch size
    assert 2 * 1 * 3 * 2 * 32 * 16 * 4 == 24576

    # Exercise 5: Preserve total width
    assert 2 * 4 * 32 * 8 * 4 == 2 * 2 * 32 * 16 * 4

    # Exercise 6: State exclusions
    estimate = {
        "raw_kv_bytes": 8192,
        "excludes": ["parameters", "temporary tensors", "allocator overhead"],
        "measured_peak": False,
    }
    assert len(estimate["excludes"]) == 3 and not estimate["measured_peak"]

    # Exercise 1: Count scores for a larger configuration
    scores_big = 2 * 4 * 64 * 64
    assert scores_big == 32768 and scores_big * 4 == 131072

    # Exercise 2: Predict cache growth with depth and context
    cache3 = [2 * 3 * 1 * 2 * t * 16 * 4 for t in [48, 96]]
    assert cache3 == [36864, 73728] and cache3[1] == 2 * cache3[0]
    assert (1 * 2 * 96 * 96) // (1 * 2 * 48 * 48) == 4
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

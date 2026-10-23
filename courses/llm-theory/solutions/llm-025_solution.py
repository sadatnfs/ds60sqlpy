"""llm-025: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Count attention scores
    b,h=1,2; counts=[b*h*t*t for t in [16,32]]
    assert counts==[512,2048]

    # Exercise 2: Count raw cache bytes
    cache=[2*1*1*2*t*16*4 for t in [16,32]]
    assert cache==[4096,8192]

    # Exercise 3: Compare element precision
    assert 2*1*1*2*32*16*2==4096
    assert 2*1*1*2*32*16*4==8192

    # Exercise 4: Scale batch size
    assert 2*1*3*2*32*16*4==24576

    # Exercise 5: Preserve total width
    assert 2*4*32*8*4==2*2*32*16*4

    # Exercise 6: State exclusions
    estimate={'raw_kv_bytes':8192,'excludes':['parameters','temporary tensors','allocator overhead'],'measured_peak':False}
    assert len(estimate['excludes'])==3 and not estimate['measured_peak']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

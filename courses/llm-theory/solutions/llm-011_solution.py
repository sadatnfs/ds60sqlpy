"""llm-011: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Split and rejoin
    x=np.arange(8).reshape(2,4); heads=x.reshape(2,2,2).transpose(1,0,2)
    restored=heads.transpose(1,0,2).reshape(2,4)
    np.testing.assert_array_equal(restored,x); assert heads.shape==(2,2,2)

    # Exercise 2: Calculate a residual
    branch=2*x; residual=x+branch
    np.testing.assert_array_equal(residual,3*x); assert residual.shape==x.shape

    # Exercise 3: Use a tokenwise nonlinear block
    feed=np.maximum(x-2,0)@np.eye(4)
    np.testing.assert_array_equal(feed[0],[0,0,0,1])

    # Exercise 4: Test a prefix
    np.testing.assert_array_equal(np.maximum(x[:1]-2,0)@np.eye(4),feed[:1])

    # Exercise 5: Reject an indivisible width
    width,head_count=5,2
    assert width%head_count!=0

    # Exercise 6: Detect a wrong rejoin
    wrong=heads.reshape(2,4)
    assert not np.array_equal(wrong,x)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

"""tf-033: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf

def predict(values):
    x=np.asarray(values)
    if x.dtype!=np.float32: raise TypeError('float32 dtype required')
    if x.ndim!=2 or x.shape[1]!=2: raise ValueError('shape must be (batch,2)')
    if not 1<=len(x)<=4: raise ValueError('batch must contain 1..4 records')
    if not np.isfinite(x).all(): raise ValueError('finite values required')
    return (tf.constant(x)@tf.constant([[2.],[-1.]])).numpy()[:,0].copy()


def verify():
    # Exercise 1: Predict a valid batch
    x=np.array([[1,2],[3,4]],dtype='float32'); result=predict(x)
    np.testing.assert_array_equal(result,[0,2]); assert result.shape==(2,)

    # Exercise 2: Compare batch independence
    single=np.concatenate([predict(x[i:i+1]) for i in range(2)])
    np.testing.assert_array_equal(single,result)

    # Exercise 3: Reject empty and oversized batches
    for bad in [np.empty((0,2),dtype='float32'),np.zeros((5,2),dtype='float32')]:
        try: predict(bad)
        except ValueError as error: assert 'batch' in str(error)
        else: raise AssertionError('bad batch accepted')

    # Exercise 4: Reject wrong feature structure
    for bad in [np.array([1,2],dtype='float32'),np.zeros((2,3),dtype='float32')]:
        try: predict(bad)
        except ValueError as error: assert 'shape' in str(error)
        else: raise AssertionError('bad shape accepted')

    # Exercise 5: Reject nonfinite values and wrong dtype
    try: predict(np.array([[np.nan,1]],dtype='float32'))
    except ValueError: pass
    else: raise AssertionError('NaN accepted')
    try: predict(np.array([[1,2]],dtype='int64'))
    except TypeError: pass
    else: raise AssertionError('dtype silently coerced')

    # Exercise 6: Preserve the input
    before=x.copy(); answer=predict(x); answer[0]=999
    np.testing.assert_array_equal(x,before)
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

"""tf-015: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Observe batches
    ds=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32')))
    batches=list(ds.batch(2).as_numpy_iterator())
    assert [len(ids) for ids,values in batches]==[2,2,1]

    # Exercise 2: Apply training statistics
    mean=np.mean([1.,2.,3.]); centered=ds.map(lambda i,v:(i,v-tf.cast(mean,tf.float32)))
    values=np.array([float(v) for i,v in centered.as_numpy_iterator()])
    np.testing.assert_array_equal(values,[-1,0,1,2,3])

    # Exercise 3: Retain IDs through mapping
    got=np.concatenate([i for i,v in centered.batch(2).prefetch(1).as_numpy_iterator()])
    np.testing.assert_array_equal(got,np.arange(5))

    # Exercise 4: Compare explicit dropping
    dropped=list(ds.batch(2,drop_remainder=True).as_numpy_iterator())
    assert [len(i) for i,v in dropped]==[2,2]
    assert np.concatenate([i for i,v in dropped]).tolist()==[0,1,2,3]

    # Exercise 5: Recreate a deterministic traversal
    again=tf.data.Dataset.from_tensor_slices((np.arange(5),np.arange(1,6,dtype='float32')))
    a=[(int(i),float(v)) for i,v in ds.as_numpy_iterator()]
    b=[(int(i),float(v)) for i,v in again.as_numpy_iterator()]
    assert a==b==[(0,1.),(1,2.),(2,3.),(3,4.),(4,5.)]

    # Exercise 6: Check paired transformation
    scaled=ds.map(lambda i,v:(i,2*v))
    assert all(float(v)==2*(int(i)+1) for i,v in scaled.as_numpy_iterator())
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

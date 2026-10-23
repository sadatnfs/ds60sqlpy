"""tf-021: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Mark valid positions
    ids=tf.constant([2,3,0]); mask=ids!=0
    assert mask.numpy().tolist()==[True,True,False]
    assert int(tf.reduce_sum(tf.cast(mask,tf.int32)))==2

    # Exercise 2: Normalize masked losses
    losses=tf.constant([np.log(2),np.log(2),100.],dtype=tf.float64)
    mean=tf.reduce_sum(tf.where(mask,losses,0.))/tf.reduce_sum(tf.cast(mask,tf.float64))
    np.testing.assert_allclose(float(mean),np.log(2),atol=1e-12,rtol=0)

    # Exercise 3: Check embedding axes
    table=tf.constant([[0.,0.],[1.,0.],[2.,2.],[3.,-1.]])
    emb=tf.gather(table,ids)
    assert tuple(emb.shape)==(3,2); np.testing.assert_array_equal(emb.numpy()[0],[2,2])

    # Exercise 4: Append padding
    extended=tf.constant([2,3,0,0,0]); m=extended!=0; l=tf.constant([np.log(2),np.log(2),100.,200.,300.],tf.float64)
    v=tf.reduce_sum(tf.where(m,l,0.))/tf.reduce_sum(tf.cast(m,tf.float64))
    np.testing.assert_allclose(float(v),float(mean),atol=1e-12,rtol=0)

    # Exercise 5: Select the last valid state
    states=tf.constant([[2.,2.],[3.,-1.],[99.,99.]])
    valid_states=tf.boolean_mask(states,mask)
    np.testing.assert_array_equal(valid_states[-1].numpy(),[3,-1])

    # Exercise 6: Refuse an empty denominator
    def masked_mean(values,valid):
        values=np.asarray(values); valid=np.asarray(valid,dtype=bool)
        if values.shape!=valid.shape or not valid.any(): raise ValueError('valid targets required')
        return values[valid].mean()
    try: masked_mean([1,2],[False,False])
    except ValueError: pass
    else: raise AssertionError('empty denominator accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

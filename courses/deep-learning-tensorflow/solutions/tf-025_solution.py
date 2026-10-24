"""tf-025: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf




def verify():
    # Exercise 1: Compare similarity measures
    a=np.array([1.,0.]); pos=np.array([1.,1.]); neg=np.array([0.,1.])
    assert (a@pos,a@neg)==(1,0)
    np.testing.assert_allclose([(a@pos)/(np.linalg.norm(a)*np.linalg.norm(pos)),a@neg],[1/np.sqrt(2),0],atol=1e-12,rtol=0)

    # Exercise 2: Scale a candidate
    scaled=10*pos
    assert a@scaled==10
    np.testing.assert_allclose((a@scaled)/(np.linalg.norm(a)*np.linalg.norm(scaled)),1/np.sqrt(2),atol=1e-12,rtol=0)

    # Exercise 3: Calculate a contrastive loss
    loss=tf.nn.sparse_softmax_cross_entropy_with_logits(labels=[0],logits=[[1.,0.]])
    np.testing.assert_allclose(loss.numpy(),[np.log1p(np.exp(-1))],atol=1e-6,rtol=0)

    # Exercise 4: Detect a false negative
    positive_id='doc-a'; negative_id='doc-a'; duplicate=np.array_equal(pos,pos.copy())
    assert duplicate and positive_id==negative_id

    # Exercise 5: Observe temperature
    p1=tf.nn.softmax([1.,0.]).numpy(); p2=tf.nn.softmax(np.array([1.,0.],dtype='float32')/.5).numpy()
    assert p2[0]>p1[0] and int(p1.argmax())==int(p2.argmax())==0

    # Exercise 6: Reject undefined cosine
    def cosine(x,y):
        x,y=np.asarray(x),np.asarray(y); den=np.linalg.norm(x)*np.linalg.norm(y)
        if x.shape!=y.shape or not np.isfinite(den) or den==0: raise ValueError('finite nonzero vectors')
        return float(x@y/den)
    try: cosine([0,0],[1,1])
    except ValueError: pass
    else: raise AssertionError('undefined cosine accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

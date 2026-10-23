"""tf-022: bounded local reference checks. No network or persistent data writes."""

import numpy as np
import tensorflow as tf

def attention(q,k,v):
    q,k,v=(np.asarray(a,dtype=np.float64) for a in (q,k,v))
    if any(a.ndim!=2 for a in (q,k,v)) or not len(q) or q.shape[1]==0: raise ValueError('nonempty matrices required')
    if k.shape!=q.shape or v.shape[0]!=len(q) or not all(np.isfinite(a).all() for a in (q,k,v)): raise ValueError('shape or finite contract')
    q,k,v=(tf.constant(a,tf.float64) for a in (q,k,v))
    scores=q@tf.transpose(k)/tf.sqrt(tf.cast(q.shape[1],tf.float64))
    allowed=tf.linalg.band_part(tf.ones((q.shape[0],q.shape[0]),dtype=tf.bool),-1,0)
    return tf.nn.softmax(tf.where(allowed,scores,tf.constant(-np.inf,tf.float64)),axis=-1)@v


def verify():
    # Exercise 1: Calculate uniform mixtures
    q=np.zeros((3,2)); v=np.array([[2.,0.],[0.,2.],[6.,6.]])
    out=attention(q,q,v).numpy()
    np.testing.assert_allclose(out,[[2,0],[1,1],[8/3,8/3]],atol=1e-6,rtol=0)

    # Exercise 2: Perturb the future
    future=v.copy(); future[2]=[100,200]; changed=attention(q,q,future).numpy()
    np.testing.assert_allclose(changed[:2],out[:2],atol=1e-6,rtol=0)
    np.testing.assert_allclose(changed[2],[34,202/3],atol=1e-6,rtol=0)

    # Exercise 3: Recompute every prefix
    for cut in range(1,4):
        prefix=attention(q[:cut],q[:cut],v[:cut]).numpy()
        np.testing.assert_allclose(prefix,out[:cut],atol=1e-6,rtol=0)

    # Exercise 4: Expose post-softmax masking
    broken=np.ones((3,3))/3*np.tri(3)
    np.testing.assert_allclose(broken.sum(1),[1/3,2/3,1],atol=1e-12,rtol=0)

    # Exercise 5: Use nonuniform scores
    non=np.array([[1.,0.],[0.,1.],[1.,1.]])
    full=attention(non,non,v).numpy()
    for cut in range(1,4): np.testing.assert_allclose(attention(non[:cut],non[:cut],v[:cut]).numpy(),full[:cut],atol=1e-6,rtol=0)

    # Exercise 6: Refuse malformed input
    for args in [(np.empty((0,2)),np.empty((0,2)),np.empty((0,2))),(q,q,v[:2])]:
        try: attention(*args)
        except ValueError: pass
        else: raise AssertionError('bad shape accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

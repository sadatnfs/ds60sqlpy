"""llm-043: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def attention(q,k,v,allowed):
    q,k,v=(np.asarray(value,dtype=np.float64) for value in (q,k,v)); allowed=np.asarray(allowed)
    if any(value.ndim!=2 for value in (q,k,v)) or not len(q) or not len(k) or q.shape[1]==0: raise ValueError('nonempty matrices required')
    if q.shape[1]!=k.shape[1] or k.shape[0]!=v.shape[0] or allowed.shape!=(len(q),len(k)): raise ValueError('attention shape mismatch')
    if allowed.dtype!=np.bool_: raise TypeError('boolean allowed mask required')
    if not allowed.any(1).all() or not all(np.isfinite(value).all() for value in (q,k,v)): raise ValueError('finite legal rows required')
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        scores=q@k.T/np.sqrt(q.shape[1])
    if not np.isfinite(scores[allowed]).all(): raise ValueError('finite computed attention scores required')
    masked=np.where(allowed,scores,-np.inf)
    with np.errstate(over='ignore',under='ignore'):
        mass=np.exp(masked-masked.max(1,keepdims=True))
    weights=mass/mass.sum(1,keepdims=True)
    return weights@v,weights


def verify():
    # Exercise 1: Compare bidirectional and causal mixtures
    q=np.zeros((3,2)); values=np.array([[2.,0.],[0.,2.],[6.,6.]])
    encoder,_=attention(q,q,values,np.ones((3,3),dtype=bool))
    decoder,_=attention(q,q,values,np.tri(3,dtype=bool))
    np.testing.assert_allclose(encoder,np.tile([8/3,8/3],(3,1)),atol=1e-12,rtol=0)
    np.testing.assert_allclose(decoder,[[2,0],[1,1],[8/3,8/3]],atol=1e-12,rtol=0)

    # Exercise 2: Trace rectangular cross-attention
    target_queries=np.zeros((2,2)); source_keys=np.zeros((3,2))
    cross,weights=attention(target_queries,source_keys,values,np.ones((2,3),dtype=bool))
    assert weights.shape==(2,3) and cross.shape==(2,2)
    np.testing.assert_allclose(cross,np.tile([8/3,8/3],(2,1)),atol=1e-12,rtol=0)

    # Exercise 3: Build shifted decoder targets
    target=np.array([5,7,3]); inputs=np.concatenate([[1],target[:-1]]); labels=target.copy(); mask=np.tri(3,dtype=bool)
    np.testing.assert_array_equal(inputs,[1,5,7]); np.testing.assert_array_equal(labels,[5,7,3])
    assert mask[0,0] and not mask[0,1]

    # Exercise 4: Separate masked-token supervision
    original=np.array([2,5,7]); corrupted=original.copy(); corrupted[1]=0; active=np.array([False,True,False])
    np.testing.assert_array_equal(corrupted,[2,0,7]); assert original[active].tolist()==[5]
    assert np.ones((3,3),dtype=bool)[1].all()

    # Exercise 5: Perturb future target values
    changed=values.copy(); changed[2]=[100,200]
    new_encoder,_=attention(q,q,changed,np.ones((3,3),dtype=bool)); new_decoder,_=attention(q,q,changed,np.tri(3,dtype=bool))
    assert not np.allclose(new_encoder[:2],encoder[:2])
    np.testing.assert_allclose(new_decoder[:2],decoder[:2],atol=1e-12,rtol=0)

    # Exercise 6: Combine source padding with cross-attention
    allowed=np.array([[True,True,False],[True,True,False]])
    masked,weights=attention(target_queries,source_keys,values,allowed)
    np.testing.assert_allclose(masked,[[1,1],[1,1]],atol=1e-12,rtol=0)
    np.testing.assert_array_equal(weights[:,2],[0,0])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

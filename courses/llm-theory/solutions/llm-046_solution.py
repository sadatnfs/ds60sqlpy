"""llm-046: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def scaled_scores(q,k):
    if q.ndim!=2 or k.ndim!=2 or q.shape[1]==0 or q.shape[1]!=k.shape[1]: raise ValueError('positive matching head width required')
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        scores=q@k.T/np.sqrt(q.shape[1])
    if not np.isfinite(scores).all(): raise ValueError('finite computed attention scores required')
    return scores
def dense(q,k,v,allowed):
    scores=scaled_scores(q,k); masked=np.where(allowed,scores,-np.inf)
    if not allowed.any(1).all(): raise ValueError('each query requires a legal key')
    mass=np.exp(masked-masked.max(1,keepdims=True)); return mass/mass.sum(1,keepdims=True)@v
def gqa(q,k,v):
    q,k,v=(np.asarray(value,dtype=float) for value in (q,k,v))
    if any(value.ndim!=3 for value in (q,k,v)) or not len(q) or not len(k) or q.shape[1]==0 or q.shape[2]==0 or v.shape[2]==0 or not all(np.isfinite(value).all() for value in (q,k,v)) or len(q)%len(k) or k.shape[:2]!=v.shape[:2] or q.shape[1:]!=k.shape[1:]: raise ValueError('self-attention grouped head contract')
    group=len(q)//len(k); allowed=np.tri(q.shape[1],dtype=bool)
    return np.stack([dense(q[head],k[head//group],v[head//group],allowed) for head in range(len(q))])
def online_row(scores,values,block_size):
    scores=np.asarray(scores,dtype=float); values=np.asarray(values,dtype=float)
    if scores.ndim!=1 or not len(scores) or values.ndim!=2 or len(values)!=len(scores) or type(block_size) is not int or block_size<=0 or not np.isfinite(scores).all() or not np.isfinite(values).all(): raise ValueError('finite nonempty online row and positive block required')
    maximum=-np.inf; denominator=0.; numerator=np.zeros(values.shape[1]); peak=0
    for start in range(0,len(scores),block_size):
        block=scores[start:start+block_size]; local_values=values[start:start+block_size]; peak=max(peak,len(block))
        new_maximum=max(maximum,float(block.max()))
        with np.errstate(over='ignore',invalid='ignore',divide='ignore',under='ignore'):
            scale=0. if maximum==-np.inf else np.exp(maximum-new_maximum)
            mass=np.exp(block-new_maximum)
            numerator=scale*numerator+mass@local_values
            denominator=scale*denominator+mass.sum()
        if not np.isfinite(numerator).all() or not np.isfinite(denominator) or denominator<=0:
            raise ValueError('finite online attention accumulators required')
        maximum=new_maximum
    with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
        output=numerator/denominator
    if not np.isfinite(output).all(): raise ValueError('finite online attention output required')
    return output,peak
def online_attention(q,k,v,allowed,block_size):
    q,k,v=(np.asarray(value,dtype=float) for value in (q,k,v)); allowed=np.asarray(allowed)
    if any(value.ndim!=2 for value in (q,k,v)) or not len(q) or q.shape[1]==0 or q.shape[1]!=k.shape[1] or len(k)!=len(v) or allowed.shape!=(len(q),len(k)) or allowed.dtype!=np.bool_: raise ValueError('attention shapes and boolean mask required')
    if not allowed.any(1).all() or not all(np.isfinite(value).all() for value in (q,k,v)) or type(block_size) is not int or block_size<=0: raise ValueError('finite legal attention rows and positive block required')
    outputs=[]; peak=0
    for row in range(len(q)):
        maximum=-np.inf; denominator=0.; numerator=np.zeros(v.shape[1])
        for start in range(0,len(k),block_size):
            mask=allowed[row,start:start+block_size]
            if not mask.any(): continue
            keys=k[start:start+block_size][mask]; values=v[start:start+block_size][mask]; scores=scaled_scores(q[row:row+1],keys)[0]; peak=max(peak,len(scores))
            new_maximum=max(maximum,float(scores.max()))
            with np.errstate(over='ignore',invalid='ignore',divide='ignore',under='ignore'):
                scale=0. if maximum==-np.inf else np.exp(maximum-new_maximum)
                mass=np.exp(scores-new_maximum)
                numerator=scale*numerator+mass@values
                denominator=scale*denominator+mass.sum()
            if not np.isfinite(numerator).all() or not np.isfinite(denominator) or denominator<=0:
                raise ValueError('finite online attention accumulators required')
            maximum=new_maximum
        with np.errstate(over='ignore',invalid='ignore',divide='ignore'):
            output=numerator/denominator
        if not np.isfinite(output).all(): raise ValueError('finite online attention output required')
        outputs.append(output)
    return np.stack(outputs),peak


def verify():
    # Exercise 1: Count cache andprojection dimensions
    query_heads=4; head_width=2; width=8; time=5
    cache_bytes=[2*1*time*kv_heads*head_width*4 for kv_heads in [4,2,1]]
    parameters=[width*(query_heads*head_width)+2*width*(kv_heads*head_width)+(query_heads*head_width)*width for kv_heads in [4,2,1]]
    assert cache_bytes==[320,160,80] and parameters==[256,192,160]

    # Exercise 2: Verify grouped heads against an equivalent repeated-head oracle
    q=np.arange(24,dtype=float).reshape(4,3,2)/10
    k=np.arange(12,dtype=float).reshape(2,3,2)/7
    v=np.array([[[1.,0.],[0.,2.],[3.,1.]],[[2.,1.],[1.,4.],[5.,2.]]])
    grouped=gqa(q,k,v)
    expanded_k=np.repeat(k,2,axis=0); expanded_v=np.repeat(v,2,axis=0)
    oracle=np.stack([dense(q[h],expanded_k[h],expanded_v[h],np.tri(3,dtype=bool)) for h in range(4)])
    assert grouped.shape==(4,3,2); np.testing.assert_allclose(grouped,oracle,atol=1e-12,rtol=0)

    # Exercise 3: Trace online softmax at extreme scores
    scores=np.array([1000.,999.,998.]); values=np.array([[1.],[3.],[5.]])
    online,peak=online_row(scores,values,2)
    mass=np.exp(np.array([0.,-1.,-2.])); expected=(mass@values)/mass.sum()
    np.testing.assert_allclose(online,expected,atol=1e-12,rtol=0); assert peak==2 and np.isfinite(online).all()

    # Exercise 4: Compare several block sizes under causal masking
    queries=np.array([[1.,0.],[0.,1.],[1.,1.],[-1.,2.],[2.,-1.]])
    keys=np.array([[2.,0.],[1.,1.],[0.,2.],[-1.,1.],[1.,-2.]])
    values=np.arange(10,dtype=float).reshape(5,2); allowed=np.tri(5,dtype=bool); expected=dense(queries,keys,values,allowed)
    for block in [1,2,3,5]:
        output,peak=online_attention(queries,keys,values,allowed,block)
        np.testing.assert_allclose(output,expected,atol=1e-12,rtol=0); assert peak<=block

    # Exercise 5: Preserve a causal prefix under future changes
    changed=values.copy(); changed[3:]+=100
    altered,_=online_attention(queries,keys,changed,allowed,2)
    np.testing.assert_allclose(altered[:3],expected[:3],atol=1e-12,rtol=0)

    # Exercise 6: Reject invalid grouping andempty support
    try: gqa(np.zeros((4,2,2)),np.zeros((3,2,2)),np.zeros((3,2,2)))
    except ValueError: pass
    else: raise AssertionError('indivisible head grouping accepted')
    bad=allowed.copy(); bad[0]=False
    try: online_attention(queries,keys,values,bad,2)
    except ValueError: pass
    else: raise AssertionError('empty attention support accepted')
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

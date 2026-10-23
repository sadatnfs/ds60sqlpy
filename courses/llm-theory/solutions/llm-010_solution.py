"""llm-010: bounded local reference checks. No network or persistent data writes."""

import numpy as np

def attention(q,k,v):
    scores=q@k.T/np.sqrt(q.shape[-1]); mass=np.exp(scores-scores.max(-1,keepdims=True)); return mass/mass.sum(-1,keepdims=True)@v
def layer_norm(x):
    return (x-x.mean(-1,keepdims=True))/np.sqrt(x.var(-1,keepdims=True)+1e-5)


def verify():
    # Exercise 1: Permute content-only attention
    q=np.array([[1.,0.],[0.,1.],[1.,1.]]); v=np.array([[1.,2.],[3.,4.],[5.,6.]]); order=[2,0,1]
    out=attention(q,q,v); changed=attention(q[order],q[order],v[order])
    np.testing.assert_allclose(changed,out[order],atol=1e-12,rtol=0)

    # Exercise 2: Normalize each token
    x=np.array([[1.,3.],[10.,20.]]); changed=x.copy(); changed[1]=[1000,2000]
    np.testing.assert_allclose(layer_norm(x)[0],layer_norm(changed)[0],atol=1e-12,rtol=0)

    # Exercise 3: Expose sequence-wide leakage
    assert not np.allclose((x-x.mean(0))[0],(changed-changed.mean(0))[0])

    # Exercise 4: Attach fixed positions
    pos=np.array([[0.,0.],[1.,0.],[0.,2.]])
    a=attention(q+pos,q+pos,v); b=attention(q[order]+pos,q[order]+pos,v[order])
    assert not np.allclose(b,a[order])

    # Exercise 5: Check feature centering
    np.testing.assert_allclose(layer_norm(x).mean(-1),[0,0],atol=1e-12,rtol=0)

    # Exercise 6: Handle constant tokens
    np.testing.assert_array_equal(layer_norm(np.array([[5.,5.]])),[[0,0]])
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

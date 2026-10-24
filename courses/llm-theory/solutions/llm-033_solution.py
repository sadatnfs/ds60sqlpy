"""llm-033: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Evaluate equal margins
    margin=.1*((-2-(-3))-(-4-(-5))); loss=np.logaddexp(0,-margin)
    assert margin==0; np.testing.assert_allclose(loss,np.log(2),atol=1e-12,rtol=0)

    # Exercise 2: Favor the chosen response
    margin=.5*(2-0); loss=np.logaddexp(0,-margin)
    np.testing.assert_allclose(loss,np.log1p(np.exp(-1)),atol=1e-12,rtol=0)

    # Exercise 3: Reverse the labels
    reversed_margin=-margin; reversed_loss=np.logaddexp(0,-reversed_margin)
    assert reversed_margin==-1 and reversed_loss>loss

    # Exercise 4: Check numeric stability
    values=np.logaddexp(0,-np.array([1000.,-1000.]))
    assert np.isfinite(values).all(); np.testing.assert_allclose(values,[0,1000],atol=1e-12,rtol=0)

    # Exercise 5: Track pair identity
    scores={'r1':-2.,'r2':-4.}; pair={'chosen':'r1','rejected':'r2'}; flipped={'chosen':pair['rejected'],'rejected':pair['chosen']}
    assert flipped['chosen']=='r2' and scores['r1']==-2

    # Exercise 6: Limit the claim
    report={'preference_agreement':True,'factuality_verified':False,'online_rl_executed':False}
    assert not report['factuality_verified'] and not report['online_rl_executed']
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

"""tf-034: bounded local reference checks. No network or persistent data writes."""

import numpy as np




def verify():
    # Exercise 1: Count errors by group
    rows=[('a','A',1,1),('b','A',1,0),('c','B',0,0)]
    report={g:(sum(t!=p for i,k,t,p in rows if k==g),sum(k==g for i,k,t,p in rows)) for g in ['A','B']}
    assert report=={'A':(1,2),'B':(0,1)}

    # Exercise 2: Expose duplicate confidence
    repeated=rows+[rows[-1]]*5
    assert len(repeated)==8 and len({r[0] for r in repeated})==3

    # Exercise 3: Evaluate fixed perturbations
    base=1.; shifts=[-.1,-.9,-1.1]; pred=[int(base+s>=0) for s in shifts]
    assert pred==[1,1,0]

    # Exercise 4: Keep severities separate
    severity=['minor']*9+['severe']; passed=[True]*9+[False]
    assert sum(passed)/len(passed)==.9
    assert sum(s=='severe' and not p for s,p in zip(severity,passed))==1

    # Exercise 5: Write bounded claims
    card={'evaluation_units':3,'intended_use':'synthetic teaching','untested':['future population','private training data'],'privacy_guarantee':False}
    assert card['evaluation_units']==3 and 'future population' in card['untested'] and card['privacy_guarantee'] is False

    # Exercise 6: Reject an empty group rate
    def rate(errors,count): return None if count==0 else errors/count
    assert rate(0,0) is None and rate(0,1)==0
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

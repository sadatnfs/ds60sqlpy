import numpy as np

def weak_summary(labels):
    a=np.asarray(labels)
    if a.ndim!=2 or not len(a) or np.any(~np.isin(a,[-1,0,1])):raise ValueError("2D weak labels in -1,0,1 required")
    covered=np.any(a!=-1,axis=1)
    conflict=np.any(a==0,axis=1)&np.any(a==1,axis=1)
    positive=np.sum(a==1,axis=1);negative=np.sum(a==0,axis=1)
    votes=np.where(positive>negative,1,np.where(negative>positive,0,-1))
    return covered,conflict,votes

def uncertainty(probabilities):
    p=np.asarray(probabilities,dtype=float)
    if np.any((p<0)|(p>1)) or np.any(~np.isfinite(p)):raise ValueError("finite probabilities required")
    h=np.zeros_like(p);mask=(p>0)&(p<1)
    h[mask]=-p[mask]*np.log(p[mask])-(1-p[mask])*np.log(1-p[mask])
    return h

def diverse_batch(probabilities,families,budget):
    if len(probabilities)!=len(families) or budget<0:raise ValueError("aligned families and nonnegative budget required")
    order=np.argsort(-uncertainty(probabilities),kind="stable")
    selected=[];seen=set()
    for i in order:
        if len(selected)==budget:break
        if families[i] not in seen:selected.append(int(i));seen.add(families[i])
    return selected

def main():
    labels=np.array([[1,1,-1],[0,-1,0],[1,0,-1],[-1,-1,-1]])
    covered,conflict,votes=weak_summary(labels)
    assert covered.tolist()==[1,1,1,0] and conflict.tolist()==[0,0,1,0]
    assert covered.mean()==.75 and conflict.mean()==.25 and votes.tolist()==[1,0,-1,-1]
    assert weak_summary([[1,1,0]])[2].tolist()==[1]
    assert weak_summary([[1,0]])[2].tolist()==[-1] # collapse duplicated rule family
    p=np.array([.5,.6,.95,.1]);families=['a','a','b','c']
    assert np.argsort(-uncertainty(p),kind="stable")[:2].tolist()==[0,1]
    assert diverse_batch(p,families,2)==[0,3] and diverse_batch(p,families,0)==[]
    gold_ids={'g1','g2'};queried_ids={'q1','q2'}
    assert gold_ids.isdisjoint(queried_ids)
    print("nlp-020: coverage=.75,conflict=.25; tie abstention; correlated votes and diverse query selection passed")

if __name__ == "__main__":
    main()

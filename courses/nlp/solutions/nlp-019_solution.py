import numpy as np
from sklearn.metrics import cohen_kappa_score

def binary_agreement(a,b):
    a=np.asarray(a);b=np.asarray(b)
    if a.shape!=b.shape or a.ndim!=1 or not a.size or np.any((a!=0)&(a!=1)) or np.any((b!=0)&(b!=1)):
        raise ValueError("equal nonempty binary label arrays required")
    observed=float(np.mean(a==b))
    expected=float(a.mean()*b.mean()+(1-a.mean())*(1-b.mean()))
    return observed,None if expected==1 else (observed-expected)/(1-expected)

def entropy(probability):
    p=np.asarray(probability,dtype=float)
    if np.any((p<0)|(p>1)):raise ValueError("probabilities required")
    out=np.zeros_like(p);mask=(p>0)&(p<1)
    out[mask]=-p[mask]*np.log(p[mask])-(1-p[mask])*np.log(1-p[mask])
    return out

def main():
    a=np.array([1,1,0,0,1,0]);b=np.array([1,0,0,0,1,1])
    observed,kappa=binary_agreement(a,b)
    assert np.isclose(observed,2/3) and np.isclose(kappa,1/3)
    assert np.isclose(kappa,cohen_kappa_score(a,b))
    first=np.array([1]*99+[0]);second=np.array([1]*98+[0,1])
    high,k=binary_agreement(first,second)
    assert high==.98 and k<0
    ratings=np.array([[1,1,0],[1,1,1],[0,0,0]])
    soft=ratings.mean(axis=1)
    assert np.allclose(soft,[2/3,1,0]) and entropy(soft)[0]>0 and np.all(entropy(soft)[1:]==0)
    original=tuple(int(x) for x in ratings[0])
    adjudication={"item_id":"a","original_ratings":original,"final_label":1,"reason":"rubric criterion C with quoted evidence"}
    assert adjudication["original_ratings"]==(1,1,0) and len(adjudication["reason"])>0
    assert binary_agreement([1,1],[1,1])==(1.,None)
    print("nlp-019: manual/library kappa; prevalence counterexample; soft labels and preserved adjudication passed")

if __name__ == "__main__":
    main()

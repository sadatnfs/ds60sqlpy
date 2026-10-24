import itertools
import numpy as np

def logs(values):
    values=np.asarray(values,dtype=float)
    if np.any(~np.isfinite(values)) or np.any((values<0)|(values>1)):
        raise ValueError("probabilities must be finite and within [0,1]")
    result=np.full(values.shape,-np.inf)
    np.log(values,out=result,where=values>0)
    return result

def viterbi(start,transition,emission):
    start=np.asarray(start,dtype=float);transition=np.asarray(transition,dtype=float)
    emission=np.asarray(emission,dtype=float)
    k=len(start)
    if start.ndim!=1 or transition.shape!=(k,k) or emission.ndim!=2 or emission.shape[1]!=k:
        raise ValueError("incompatible state/sequence shapes")
    if not np.isclose(start.sum(),1) or not np.allclose(transition.sum(axis=1),1):
        raise ValueError("start and transition distributions must normalize")
    ls,lt,le=logs(start),logs(transition),logs(emission)
    if len(emission)==0:return [],0.
    dp=ls+le[0];back=[]
    for t in range(1,len(emission)):
        candidates=dp[:,None]+lt
        previous=np.argmax(candidates,axis=0)
        dp=candidates[previous,np.arange(k)]+le[t]
        back.append(previous)
    state=int(np.argmax(dp));score=float(dp[state])
    if not np.isfinite(score):raise ValueError("no legal nonzero-probability path")
    path=[state]
    for previous in reversed(back):path.append(int(previous[path[-1]]))
    return list(reversed(path)),score

def bio_valid(tags):
    previous="O"
    for tag in tags:
        if tag!="O" and (len(tag)<3 or tag[:2] not in {"B-","I-"}):return False
        if tag.startswith("I-") and previous not in {"B-"+tag[2:],"I-"+tag[2:]}:return False
        previous=tag
    return True

def main():
    start=np.array([.6,.4]);transition=np.array([[.7,.3],[.4,.6]])
    emission=np.array([[.6,.1],[.2,.7]])
    path,score=viterbi(start,transition,emission)
    assert path==[0,1] and np.isclose(np.exp(score),.0756)
    brute=[]
    for candidate in itertools.product(range(2),repeat=2):
        value=start[candidate[0]]*emission[0,candidate[0]]*transition[candidate[0],candidate[1]]*emission[1,candidate[1]]
        brute.append((value,candidate))
    assert max(brute)[1]==tuple(path)
    persistent=np.array([[.99,.01],[.01,.99]])
    second=viterbi([.5,.5],persistent,[[.6,.4],[.2,.7]])
    assert second[0]==[1,1] and np.isclose(np.exp(second[1]),.1386)
    assert viterbi(start,transition,np.empty((0,2)))==([],0.)
    assert viterbi([.5,.5],[[.5,.5],[.5,.5]],[[1.,1.],[1.,1.]])[0]==[0,0]
    try:viterbi(start,transition,[[0.,0.]])
    except ValueError:pass
    else:raise AssertionError("impossible path accepted")
    assert bio_valid(["B-ORG","I-ORG","O"])
    assert not bio_valid(["I-ORG","O"]) and not bio_valid(["B-PER","I-ORG"])
    gold=["B-ORG","I-ORG","O"];pred=["B-ORG","O","O"]
    assert sum(a==b for a,b in zip(gold,pred))/len(gold)==2/3
    print("nlp-010: best paths [0,1]/[1,1]; probabilities .0756/.1386; BIO boundaries passed")

if __name__ == "__main__":
    main()

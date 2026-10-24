import numpy as np
from scipy.special import expit,logsumexp

EMBED={"bank":np.array([1.,0.]),"river":np.array([0.,1.]),"money":np.array([0.,-1.])}

def encode(values,valid):
    x=np.asarray(values,dtype=float);mask=np.asarray(valid,dtype=bool)
    if x.ndim!=2 or mask.shape!=(len(x),) or not mask.any():raise ValueError("valid positions required")
    scores=x@x.T/np.sqrt(x.shape[1])
    scores=np.where(mask[None,:],scores,-np.inf)
    weights=np.exp(scores-logsumexp(scores,axis=1,keepdims=True))
    output=weights@x
    output[~mask]=0.
    return output,weights

def pooled(tokens):
    x=np.array([EMBED[token] for token in tokens]);h,_=encode(x,np.ones(len(x),dtype=bool))
    return h.mean(axis=0)

def tag_loss(logits,labels):
    logits=np.asarray(logits,dtype=float);labels=np.asarray(labels,dtype=int)
    valid=labels!=-100
    if logits.ndim!=2 or labels.shape!=(len(logits),) or not valid.any():raise ValueError("supervised positions required")
    if np.any((labels[valid]<0)|(labels[valid]>=logits.shape[1])):raise ValueError("invalid label")
    chosen=logits[valid];target=labels[valid]
    return float(np.mean(logsumexp(chosen,axis=1)-chosen[np.arange(len(chosen)),target]))

def main():
    river=np.array([EMBED["bank"],EMBED["river"]]);money=np.array([EMBED["bank"],EMBED["money"]])
    hr,wr=encode(river,[1,1]);hm,_=encode(money,[1,1])
    assert hr[0,1]>0 and hm[0,1]<0 and not np.allclose(hr[0],hm[0])
    assert np.allclose(wr.sum(axis=1),1.)
    padded=np.vstack([river,[99.,99.]])
    hp,wp=encode(padded,[1,1,0])
    assert np.allclose(hp[:2],hr) and np.allclose(wp[:2,2],0.) and np.all(hp[2]==0)
    data=np.array([pooled(tokens) for tokens in [["bank","river"],["bank","money"],["river","bank"],["money","bank"]]])
    y=np.array([0.,1.,0.,1.]);w=np.zeros(2);b=0.
    before=float(np.mean(np.logaddexp(0.,data@w+b)-y*(data@w+b)))
    for _ in range(400):
        error=expit(data@w+b)-y
        w-=.3*(data.T@error/len(y));b-=.3*error.mean()
    after=float(np.mean(np.logaddexp(0.,data@w+b)-y*(data@w+b)))
    assert after<.1 and after<before and ((data@w+b)>=0).astype(int).tolist()==[0,1,0,1]
    logits=np.array([[2.,0.],[99.,-99.],[0.,2.],[-99.,99.]])
    labels=np.array([0,-100,1,-100])
    loss=tag_loss(logits,labels);changed=logits.copy();changed[[1,3]]*=100
    assert np.isclose(loss,np.log1p(np.exp(-2))) and np.isclose(tag_loss(changed,labels),loss)
    for operation in [lambda: encode([[1.,0.]],[False]),lambda: tag_loss([[1.,0.]],[-100])]:
        try:operation()
        except ValueError:pass
        else:raise AssertionError("absent supervision was accepted")
    print("nlp-015: contextual bank states, padding invariance, actual tiny head training and masked tagging loss passed")

if __name__ == "__main__":
    main()

import math
import numpy as np
from scipy.special import logsumexp

TRANSITIONS={"<BOS>":{"tea":.6,"coffee":.4},"tea":{"<EOS>":.5,"sugar":.5},"coffee":{"<EOS>":1.},"sugar":{"<EOS>":1.}}

def cross_attention(query,keys,values,valid):
    q=np.asarray(query,dtype=float);k=np.asarray(keys,dtype=float);v=np.asarray(values,dtype=float);mask=np.asarray(valid,dtype=bool)
    if q.ndim!=2 or k.ndim!=2 or v.ndim!=2 or q.shape[1]!=k.shape[1] or len(k)!=len(v) or mask.shape!=(len(k),) or not mask.any():raise ValueError("compatible nonempty source required")
    score=q@k.T/np.sqrt(k.shape[1]);score=np.where(mask[None,:],score,-np.inf)
    weights=np.exp(score-logsumexp(score,axis=1,keepdims=True))
    return weights@v,weights

def shifted_targets(tokens):
    if any(token in {"<BOS>","<EOS>"} for token in tokens):raise ValueError("raw target contains markers")
    return ["<BOS>",*tokens],[*tokens,"<EOS>"]

def beam_search(width,max_steps=3):
    if width<1 or max_steps<1:raise ValueError("positive search budget required")
    beam=[(0.,())]
    for _ in range(max_steps):
        candidates=[]
        for score,path in beam:
            if path and path[-1]=="<EOS>":candidates.append((score,path));continue
            last=path[-1] if path else "<BOS>"
            for token,p in TRANSITIONS[last].items():candidates.append((score+math.log(p),path+(token,)))
        beam=sorted(candidates,key=lambda item:(-item[0],item[1]))[:width]
    completed=[item for item in beam if item[1] and item[1][-1]=="<EOS>"]
    if not completed:raise ValueError("no completed sequence within budget")
    return completed[0]

def extractive_summary(sentences,query):
    words=set(query.lower().split())
    if not sentences:return None
    scores=[len(words & set(sentence.lower().replace(".","").split())) for sentence in sentences]
    best=max(range(len(sentences)),key=lambda i:(scores[i],-i))
    return None if scores[best]==0 else (best,sentences[best])

def main():
    decoder,targets=shifted_targets(["repair"])
    assert decoder==["<BOS>","repair"] and targets==["repair","<EOS>"]
    assert shifted_targets([])==(["<BOS>"],["<EOS>"])
    out,weights=cross_attention([[1.,0.]],[[1.,0.],[0.,1.]],[[10.,0.],[0.,20.]],[1,1])
    p=1/(1+np.exp(-1/np.sqrt(2)))
    assert np.allclose(out,[[10*p,20*(1-p)]]) and np.allclose(weights.sum(axis=1),1.)
    masked,_=cross_attention([[1.,0.]],[[1.,0.],[0.,1.]],[[10.,0.],[0.,20.]],[1,0])
    assert np.allclose(masked,[[10.,0.]])
    greedy=beam_search(1);beam=beam_search(2)
    assert greedy[1]==("tea","<EOS>") and math.isclose(math.exp(greedy[0]),.3)
    assert beam[1]==("coffee","<EOS>") and math.isclose(math.exp(beam[0]),.4)
    sentences=["The service is unavailable.","A repair is scheduled."]
    summary=extractive_summary(sentences,"service")
    assert summary==(0,sentences[0]) and extractive_summary(sentences,"refund") is None
    print("nlp-016: shifted targets, source attention, greedy/beam .3/.4 and extractive provenance checks passed")

if __name__ == "__main__":
    main()

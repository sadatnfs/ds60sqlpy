from collections import Counter,defaultdict
import math

TRAIN=[["we","like","tea"],["we","like","coffee"],["they","like","tea"]]
BOS="<BOS>";EOS="<EOS>";UNK="<UNK>"

def fit_bigram(documents,alpha=1.):
    if alpha<=0:raise ValueError("positive smoothing required")
    words={word for doc in documents for word in doc}
    if words & {BOS,EOS,UNK}:raise ValueError("reserved marker in raw input")
    vocabulary=tuple(sorted(words|{EOS,UNK}));counts=defaultdict(Counter)
    for doc in documents:
        sequence=[BOS,*doc,EOS]
        for left,right in zip(sequence,sequence[1:]):counts[left][right]+=1
    return vocabulary,dict(counts),alpha

def probability(model,context,word):
    vocabulary,counts,alpha=model
    if word==BOS:raise ValueError("BOS is not a prediction target")
    context=context if context==BOS or context in vocabulary else UNK
    word=word if word in vocabulary else UNK
    row=counts.get(context,{})
    return (row.get(word,0)+alpha)/(sum(row.values())+alpha*len(vocabulary))

def score(model,tokens):
    if any(token in {BOS,EOS,UNK} for token in tokens):raise ValueError("raw tokens contain markers")
    sequence=[BOS,*tokens,EOS]
    logp=sum(math.log(probability(model,left,right)) for left,right in zip(sequence,sequence[1:]))
    events=len(tokens)+1
    return logp,math.exp(-logp/events),events

def main():
    model=fit_bigram(TRAIN);vocab=model[0]
    assert len(vocab)==7 and BOS not in vocab and {EOS,UNK}<=set(vocab)
    values=[probability(model,BOS,"we"),probability(model,"we","like"),probability(model,"like","tea"),probability(model,"tea",EOS)]
    assert all(math.isclose(a,b) for a,b in zip(values,[.3,1/3,.3,1/3]))
    logp,ppl,events=score(model,["we","like","tea"])
    assert math.isclose(math.exp(logp),.01) and math.isclose(ppl,math.sqrt(10)) and events==4
    for context in [BOS,"we","like",UNK]:assert math.isclose(sum(probability(model,context,w) for w in vocab),1.)
    snapshot=(model[0],repr(model[1]))
    unknown=score(model,["we","like","cocoa"])
    assert math.isfinite(unknown[0]) and "cocoa" not in model[0] and snapshot==(model[0],repr(model[1]))
    assert score(model,[])[2]==1 and math.isclose(score(model,[])[1],10.)
    try:probability(model,BOS,BOS)
    except ValueError:pass
    else:raise AssertionError("BOS predicted")
    print("nlp-006: V=7; joint=.01; four-event perplexity=sqrt(10); OOV and EOS checks passed")

if __name__ == "__main__":
    main()

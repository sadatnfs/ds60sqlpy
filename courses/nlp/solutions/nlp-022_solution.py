from collections import Counter,defaultdict
import math

DOCS={"d0":"router reset","d1":"router router reset guide","d2":"payment failed"}

def build_index(documents):
    tokens={key:text.lower().split() for key,text in documents.items()}
    inverted=defaultdict(set)
    for key,words in tokens.items():
        for word in set(words):inverted[word].add(key)
    return tokens,dict(inverted)

def bm25(documents,query,k1=1.2,b=.75):
    if not documents or k1<=0 or not 0<=b<=1:raise ValueError("nonempty corpus and valid BM25 settings required")
    tokens,index=build_index(documents);n=len(tokens);average=sum(map(len,tokens.values()))/n
    if average==0:return {key:0. for key in tokens}
    terms=set(query.lower().split());result={}
    for key,words in tokens.items():
        counts=Counter(words);score=0.
        for term in terms:
            tf=counts[term]
            if not tf:continue
            df=len(index.get(term,set()));idf=math.log(1+(n-df+.5)/(df+.5))
            score+=idf*tf*(k1+1)/(tf+k1*(1-b+b*len(words)/average))
        result[key]=score
    return result

def rrf(rankings,k=60):
    if k<0:raise ValueError("nonnegative fusion constant required")
    result=defaultdict(float)
    for ranking in rankings:
        if len(set(ranking))!=len(ranking):raise ValueError("duplicate ID in ranking")
        for rank,key in enumerate(ranking,1):result[key]+=1/(k+rank)
    return sorted(result,key=lambda key:(-result[key],key)),dict(result)

def ndcg(order,relevance):
    def dcg(values):return sum((2**value-1)/math.log2(rank+1) for rank,value in enumerate(values,1))
    actual=dcg([relevance.get(key,0) for key in order]);ideal=dcg(sorted(relevance.values(),reverse=True)[:len(order)])
    return actual/ideal if ideal else 0.

def main():
    tokens,index=build_index(DOCS)
    assert index['router']=={'d0','d1'}
    score=bm25(DOCS,"router reset")
    a=math.log(1+(3-2+.5)/(2+.5));expected=2*a*2.2/(1+1.2*(.25+.75*2/(8/3)))
    assert math.isclose(score['d0'],expected) and score['d0']>score['d1']>score['d2']==0
    assert all(value==0 for value in bm25(DOCS,"unseen").values())
    order,fused=rrf([['a','b','c'],['b','c','a']])
    assert order[0]=='b' and math.isclose(fused['b'],1/62+1/61)
    relevance={'d0':3,'d1':2,'d2':0};ranking=['d2','d0','d1']
    assert math.isclose(ndcg(ranking,relevance),(7/math.log2(3)+3/2)/(7+3/math.log2(3)))
    reciprocal=1/next(i for i,key in enumerate(ranking,1) if relevance[key]>0)
    assert reciprocal==.5
    permitted={key:text for key,text in DOCS.items() if key in {'d0'}}
    assert set(bm25(permitted,"router"))=={'d0'}
    print("nlp-022: inverted index, hand-checked BM25, rank fusion, nDCG/MRR and pre-retrieval filtering passed")

if __name__ == "__main__":
    main()

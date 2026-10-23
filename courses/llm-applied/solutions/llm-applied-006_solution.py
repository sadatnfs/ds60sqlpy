"""llm-applied-006: bounded local reference checks. No network or persistent data writes."""

import math,re
from collections import Counter

def tokens(text): return re.findall(r'[a-z0-9]+',text.lower())
def bm25(query,documents,k1=1.2,b=.75):
    if not documents: return []
    bags={key:Counter(tokens(text)) for key,text in documents.items()}; lengths={key:sum(v.values()) for key,v in bags.items()}
    average=sum(lengths.values())/len(lengths); terms=set(tokens(query)); scored=[]
    for key,bag in bags.items():
        score=0.
        for term in terms:
            tf=bag[term]
            if not tf: continue
            df=sum(term in other for other in bags.values()); idf=math.log(1+(len(bags)-df+.5)/(df+.5))
            score+=idf*tf*(k1+1)/(tf+k1*(1-b+b*lengths[key]/average))
        scored.append((key,score))
    return sorted(scored,key=lambda row:(-row[1],row[0]))


def verify():
    # Exercise 1: Rank a discriminating term
    docs={'a':'account randomization','b':'visit counts','c':'account outcomes'}; scores=bm25('randomization',docs)
    assert scores[0][0]=='a' and scores[0][1]>0 and all(score==0 for _,score in scores[1:])

    # Exercise 2: Inspect term rarity
    rare=math.log(1+(3-1+.5)/(1+.5)); common=math.log(1+(3-2+.5)/(2+.5))
    assert rare>common>0

    # Exercise 3: Verify saturation
    k1=1.2; contribution=lambda tf:tf*(k1+1)/(tf+k1)
    a,b,c=[contribution(n) for n in [1,2,10]]
    assert a<b<c and c<10*a

    # Exercise 4: Expose a synonym miss
    assert bm25('purchase',{'d':'buy'})==[('d',0.0)]

    # Exercise 5: Make ties deterministic
    assert [key for key,score in bm25('missing',{'z':'x','a':'y','b':'z'})]==['a','b','z']

    # Exercise 6: Check corpus edge cases
    assert bm25('x',{})==[]
    assert bm25('x',{'empty':''})==[('empty',0.0)]
    return {"checks": 6, "status": "passed"}


if __name__ == "__main__":
    print(verify())

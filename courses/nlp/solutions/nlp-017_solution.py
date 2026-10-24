from collections import Counter
import math

def ngrams(tokens,n):
    if n<1:raise ValueError("positive n required")
    return Counter(tuple(tokens[i:i+n]) for i in range(max(0,len(tokens)-n+1)))

def clipped_precision(candidate,reference,n=1):
    c=ngrams(candidate,n);r=ngrams(reference,n);total=sum(c.values())
    return sum(min(count,r[gram]) for gram,count in c.items())/total if total else 0.

def teaching_bleu(candidate,reference,max_order=2):
    if not candidate:return 0.
    p=[clipped_precision(candidate,reference,n) for n in range(1,max_order+1)]
    if any(value==0 for value in p):return 0.
    bp=min(1.,math.exp(1-len(reference)/len(candidate)))
    return bp*math.exp(sum(math.log(value) for value in p)/max_order)

def lcs_length(a,b):
    table=[[0]*(len(b)+1) for _ in range(len(a)+1)]
    for i,x in enumerate(a,1):
        for j,y in enumerate(b,1):table[i][j]=table[i-1][j-1]+1 if x==y else max(table[i-1][j],table[i][j-1])
    return table[-1][-1]

def main():
    assert clipped_precision("the the the the".split(),"the cat".split())==.25
    assert math.isclose(teaching_bleu("the cat".split(),"the cat sat".split()),math.exp(-.5))
    assert teaching_bleu([],"the cat".split())==0.
    reference="service is not ready".split();candidate="service is ready".split()
    lcs=lcs_length(candidate,reference);p=lcs/len(candidate);r=lcs/len(reference)
    assert lcs==3 and p==1 and r==.75 and math.isclose(2*p*r/(p+r),6/7)
    assert "not" in reference and "not" not in candidate # human-readable contradiction case, not a general entailment detector
    cases=[{"family":"a","supported":True},{"family":"a","supported":False},{"family":"b","supported":False}]
    family_rates=[sum(c['supported'] for c in cases if c['family']==f)/sum(c['family']==f for c in cases) for f in ['a','b']]
    assert family_rates==[.5,0.] and sum(family_rates)/2==.25
    assert lcs_length([],reference)==0
    print("nlp-017: clipped precision=.25; brevity penalty; high-overlap contradiction; family aggregation passed")

if __name__ == "__main__":
    main()

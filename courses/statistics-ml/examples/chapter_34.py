import numpy as np

def wilson_interval(successes,total,z=1.96):
    p=successes/total;denominator=1+z*z/total
    center=(p+z*z/(2*total))/denominator
    half=z*np.sqrt(p*(1-p)/total+z*z/(4*total*total))/denominator
    return center-half,center+half

def repeated_reliability():
    outcomes=np.array([1,1,1,0,1,1,0,1,1,1])
    low,high=wilson_interval(int(outcomes.sum()),len(outcomes))
    assert outcomes.mean()==.8 and low<.8<high and low>.45 and high<.96
    print("Independent-case success rate and Wilson interval:",outcomes.mean(),low,high)

def retrieval_and_claim_support():
    needed={"policy-v2","runtime-17"};retrieved=["policy-v2","glossary-v1"]
    recall=len(needed & set(retrieved))/len(needed)
    # Human-supplied support labels for three atomic claims, not an automatic entailment model.
    claim_support=np.array([True,True,False]);has_citation=np.array([True,True,True])
    supported_citations=np.sum(claim_support & has_citation)/np.sum(has_citation)
    assert recall==.5 and np.isclose(supported_citations,2/3)
    assert has_citation.mean()==1 and supported_citations<1
    print("Evidence recall:",recall,"citations present:",has_citation.mean(),"supported:",supported_citations)

def paired_and_agreement():
    first=np.array([1,1,0,0,1,0]);second=np.array([1,0,0,0,1,1])
    agreement=np.mean(first==second)
    expected=first.mean()*second.mean()+(1-first.mean())*(1-second.mean())
    kappa=(agreement-expected)/(1-expected)
    assert np.isclose(agreement,2/3) and np.isclose(kappa,1/3)
    a=np.array([1,1,0,0,1]);b=np.array([1,1,1,0,1])
    assert np.sum((b==1)&(a==0))==1 and np.sum((a==1)&(b==0))==0
    print("Raw agreement, kappa:",agreement,kappa,"paired B-only success:",1)

def pareto_tradeoff():
    # Higher quality, lower cost and latency are preferred.
    systems=[("A",.80,1.,2.),("B",.85,2.,3.),("C",.78,2.,4.)]
    efficient=[]
    for name,q,c,l in systems:
        dominated=any(q2>=q and c2<=c and l2<=l and (q2>q or c2<c or l2<l)
                      for name2,q2,c2,l2 in systems if name2!=name)
        if not dominated:efficient.append(name)
    assert efficient==["A","B"]
    print("Pareto-efficient alternatives:",efficient)

def main():
    repeated_reliability();retrieval_and_claim_support();paired_and_agreement();pareto_tradeoff()

if __name__ == "__main__":
    main()

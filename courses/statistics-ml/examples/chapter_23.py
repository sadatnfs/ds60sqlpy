import numpy as np

def conformal_rank():
    scores=np.arange(1.,20.)
    alpha=.1;n=len(scores);k=int(np.ceil((n+1)*(1-alpha)))
    q=np.sort(scores)[k-1] if k<=n else np.inf
    assert k==18 and q==18
    possible_new_scores=np.arange(.5,20.,1.)
    rank_coverage=np.mean(possible_new_scores<=q)
    assert rank_coverage==.9
    print("Calibration n/k/q:",n,k,q,"coverage over illustrative equally likely ranks:",rank_coverage)

def shift_weighting():
    source=np.array([.8,.2]);target=np.array([.2,.8]);outcome=np.array([1.,9.])
    weights=target/source
    target_mean=np.sum(source*weights*outcome)
    assert np.isclose(target_mean,target@outcome) and np.isclose(target_mean,7.4)
    assert np.isclose(source@outcome,2.6)
    print("Source mean:",source@outcome,"target reweighted mean:",target_mean,"ratios:",weights)

def selective_prediction():
    confidence=np.array([.55,.6,.8,.95]);error=np.array([1.,1.,0.,0.])
    accepted=confidence>=.8
    coverage=accepted.mean();risk=error[accepted].mean()
    assert coverage==.5 and risk==0 and error.mean()==.5
    print("Accepted fraction:",coverage,"accepted empirical error:",risk,"all-case error:",error.mean())

def main():
    conformal_rank();shift_weighting();selective_prediction()

if __name__ == "__main__":
    main()

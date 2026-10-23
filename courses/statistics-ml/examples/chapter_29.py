import numpy as np

def robust_score():
    reference=np.array([9.,10.,10.,11.,12.])
    median=np.median(reference);mad=np.median(np.abs(reference-median))
    score=(30-median)/(1.4826*mad)
    assert median==10 and mad==1 and score>13
    print("Median, MAD, score for 30:",median,mad,score)

def cumulative_shift():
    x=np.array([0.,0.,0.,1.,1.,1.,1.]);state=0.;trace=[]
    for value in x:
        state=max(0.,state+value-.25);trace.append(state)
    alarms=np.flatnonzero(np.array(trace)>2.)
    assert trace==[0.,0.,0.,.75,1.5,2.25,3.]
    assert alarms[0]==5
    print("CUSUM trace:",trace,"first alarm index:",alarms[0])

def alert_precision():
    prevalence=.001;sensitivity=.9;false_positive=.01
    ppv=prevalence*sensitivity/(prevalence*sensitivity+(1-prevalence)*false_positive)
    assert np.isclose(ppv,.0009/.01089) and ppv<.1
    print("Alert precision at rare prevalence:",ppv)

def main():
    robust_score();cumulative_shift();alert_precision()

if __name__ == "__main__":
    main()

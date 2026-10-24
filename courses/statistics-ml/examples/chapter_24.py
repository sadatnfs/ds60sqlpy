import numpy as np

def exact_shapley_game():
    empty,a,b,ab=0.,1.,2.,7.
    phi_a=.5*((a-empty)+(ab-b))
    phi_b=.5*((b-empty)+(ab-a))
    assert phi_a==3 and phi_b==4 and phi_a+phi_b==ab-empty
    print("Specified two-feature game attributions:",phi_a,phi_b)

def fairness_conditioning():
    # Rows are groups; columns are TP, FN, FP, TN.
    counts=np.array([[16.,4.,8.,72.],[64.,16.,2.,18.]])
    tp,fn,fp,tn=counts.T
    tpr=tp/(tp+fn);fpr=fp/(fp+tn)
    positive_rate=(tp+fp)/counts.sum(axis=1)
    precision=tp/(tp+fp)
    assert np.allclose(tpr,[.8,.8]) and np.allclose(fpr,[.1,.1])
    assert not np.isclose(positive_rate[0],positive_rate[1])
    assert not np.isclose(precision[0],precision[1])
    print("Equalized odds rates:",tpr,fpr,"positive rates:",positive_rate,"precision:",precision)

def adversarial_linear_margin():
    weights=np.array([2.,-1.]);x=np.array([1.,1.]);epsilon=.4
    delta=-epsilon*np.sign(weights)
    before=weights@x;after=weights@(x+delta)
    assert before==1 and np.isclose(after,-.2)
    assert np.isclose(before-after,epsilon*np.abs(weights).sum())
    print("Linear margin before/after bounded perturbation:",before,after)

def main():
    exact_shapley_game();fairness_conditioning();adversarial_linear_margin()

if __name__ == "__main__":
    main()

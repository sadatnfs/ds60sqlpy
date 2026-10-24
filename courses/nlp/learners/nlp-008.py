import numpy as np
X=np.array([[2.,1.],[1.,0.],[0.,2.],[0.,1.]])
Y=np.array([1,1,0,0])

def manual_nb(x,y,alpha=1.):
    raise NotImplementedError("Derive class counts, priors and smoothed log likelihoods")

def main():
    print("Feature order is urgent,thanks. Derive the fractions before comparing a library fit.")

if __name__ == "__main__":
    main()

# Exercise 1: Aggregate by class. Calculate the two class-by-feature count rows and document priors. Expected: Counts [[0,3],[3,1]] in class order[0,1]; priors [.5,.5].
# Exercise 2: Apply Laplace smoothing. Compute the class token probabilities with alpha=1 and V=2. Expected: Likelihoods [[1/5,4/5],[4/6,2/6]], each summing to one.
# Exercise 3: Compute stable posteriors. Score probe [1,0] in log space and normalize with logsumexp. Expected: Posterior [3/13,10/13] for classes[0,1].
# Exercise 4: Verify library parity. Fit MultinomialNB on the exact matrix and compare classes, feature logs and posterior. Expected: All three agree with the independent manual oracle.
# Exercise 5: Inspect prior and empty input. Use an all-zero probe and then change prior to [.9,.1] for the urgent-only probe. Expected: Empty evidence returns prior; changed prior makes class zero more probable.
# Exercise 6: Expose negation and overconfidence. Compare urgent and not urgent under the fixed two-term vocabulary and explain correlated-word evidence. Expected: Identical represented inputs/posteriors; a written warning distinguishes class accuracy from probability calibration.

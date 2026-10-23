import numpy as np
START=np.array([.6,.4])
TRANSITION=np.array([[.7,.3],[.4,.6]])
EMISSION=np.array([[.6,.1],[.2,.7]])

def viterbi(start,transition,emission):
    raise NotImplementedError("Implement scores and backpointers after a hand trace")

def main():
    print("Two-state probability fixtures loaded. Record your trace and implement the six tasks.")

if __name__ == "__main__":
    main()

# Exercise 1: Trace the first column. Compute initialization log scores for the first fixture before any transition. Expected: Exponentiated initial scores are [0.36,0.04].
# Exercise 2: Implement backpointers. Implement Viterbi and decode the first two-token fixture. Expected: Path [0,1], probability 0.0756 and two labels for two observations.
# Exercise 3: Compare an independent oracle. Enumerate all four two-state paths and compare the optimum with the decoder; then run the persistent-transition fixture. Expected: First optimum N,V at 0.0756; second optimum V,V at 0.1386.
# Exercise 4: Handle boundaries. Test an empty sequence, an all-zero emission row and exact ties. Expected: Empty path/log score 0; impossible row raises ValueError; tied fixture chooses [0,0].
# Exercise 5: Validate BIO structure. Implement strict BIO validation for the three stated sequences. Expected: Valid [B-ORG,I-ORG,O]; reject leading I-ORG and a PER-to-ORG continuation.
# Exercise 6: Compare token and entity evidence. Analyze the gold/predicted three-tag example and explain the exact-span result. Expected: Token accuracy 2/3 but zero exactly recovered two-token ORG entities.

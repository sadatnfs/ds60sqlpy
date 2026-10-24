import numpy as np
COUNTS=np.array([[4.,3.,0.],[3.,4.,0.],[0.,0.,6.]])

def ppmi(counts):
    raise NotImplementedError("Implement masked PMI from explicit corpus totals")

def main():
    print("The authored context matrix is ready. Trace counts before implementing the six tasks.")

if __name__ == "__main__":
    main()

# Exercise 1: Count a local window. Implement radius-one co-occurrence for the two-token vocabulary and cat pet cat. Expected: Matrix [[0,2],[2,0]] with total four directed context events.
# Exercise 2: Protect document boundaries. Compare one three-token document with separate one-token documents. Expected: Separate documents yield zero context events; no cross-document pair is created.
# Exercise 3: Implement finite PPMI. Compute PPMI for the supplied 3-by-3 counts and an all-zero matrix. Expected: First cell log(80/49); all values finite/nonnegative; zero-count cells and empty matrix remain zero.
# Exercise 4: Handle cosine carefully. Compare the first two PPMI rows, the first/third rows and a zero vector. Expected: Positive first-pair similarity, zero cross-group similarity, None for a zero-norm comparison.
# Exercise 5: Inspect rank-two compression. Construct U_k times singular values and reconstruct with V_k transpose. Expected: Positive reconstruction error smaller than the matrix norm; first two reduced rows have cosine one.
# Exercise 6: Test geometric invariance. Rotate both two-dimensional embeddings by the same orthogonal matrix and compare cosine. Expected: Cosine unchanged; a written explanation rejects unique semantic meaning for one coordinate.

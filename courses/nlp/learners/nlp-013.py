DOCS=["cat kitten pet","dog puppy pet","car wheel road","truck wheel road"]

def fit_and_compare(documents):
    raise NotImplementedError("Fit the three specified models and inspect their different contracts")

def main():
    print("Four authored documents loaded. Keep numerical component IDs separate from human labels.")

if __name__ == "__main__":
    main()

# Exercise 1: Build the corpus matrix. Fit a count vocabulary on the four authored documents and retain its column mapping. Expected: Four rows with a fixed vocabulary; held-out newplanet does not add a column.
# Exercise 2: Fit and inspect LSA. Fit two-component TruncatedSVD on TF-IDF and reconstruct the matrix. Expected: Document coordinates shape(4,2); reconstruction error below the zero-matrix baseline.
# Exercise 3: Fit nonnegative components. Fit two-component NMF on counts and inspect pet and wheel loadings. Expected: W and H nonnegative; pet and wheel have different dominant component indices.
# Exercise 4: Inspect LDA mixtures. Fit actual two-topic LDA to the count matrix and inspect document mixtures. Expected: Four rows, two columns and each row sums to one.
# Exercise 5: Align topic identities. Compare H with its reversed row order using cosine and assignment. Expected: Permutation[1,0] and matched similarities[1,1].
# Exercise 6: Write an error-aware topic interpretation. Label one component using top words and source documents, then state what remains unproven. Expected: A label linked to concrete words/documents, plus limits on uniqueness, coherence and downstream causal meaning.

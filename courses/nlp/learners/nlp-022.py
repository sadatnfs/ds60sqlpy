DOCS={"d0":"router reset","d1":"router router reset guide","d2":"payment failed"}

def bm25(documents,query,k1=1.2,b=.75):
    raise NotImplementedError("Implement the declared term score and preserve document IDs")

def main():
    print("Three lexical retrieval documents loaded. Keep retrieval, permission and answer support separate.")

if __name__ == "__main__":
    main()

# Exercise 1: Construct postings. Build the inverted index from the three documents. Expected: router postings{d0,d1}; term frequency and document frequency remain distinct.
# Exercise 2: Reproduce BM25 by hand. Calculate d0's router reset score with the stated k1,b and IDF variant. Expected: Implementation matches the explicit formula; d0>d1>d2=0.
# Exercise 3: Handle unsupported queries. Score unseen and inspect the result semantics. Expected: All numerical scores zero; the application should report no lexical evidence rather than a meaningful top result.
# Exercise 4: Implement reciprocal-rank fusion. Fuse the two supplied rankings with k=60. Expected: b first with score1/62+1/61; duplicate IDs in one ranking rejected.
# Exercise 5: Compute nDCG and MRR. Evaluate [d2,d0,d1] using the declared graded relevance. Expected: MRR.5 and nDCG=(7/log2(3)+3/2)/(7+3/log2(3)).
# Exercise 6: Enforce the permitted corpus. Restrict searchable documents to d0 before scoring. Expected: Only d0 appears in results; a written handoff records source version and support limits.

TRAIN = ["tea tea cup", "coffee cup"]


def manual_tfidf(documents):
    raise NotImplementedError("Derive counts, DF, IDF and row normalization")


def main():
    print("Two local documents loaded. Keep the training vocabulary frozen for query tests.")


if __name__ == "__main__":
    main()

# Exercise 1: Count documents, not occurrences. Calculate DF for the three sorted terms from the two-document corpus. Expected: [1,2,1] for [coffee,cup,tea].
# Exercise 2: Match the IDF formula. Implement the stated smoothed IDF and compare with vectorizer.idf_. Expected: [log(3/2)+1,1,log(3/2)+1] in the verified vocabulary order.
# Exercise 3: Build the normalized rows. Construct both weighted rows manually and normalize each nonzero row. Expected: Manual dense oracle matches the 2-by-3 sparse result within tolerance.
# Exercise 4: Compute sparse cosine. Transform query tea and multiply X by its transpose. Expected: First score 2a/sqrt(1+4a^2); second score zero.
# Exercise 5: Handle OOV without refitting. Transform matcha and empty text, then compare the vocabulary before/after. Expected: Zero nonzero entries and unchanged vocabulary; record an explicit no-known-terms outcome.
# Exercise 6: Change one weighting choice. Enable sublinear_tf without normalization and inspect the tea weight. Expected: Tea weight becomes (1+log(2))*a, distinct from 2a.

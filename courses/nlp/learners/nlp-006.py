TRAIN=[["we","like","tea"],["we","like","coffee"],["they","like","tea"]]

def fit_bigram(documents,alpha=1.):
    raise NotImplementedError("Count sentence-bounded transitions and freeze the vocabulary")

def main():
    print("Three authored sentences loaded. Derive the four likelihood factors before coding.")

if __name__ == "__main__":
    main()

# Exercise 1: Construct the event vocabulary. Fit the authored sentences with EOS and UNK but no predicted BOS. Expected: Seven prediction targets, five observed words plus EOS/UNK.
# Exercise 2: Derive smoothed rows. Calculate the four conditional factors for we like tea at alpha=1. Expected: [0.3,1/3,0.3,1/3].
# Exercise 3: Implement log scoring. Return log likelihood, perplexity and predicted-event count. Expected: Joint probability .01, four events and perplexity sqrt(10).
# Exercise 4: Prove normalization. Sum probabilities over the frozen vocabulary for BOS,we,like and UNK. Expected: Each row sums to one within numerical tolerance.
# Exercise 5: Keep evaluation immutable. Score we like cocoa and compare model state before and after. Expected: Finite score; cocoa absent from vocabulary; counts and vocabulary unchanged.
# Exercise 6: Explain empty and incomparable scores. Score empty raw input and explain why tokenizer or EOS changes invalidate naive perplexity comparisons. Expected: One EOS prediction with perplexity 10; a written comparison lists tokenization, corpus and boundary conventions.

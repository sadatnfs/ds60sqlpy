EXAMPLES=[["I","saw","her"],["the","saw","broke"],["the","old","saw"]]

def lemma(word,pos):
    raise NotImplementedError("Implement only the explicit covered mappings")

def valid_dependency_tree(heads):
    raise NotImplementedError("Check indices, one root and cycles")

def main():
    print("Authored language examples loaded. Preserve the known rule failure in your analysis.")

if __name__ == "__main__":
    main()

# Exercise 1: Retain grammatical context. Implement the four explicit lemma mappings and preserve raw/POS/lemma records. Expected: saw/VERB -> see; saw/NOUN -> saw; studies/NOUN -> study; better/ADJ -> good.
# Exercise 2: Trace the context rule. Implement the one-token determiner rule for saw in the first two sentences. Expected: I saw her gives VERB; the saw broke gives NOUN.
# Exercise 3: Preserve a known error. Run the old saw and compare with an independently stated NOUN label. Expected: The rule returns VERB, and the error is recorded rather than relabeled as correct.
# Exercise 4: Validate head indices. Check one-root, range and cycle rules on the supplied arrays. Expected: Accept [1,-1,1]; reject [1,0,-1],[-1,-1],[2,-1] and empty input.
# Exercise 5: Separate structure from meaning. Compare [1,-1,1] and [1,-1,0] for I saw her. Expected: Both structurally valid; only the first matches the intended head assignment.
# Exercise 6: Choose task-specific normalization. Explain whether tense and number should be collapsed for search versus event extraction. Expected: A concrete policy preserves raw text and names at least one lost distinction for each transformation.

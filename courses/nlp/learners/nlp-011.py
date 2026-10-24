TEXT = "Ada joined Acme Labs in Paris."
LEXICON = {"Ada": "PER", "Acme": "ORG", "Acme Labs": "ORG", "Paris": "LOC"}


def extract_entities(text, lexicon):
    raise NotImplementedError("Return auditable raw spans after reading the guide")


def main():
    print(TEXT)
    print("Implement span extraction, exact scoring and the declared relation boundary.")


if __name__ == "__main__":
    main()

# Exercise 1: Extract raw spans. Implement the dictionary matcher for the three-entity sentence. Expected: Exact spans [0,3),[11,20),[24,29) and correct PER/ORG/LOC types.
# Exercise 2: Handle overlap and repetition. Include Acme and Acme Labs in the lexicon; also match Ada met Ada. Expected: Longer organization wins; repeated Ada mentions occupy [0,3) and [8,11).
# Exercise 3: Treat names as data. Match the literal C++ Labs and reject an empty lexicon name. Expected: C++ Labs occupies [0,8); empty names raise a clear error.
# Exercise 4: Compute entity metrics. Compare the stated three gold mentions with the two predicted mentions. Expected: TP=1,FP=1,FN=2,precision=.5,recall=1/3,F1=.4.
# Exercise 5: Extract directed relations. Implement the strict affirmative acquisition grammar and reverse the company order. Expected: Roles reverse exactly; negation and rumor-prefixed sentences abstain.
# Exercise 6: Review coreference and scope. Explain why Ada told Bea that she joined Acme Labs cannot be resolved by nearest-name matching alone. Expected: A written ambiguity record identifies Ada/Bea candidates and withholds a confirmed person-organization relation.

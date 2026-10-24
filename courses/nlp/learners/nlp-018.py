TEXT="服务正常"
PROBES=["the service is ready","el servicio es correcto","bank","the servicio es ready"]

def language_hint(text):
    raise NotImplementedError("Implement only the declared cue rule with abstention")

def main():
    print("Unicode and domain-shift fixtures loaded. Preserve raw strings and unknown outcomes.")

if __name__ == "__main__":
    main()

# Exercise 1: Measure representation units. Count code points, UTF-8 bytes and whitespace segments for the supplied Chinese string. Expected: Counts4,12,1 respectively, with no claim that whitespace identifies linguistic words.
# Exercise 2: Retain ambiguous language. Implement the narrow cue rule and test English,Spanish,bank and the mixed cue sentence. Expected: en,es,None,None under the declared cue inventory.
# Exercise 3: Trace normalization loss. Apply mark removal to résumé and compare with the original resume string. Expected: Both transformed strings equal resume although raw strings differ.
# Exercise 4: Check length-changing case operations. Inspect lowercased İ and casefolded Straße. Expected: i plus combining dot has length2; Straße casefolds to strasse.
# Exercise 5: Report language slices. Compute pooled and equal-language accuracy from the two sample arrays. Expected: English.9,Spanish.5,pooled5/6,macro.7 with counts10 and2.
# Exercise 6: Design target-domain evidence. Analyze charge in payment versus battery messages and propose a held-out transfer evaluation. Expected: A plan includes target labels, ambiguous cases, source/target family separation and an abstention policy.

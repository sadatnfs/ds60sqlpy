DOCS=[{"id":"policy","version":1,"published":1,"expires":8,"roles":["ops"]},
      {"id":"policy","version":2,"published":7,"expires":20,"roles":["ops"]}]

def eligible(documents,role,now):
    raise NotImplementedError("Enforce trusted role and validity before context construction")

def main():
    print("Version and monitoring fixtures loaded. Separate drift, delayed labels and source authorization.")

if __name__ == "__main__":
    main()

# Exercise 1: Filter permission and freshness. Apply the role/time rule to the three source records at time10. Expected: Only policy version2 for ops; unknown role and expired time30 yield no records.
# Exercise 2: Fingerprint content reproducibly. Hash canonical records, reverse their input order and change one text field. Expected: Reordering leaves hash unchanged; text change produces a different hash.
# Exercise 3: Measure a defined drift. Compute total variation for [50,50] and [80,20]. Expected: Distance.3; negative,nonfinite or zero-total count vectors are rejected.
# Exercise 4: Respect label maturity. Evaluate predictions[1,1,0] with labels[1,None,0], then an all-unknown case. Expected: Two mature cases with accuracy1; all-unknown returns count0 and no accuracy.
# Exercise 5: Treat external text as data. Store the adversarial fixture in an evidence packet and apply the synthetic email redaction. Expected: Text remains inert; only the declared email pattern is replaced; no broad anonymization claim.
# Exercise 6: Write a recovery and monitoring contract. Specify a stale-document incident with versions,diagnostics,rollback/reindex choice and acceptance evidence. Expected: A concrete record distinguishes observed failure,hypothesis,authorized action and verified recovery.

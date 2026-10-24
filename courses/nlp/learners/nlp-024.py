TRAIN_TEXTS=["router outage packet loss","network outage router","invoice payment refund","billing invoice payment"]
TRAIN_LABELS=["network","network","billing","billing"]
REQUEST="TKT-301 router packet loss"

def analyze(text,role,now):
    raise NotImplementedError("Build the staged parser/classifier/evidence packet with explicit failure states")

def main():
    print("Capstone fixtures loaded. Keep categories,source evidence and operational actions distinct.")

if __name__ == "__main__":
    main()

# Exercise 1: Audit family separation. Compare training and held-out family inventories before fitting. Expected: No shared families; two held-out labels match the stated network/billing probes.
# Exercise 2: Implement exact identifier extraction. Accept one TKT-301 and reject missing,multiple or four-digit variants. Expected: Canonical TKT-301; three malformed/ambiguous cases raise ValueError.
# Exercise 3: Fit the real classifier and expose OOV. Train the pipeline and test the two held-out probes plus botanical specimen. Expected: Expected labels for represented probes; unsupported-vocabulary for the all-OOV message.
# Exercise 4: Retrieve current permitted evidence. Run the supported network case for ops at time10. Expected: Exactly network version2 and the unchanged approval-rule quote; old version absent.
# Exercise 5: Exercise failure paths. Repeat under billing role,time30 and malformed-ID inputs. Expected: Insufficient-evidence for role/time changes; explicit parser failures; no unauthorized or stale quote.
# Exercise 6: Deliver a reviewable analytics packet. Record normal and failure results with evidence hash,component identities and limitations. Expected: A reviewer can reproduce parsing,prediction,source eligibility and quote provenance; no claim of generative or production-quality coverage from the toy corpus.

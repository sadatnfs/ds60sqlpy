# nlp-024: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Audit family separation

The split prevents direct family identity from crossing the boundary in this fixture. It remains too small and easy for a production accuracy claim. A complete report retains the exact texts and labels so the scope of the regression evidence is visible.

**Expected:** No shared families; two held-out labels match the stated network/billing probes.

## Exercise 2: Implement exact identifier extraction

A regex that captures the first three digits of TKT-3019 would silently create the wrong identity. Counting matches also prevents an arbitrary first-ID choice in a message containing two tickets. The parser proves format consistency only, not external ticket existence.

**Expected:** Canonical TKT-301; three malformed/ambiguous cases raise ValueError.

## Exercise 3: Fit the real classifier and expose OOV

The fitted classifier performs genuine local learning, but an empty feature row contains no lexical evidence. Detecting that condition prevents a prior-based output from masquerading as an informed domain judgment. Preserve this boundary when changing the representation.

**Expected:** Expected labels for represented probes; unsupported-vocabulary for the all-OOV message.

## Exercise 4: Retrieve current permitted evidence

The deterministic filters enforce a separate evidence eligibility contract. The quote retains source identity and version, allowing a reviewer to verify what it says. Its presence supports a procedure statement, not an assertion about completed operational work.

**Expected:** Exactly network version 2 and the unchanged approval-rule quote; old version absent.

## Exercise 5: Exercise failure paths

Independent perturbations localize the boundary being tested. A category prediction does not override access, and source expiry does not become a classification error. The failure ledger makes the appropriate repair or escalation concrete.

**Expected:** Insufficient-evidence for role/time changes; explicit parser failures; no unauthorized or stale quote.

## Exercise 6: Deliver a reviewable analytics packet

The handoff should include exact fixtures, code/configuration, observed outputs and unsupported cases. It creates a stable interface for later neural retrieval or generation. Any extension must preserve authorization, freshness and provenance while demonstrating task utility on new independent families.

**Expected:** A reviewer can reproduce parsing,prediction,source eligibility and quote provenance; no claim of generative or production-quality coverage from the toy corpus.

## Transfer and limits

The capstone combines the preceding mechanisms into a small domain text-analytics pipeline. It classifies a support message, extracts a ticket identifier, retrieves current permitted procedure evidence and returns an auditable packet. It deliberately stops before free-form generation. A source-quoted evidence packet is a useful deliverable and a clean boundary for a later domain assistant.

The classifier is an actual fitted scikit-learn logistic baseline over authored network and billing messages. The retriever is an explicitly lexical overlap baseline with role and validity filters. The identifier parser accepts one exact three-digit format. No pretrained model, external data or online service is needed. These are genuine limited components, not stand-ins mislabeled as a production language model.

Two held-out text families check that the implementation can apply its fixed vocabulary and model to separate probes. The fixture is tiny and deliberately easy, so two correct predictions establish a regression receipt rather than a reliable accuracy estimate. The capstone emphasizes the complete evidence chain and failure categories that must survive as components become more capable.

## Mechanism review and counterexample

The reference rejects missing, multiple and overlong ticket identifiers. It distinguishes unsupported vocabulary from insufficient permitted evidence. Those categories identify different repair paths: improve parsing contract, expand representative training data, update the authorized corpus or improve retrieval. Automatically fine-tuning the classifier would not repair an expired source document.

The final case study report should show the input, extracted identifier, model category, source IDs/versions, quoted evidence, status and limitations. Include the positive path and each deliberate failure. Record which checks are structural, numerical, task-level or operational. A successful process exit is not enough if an unauthorized source or malformed ID entered the result.

Before scaling, define resource limits, corpus ownership, privacy requirements and review/escalation authority. Evaluate new document families and source changes using the same packet contract. Preserve a simple baseline so a neural or generative extension must demonstrate added utility rather than only more fluent text.

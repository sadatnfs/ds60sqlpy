# NLP005-024 authoring and validation checkpoint

Updated 22 October 2026. All twenty assigned IDs, `nlp-005` through `nlp-024`, are authored and merged into canonical `courses/nlp/lessons.json`. The coordinator merged the registrations; the portable authoring entry point now updates only IDs005-024 while preserving root-owned NLP001-004 artifacts and registrations. The temporary handoff inventory was removed after exact entry parity was verified.

## Complete teaching artifacts

Each ID has a guide, an answer-free learner scaffold under `learners/`, a separate executable reference and explanatory solution under `solutions/`, and a deterministic six-case ledger under `fixtures/`. Across the twenty guides there are approximately 33,228 words, 60 narrated worked examples, 40 executable guide snippets, 120 distinct exercises and 60 answered interview discussions. Explanatory solutions total approximately 13,807 words and each contains at least 600 words. The guides retain direct stable prerequisites and lesson-specific coaching prompts.

The complete prerequisite route includes contextual morphology with a preserved known rule error; exact bigram smoothing and EOS accounting; manual/library TF-IDF and Naive Bayes parity; logistic classification and calibration limits; exact Viterbi with exhaustive-oracle comparison; raw typed entity spans and directed relation abstention; PPMI/SVD embeddings; actual local LSA/NMF/LDA fits; masked pooling and contrastive geometry; genuine NumPy attention with a trained tiny logistic head; target shifting and bounded beam search; overlap-metric counterexamples; multilingual representation limits; annotation agreement and soft labels; weak-label diagnostics and active-review selection; family/time leakage controls; BM25/rank fusion; corpus authorization/freshness/lineage; and a staged domain text-analytics capstone.

The capstone fits a real local classifier, extracts a single exact ticket identifier, retrieves only current role-permitted source text, and produces a source/version/quote packet with an evidence hash. It distinguishes malformed IDs, unsupported vocabulary and insufficient permitted evidence. It does not claim that the quoted procedure was executed or that an extractive packet is a pretrained generator.

## Runtime scope

All twenty references use `python-core`, standard library, NumPy, SciPy and/or scikit-learn. Default execution is fully offline after dependency preparation. No model, corpus, tokenizer, NLTK/spaCy resource or Hub asset is downloaded. All verification IDs remain null; process success does not automatically grade understanding or written exercises.

Handcrafted token vectors are labeled as handcrafted. The NumPy attention layer and tiny head optimization are actual mechanisms, but are not described as pretrained BERT or a complete transformer. The weak-label reference is transparent voting, not a learned Snorkel label model. The sentence-level BLEU teaching variant documents its reference, smoothing and aggregation limits. Retrieval scores, citation support, authorization and factual claims remain separate contracts.

Existing applied-LLM guides and statistics-book chapters are crosslinked for adaptation, grounding and evaluation. These links resolve in the focused tests. Wider pretrained recipes and actual worker/Docker qualification remain coordinated root integration work.

## Executed validation

`python -m pytest -p no:cacheprovider tests/test_nlp_advanced.py -n 4 --dist loadgroup -q` passed **50 tests in 2.50 seconds**, with no failures or skips. The suite executes every guide Python block in order and every reference with socket connections denied, validates all stable IDs and prerequisites, verifies learner/reference separation, and checks real relative links.

Eight negative controls are rejected: dropping EOS from the perplexity denominator, ignoring previous Viterbi path scores, ignoring entity end boundaries, allowing padding keys into attention, crediting unlimited repeated n-grams, turning weak-label ties into negatives, removing document-role filtering, and accepting a three-digit prefix from an overlong ticket ID. Additional boundary checks reject invalid probabilities, fractional weak labels, all-padding encoders and absent token supervision. All twenty reference programs also passed individual execution. Ruff passed `tests/test_nlp_advanced.py`.

The first focused run exposed two content-test gaps: the contextual example lacked an explicit attention-row normalization assertion, and the family-bootstrap explanation needed a fuller account of the excluded known-family case. Both were improved before the passing run. No checks were removed or weakened.

## Portable maintenance and integration handoff

`courses/nlp/authoring/advanced/` contains the explicit original lesson source, worked snippets and a portable `build_all.py` entry point. It derives the repository path from its own location, updates only IDs005-024 and merges those entries into canonical `lessons.json` without changing other entries or executing language-model jobs. Its README documents regeneration and validation.

Root integration completed the initial central manifest merge and owns shared registrations, generated readers, navigation, complete-suite checks, browser behavior and actual Docker receipts. Content authoring performed no Docker/cluster mutation, tool installation, Git staging, commit or push. This author returns to the remaining Kubernetes content after this freeze; Scala/Spark remains separately queued.

After canonical registration, the combined foundation and advanced NLP suite passed **58 tests in 3.03 seconds**. The temporary handoff inventory is gone; both tests and the portable generator use the single canonical lessons.json.

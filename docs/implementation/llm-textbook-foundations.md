# LLM textbook pass: chapters 001-024

Updated 2026-10-23. All 24 assigned theory chapters now have connected textbook openings and explicit bridges to the next chapter. The new prose replaces the earlier purpose summaries rather than being appended as an implementation-status section. Existing detailed derivations, worked programs, six exercise contracts, hints and separate solutions remain in place.

## Concrete chapter improvements

| Chapter | Connected explanation added or strengthened |
| --- | --- |
| 001 | Follows a contract-assistant request through text representation, next-token distributions, generation and independent answer assessment; separates those mechanisms from the three-record/two-family evidence unit. |
| 002 | Builds softmax from relative odds, defines candidate versus question axes, derives the stable shift and explains why the legal candidate set determines the denominator. |
| 003 | Traces a sequence as a path through changing conditional distributions, derives its three loss contributions and connects observed-prefix scoring to generation. |
| 004 | Fits every transition in the literal corpus, explains pseudocounts and vocabulary identity, and shows precisely what a one-token context cannot distinguish. |
| 005 | Connects one-hot cross entropy to observed-event loss, derives total/mean/perplexity and explains the geometric-mean interpretation and padding-induced gradient scaling. |
| 006 | Walks through glyphs, code points, UTF-8 bytes, normalization and model tokens; connects raw identity and normalized identity to citation offsets and provenance. |
| 007 | Explains the subword design problem, byte tuples and boundary marker, deterministic tied pair choice, scan/rewrite policy and frozen validation encoding. |
| 008 | Distinguishes vocabulary, occurrence and feature axes; derives lookup through one-hot selection, repeated-row gradient accumulation and tokenizer/table compatibility. |
| 009 | Separates query/key scoring from value mixing, derives the three causal averages and future-value counterexample, and explains why several independent properties are needed. |
| 010 | Separates content, location and visibility; introduces equivariance before its proof; connects feature statistics and the exact future-token normalization leak. |
| 011 | Traces distinctive feature values through head splitting/rejoining, then explains independent mixtures, output projection, residual cancellation and tokenwise nonlinear transformations. |
| 012 | Separates the model's logits from a decoding policy, constructs sampling intervals and explains temperature, truncation, tie rules and replay state. |
| 013 | Derives shifted prediction events before discussing leakage, separates objective and visibility boundaries, then follows exact/family/representation-fitting information paths. |
| 014 | Connects the full baseline experiment from documents through counts, smoothed rows, two held-out events and a bounded evidence report. |
| 015 | Introduces gradients as local sensitivity, follows backward versus update, derives scalar accumulation and finite differences, then connects those ideas to shared embeddings. |
| 016 | Narrates the entire decoder forward path with defined B/T/V/D notation, head/score/output shapes and the 10,464-parameter versus activation distinction. |
| 017 | Distinguishes rectangular storage from prediction events, traces loss and gradient denominators, and separates target ignore values from valid input IDs and attention masks. |
| 018 | Explains training as an ordered transition of parameters, gradient buffers and optimizer state; derives the global norm reduction and snapshot/logging timing. |
| 019 | Builds a controlled memorization diagnostic from independently owned identical states, explains no-update controls and isolates the narrow conclusion of a fitted batch. |
| 020 | Derives separate activation, loss and gradient scale effects, locates overflow after a finite forward value and connects residual magnitude to numerical stability. |
| 021 | Chooses a split unit from the generalization question, traces whole-family assignment and distinguishes record/raw/normalized/family/assignment identities. |
| 022 | Explains inference restoration versus training continuation, derives Adam's first moment/variance update and separates saved state, forward mode and gradient recording. |
| 023 | Derives the minimum top-p prefix and renormalization, explains policy order and vocabulary remapping, then separates EOS, generated-token caps and total context. |
| 024 | Derives why causal state can be reused, traces four incremental calls and absolute offsets, computes 1,024 raw KV bytes and connects numerical parity to cache ownership. |

The source prose is original explanatory material tied to the existing fixtures. Primary checks use the Transformer and subword papers, Python 3.12 Unicode documentation and PyTorch 2.9 autograd, cross-entropy and Adam documentation, linked at the relevant explanations. Arithmetic examples derived in prose are identified separately from operations actually performed by the reference programs.

## Durable application

Readable inputs live in `courses/llm-theory/authoring/textbook_foundations/llm-001.md` through `llm-024.md`. Each contains the chapter opening and a bridge separated by a marker. `textbook_foundations.py` applies the layer idempotently, preserves the earlier mechanism-review sections and refuses any change to fenced programs or copy-ready prompts. It also leads the original executable pilot run sections with Docker classroom instructions while retaining their explicitly optional native commands.

The coordinated runner is `courses/llm-theory/authoring/apply_textbook.py`. It dispatches 001-024 to this layer and 025-048 to the advanced author's layer. Both existing authoring build entrypoints call it after ordinary guide generation. Shared renderers, plans, manifests, README and application code were not changed by this pass.

For an already generated complete route, the final application command is:

```text
python courses/llm-theory/authoring/apply_textbook.py --require-complete
```

The complete flag requires a prose input for every selected ID. During coordinated authoring, selected IDs can be passed with `--ids`; each layer leaves the other author's range unchanged. The runner checks idempotence and Python-fence parity before saving a guide.

## Verification and limits

The captured before/after receipt is `work/llm-textbook-001-024-parity.json`. All 47 Python worked blocks are byte-identical. All 72 learner and solution artifacts are byte-identical, including explained solutions. Each guide retains six numbered exercise contracts, every local file link resolves, and no em dash was introduced. The application hook additionally checked every fenced block, including copy-ready prompts and optional native commands.

The 24 guide word total changed from 52,510 to 61,294 because the more connected openings replaced shorter summaries and the next-step sections became substantive chapter bridges. These counts describe the edit, not a pedagogical acceptance test. The improvements above, numerical traces and preserved evidence boundaries are the substantive review record.

The focused ML suite reports 110 passed and 125 explicit optional-framework skips in the prepared host environment. The two new prose tools pass Ruff. Existing source-matching Docker receipts remain applicable because no executable program changed. This pass makes no new runtime, generalization, long-context, GPU-performance or production-assistant claim.

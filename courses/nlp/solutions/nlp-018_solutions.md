# nlp-018: Explanatory solutions

The executable reference checks the declared fixtures. It is separate from the learner scaffold and does not certify general task quality.

## Exercise 1: Measure representation units

Each count measures a different object. A model's tokenizer is another transformation and must be measured directly when context budgets matter. The example prevents a common mistake of comparing languages using an English-specific whitespace definition.

**Expected:** Counts4,12,1 respectively, with no claim that whitespace identifies linguistic words.

## Exercise 2: Retain ambiguous language

The rule has no general language-model capability. Its explicit unknown output is preferable to inventing a label from a short ambiguous string. A production identifier requires broader data and a confidence/mixture policy validated for the intended text lengths and domains.

**Expected:** en,es,None,None under the declared cue inventory.

## Exercise 3: Trace normalization loss

The transformation can help broad search but destroys a distinction. Preserve raw values and state the purpose. Treating this as universally harmless cleaning can create incorrect merges, labels or evidence spans.

**Expected:** Both transformed strings equal resume although raw strings differ.

## Exercise 4: Check length-changing case operations

A visible character can map to multiple code points, so indices in the transformed string do not necessarily identify the same raw span. The operation is defined by Unicode/runtime behavior and is not a substitute for a locale-specific linguistic policy.

**Expected:** i plus combining dot has length2; Straße casefolds to strasse.

## Exercise 5: Report language slices

The pooled result weights English five times as heavily because of sample size. Macro averaging gives each language equal influence. Both need an explicit interpretation and uncertainty; neither justifies extrapolating the two-case Spanish result as a precise population rate.

**Expected:** English.9,Spanish.5,pooled5/6,macro.7 with counts10 and2.

## Exercise 6: Design target-domain evidence

Shared spelling does not guarantee shared semantics. A useful adaptation experiment starts with reviewed target-domain examples and a baseline, then changes the implicated component. Evaluate regressions in the original domain and avoid using the final target test set for repeated prompt or weight tuning.

**Expected:** A plan includes target labels, ambiguous cases, source/target family separation and an abstention policy.

## Transfer and limits

Multilingual NLP must distinguish language, script, locale, domain and the individual task. A Latin-script message is not automatically English, a short word can belong to several languages, and one document can mix languages. A system that accepts Unicode text may still tokenize, represent and evaluate some languages poorly. Coverage, efficiency and task quality are separate claims.

This lesson uses local strings to inspect encoding lengths, normalization effects, a deliberately narrow language-hint rule and subgroup aggregation. It does not download or claim a multilingual language identifier or translation model. The small rule recognizes only a few authored cue words and explicitly abstains when evidence is tied or absent.

Domain shift can occur within one language as well as across languages. Charge may concern a payment, an electrical battery or an accusation. A model trained on one domain can assign the wrong sense in another while every token is familiar. Evaluate the actual target population and retain uncertainty rather than assuming shared vocabulary implies shared meaning.

## Mechanism review and counterexample

Suppose a classifier trained on payment complaints flags every message containing charge as billing-related. Battery charge is low exposes a new sense. Inspect source domain, tokenization, context and label definitions before deciding whether to adapt weights. A prompt, retrieval context or a small supervised adaptation can address different failure mechanisms, but each needs held-out target-domain cases.

Keep source and target data identities, annotate ambiguous examples and evaluate whether an abstention fallback is preferable to confident misclassification. Do not infer a person's nationality or demographic traits from the language or name in a message. The task is processing the text under a declared contract.
